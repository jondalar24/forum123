import os
import torch # type: ignore

from langchain.text_splitter import RecursiveCharacterTextSplitter # type: ignore
from langchain.vectorstores import Chroma # type: ignore
from langchain.chains import RetrievalQA # type: ignore
from sentence_transformers import SentenceTransformer, util # type: ignore
from ibm_watson_machine_learning.foundation_models.extensions.langchain import WatsonxLLM # type: ignore
from ibm_watson_machine_learning.foundation_models import Model # type: ignore
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams # type: ignore
from langchain.schema import Document # type: ignore
from dotenv import load_dotenv,find_dotenv # type: ignore
from langchain import PromptTemplate # type: ignore
#from huggingface_hub import InferenceClient # type: ignore

from src.database import session_var
from src.posts.models import Post
from src.topics.models import Topic

# Check for GPU availability and set the appropriate device for computation.
#DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

# Global variables
conversation_retrieval_chain = None
chat_history = []
llm_hub = None
embeddings = None

# Cargar la API Key desde el archivo .env
dotenv_path = find_dotenv()
print(f"Ruta del archivo .env: {dotenv_path}")# Comprobación

load_dotenv(dotenv_path)

# Configurar las API key de Hugging Face y Watsonx
#HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
Watsonx_API = os.getenv("WATSONX_API")
Project_id = os.getenv("PROJECT_ID")

# Clase personalizada para manejar los embeddings en Chroma
class CustomEmbeddings:
    def __init__(self, model):
        self.model = model

    def embed_documents(self, texts):
        # Convierte una lista de textos en embeddings, y convierte cada embedding a lista
        embeddings = [self.model.encode(text).tolist() for text in texts]  # Convertir a lista
        return embeddings

    def embed_query(self, text):
        # Convierte una única consulta en un embedding y convierte a lista
        embedding = self.model.encode(text).tolist()
        return embedding

# Creamos una plantilla de prompt para ayudar a dar contexto
prompt = PromptTemplate(
    input_variables=["question", "context"],
    template=(
        "Pregunta: {question}\n"
        "Proporciona una respuesta basada únicamente en la información relevante siguiente y sin añadir detalles adicionales.\n"
        "{context}\n"
        "Respuesta breve y concisa basada solo en el contexto:"
    )
)

#1) configurar el modelo LLM y de embeddings
def init_llm():
    global llm_hub, embeddings
    print("Inicializando el modelo LLM...")

    #configurar credenciales y parámetros para el llm
    credentials = {
        'url': "https://eu-de.ml.cloud.ibm.com",
        'apikey': Watsonx_API
    }
    params = {
        GenParams.MAX_NEW_TOKENS: 200,
        GenParams.TEMPERATURE: 0.0,
        "language": "es"
    }

    # Inicialización del modelo LLAMA3 en Watsonx
    LLAMA3_model = Model(
        model_id= 'meta-llama/llama-3-8b-instruct',
        credentials=credentials,
        params=params,
        project_id=Project_id
    )

    # Configuración de LLM para LangChain
    llm_hub = WatsonxLLM(model=LLAMA3_model)

    # Inicializar embeddings usando Hugging Face
    print("iniciando sentenceTransformers...")
    hf_model = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = CustomEmbeddings(hf_model)

# 2)Función para obtener los posts más relevantes escritos por profesores
def get_relevant_topics_and_posts():
    session = session_var.get()  # Usar la sesión actual de la base de datos

    # Extraer todos los topics y posts escritos por profesores de la base de datos
    posts = session.query(Post).filter_by(role="teacher").all()  # Usamos "teacher" como está en la base de datos
    topics = session.query(Topic).all()
    
    # Crear una lista de concatenaciones de los Topics y Posts asociados
    topic_posts_content = []
    for topic in topics:
        # Obtener los posts asociados a este topic escritos por profesores
        associated_posts = [
            f"Respuesta del profesor: {post.body}"
            for post in posts 
            if post.topic_id == topic.id
        ]

        # Si hay posts de profesores asociados, agregar el topic y los posts al contenido relevante
        if associated_posts:
            # Concatenar el título y descripción del Topic
            topic_content = f"Título: {topic.title}\nPregunta del alumno: {topic.description}\n"
            # Añadir los posts de profesores al contenido del topic
            topic_content += "\n".join(associated_posts)
            topic_posts_content.append(topic_content)
            print(f"Contenido relevante del topic '{topic.title}': {topic_content}")

    # Devolver solo los topics con posts de profesores
    print(f"Contenido final relevante (topics con respuestas de profesores): {topic_posts_content}")
    
    return topic_posts_content

# 3)Partir el contenido en fragmentos (chunks) para crear embeddings
def split_content_into_chunks(content_list):
    print("partir el contenido en chunks...")
    
    if not content_list or not all(isinstance(content, str) for content in content_list):
        raise ValueError("Invalid content passed to split_content_into_chunks. Expected a list of strings.")
   
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)
    
    #crear chunks y empaquetarlos como Document
    documents = []
    for content in content_list:
        chunks = text_splitter.split_text(content)
        documents.extend([Document(page_content=chunk) for chunk in chunks])
    
    return documents

# 4) Crear el índice de embeddings en Chroma
def create_embeddings_index(documents):
    print("creando el índice en chroma...")
    db = Chroma.from_documents(
        documents=documents,
        embedding=embeddings
    )
    return db

# 5) Comprobar similitudes para temas relevantes
def check_relevance_with_similarity(question, topic_posts_content, similarity_threshold=0.5, num_topics=5):
    print("Verificando similitudes entre la pregunta y los topics/posts...")
    
    # Generar embeddings para la pregunta y el contenido
    question_embedding = embeddings.embed_query(question)
    topic_post_embeddings = embeddings.embed_documents(topic_posts_content)
    
    # Calcular similitudes entre la pregunta y los topics/posts
    similarities = util.pytorch_cos_sim(question_embedding, topic_post_embeddings)
    print(f"Similaridades: {similarities}")
    
    # Manejar casos de una única similitud (dimensión 0)
    if similarities.dim() == 0:
        # Si solo hay una similitud, convertimos a una lista con un único elemento
        similarities = torch.tensor([[similarities.item()]])
    elif similarities.dim() == 1:
        # Si hay una única fila, añadimos una dimensión extra
        similarities = similarities.unsqueeze(0)
    
    # Depurar cada similitud
    for idx, similarity in enumerate(similarities[0]):  # Aseguramos iteración sobre la primera fila
        print(f"Similitud con el topic/post en posición {idx}: {similarity:.4f} ({topic_posts_content[idx]})")
    
    # Filtrar y seleccionar el índice con la mayor similitud por encima del umbral
    max_index = -1
    max_similarity = similarity_threshold
    for idx, similarity in enumerate(similarities[0]):
        if similarity > max_similarity:
            max_similarity = similarity
            max_index = idx
    
    if max_index == -1:    
        return None  # No hay temas relevantes
    
    # Devolver solo el contenido más relevante
    relevant_content = [topic_posts_content[max_index]]
    print(f"Contenido seleccionado: {relevant_content}")

    return relevant_content

# 6) Configurar la cadena de recuperación para responder preguntas
def configure_retrieval_chain(db):
    print("Configurando la cadena de recuperación (RetrievalQA)...")
    return RetrievalQA.from_chain_type(
        llm=llm_hub,
        chain_type="stuff",
        retriever=db.as_retriever(search_type="mmr", search_kwargs={'k': 2, 'lambda_mult': 0.15}),
        return_source_documents=False,
        input_key="question",
        chain_type_kwargs={"prompt": prompt}
    )

# 7) Procesar la pregunta del usuario y obtener la respuesta
def ask_forum_question(question,topic):
    global conversation_retrieval_chain, chat_history
    relevant_content_list= None
    relevant_content = None
    chat_history= []

    # Cargar y filtrar el contenido relevante para la pregunta
    relevant_content_list = get_relevant_topics_and_posts()    
    relevant_content = check_relevance_with_similarity(question, relevant_content_list)
    print(f"Contenido relevante después de filtrar por similitud: {relevant_content}")  # Depuración


    if not relevant_content:
        # Marcar el topic como pendiente y regresar el mensaje
        session = session_var.get()
        topic.pending_for_teacher = True
        session.commit()
        
        return "Tu pregunta ha sido enviada al profesor."
       
    
    # Dividir en fragmentos y crear embeddings para los temas y posts relevantes
    documents = split_content_into_chunks(relevant_content)
    print(f"Documentos generados (chunks): {documents}")  # Depuración

    
    # Crear el índice en el store vectorial
    db = create_embeddings_index(documents)
    print(f"Índice creado en Chroma.")

    # Configurar la cadena de recuperación
    conversation_retrieval_chain = configure_retrieval_chain(db)
    print(f"Cadena de recuperación configurada.")  # Depuración


    # Generar una respuesta usando los fragmentos relevantes como contexto    
    output = conversation_retrieval_chain({"question": question, "chat_history": chat_history})
    answer = output["result"]

    # Procesar la respuesta para cortar cualquier contenido adicional más allá de la información relevante
    if "Respuesta dada" in answer:
        answer = answer.split("Respuesta dada", 1)[1]  # Mantener solo lo relevante
    answer = answer.strip()

    # Actualizar el historial de conversación
    chat_history.append((question, answer))
    
    session = session_var.get()
    previous_posts = session.query(Post).filter_by(topic_id=topic.id, pending_for_teacher=True).all()
    for post in previous_posts:
        post.pending_for_teacher = False

    topic.pending_for_teacher = False
    session.commit()

    if not answer:
        return "No se pudo procesar una respuesta válida."
    
    
    return answer     

