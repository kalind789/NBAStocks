from datetime import datetime, timedelta
from flask import Flask, render_template, redirect, url_for, request, flash, jsonify
from flask_cors import CORS
from data_collection import update_player_stock, fetch_player_data, calculate_fantasy_points
from models import db, User, PortfolioEntry, PlayerStock
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from apscheduler.schedulers.background import BackgroundScheduler
from random import uniform

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


scheduler = BackgroundScheduler()


def scheduled_stock_update():
    with app.app_context():
        player_ids = [player.player_id for player in PlayerStock.query.all()]
        for player_id in player_ids:
            update_player_stock(player_id)



scheduler.add_job(scheduled_stock_update, 'interval', hours=1)
scheduler.start()

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/index')
@login_required
def index():
    csv_path = 'static/players.csv'
    try:
        player_df = pd.read_csv(csv_path)
        if 'full_name' not in player_df.columns or 'picture_link' not in player_df.columns:
            raise ValueError("CSV file must contain 'full_name' and 'picture_link' columns.")
        
        # get vals from db
        players_data = []
        for _, row in player_df.iterrows():
            player_stock = PlayerStock.query.filter_by(player_id=row['id']).first()
            player_value = player_stock.value if player_stock else 0  
            
            players_data.append({
                'name': row['full_name'],
                'picture': row['picture_link'],
                'value': player_value 
            })

        
        batch_size = 3
        players_batches = [players_data[i:i + batch_size] for i in range(0, len(players_data), batch_size)]
    except Exception as e:
        players_batches = []
        flash(f"Error reading player data: {e}", "danger")

    return render_template("index.html", players_batches=players_batches, current_user=current_user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        if not username or not password:
            flash('Username and password are required.', 'danger')
            return redirect(url_for('signup'))
        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('signup'))
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully. Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
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
                'player_id': player.player_id, 
                'player_name': f"{player.player_first_name} {player.player_last_name}",
                'shares': entry.shares,
                'value': player.value,
                'total_value': entry.shares * player.value
            })
    return jsonify(data)

@app.route('/search')
@login_required
def search_page():
    return render_template('read_players.html')

@app.route('/player-data', methods=['GET'])
def player_data():
    player_id = request.args.get('player_id')
    if not player_id:
        return jsonify({'status': 'error', 'message': 'Player ID is required'}), 400

    try:
        player_stats = fetch_player_data(player_id, last_n_games=5)
        if player_stats:
            return jsonify({'status': 'success', 'player_id': player_id, 'stats': player_stats}), 200
        else:
            return jsonify({'status': 'error', 'message': f'No stats available for player ID {player_id}'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/search-players', methods=['GET'])
@login_required
def search_players():
    query = request.args.get('query', '').strip().lower()
    if not query:
        return jsonify([])

    players = PlayerStock.query.filter(
        db.or_(
            PlayerStock.player_first_name.ilike(f'%{query}%'),
            PlayerStock.player_last_name.ilike(f'%{query}%')
        )
    ).all()

    players_data = [
        {
            'full_name': f"{player.player_first_name} {player.player_last_name}",
            'player_id': player.player_id,
            'fantasy_points': player.value  
        }
        for player in players
    ]

    return jsonify(players_data)


@app.route('/get_fantasy_points/<int:player_id>', methods=['GET'])
def get_fantasy_points_route(player_id):
    """Fetch and calculate the average fantasy points for the last 5 games of a specific player."""
    
    player = PlayerStock.query.filter_by(player_id=player_id).first()
    if not player:
        return jsonify({'status': 'error', 'message': f'Player ID {player_id} not found'}), 404

    #  stats for the last 5 games
    stats = fetch_player_data(player_id, last_n_games=5)
    if stats:
        fantasy_points = calculate_fantasy_points(stats)
        return jsonify({
            'status': 'success',
            'player_id': player_id,
            'player_name': f"{player.player_first_name} {player.player_last_name}",
            'average_stats': stats,
            'fantasy_points': fantasy_points
        }), 200
    else:
        return jsonify({'status': 'error', 'message': 'No game data available for this player.'}), 404


@app.route('/update-player-stock/<int:player_id>', methods=['POST'])
def update_player_stock_route(player_id):
    """Update the stock value of a specific player."""
    try:
        update_player_stock(player_id)
        player_stock = PlayerStock.query.filter_by(player_id=player_id).first()
        if not player_stock:
            return jsonify({'status': 'error', 'message': f'Player ID {player_id} not found'}), 404

        return jsonify({
            'status': 'success',
            'player_id': player_id,
            'new_value': player_stock.value
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/get_price_history/<int:player_id>', methods=['GET'])
def get_price_history(player_id):
    """Dynamically generate the last 5 prices for a given player."""
    try:
        
        player = PlayerStock.query.filter_by(player_id=player_id).first()
        if not player:
            return jsonify({'status': 'error', 'message': 'Player not found'}), 404

        # faking history :(
        base_price = player.value
        prices = [round(base_price + i * uniform(-5, 5), 2) for i in range(5)]

        return jsonify({'status': 'success', 'player_id': player_id, 'prices': prices}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
    
@app.route('/add-portfolio-entry', methods=['POST'])
@login_required
def add_portfolio_entry():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'No data provided.'}), 400

    player_name = data.get('player_name')
    shares = data.get('shares', 1)
    if not player_name:
        return jsonify({'status': 'error', 'message': 'Player name is required.'}), 400
    try:
        shares = int(shares)
        if shares <= 0:
            return jsonify({'status': 'error', 'message': 'Number of shares must be a positive integer.'}), 400
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Number of shares must be an integer.'}), 400

    try:
        first_name, last_name = player_name.strip().split(' ', 1)
    except ValueError:
        return jsonify({'status': 'error', 'message': 'Player name must include both first and last names.'}), 400

    player_stock = PlayerStock.query.filter_by(player_first_name=first_name, player_last_name=last_name).first()
    if not player_stock:
        return jsonify({'status': 'error', 'message': 'Player not found.'}), 404

    existing_entry = PortfolioEntry.query.filter_by(user_id=current_user.id, player_stock_id=player_stock.id).first()
    if existing_entry:
        existing_entry.shares += shares
        message = f'Updated shares for {player_name}. Total shares: {existing_entry.shares}.'
    else:
        new_entry = PortfolioEntry(user_id=current_user.id, player_stock_id=player_stock.id, shares=shares)
        db.session.add(new_entry)
        message = f'Added {player_name} to your portfolio with {shares} shares.'

    try:
        db.session.commit()
        return jsonify({'status': 'success', 'message': message}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Failed to add portfolio entry.'}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        #scheduled_stock_update()
    app.run(debug=True)