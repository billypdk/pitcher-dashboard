#!/usr/bin/env python3
"""
Automated weekly data update for pitcher statistics.
- Scrapes Baseball Savant pitch mix and velocity data
- Adds team information
- Rebuilds interactive dashboards
- Logs all activity
"""

import csv
import json
import time
from datetime import datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import html as html_module

# Configuration
WORKSPACE = Path(__file__).parent
LOG_FILE = WORKSPACE / 'update_log.json'
TEAMS_CACHE = WORKSPACE / 'team_rosters.json'

# Savant URLs
URL_PITCH_MIX = "https://baseballsavant.mlb.com/leaderboard/custom?year=2025%2C2024%2C2023&type=pitcher&filter=&min=50&selections=pitch_count%2Cn_ff_formatted%2Cn_sl_formatted%2Cn_ch_formatted%2Cn_cu_formatted%2Cn_si_formatted%2Cn_fc_formatted%2Cn_fs_formatted%2Cn_kn_formatted%2Cn_st_formatted%2Cn_sv_formatted%2Cn_fo_formatted&chart=false&x=n_ff_formatted&y=n_ff_formatted&r=no&chartType=beeswarm&sort=player_name&sortDir=asc"
URL_VELOCITIES = "https://baseballsavant.mlb.com/leaderboard/custom?year=2025%2C2024%2C2023&type=pitcher&filter=&min=50&selections=pitch_count%2Cff_avg_speed%2Csl_avg_speed%2Cch_avg_speed%2Ccu_avg_speed%2Csi_avg_speed%2Cfc_avg_speed%2Cfs_avg_speed%2Ckn_avg_speed%2Cst_avg_speed%2Csv_avg_speed%2Cfo_avg_speed&chart=false&x=ff_avg_speed&y=ff_avg_speed&r=no&chartType=beeswarm&sort=player_name&sortDir=asc"

# Output files
OUT_PITCH_MIX_CSV = WORKSPACE / 'Test Pitchers - Copy of 2023-2025 pitch mix.csv'
OUT_VELOCITIES_CSV = WORKSPACE / 'Test Pitchers - Copy of 2023-2025 pitch velos.csv'
OUT_MIX_DASHBOARD = WORKSPACE / 'pitcher_pitch_mix_dashboard.html'
OUT_VELO_DASHBOARD = WORKSPACE / 'pitcher_dashboard.html'

class Logger:
    """Simple logging system for update tracking."""
    def __init__(self, log_file):
        self.log_file = log_file
        self.logs = []
        self.load_logs()
    
    def load_logs(self):
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    self.logs = json.load(f)
            except:
                self.logs = []
    
    def add(self, status, message):
        entry = {
            'timestamp': datetime.now().isoformat(),
            'status': status,
            'message': message
        }
        self.logs.append(entry)
        self.save_logs()
        print(f"[{status}] {message}")
    
    def save_logs(self):
        with open(self.log_file, 'w') as f:
            json.dump(self.logs[-100:], f, indent=2)  # Keep last 100 entries
    
    def get_last_update(self):
        if self.logs:
            return self.logs[-1]['timestamp']
        return None

def scrape_savant_table(url, timeout=60):
    """Scrape a Savant leaderboard table and return CSV content."""
    options = webdriver.ChromeOptions()
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--headless')  # Run in background
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    try:
        driver.get(url)
        
        # Wait for table to load
        wait = WebDriverWait(driver, timeout)
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
        time.sleep(2)  # Extra time for JS rendering
        
        # Extract table HTML
        table_html = driver.execute_script('return arguments[0].outerHTML;', table)
        
        # Parse HTML table to CSV
        csv_content = html_table_to_csv(table_html)
        return csv_content
        
    finally:
        driver.quit()

def html_table_to_csv(table_html):
    """Convert HTML table to CSV format."""
    from bs4 import BeautifulSoup
    
    soup = BeautifulSoup(table_html, 'html.parser')
    rows = []
    
    for tr in soup.find_all('tr'):
        cells = []
        for td in tr.find_all(['td', 'th']):
            text = td.get_text(strip=True)
            cells.append(text)
        if cells:
            rows.append(cells)
    
    # Convert to CSV format
    csv_lines = []
    for row in rows:
        # Quote fields if they contain commas
        quoted_row = [f'"{cell}"' if ',' in cell else cell for cell in row]
        csv_lines.append(','.join(quoted_row))
    
    return '\n'.join(csv_lines)

def load_team_roster():
    """Load cached team roster data."""
    team_map = {}
    
    # Try to load from cache first
    if TEAMS_CACHE.exists():
        try:
            with open(TEAMS_CACHE, 'r') as f:
                team_map = json.load(f)
        except:
            pass
    
    # Also check if we have the final teams CSV
    teams_csv = WORKSPACE / 'stats_with_teams_final.csv'
    if teams_csv.exists():
        with open(teams_csv, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if 'Player' in row and 'Team' in row:
                    team_map[row['Player']] = row['Team']
    
    return team_map

def add_team_to_csv(csv_content, team_map):
    """Add team column to CSV if not present."""
    lines = csv_content.strip().split('\n')
    headers = lines[0].split(',')
    
    # Check if Team column exists
    if 'Team' in headers:
        return csv_content
    
    # Add Team header
    headers.insert(1, 'Team')
    new_lines = [','.join(headers)]
    
    # Add team data for each player
    for line in lines[1:]:
        cells = line.split(',')
        if cells:
            player_name = cells[0].strip('"')
            team = team_map.get(player_name, 'Unknown')
            cells.insert(1, f'"{team}"')
            new_lines.append(','.join(cells))
    
    return '\n'.join(new_lines)

def save_csv(content, filepath):
    """Save CSV content to file."""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def rebuild_dashboards():
    """Rebuild both HTML dashboards from CSV files."""
    import subprocess
    
    # Run the dashboard builders
    scripts = [
        'build_pitch_mix_dashboard.py',
        'build_dashboard.py'
    ]
    
    for script in scripts:
        script_path = WORKSPACE / script
        if script_path.exists():
            try:
                subprocess.run(['python', str(script_path)], cwd=str(WORKSPACE), timeout=120)
            except Exception as e:
                print(f"Error rebuilding dashboard {script}: {e}")

def main():
    """Main update routine."""
    logger = Logger(LOG_FILE)
    
    try:
        logger.add('INFO', 'Starting weekly data update...')
        
        # Load team roster
        logger.add('INFO', 'Loading team roster data...')
        team_map = load_team_roster()
        logger.add('INFO', f'Loaded {len(team_map)} player-team mappings')
        
        # Scrape pitch mix data
        logger.add('INFO', 'Scraping Savant pitch mix data...')
        pitch_mix_csv = scrape_savant_table(URL_PITCH_MIX)
        pitch_mix_csv = add_team_to_csv(pitch_mix_csv, team_map)
        save_csv(pitch_mix_csv, OUT_PITCH_MIX_CSV)
        logger.add('SUCCESS', f'Saved pitch mix data: {OUT_PITCH_MIX_CSV.name}')
        
        # Scrape velocity data
        logger.add('INFO', 'Scraping Savant velocity data...')
        velocities_csv = scrape_savant_table(URL_VELOCITIES)
        velocities_csv = add_team_to_csv(velocities_csv, team_map)
        save_csv(velocities_csv, OUT_VELOCITIES_CSV)
        logger.add('SUCCESS', f'Saved velocity data: {OUT_VELOCITIES_CSV.name}')
        
        # Rebuild dashboards
        logger.add('INFO', 'Rebuilding dashboards...')
        rebuild_dashboards()
        logger.add('SUCCESS', 'Dashboards rebuilt successfully')
        
        logger.add('SUCCESS', 'Weekly update completed successfully!')
        
    except Exception as e:
        logger.add('ERROR', f'Update failed: {str(e)}')
        raise

if __name__ == '__main__':
    main()
