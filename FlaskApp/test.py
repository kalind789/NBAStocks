# Test database 
from app import app
from models import db, User, PortfolioEntry, PlayerStock

with app.app_context():
    db.drop_all()  #clear database
    db.create_all() #create tables

    ##CREATE DATA
    # Create a PlayerStock
    stock = PlayerStock(player_first_name="LeBron", player_last_name="James", value=100.0)
    db.session.add(stock)
    db.session.commit()

    # Create a User
    user = User(username="kavni", email="kavni@u.rochester.edu", password="hashed_password")
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
        stock = db.session.get(PlayerStock, entry.player_stock_id)
        print(f"{user.username} owns {entry.shares} shares of {stock.player_first_name} {stock.player_last_name}")

    # Get all users who own shares in a particular stock
    stock = PlayerStock.query.first()
    #all the user id's from portfolio entry table that own a specfic stock
    portfolio_entries = PortfolioEntry.query.filter_by(player_stock_id=stock.id).all()
    for entry in portfolio_entries:
        #then we get the specific user 
        user = db.session.get(User, entry.user_id)
        print(f"{user.username} owns {entry.shares} shares of {stock.player_first_name} {stock.player_last_name}")
