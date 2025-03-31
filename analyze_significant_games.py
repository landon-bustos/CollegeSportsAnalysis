import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def load_data():
    significant_games = pd.read_csv('significant_games.csv', parse_dates=['date'])
    betting_lines = pd.read_csv('betting_lines.csv', parse_dates=['start_date'])
    team_records = pd.read_csv('team_records.csv')
    return significant_games, betting_lines, team_records

def analyze_significant_games(games_df):
    significance_counts = games_df['significance'].value_counts()
    print('Types of Significant Games:')
    print(significance_counts)
    
    home_conf = games_df['home_conference'].value_counts()
    away_conf = games_df['away_conference'].value_counts()
    all_conf = pd.concat([home_conf, away_conf]).groupby(level=0).sum()
    print('\nTop Conferences:')
    print(all_conf.sort_values(ascending=False).head(5))
    
    ranked_games = games_df[games_df['home_rank'].notna() | games_df['away_rank'].notna()]
    print(f'\nTotal Ranked Games: {len(ranked_games)}')
    
    upsets = games_df[games_df['significance'].str.contains('upset_victory', na=False)]
    print(f'\nTotal Upsets: {len(upsets)}')
    if len(upsets) > 0:
        print('\nUpsets:')
        for _, upset in upsets.iterrows():
            print(f"{upset['away_team']} ({upset['away_points']}) @ {upset['home_team']} ({upset['home_points']})")

def main():
    significant_games, betting_lines, team_records = load_data()
    analyze_significant_games(significant_games)
    
    analysis_results = significant_games.groupby(['year', 'home_conference', 'away_conference']).agg({
        'significance': 'count',
        'home_points': 'mean',
        'away_points': 'mean'
    }).round(2)
    
    analysis_results.to_csv('significant_games_analysis.csv')
    print('\nAnalysis saved to significant_games_analysis.csv')

if __name__ == "__main__":
    main()
