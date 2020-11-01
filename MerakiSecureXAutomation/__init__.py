import logging
import azure.functions as func
from ..FlaskApp.app import app as application


def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return func.WsgiMiddleware(application).handle(req, context)
