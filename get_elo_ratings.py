import time
import os
import cfbd
import csv
from cfbd.rest import ApiException

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API client
configuration = cfbd.Configuration(
    host = "https://apinext.collegefootballdata.com",
    access_token = os.getenv('CFBD_API_KEY')
)

def get_elo_ratings(api_client, year):
    ratings_api = cfbd.RatingsApi(api_client)
    all_ratings = []
    
    try:
        # Get number of weeks in the season
        games_api = cfbd.GamesApi(api_client)
        games = games_api.get_games(year=year)
        max_week = max(game.week for game in games) if games else 0
        
        # Get ratings for each week
        for week in range(1, max_week + 1):
            print(f"Fetching week {week} of {year}...")
            try:
                ratings = ratings_api.get_elo(year=year, week=week)
                if ratings:
                    for rating in ratings:
                        all_ratings.append({
                            'year': year,
                            'week': week,
                            'team': rating.team,
                            'conference': rating.conference,
                            'elo': rating.elo
                        })
            except Exception as e:
                print(f"Error getting ratings for week {week} of {year}: {str(e)}")
                continue
                
        return all_ratings
    except Exception as e:
        print(f"Error getting games for {year}: {str(e)}")
        return []

# Main execution
with cfbd.ApiClient(configuration) as api_client:
    all_data = []
    
    # Create CSV file and write header
    with open('team_elo_ratings.csv', 'w', newline='') as csvfile:
        fieldnames = ['year', 'week', 'team', 'conference', 'elo']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        # Get data for years 2000-2024
        for year in range(2000, 2024):
            print(f"\nProcessing year {year}...")
            ratings = get_elo_ratings(api_client, year)
            
            # Write ratings to CSV
            for rating in ratings:
                writer.writerow(rating)
            
            # Add delay to avoid rate limiting
            time.sleep(0.5)

print("\nData has been saved to team_elo_ratings.csv")
