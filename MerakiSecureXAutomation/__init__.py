import logging
import azure.functions as func
from ..FlaskApp.app import app as application


# def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
#     return func.WsgiMiddleware(application).handle(req, context)

#def main(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
#    return AzureFunctionsWsgi(application).main(req, context)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    name = req.params.get('name')
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get('name')

    if name:
        return func.HttpResponse(f"Hello {name}!")
    else:
        return func.HttpResponse(
            "Please pass a name on the query string or in the request body",
            status_code=400
        )
