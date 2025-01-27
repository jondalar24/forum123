import os
from sentence_transformers import SentenceTransformer

# Descarga explícita del modelo
model_name = 'all-MiniLM-L6-v2'
model = SentenceTransformer(model_name)

# Verificar la ruta de descarga en la caché predeterminada
cache_path = os.path.join(os.path.expanduser("~"), ".cache", "torch", "sentence_transformers", model_name)
print("Ruta de caché predeterminada del modelo:", cache_path)

# Comprobación si los archivos existen en esa ruta
if os.path.exists(cache_path):
    print("Modelo descargado correctamente en:", cache_path)
else:
    print("Modelo no encontrado en la ruta de caché predeterminada.")