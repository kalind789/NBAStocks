from apscheduler.schedulers.background import BackgroundScheduler
from data_collection import get_player_stats, calculate_fantasy_points
from models import db, PlayerStock

def update_player_stocks():
    """Fetches player data and updates their stock values."""
    # Example player IDs
    player_ids = [1630173, 203500, 1628389]  # Extend with more IDs
    for player_id in player_ids:
        player_stats = get_player_stats(player_id)
        if not player_stats.empty:
            latest_stats = player_stats.iloc[-1].to_dict()  # Get the most recent stats
            fantasy_points = calculate_fantasy_points(latest_stats)
            
            # Example logic to update stock value (simplified for illustration)
            stock = PlayerStock.query.filter_by(id=player_id).first()
            if stock:
                stock.value = fantasy_points
                db.session.commit()

# Scheduler setup
scheduler = BackgroundScheduler()
scheduler.add_job(func=update_player_stocks, trigger="interval", minutes=60)  # Adjust the interval as needed
scheduler.start()