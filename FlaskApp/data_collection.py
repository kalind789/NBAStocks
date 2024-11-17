from nba_api.stats.endpoints import playercareerstats, playergamelog
import random
from models import PlayerStock, db

def fetch_player_data(player_id, last_n_games=5):
    """Fetch player data from the NBA API for the last `n` games and calculate fantasy points."""
    try:
        # Fetch the player's game logs
        gamelog = playergamelog.PlayerGameLog(player_id=str(player_id))
        gamelog_df = gamelog.get_data_frames()[0]

        # Filter the last `n` games
        last_games = gamelog_df.head(last_n_games)

        if not last_games.empty:
            stats_list = []
            for _, game in last_games.iterrows():
                stats = {
                    'PTS': int(game['PTS']),
                    'AST': int(game['AST']),
                    'REB': int(game['REB']),
                    'BLK': int(game['BLK']),
                    'STL': int(game['STL'])
                }
                stats_list.append(stats)
            return stats_list
        else:
            return None
    except Exception as e:
        print(f"Error fetching data for player {player_id}: {e}")
        return None

def calculate_fantasy_points(stats):
    """Calculate fantasy points using a custom formula."""
    if stats is None:
        return 0
    return stats['PTS'] + 3 * stats['AST'] + 1.5 * stats['REB'] + 5 * stats['BLK'] + 5 * stats['STL']

def update_player_stock(player_id):
    """Fetches data for a player, calculates fantasy points, and updates their stock value in the database."""
    player_stats = fetch_player_data(player_id, last_n_games=5)
    if player_stats:
        total_fantasy_points = sum([calculate_fantasy_points(stats) for stats in player_stats])
        avg_fantasy_points = total_fantasy_points / len(player_stats) if player_stats else 0

        # Update the PlayerStock record
        player_stock = PlayerStock.query.filter_by(id=player_id).first()
        if player_stock:
            player_stock.value = avg_fantasy_points  # Update value to reflect the average fantasy points
            db.session.commit()