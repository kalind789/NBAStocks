# data_collection.py

from nba_api.stats.endpoints import playercareerstats, playergamelog
import random
from models import PlayerStock, db


def fetch_player_data(player_id, date=None):
    """Fetch player data from the NBA API for a specific date."""
    try:
        # Fetch the player's game logs
        gamelog = playergamelog.PlayerGameLog(player_id=str(player_id))
        gamelog_df = gamelog.get_data_frames()[0]

        print("Columns in gamelog_df:", gamelog_df.columns)
        print("First few rows of gamelog_df:\n", gamelog_df.head())

        if date:
            # Convert 'GAME_DATE' to datetime objects for accurate comparison
            gamelog_df['GAME_DATE'] = pd.to_datetime(gamelog_df['GAME_DATE'])
            date_obj = pd.to_datetime(date)
            # Filter the DataFrame for the specific date
            game_stats = gamelog_df[gamelog_df['GAME_DATE'] == date_obj]
        else:
            # Use the most recent game if no date is provided
            game_stats = gamelog_df.iloc[:1]

        print("game_stats:\n", game_stats)

        if not game_stats.empty:
            stats = game_stats.iloc[0]
            print("stats:\n", stats)
            print("Type of stats:", type(stats))
            return {
                'PTS': stats['PTS'],
                'AST': stats['AST'],
                'REB': stats['REB'],
                'BLK': stats['BLK'],
                'STL': stats['STL']
            }
        else:
            print(
                f"No game stats available for player {player_id} on date {date}.")
            return None
    except Exception as e:
        print(
            f"Error fetching data for player {player_id} on date {date}: {e}")
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