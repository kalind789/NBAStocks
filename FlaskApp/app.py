from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash, json, jsonify, Response
from flask_cors import CORS
from data_collection import calculate_fantasy_points, fetch_player_data  

from models import db, User, PortfolioEntry
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import random
import pandas as pd
from models import PlayerStock

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
    csv_path = 'static/players.csv'  # Path to the CSV file
    try:
        player_df = pd.read_csv(csv_path)
        # Ensure the required columns exist
        if 'full_name' not in player_df.columns or 'picture_link' not in player_df.columns:
            raise ValueError("CSV file must contain 'full_name' and 'picture_link' columns.")
        
        # Convert the DataFrame columns to lists
        players_names = player_df['full_name'].tolist()
        players_pictures = player_df['picture_link'].tolist()
        
        # Combine the names and pictures into a list of dictionaries
        players = [{'name': name, 'picture': picture} for name, picture in zip(players_names, players_pictures)]
        
        # Group players into batches of 3 for multiple cards per slide
        batch_size = 3
        players_batches = [players[i:i + batch_size] for i in range(0, len(players), batch_size)]
    except Exception as e:
        players_batches = []  # Fallback in case of error
        flash(f"Error reading player data: {e}", "danger")
        print(f"Error reading CSV file: {e}")

    return render_template(
        "index.html",
        players_batches=players_batches,
        current_user=current_user  # Pass current_user to the template
    )

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


@app.route('/secondTemperature', methods=["GET", "POST"])
def secondTemperature():
    temperature = []
    for i in range(1, 10):
        temperature.append(random.randint(0, 100))
    data = {
        "temperature": temperature
    }
    return jsonify(data)


@app.route('/update_player_stocks_2')
def update_player_stocks2():
    player_ids = [1630173, 203500, 1628389]  
    for player_id in player_ids:
        update_player_stock(player_id)
    flash('Player stocks updated successfully!', 'success')
    return redirect(url_for('index'))


@app.route('/get_fantasy_points/<int:player_id>', methods=['GET'])
def get_fantasy_points_route(player_id):
    """Flask route to fetch fantasy points over the last 5 days for a specific player."""
    # Initialize lists to store dates and fantasy points
    dates = []
    fantasy_points_list = []

    # Fetch data for the last 5 days
    today = datetime.now()
    for i in range(5):
        # Corrected line: use timedelta without the datetime prefix
        date = today - timedelta(days=4 - i)
        date_str = date.strftime('%Y-%m-%d')
        dates.append(date_str)

        # Fetch player data for the specific date
        stats = fetch_player_data(player_id, date=date_str)
        if stats:
            fantasy_points = calculate_fantasy_points(stats)
            fantasy_points_list.append(fantasy_points)
        else:
            fantasy_points_list.append(0.0)

    # Convert data types to native Python types
    player_id = int(player_id)
    fantasy_points_list = [float(fp) for fp in fantasy_points_list]
    dates = [str(date) for date in dates]

    # Return the data in JSON format
    return jsonify({
        'status': 'success',
        'player_id': player_id,
        'dates': dates,
        'fantasy_points': fantasy_points_list
    }), 200

@app.route('/update_player_stocks')
@login_required  
def update_player_stocks():
    player_ids = [1630173, 203500, 1628389]  
    for player_id in player_ids:
        update_player_stock(player_id)
    flash('Player stocks updated successfully!', 'success')
    return redirect(url_for('index'))

'''
@app.route('/search-players', methods=['GET'])
def read_players():
    query = request.args.get('query')  # Get the query parameter from the URL
    if query:
        
        results = PlayerStock.query.filter(
            PlayerStock.player_first_name.contains(query)
        ).all()

        
        return jsonify([{
            'full_name': f"{item.player_first_name} {item.player_last_name}",
            'value': item.value
        } for item in results])
    return jsonify([])
'''


@app.route('/search')
@login_required
def search_page():
    return render_template('read_players.html')

''''
@app.route('/search-players', methods=['GET'])
def search_players():
    query = request.args.get('query')
    if query:
       
        results = PlayerStock.query.filter(
            PlayerStock.player_first_name.ilike(f'%{query}%') |
            PlayerStock.player_last_name.ilike(f'%{query}%')
        ).all()

        
        if results:
            return jsonify([f'{player.player_first_name} {player.player_last_name}' for player in results])
        else:
            return jsonify([])  
    return jsonify([])  
'''

#updated and new search players func:


@app.route('/search-players', methods=['GET'])
@login_required
def search_players():
    """
    Route to search for players based on the query.
    Returns a list of player full names matching the search term.
    """
    query = request.args.get('query', '').strip().lower()
    if not query:
        return jsonify([])

    # Search in the PlayerStock table (case-insensitive)
    players = PlayerStock.query.filter(
        db.or_(
            PlayerStock.player_first_name.ilike(f'%{query}%'),
            PlayerStock.player_last_name.ilike(f'%{query}%')
        )
    ).all()

    # Serialize the data as full names
    players_data = [
        f"{player.player_first_name} {player.player_last_name}" for player in players]

    return jsonify(players_data)


@app.route('/portfolio')
@login_required
def portfolio():
    return render_template('portfolio.html')


@app.route('/portfolio-data', methods=['GET'])
@login_required
def portfolio_data():
    entries = PortfolioEntry.query.filter_by(user_id=current_user.id).all()
    data = []

    for entry in entries:
        player = PlayerStock.query.get(entry.player_stock_id)
        if player:
            data.append({
                'player_name': f"{player.player_first_name} {player.player_last_name}",
                'shares': entry.shares,
                'value': player.value,
                'total_value': entry.shares * player.value
            })

    return jsonify(data)



@app.route('/add-portfolio-entry', methods=['POST'])
@login_required
def add_portfolio_entry():
    """
    Route to add a selected player to the current user's portfolio.
    Expects JSON data with 'player_name' (e.g., "LeBron James") and 'shares'.
    """
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided.'}), 400

    player_name = data.get('player_name')
    shares = data.get('shares', 1)  # Default to 1 share if not specified

    # Validate input
    if not player_name:
        return jsonify({'status': 'error', 'message': 'Player name is required.'}), 400

    try:
        shares = int(shares)
        if shares <= 0:
            return jsonify({'status': 'error', 'message': 'Number of shares must be a positive integer.'}), 400
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Number of shares must be an integer.'}), 400

    # Split player_name into first and last name
    try:
        first_name, last_name = player_name.strip().split(' ', 1)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Player name must include both first and last names.'}), 400

    # Retrieve the PlayerStock by first and last name
    player_stock = PlayerStock.query.filter_by(
        player_first_name=first_name,
        player_last_name=last_name
    ).first()

    if not player_stock:
        return jsonify({'status': 'error', 'message': 'Player not found.'}), 404

    # Check if the user already has an entry for this player_stock_id
    existing_entry = PortfolioEntry.query.filter_by(
        user_id=current_user.id,
        player_stock_id=player_stock.id
    ).first()

    if existing_entry:
        # Update the number of shares
        existing_entry.shares += shares
        message = f'Updated shares for {player_name}. Total shares: {existing_entry.shares}.'
    else:
        # Create a new portfolio entry
        new_entry = PortfolioEntry(
            user_id=current_user.id,
            player_stock_id=player_stock.id,
            shares=shares
        )
        db.session.add(new_entry)
        message = f'Added {player_name} to your portfolio with {shares} shares.'

    # Commit the changes to the database
    try:
        db.session.commit()
        return jsonify({'status': 'success', 'message': message}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to add portfolio entry.'}), 500
    
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)