from app import db
from datetime import datetime


class WeatherData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    source_topic = db.Column(db.String(120), index=True)
    data = db.Column(db.String(120))

