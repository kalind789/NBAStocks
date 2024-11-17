# Defines SQL Alechemy models for interacting with application database
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    portfolio = db.relationship('PortfolioEntry', backref='user', lazy=True)

    def __repr__(self):
        return f"User(username: {self.username}, email: {self.email})"

class PortfolioEntry(db.Model):
    __tablename__ = 'portfolio_entry'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    player_stock_id = db.Column(db.Integer, db.ForeignKey('player_stock.id'), nullable=False)
    shares = db.Column(db.Integer, nullable=False)  # Number of shares owned   

class PlayerStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    player_first_name = db.Column(db.String(100), nullable=False)
    player_last_name = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Float, nullable=False)
    player_id = db.Column(db.Integer, unique=True, nullable=False)  


    def __repr__(self):
        return f"PlayerStock, name is: {self.player_first_name} {self.player_last_name}), value: {self.value}"
