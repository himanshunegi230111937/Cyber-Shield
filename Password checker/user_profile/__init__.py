from flask import Blueprint

profile_bp = Blueprint('profile_bp', __name__, template_folder='../templates', static_folder='../static')

from . import routes
