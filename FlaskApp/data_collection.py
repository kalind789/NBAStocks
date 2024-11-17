# data_collection.py

from nba_api.stats.endpoints import playercareerstats, playergamelog
import random
from models import PlayerStock, db


def fetch_player_data(player_id, last_n_games=5):
    """Fetch player data from the NBA API for the last `n` games and calculate fantasy points."""
    try:
        # Fetch the player's game logs
        gamelog = playergamelog.PlayerGameLog(player_id=str(player_id))
        gamelog_df = gamelog.get_data_frames()[0]

        print("Columns in gamelog_df:", gamelog_df.columns)
        print("First few rows of gamelog_df:\n", gamelog_df.head())

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
                # Calculate fantasy points
                fantasy_points = calculate_fantasy_points(stats)

                stats_list.append({
                    # Ensure the date is JSON serializable
                    'GAME_DATE': str(game['GAME_DATE']),
                    'PTS': stats['PTS'],
                    'AST': stats['AST'],
                    'REB': stats['REB'],
                    'BLK': stats['BLK'],
                    'STL': stats['STL'],
                    'fantasy_points': fantasy_points  # Include fantasy points
                })

            return stats_list
        else:
            print(f"No recent games found for player {player_id}.")
            return None
    except Exception as e:
        print(f"Error fetching data for player {player_id}: {e}")
        return None


def calculate_fantasy_points(stats) -> int:
    """Calculate fantasy points using a custom formula."""
    if stats is None:
        return 0
    return stats['PTS'] + 3 * stats['AST'] + 1.5 * stats['REB'] + 5 * stats['BLK'] + 5 * stats['STL']

def update_player_stock(player_id):
    """Fetches data and updates player stock in the database."""
    stats = fetch_player_data(player_id)
    if stats:
        fantasy_points = calculate_fantasy_points(stats)
        player_stock = PlayerStock.query.filter_by(id=player_id).first()
        if player_stock:
            player_stock.value = fantasy_points
            db.session.commit()