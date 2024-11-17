from app import app
from models import db, User, PortfolioEntry, PlayerStock


players = []

with app.app_context():
    #might want to remove the drop all later when were done
    db.drop_all()  
    db.create_all() 


    with open('static/players.csv', 'r') as file:
        for line in file:
            string = str(line)
       
            arr = string.split(',')

            players.append((arr[3],arr[4]))
    
    for i in range(len(players)):
        stock = PlayerStock(player_first_name=players[i][0],
                            player_last_name=players[i][1], value=100.0)
        db.session.add(stock)
        db.session.commit()
        

print(players)
