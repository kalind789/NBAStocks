import random
from nba_api.stats.endpoints import playercareerstats, boxscoretraditionalv2
import pandas as pd
from datetime import datetime

def get_player_stats(player_id):
    """Fetches the player's career statistics using nba_api."""
    career = playercareerstats.PlayerCareerStats(player_id=str(player_id))
    return career.get_data_frames()[0]  # Returns DataFrame

def get_game_stats(game_id):
    """Fetches box score stats for a given game ID."""
    boxscore = boxscoretraditionalv2.BoxScoreTraditionalV2(game_id=game_id)
    return boxscore.get_data_frames()[0]  # Returns DataFrame

def calculate_fantasy_points(stats):
    """Calculates fantasy points using custom formula."""
    points = stats.get('PTS', 0)
    assists = stats.get('AST', 0)
    rebounds = stats.get('REB', 0)
    blocks = stats.get('BLK', 0)
    steals = stats.get('STL', 0)
    fantasy_points = points + 3 * assists + 1.5 * rebounds + 5 * blocks + 5 * steals
    return fantasy_points