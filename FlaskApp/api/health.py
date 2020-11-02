from flask import Blueprint
from .utils import get_jwt, jsonify_data

health_api = Blueprint('health', __name__)


@health_api.route('/health', methods=['POST'])
def health():
    return jsonify_data({'status': 'ok'})


@health_api.route('/health', methods=['GET'])
def health_get():
    return jsonify_data({'status': 'ok'})
