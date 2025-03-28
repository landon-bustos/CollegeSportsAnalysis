import time
import os
import cfbd
import csv
from cfbd.rest import ApiException
from datetime import datetime

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API client
configuration = cfbd.Configuration(
    host = "https://apinext.collegefootballdata.com",
    access_token = os.getenv('CFBD_API_KEY')
)

def get_betting_lines(api_client, year):
    betting_api = cfbd.BettingApi(api_client)
    all_lines = []
    
    try:
        # Get games for the year to determine max week
        games_api = cfbd.GamesApi(api_client)
        games = games_api.get_games(year=year)
        max_week = max(game.week for game in games) if games else 0
        
        # Get betting lines for each week
        for week in range(1, max_week + 1):
            print(f"Fetching betting lines for week {week} of {year}...")
            try:
                lines = betting_api.get_lines(year=year, week=week)
                if lines:
                    for game in lines:
                        for line in game.lines:
                            game_line = {
                                'year': year,
                                'week': week,
                                'game_id': game.id,
                                'season_type': game.season_type,
                                'start_date': game.start_date.isoformat() if game.start_date else None,
                                'home_team': game.home_team,
                                'home_conference': game.home_conference,
                                'home_score': game.home_score,
                                'away_team': game.away_team,
                                'away_conference': game.away_conference,
                                'away_score': game.away_score,
                                'provider': line.provider,
                                'spread': line.spread,
                                'formatted_spread': line.formatted_spread,
                                'spread_open': line.spread_open,
                                'over_under': line.over_under,
                                'over_under_open': line.over_under_open,
                                'home_moneyline': line.home_moneyline,
                                'away_moneyline': line.away_moneyline
                            }
                            all_lines.append(game_line)
            except Exception as e:
                print(f"Error getting betting lines for week {week} of {year}: {str(e)}")
                continue
                
            # Add delay to avoid rate limiting
            time.sleep(0.5)
                
        return all_lines
    except Exception as e:
        print(f"Error getting games for {year}: {str(e)}")
        return []

# Main execution
with cfbd.ApiClient(configuration) as api_client:
    all_data = []
    
    # Create CSV file and write header
    with open('betting_lines.csv', 'w', newline='') as csvfile:
        fieldnames = ['year', 'week', 'game_id', 'season_type', 'start_date', 
                     'home_team', 'home_conference', 'home_score',
                     'away_team', 'away_conference', 'away_score',
                     'provider', 'spread', 'formatted_spread', 'spread_open',
                     'over_under', 'over_under_open', 'home_moneyline', 'away_moneyline']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Get data for years 2000-2024
        for year in range(2000, 2024):
            print(f"\nProcessing year {year}...")
            lines = get_betting_lines(api_client, year)
            
            # Write lines to CSV
            for line in lines:
                writer.writerow(line)
            
            # Add delay between years
            time.sleep(1)

print("\nData has been saved to betting_lines.csv")
