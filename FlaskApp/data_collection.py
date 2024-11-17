from nba_api.stats.endpoints import playergamelog
from models import PlayerStock, db


def fetch_player_data(player_id, last_n_games=5):
    """Fetch player data for the last `n` games and return aggregated stats."""
    try:
        # Fetch the player's game logs
        gamelog = playergamelog.PlayerGameLog(player_id=str(player_id))
        gamelog_df = gamelog.get_data_frames()[0]

        if gamelog_df.empty:
            print(f"No game logs found for player {player_id}.")
            return None

        # Get the last `n` games
        last_games = gamelog_df.head(last_n_games)

        # Aggregate stats
        total_stats = {
            'PTS': last_games['PTS'].sum(),
            'AST': last_games['AST'].sum(),
            'REB': last_games['REB'].sum(),
            'BLK': last_games['BLK'].sum(),
            'STL': last_games['STL'].sum()
        }

        # Average out the stats
        avg_stats = {key: total / last_n_games for key,
                     total in total_stats.items()}
        return avg_stats

    except IndexError:
        print(f"IndexError: No data found for player {player_id}.")
        return None
    except ValueError as ve:
        print(f"ValueError fetching data for player {player_id}: {ve}")
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
    # Fetch the aggregated data for the last 5 games
    player_stats = fetch_player_data(player_id, last_n_games=5)
    if player_stats:
        # Calculate the player's fantasy points based on the aggregated stats
        avg_fantasy_points = calculate_fantasy_points(player_stats)

        # Stock price logic: base price + (average fantasy points * multiplier)
        base_price = 50
        multiplier = 1.2
        stock_price = base_price + (avg_fantasy_points * multiplier)

        # Update the PlayerStock record
        player_stock = PlayerStock.query.filter_by(player_id=player_id).first()
        if player_stock:
            # Round to 2 decimal places
            player_stock.value = round(stock_price, 2)
            db.session.commit()
