
import time
import cfbd
from cfbd.rest import ApiException
from pprint import pprint
import os

# Defining the host is optional and defaults to https://apinext.collegefootballdata.com
# See configuration.py for a list of all supported configuration parameters.
configuration = cfbd.Configuration(
    host = "https://apinext.collegefootballdata.com"
)

# The client must configure the authentication and authorization parameters
# in accordance with the API server security policy.
# Examples for each auth method are provided below, use the example that
# satisfies your auth use case.

# Configure Bearer authorization: apiKey
configuration = cfbd.Configuration(
    access_token = "06Qq3nXJp+G9BVCZId6QGxmYF6k1DPzRqvB0iRcVGiJ0xL3S8sNS0hlO/E32EfYs"
)


# Enter a context with an instance of the API client
# with cfbd.ApiClient(configuration) as api_client:
#     api_instance = cfbd.TeamsApi(api_client)
    
#     try:
#         print("Fetching FBS teams...")
#         teams = api_instance.get_fbs_teams()
        
#         # Create lists to store team information
#         team_names = []
#         team_info = []
        
#         for team in teams:
#             # Add team name to simple list
#             team_names.append(team.school)
            
#             # Create more detailed team info dictionary
#             team_data = {
#                 'school': team.school,
#                 'abbreviation': team.abbreviation,
#                 'conference': team.conference,
#                 'location': {
#                     'city': team.location.city if hasattr(team, 'location') else None,
#                     'state': team.location.state if hasattr(team, 'location') else None,
#                 }
#             }
#             team_info.append(team_data)
        
#         # Print results
#         print("\nTotal number of FBS teams:", len(team_names))
#         print("\nAll FBS team names:")
#         pprint(sorted(team_names))
        
#         print("\nDetailed team information:")
#         pprint(team_info)
        
#     except ApiException as e:
#         error_body = e.body if hasattr(e, 'body') else 'No additional error details'
#         print(f"API Error: {e.reason} (Status: {e.status})")
#         print(f"Error details: {error_body}")
#     except Exception as e:
#         print(f"Unexpected error: {str(e)}")

import csv

with cfbd.ApiClient(configuration) as api_client:
    api_instance = cfbd.GamesApi(api_client)
    year = 2000
    
    # Create CSV file and write header
    with open('team_records.csv', 'w', newline='') as csvfile:
        fieldnames = ['year', 'team', 'conference', 'division', 'total_games', 'total_wins', 'total_losses',
                     'conference_games', 'conference_wins', 'conference_losses',
                     'home_games', 'home_wins', 'home_losses',
                     'away_games', 'away_wins', 'away_losses',
                     'expected_wins']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        while year <= 2024:
            try:
                print(f"Fetching records for {year}...")
                records = api_instance.get_records(year=year)
                
                # Write records to CSV
                for record in records:
                    if record.classification and record.classification.value == 'fbs':
                        writer.writerow({
                            'year': year,
                            'team': record.team,
                            'conference': record.conference,
                            'division': record.division,
                            'total_games': record.total.games,
                            'total_wins': record.total.wins,
                            'total_losses': record.total.losses,
                            'conference_games': record.conference_games.games,
                            'conference_wins': record.conference_games.wins,
                            'conference_losses': record.conference_games.losses,
                            'home_games': record.home_games.games,
                            'home_wins': record.home_games.wins,
                            'home_losses': record.home_games.losses,
                            'away_games': record.away_games.games,
                            'away_wins': record.away_games.wins,
                            'away_losses': record.away_games.losses,
                            'expected_wins': record.expected_wins
                        })
                print(f"Completed {year}")
                year += 1
            except ApiException as e:
                error_body = e.body if hasattr(e, 'body') else 'No additional error details'
                print(f"API Error for year {year}: {e.reason} (Status: {e.status})")
                print(f"Error details: {error_body}")
                year += 1
            except Exception as e:
                print(f"Unexpected error for year {year}: {str(e)}")
                year += 1

print("\nData has been saved to team_records.csv")        