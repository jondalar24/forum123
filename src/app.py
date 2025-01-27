"""Main package for source code."""

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from src.ia.worker import init_llm

import src.api.routes
import src.index.routes
import src.posts.routes
import src.topics.routes
import src.users.routes
import src.admin.routes
import src.ia.routes
from src.config import Config


app = Flask(__name__)
app.register_blueprint(src.users.routes.bp)
app.register_blueprint(src.topics.routes.bp)
app.register_blueprint(src.index.routes.bp)
app.register_blueprint(src.posts.routes.bp)
app.register_blueprint(src.api.routes.bp)
app.register_blueprint(src.admin.routes.bp)
app.register_blueprint(src.ia.routes.bp)
app.config.from_object(Config)

# Llama a init_llm() una sola vez al arrancar la aplicación
try:
    init_llm()
except Exception as e:
    print("Error al inicializar LLM: ",e)


if Config.PROXIES:  # pragma: no cover
    # flask app has to know that it's behind a proxy
    # see: https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/
    app.wsgi_app = ProxyFix(  # type: ignore
        app.wsgi_app,
        x_for=Config.PROXIES_X_FOR,
        x_proto=Config.PROXIES_X_PROTO,
        x_host=Config.PROXIES_X_HOST,
        x_prefix=Config.PROXIES_X_PREFIX,
    )
