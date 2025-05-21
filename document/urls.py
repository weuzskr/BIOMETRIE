
from starterkit import app
from _keenthemes.settings import settings

from flask import Blueprint
from document.views import UploadView


documents_bp = Blueprint('documents', __name__)

documents_bp.add_url_rule('/upload',view_func=UploadView.as_view('upload'))


#app.add_url_rule('/upload', view_func=UploadView.as_view('upload'))
