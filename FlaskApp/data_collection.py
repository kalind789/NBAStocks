# data_collection.py

from nba_api.stats.endpoints import playercareerstats
import random
from models import PlayerStock, db

def fetch_player_data(player_id):
    """Fetch player data from the NBA API."""
    try:
        career = playercareerstats.PlayerCareerStats(player_id=str(player_id))
        career_df = career.get_data_frames()[0]
        if not career_df.empty:
            latest_stats = career_df.iloc[-1]
            return {
                'PTS': latest_stats['PTS'],
                'AST': latest_stats['AST'],
                'REB': latest_stats['REB'],
                'BLK': latest_stats['BLK'],
                'STL': latest_stats['STL']
            }
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
    """Fetches data and updates player stock in the database."""
    stats = fetch_player_data(player_id)
    if stats:
        fantasy_points = calculate_fantasy_points(stats)
        player_stock = PlayerStock.query.filter_by(id=player_id).first()
        if player_stock:
            player_stock.value = fantasy_points
            db.session.commit()