#!/usr/bin/env python3
"""
Scrape Baseball Savant leaderboards and combine data.
Filter for pitchers with data prior to 2024 (2023 or earlier) AND 2024/2025.
"""
import requests
from bs4 import BeautifulSoup
import json
import time
from collections import defaultdict

# URLs to scrape
URLS = [
    "https://baseballsavant.mlb.com/leaderboard/custom?year=2025%2C2024%2C2023&type=pitcher&filter=&min=10&selections=pitch_count%2Cff_avg_speed%2Csl_avg_speed%2Cch_avg_speed%2Ccu_avg_speed%2Csi_avg_speed%2Cfc_avg_speed%2Cfs_avg_speed%2Ckn_avg_speed%2Cst_avg_speed%2Csv_avg_speed%2Cfo_avg_speed&chart=false&x=ff_avg_speed&y=ff_avg_speed&r=no&chartType=beeswarm&sort=player_name&sortDir=asc",
    "https://baseballsavant.mlb.com/leaderboard/custom?year=2025%2C2024%2C2023&type=pitcher&filter=&min=10&selections=pitch_count%2Cn_ff_formatted%2Cn_sl_formatted%2Cn_ch_formatted%2Cn_cu_formatted%2Cn_si_formatted%2Cn_fc_formatted%2Cn_fs_formatted%2Cn_kn_formatted%2Cn_st_formatted%2Cn_sv_formatted%2Cn_fo_formatted&chart=false&x=n_ff_formatted&y=n_ff_formatted&r=no&chartType=beeswarm&sort=player_name&sortDir=asc"
]

def scrape_savant_table(url, source_name):
    """
    Scrape a Baseball Savant leaderboard table.
    Returns dict with player data indexed by name.
    """
    print(f"Scraping {source_name}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the data table
            table = soup.find('table', {'class': lambda x: x and 'Table' in x if x else False})
            
            if not table:
                # Try alternate selectors
                table = soup.find('table')
            
            if not table:
                print(f"  No table found in {source_name}")
                return {}
            
            players = {}
            rows = table.find_all('tr')[1:]  # Skip header
            
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    # First cell is usually player name
                    name_cell = cells[0].get_text(strip=True)
                    
                    # Extract all data from this row
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    
                    if name_cell:
                        players[name_cell] = {
                            'raw': row_data,
                            'source': source_name
                        }
            
            print(f"  Found {len(players)} players")
            return players
        else:
            print(f"  Failed: HTTP {response.status_code}")
            return {}
    
    except Exception as e:
        print(f"  Error: {e}")
        return {}

def main():
    print("Starting Baseball Savant scraping...\n")
    
    # Scrape both URLs
    data_sets = []
    for idx, url in enumerate(URLS, 1):
        source_name = f"Leaderboard {idx}"
        data = scrape_savant_table(url, source_name)
        data_sets.append(data)
        time.sleep(2)  # Rate limiting
    
    print(f"\nTotal players scraped: {len(data_sets[0])} + {len(data_sets[1])}")
    
    # Combine and filter
    combined = defaultdict(lambda: {'2023': False, '2024': False, '2025': False})
    
    # For now, output the scraped data to examine structure
    print("\nSample data from first leaderboard:")
    for i, (name, data) in enumerate(list(data_sets[0].items())[:5]):
        print(f"  {name}: {data['raw']}")
    
    # Save raw data to JSON for inspection
    with open('savant_scraped_raw.json', 'w') as f:
        json.dump({
            'leaderboard_1': {k: v['raw'] for k, v in list(data_sets[0].items())[:10]},
            'leaderboard_2': {k: v['raw'] for k, v in list(data_sets[1].items())[:10]}
        }, f, indent=2)
    
    print("\nRaw sample saved to savant_scraped_raw.json for review")

if __name__ == '__main__':
    main()
