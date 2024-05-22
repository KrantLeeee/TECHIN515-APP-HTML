from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class WeevilData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    weevil_number = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"WeevilData('{self.image_url}', '{self.description}', '{self.timestamp}', {self.weevil_number})"
