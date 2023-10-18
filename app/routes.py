from app import app
from app.models import  WeatherData
import io
from flask import Response,render_template

@app.route('/')
@app.route('/index')
def index():
    return render_template('app/dashboard.html', title=('Home'))

@app.route('/data')
def data():
    d = WeatherData.query.all()
    return  render_template('app/data.html',title='Data',data=d)