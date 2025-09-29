from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with waste reports
    waste_reports = db.relationship('WasteReport', backref='user', lazy=True, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set the password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)

    def add_points(self, points):
        """Add points to user's total"""
        self.points += points

    def __repr__(self):
        return f'<User {self.username}>'

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'points': self.points,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class WasteReport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    waste_type = db.Column(db.String(50), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    points_earned = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<WasteReport {self.waste_type} - {self.weight}kg>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'waste_type': self.waste_type,
            'weight': self.weight,
            'points_earned': self.points_earned,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
