from app import app
from models import db, User, PortfolioEntry, PlayerStock
import pandas as pd

players = []

with app.app_context():
    #might want to remove the drop all later when were done
    db.drop_all()  
    db.create_all() 


    with open('static/players.csv', 'r') as file:
        for line in file:
            string = str(line)

            arr = string.split(',')
            print(arr)
            players.append((arr[4],arr[5]))
    
    for i in range(len(players)):
        stock = PlayerStock(player_first_name=players[i][0],
                            player_last_name=players[i][1], value=100.0)
        db.session.add(stock)
        db.session.commit()

# Load the CSV file
players_df = pd.read_csv('static/players.csv')

# Create a new column 'picture_link' using a loop
picture_links = []
for id in players_df['id']:
    picture_links.append(f"https://cdn.nba.com/headshots/nba/latest/1040x760/{id}.png")

# Assign the list to the new column
players_df['picture_link'] = picture_links
players_df.to_csv('static/players.csv')
