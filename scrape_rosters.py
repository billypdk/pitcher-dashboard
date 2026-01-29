#!/usr/bin/env python3
"""
Scrape MLB team rosters from official MLB.com pages.
Match players against CSV and assign teams.
Mark unmatched players as 'Free Agent'.
"""
import csv
import requests
from bs4 import BeautifulSoup
import time
import re

INPUT_CSV = 'stats (51).csv'
OUTPUT_CSV = 'stats_with_teams_final.csv'

# Team URLs and their abbreviations
TEAM_ROSTERS = {
    'ARI': 'https://www.mlb.com/dbacks/roster',
    'OAK': 'https://www.mlb.com/athletics/roster',
    'ATL': 'https://www.mlb.com/braves/roster',
    'BAL': 'https://www.mlb.com/orioles/roster',
    'BOS': 'https://www.mlb.com/redsox/roster',
    'CHC': 'https://www.mlb.com/cubs/roster',
    'CWS': 'https://www.mlb.com/whitesox/roster',
    'CIN': 'https://www.mlb.com/reds/roster',
    'CLE': 'https://www.mlb.com/guardians/roster',
    'COL': 'https://www.mlb.com/rockies/roster',
    'DET': 'https://www.mlb.com/tigers/roster',
    'HOU': 'https://www.mlb.com/astros/roster',
    'KC': 'https://www.mlb.com/royals/roster',
    'LAA': 'https://www.mlb.com/angels/roster',
    'LAD': 'https://www.mlb.com/dodgers/roster',
    'MIA': 'https://www.mlb.com/marlins/roster',
    'MIL': 'https://www.mlb.com/brewers/roster',
    'MIN': 'https://www.mlb.com/twins/roster',
    'NYM': 'https://www.mlb.com/mets/roster',
    'NYY': 'https://www.mlb.com/yankees/roster',
    'PHI': 'https://www.mlb.com/phillies/roster',
    'PIT': 'https://www.mlb.com/pirates/roster',
    'SD': 'https://www.mlb.com/padres/roster',
    'SF': 'https://www.mlb.com/giants/roster',
    'SEA': 'https://www.mlb.com/mariners/roster',
    'STL': 'https://www.mlb.com/cardinals/roster',
    'TB': 'https://www.mlb.com/rays/roster',
    'TEX': 'https://www.mlb.com/rangers/roster',
    'TOR': 'https://www.mlb.com/bluejays/roster',
    'WSH': 'https://www.mlb.com/nationals/roster',
}

def extract_player_id_from_url(url):
    """Extract player ID from MLB.com player URL."""
    match = re.search(r'/player/(\d+)', url)
    if match:
        return int(match.group(1))
    return None

def scrape_team_roster(team_abbr, url):
    """
    Scrape a team's roster page and extract player IDs.
    Returns dict mapping player_id -> team_abbr
    """
    player_to_team = {}
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=15)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Look for player links in the page
            # MLB.com uses links like /player/{id}
            player_links = soup.find_all('a', href=re.compile(r'/player/\d+'))
            
            found_count = 0
            for link in player_links:
                player_id = extract_player_id_from_url(link.get('href', ''))
                if player_id:
                    player_to_team[player_id] = team_abbr
                    found_count += 1
            
            if found_count > 0:
                print(f"  {team_abbr}: Found {found_count} players")
            else:
                print(f"  {team_abbr}: No players found (may need manual review)")
            
            return player_to_team
        else:
            print(f"  {team_abbr}: HTTP {response.status_code}")
            return {}
    
    except Exception as e:
        print(f"  {team_abbr}: Error - {e}")
        return {}

def main():
    print("Reading CSV...")
    
    rows = []
    header = None
    
    with open(INPUT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            rows.append(row)
    
    print(f"Found {len(rows)} players\n")
    
    # Scrape all team rosters
    print("Scraping MLB.com team rosters...")
    all_player_teams = {}
    
    for idx, (team_abbr, url) in enumerate(TEAM_ROSTERS.items(), 1):
        print(f"[{idx}/30] Fetching {team_abbr}...")
        team_players = scrape_team_roster(team_abbr, url)
        all_player_teams.update(team_players)
        time.sleep(0.3)  # Rate limiting
    
    print(f"\nTotal players found across all teams: {len(all_player_teams)}\n")
    
    # Create new header with Team column in position B
    new_header = [header[0], 'Team'] + header[1:]
    
    # Process players
    new_rows = []
    team_counts = {}
    free_agent_count = 0
    matched_count = 0
    
    print("Assigning teams to players in CSV...")
    for idx, row in enumerate(rows):
        if idx % 200 == 0:
            print(f"  {idx + 1}/{len(rows)}...")
        
        player_id_str = row[1] if len(row) > 1 else ""
        
        team = ''
        try:
            player_id = int(player_id_str)
            if player_id in all_player_teams:
                team = all_player_teams[player_id]
                matched_count += 1
        except:
            pass
        
        # Default to Free Agent if not found
        if not team:
            team = 'Free Agent'
            free_agent_count += 1
        else:
            team_counts[team] = team_counts.get(team, 0) + 1
        
        # Create new row with team in column B
        new_row = [row[0], team] + row[1:]
        new_rows.append(new_row)
    
    # Write output
    print(f"\nWriting {OUTPUT_CSV}...")
    with open(OUTPUT_CSV, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(new_header)
        writer.writerows(new_rows)
    
    # Summary
    total_with_teams = sum(team_counts.values())
    
    print(f"\n✓ Complete!")
    print(f"✓ Total players in CSV: {len(new_rows)}")
    print(f"✓ Players matched to teams: {matched_count}")
    print(f"✓ Free Agents: {free_agent_count}")
    
    if team_counts:
        print(f"\n📊 Team breakdown:")
        for team in sorted(team_counts.keys()):
            print(f"  {team}: {team_counts[team]} players")

if __name__ == '__main__':
    main()
