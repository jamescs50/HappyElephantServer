from flask import Blueprint

bp = Blueprint('shop_list', __name__)

from app.shop_list import routes