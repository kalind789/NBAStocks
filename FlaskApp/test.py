# Test database 
from app import app
from models import db, User, PortfolioEntry, PlayerStock

with app.app_context():
    ##CREATE DATA
    # Create a PlayerStock
    stock = PlayerStock(player_first_name="LeBron", player_last_name="James", value=100.0)
    db.session.add(stock)
    db.session.commit()

    # Create a User
    user = User(username="kavni", email="kavni@u.rochester.edu", password_hash="hashed_password")
    db.session.add(user)
    db.session.commit()

    # Add Portfolio Entry
    portfolio_entry = PortfolioEntry(user_id=user.id, player_stock_id=stock.id, shares=10)
    db.session.add(portfolio_entry)
    db.session.commit()

    ## QUERY DATA
    # Get a user's portfolio
    user = User.query.first()
    for entry in user.portfolio:
        stock = PlayerStock.query.get(entry.player_stock_id)
        print(f"{user.username} owns {entry.shares} shares of {stock.player_first_name} {stock.player_last_name}")

    # Get all users who own shares in a particular stock
    stock = PlayerStock.query.first()
    portfolio_entries = PortfolioEntry.query.filter_by(player_stock_id=stock.id).all()
    for entry in portfolio_entries:
        user = User.query.get(entry.user_id)
        print(f"{user.username} owns {entry.shares} shares of {stock.player_first_name} {stock.player_last_name}")
