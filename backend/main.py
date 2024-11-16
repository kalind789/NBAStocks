import time
from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static.players import _get_active_players
import pandas as pd

players = _get_active_players()
player_df = pd.DataFrame(players)
print(player_df.head())
player_df = player_df.drop(['full_name', 'is_active'], axis=1)
print(player_df.head())

player_df.to_csv('csv_data/players.csv')