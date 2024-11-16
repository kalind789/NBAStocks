from flask import Flask, render_template, redirect, url_for, request, flash, json, jsonify
from flask_cors import CORS  # Import Flask-Cors
from models import db, User  # Assuming models.py contains the User model with username, email, and password fields
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import random

from apscheduler.schedulers.background import BackgroundScheduler
from data_collection import update_player_stock

# Scheduler setup
scheduler = BackgroundScheduler()

# Example player IDs - replace these with your actual IDs
player_ids = [1630173, 203500, 1628389]

def scheduled_stock_update():
    for player_id in player_ids:
        update_player_stock(player_id)

scheduler.add_job(scheduled_stock_update, 'interval', hours=1)  # Runs every hour
scheduler.start()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'  # Use your database URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong key
db.init_app(app)

# Enable CORS
CORS(app)  # This will allow CORS for all routes by default

# Initialize Flask-Migrate
migrate = Migrate(app, db)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/index')
@login_required
def index():
    return render_template("index.html")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        # email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Basic validation
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('signup'))

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))

        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        # existing_email = User.query.filter_by(email=email).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))
        # if existing_email:
        #     flash('Email already registered. Please choose a different one.', 'danger')
        #     return redirect(url_for('signup'))

        # Hash the password
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Create a new user with the hashed password and email
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        
        #testing nvm

        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        # Check if user exists and the password is correct
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/view')
@login_required
def view():
    return render_template("view_stocks.html")

@app.route('/profile')
@login_required
def profile():
    return render_template("profile.html")

@app.route('/temperature', methods=["GET", "POST"])
def temperature():
    temperature = []
    for i in range(1, 10):
        temperature.append(random.randint(0, 100))
    data = {
        "temperature": temperature
    }
    return jsonify(data)

@app.route('/update_player_stocks')
@login_required  # Optional if you want to restrict access
def update_player_stocks():
    player_ids = [1630173, 203500, 1628389]  # Example IDs
    for player_id in player_ids:
        update_player_stock(player_id)
    flash('Player stocks updated successfully!', 'success')
    return redirect(url_for('index'))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)