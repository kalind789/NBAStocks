from nba_api.stats.endpoints import playercareerstats
from nba_api.stats.static.players import _get_active_players
import pandas as pd
import time  # for handling request timing if needed

players = _get_active_players()
player_df = pd.DataFrame(players)
print(player_df.head())

player_stats_df = pd.DataFrame()
i = 0
for player_id in player_df['id']:
    if i == 50:
        break
    try:
        # Fetch career stats for the player
        stats = playercareerstats.PlayerCareerStats(player_id=str(player_id)).get_data_frames()[0]
        
        if not stats.empty:
        # Append the fetched data to player_stats_df
            player_stats_df = pd.concat([player_stats_df, stats], ignore_index=True)

    except Exception as e:
        print(f"Error fetching data for player_id {player_id}: {e}")
    
    i += 1
    time.sleep(0.5)

print(player_stats_df.head())
