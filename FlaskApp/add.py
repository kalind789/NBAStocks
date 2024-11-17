from app import app
from models import db, User, PortfolioEntry, PlayerStock
import pandas as pd

players = []

with app.app_context():
    # Might want to remove the drop all later when we're done
    db.drop_all()  
    db.create_all() 

    # Load and process player data from the CSV file
    players_df = pd.read_csv('static/players.csv')

    # Iterate through DataFrame rows and create PlayerStock entries
    for index, row in players_df.iterrows():
        first_name = row['first_name'] if 'first_name' in row else None
        last_name = row['last_name'] if 'last_name' in row else None
        player_id = row['id'] if 'id' in row else None  # Add player_id if present in CSV

        if first_name and last_name and player_id:
            stock = PlayerStock(
                player_first_name=first_name,
                player_last_name=last_name,
                value=100.0,
                player_id=player_id  # Assuming you have added player_id to PlayerStock model
            )
            db.session.add(stock)

    db.session.commit()

    # Create a new column 'picture_link' in the DataFrame using player IDs
    players_df['picture_link'] = players_df['id'].apply(lambda id: f"https://cdn.nba.com/headshots/nba/latest/1040x760/{id}.png")

    # Save updated DataFrame back to CSV
    players_df.to_csv('static/players.csv', index=False)