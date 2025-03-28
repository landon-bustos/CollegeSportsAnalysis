import os
import cfbd
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime
from cfbd.rest import ApiException
from cfbd.models.division_classification import DivisionClassification
from cfbd.models.game_media import GameMedia
from cfbd.models.media_type import MediaType
from cfbd.models.season_type import SeasonType

# Load environment variables
load_dotenv()

# Configure API client
configuration = cfbd.Configuration(
    host = "https://apinext.collegefootballdata.com",
    access_token = os.getenv('CFBD_API_KEY')
)

def get_team_records(api_client, year):
    """Get team records for a given year"""
    games_api = cfbd.GamesApi(api_client)
    try:
        records = games_api.get_records(year=year)
        fbs_records = [r for r in records if r.classification and r.classification.value == 'fbs']
        if fbs_records:
            # Print attributes of the first record for debugging
            print("Available attributes:")
            print(dir(fbs_records[0]))
        return fbs_records
    except Exception as e:
        print(f"Error getting team records for {year}: {str(e)}")
        return []



def get_media_info(api_client, year):
    """Get media coverage information for games in a given year"""
    games_api = cfbd.GamesApi(api_client)
    media_by_game = {}
    
    try:
        for week in range(1, 16):
            media = games_api.get_media(year=year, week=week)
            for game_media in media:
                if game_media.outlet:
                    media_by_game[game_media.id] = game_media.outlet
    except Exception as e:
        print(f"Error getting media info for {year}: {str(e)}")
    
    return media_by_game

def get_betting_lines(api_client, year):
    """Get betting lines for all games in a given year"""
    betting_api = cfbd.BettingApi(api_client)
    all_lines = []
    
    # Get media coverage info
    media_by_game = get_media_info(api_client, year)
    
    try:
        for week in range(1, 16):
            print(f"Fetching betting lines for week {week} of {year}...")
            lines = betting_api.get_lines(year=year, week=week)
            
            for line in lines:
                if hasattr(line, 'lines') and line.lines:
                    outlet = media_by_game.get(line.id)
                    for betting_line in line.lines:
                        all_lines.append({
                            'year': year,
                            'week': week,
                            'game_id': line.id,
                            'season_type': line.season_type,
                            'start_date': line.start_date,
                            'home_team': line.home_team,
                            'home_score': line.home_score,
                            'away_team': line.away_team,
                            'away_score': line.away_score,
                            'provider': betting_line.provider,
                            'spread': betting_line.spread,
                            'formatted_spread': betting_line.formatted_spread,
                            'spread_open': betting_line.spread_open,
                            'over_under': betting_line.over_under,
                            'over_under_open': betting_line.over_under_open,
                            'home_moneyline': betting_line.home_moneyline,
                            'away_moneyline': betting_line.away_moneyline,
                            'outlet': outlet
                        })
    except Exception as e:
        print(f"Error getting betting lines for {year}: {str(e)}")
    
    return all_lines

def get_significant_games(api_client, year):
    """
    Get significant games (bowl games, ranked matchups, upsets)
    """
    games_api = cfbd.GamesApi(api_client)
    rankings_api = cfbd.RankingsApi(api_client)
    significant_games = []
    
    # Get media coverage info
    media_by_game = get_media_info(api_client, year)
    
    try:
        games = games_api.get_games(year=year)
        
        # Get rankings for each week
        rankings_by_week = {}
        for week in range(1, 16):
            try:
                rankings = rankings_api.get_rankings(year=year, week=week)
                if rankings and len(rankings) > 0:
                    for poll in rankings:
                        if poll.polls and len(poll.polls) > 0:
                            for rank_poll in poll.polls:
                                if rank_poll.poll == "AP Top 25":
                                    ranked_teams = {rank.school: rank.rank for rank in rank_poll.ranks}
                                    rankings_by_week[week] = ranked_teams
            except Exception as e:
                print(f"Error getting rankings for week {week}: {str(e)}")
        
        # Process each game
        for game in games:
            is_significant = False
            significance_factors = []
            
            # Check if it's a bowl game
            if game.season_type == "postseason":
                is_significant = True
                significance_factors.append("bowl_game")
            
            # Check if it involves ranked teams
            week = game.week
            if week in rankings_by_week:
                ranked_teams = rankings_by_week[week]
                home_rank = ranked_teams.get(game.home_team)
                away_rank = ranked_teams.get(game.away_team)
                
                if home_rank or away_rank:
                    is_significant = True
                    significance_factors.append("ranked_matchup")
                    
                    # Check for upset
                    if home_rank and away_rank:
                        if (home_rank > away_rank and game.home_points > game.away_points) or \
                           (away_rank > home_rank and game.away_points > game.home_points):
                            significance_factors.append("upset_victory")
            
            if is_significant:
                outlet = media_by_game.get(game.id)
                significant_games.append({
                    'year': year,
                    'week': week,
                    'date': game.start_date,
                    'home_team': game.home_team,
                    'home_conference': game.home_conference,
                    'home_points': game.home_points,
                    'away_team': game.away_team,
                    'away_conference': game.away_conference,
                    'away_points': game.away_points,
                    'significance': ','.join(significance_factors),
                    'home_rank': home_rank,
                    'away_rank': away_rank,
                    'outlet': outlet
                })
    
    except Exception as e:
        print(f"Error processing year {year}: {str(e)}")
    
    return significant_games

def main():
    # Years to process (limited by betting odds availability)
    start_year = 2013
    end_year = 2025
    
    # Lists to store all data
    all_records = []
    all_betting_lines = []
    all_significant_games = []
    
    with cfbd.ApiClient(configuration) as api_client:
        for year in range(start_year, end_year + 1):
            print(f"\nProcessing year {year}...")
            
            # Collect team records
            records = get_team_records(api_client, year)
            all_records.extend([{
                'year': year,
                'team': r.team,
                'team_id': r.team_id,
                'conference': r.conference,
                'division': r.division,
                'total': r.total,
                'conference_games': r.conference_games,
                'home_games': r.home_games,
                'away_games': r.away_games,
                'expected_wins': r.expected_wins,
                'regular_season': r.regular_season,
                'postseason': r.postseason,
                'neutral_site_games': r.neutral_site_games
            } for r in records])
            
            # Collect betting lines
            betting_lines = get_betting_lines(api_client, year)
            all_betting_lines.extend(betting_lines)
            
            # Collect significant games
            significant_games = get_significant_games(api_client, year)
            all_significant_games.extend(significant_games)
    
    # Save all data to CSV files
    pd.DataFrame(all_records).to_csv('team_records.csv', index=False)

    pd.DataFrame(all_betting_lines).to_csv('betting_lines.csv', index=False)
    pd.DataFrame(all_significant_games).to_csv('significant_games.csv', index=False)
    
    print("\nData collection complete! Files saved:")
    print("- team_records.csv")

    print("- betting_lines.csv")
    print("- significant_games.csv")

if __name__ == "__main__":
    main()
