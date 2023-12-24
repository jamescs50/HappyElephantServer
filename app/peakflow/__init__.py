from flask import Blueprint

bp = Blueprint('peakflow', __name__)

from app.peakflow import routes