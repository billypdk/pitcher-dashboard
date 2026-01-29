#!/usr/bin/env python3
"""
Assign MLB teams to players in column B.
Uses player IDs to fetch from MLB Stats API.
Marks players without teams as 'Free Agent'.
"""
import csv
import requests
import json

INPUT_CSV = 'stats (51).csv'
OUTPUT_CSV = 'stats_with_teams_complete.csv'

def get_player_team_from_api(player_id):
    """
    Fetch player's current team from MLB Stats API.
    Returns team abbreviation or empty string.
    """
    try:
        url = f'https://statsapi.mlb.com/api/v1/people/{player_id}'
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if 'people' in data and len(data['people']) > 0:
                person = data['people'][0]
                
                # Check for current team
                if 'currentTeam' in person:
                    team = person['currentTeam'].get('abbreviation', '')
                    if team:
                        return team
                
                # Check for active stats with team info
                if 'stats' in person:
                    for stat in person['stats']:
                        if 'stat' in stat and 'team' in stat['stat']:
                            team = stat['stat']['team'].get('abbreviation', '')
                            if team:
                                return team
        
        return ''
    except:
        return ''

# Fallback manual mapping for known players
KNOWN_PLAYERS = {
    663623: 'ATL',      # Irvin, Jake
    650644: 'CLE',      # Civale, Aaron
    656731: 'NYM',      # Megill, Tylor
    669093: 'PHI',      # Estrada, Jeremiah
    664199: 'ARI',      # Clarke, Taylor
    641927: 'MIN',      # Ober, Bailey
    669358: 'TB',       # Baz, Shane
    663432: 'HOU',      # Rainey, Tanner
    605347: 'BAL',      # López, Jorge
    601713: 'PHI',      # Pivetta, Nick
    666619: 'PHI',      # Santos, Gregory
    663738: 'KC',       # Lynch IV, Daniel
    682227: 'SD',       # Williamson, Brandon
    592767: 'PHI',      # Smyly, Drew
    607192: 'TB',       # Glasnow, Tyler
    663947: 'LAD',      # Holton, Tyler
    681190: 'NYY',      # Vásquez, Randy
    641793: 'SEA',      # Littell, Zack
    650633: 'NYY',      # King, Michael
    621381: 'NYM',      # Strahm, Matt
    668964: 'LAD',      # Myers, Tobias
    663986: 'CLE',      # Stephan, Trevor
    500779: 'BAL',      # Quintana, Jose
    676272: 'LAD',      # Miller, Bobby
    543056: 'LAA',      # Coulombe, Danny
    663554: 'DET',      # Mize, Casey
    671345: 'DET',      # Foley, Jason
    605397: 'SD',       # Musgrove, Joe
    680686: 'NYM',      # Gray, Josiah
    664353: 'HOU',      # Urquidy, José
    572955: 'HOU',      # Johnson, Pierce
    518585: 'WSH',      # Cruz, Fernando
    669622: 'ARI',      # Bender, Anthony
    608718: 'MIL',      # Suter, Brent
    554430: 'PHI',      # Wheeler, Zack
    592866: 'NYY',      # Williams, Trevor
    608344: 'LAA',      # Irvin, Cole
    682243: 'SEA',      # Miller, Bryce
    621244: 'MIN',      # Berríos, José
    543135: 'BOS',      # Eovaldi, Nathan
    624133: 'PHI',      # Suárez, Ranger
    571578: 'WSH',      # Corbin, Patrick
    657585: 'CIN',      # Garrett, Reed
    668933: 'CIN',      # Ashcraft, Graham
    669711: 'WSH',      # Weissert, Greg
    592836: 'NYM',      # Walker, Taijuan
    676962: 'LAD',      # Brown, Ben
    641745: 'KC',       # Keller, Brad
    691587: 'CHC',      # Pérez, Eury
    596295: 'STL',      # Gomber, Austin
    502624: 'NYY',      # Anderson, Chase
    677958: 'TB',       # Rocker, Kumar
    641755: 'MIA',      # Kinley, Tyler
    657514: 'SD',       # Bernardino, Brennan
    642100: 'NYM',      # Speier, Gabe
    676534: 'COL',      # Faucher, Calvin
    680573: 'MIN',      # Woods Richardson, Simeon
    571510: 'DET',      # Boyd, Matthew
    453286: 'NYM',      # Scherzer, Max
    605135: 'NYY',      # Bassitt, Chris
    605177: 'MIL',      # Chafin, Andrew
    641154: 'BAL',      # López, Pablo
    573186: 'NYM',      # Stroman, Marcus
}

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
    
    # Create new header with Team column in position B
    new_header = [header[0], 'Team'] + header[1:]
    
    # Process players
    new_rows = []
    team_counts = {}
    api_hits = 0
    manual_hits = 0
    free_agents = 0
    
    print("Fetching team information...")
    for idx, row in enumerate(rows):
        if idx % 100 == 0:
            print(f"  {idx + 1}/{len(rows)}...")
        
        player_id_str = row[1] if len(row) > 1 else ""
        player_name = row[0] if row else ""
        
        team = ''
        
        try:
            player_id = int(player_id_str)
            
            # Try API first
            team = get_player_team_from_api(player_id)
            
            # Fall back to manual mapping
            if not team and player_id in KNOWN_PLAYERS:
                team = KNOWN_PLAYERS[player_id]
                manual_hits += 1
            elif team:
                api_hits += 1
        except:
            pass
        
        # Default to Free Agent if not found
        if not team:
            team = 'Free Agent'
            free_agents += 1
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
    print(f"✓ Total players: {len(new_rows)}")
    print(f"✓ Players with teams: {total_with_teams}")
    print(f"  - From API: {api_hits}")
    print(f"  - From manual mapping: {manual_hits}")
    print(f"✓ Free Agents: {free_agents}")
    
    if team_counts:
        print(f"\n📊 Team breakdown:")
        for team in sorted(team_counts.keys()):
            print(f"  {team}: {team_counts[team]} players")

if __name__ == '__main__':
    main()
