from app import app
import io
from flask import Response

@app.route('/')
@app.route('/index')
def index():
    return "Welcome to the cult of the happy elephant."