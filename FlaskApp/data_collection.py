from nba_api.stats.endpoints import playercareerstats, playergamelog
import random
from models import PlayerStock, db


def fetch_player_data(player_id, last_n_games=5):
    """Fetch player data for the last `n` games and return aggregated stats."""
    try:
        # Fetch the player's game logs
        gamelog = playergamelog.PlayerGameLog(player_id=str(player_id))
        gamelog_df = gamelog.get_data_frames()[0]

        # Get the last `n` games
        last_games = gamelog_df.head(last_n_games)

        if not last_games.empty:
            total_stats = {
                'PTS': 0,
                'AST': 0,
                'REB': 0,
                'BLK': 0,
                'STL': 0
            }
            games_count = 0

            for _, game in last_games.iterrows():
                total_stats['PTS'] += int(game['PTS'])
                total_stats['AST'] += int(game['AST'])
                total_stats['REB'] += int(game['REB'])
                total_stats['BLK'] += int(game['BLK'])
                total_stats['STL'] += int(game['STL'])
                games_count += 1

            # Average out the stats
            avg_stats = {key: total / games_count for key,
                         total in total_stats.items()}
            return avg_stats
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