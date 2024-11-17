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
    with open('static/players.csv', 'r') as file:
        for line in file:
            string = str(line)

            arr = string.split(',')
            
            players.append((arr[5], arr[6],arr[4]))
    

        for i in range(len(players)):
            stock = PlayerStock(player_first_name=players[i][0],
                            player_last_name=players[i][1], value=100.0, player_id=players[i][2])
            print(stock)
            '''
            stock = PlayerStock(
                player_first_name=first_name,
                player_last_name=last_name,
                value=100.0,
                player_id=player_id  # Assuming you have added player_id to PlayerStock model
            )
            '''
            db.session.add(stock)
    db.session.commit()

   
    players_df['picture_link'] = players_df['id'].apply(lambda id: f"https://cdn.nba.com/headshots/nba/latest/1040x760/{id}.png")

   
    players_df.to_csv('static/players.csv', index=False)