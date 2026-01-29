#!/usr/bin/env python3
"""
Selenium scraper for the Baseball Savant custom leaderboard URL.

Outputs:
 - savant_leaderboard.html  (full page fragment with extracted table)
 - abbott_from_savant.html  (HTML table rows for Andrew Abbott, if present)

Usage:
    pip install selenium webdriver-manager
    python scrape_savant_selenium.py
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import html
import time

URL = "https://baseballsavant.mlb.com/leaderboard/custom?year=2025%2C2024%2C2023&type=pitcher&filter=&min=10&selections=pitch_count%2Cff_avg_speed%2Csl_avg_speed%2Cch_avg_speed%2Ccu_avg_speed%2Csi_avg_speed%2Cfc_avg_speed%2Cfs_avg_speed%2Ckn_avg_speed%2Cst_avg_speed%2Csv_avg_speed%2Cfo_avg_speed&chart=false&x=ff_avg_speed&y=ff_avg_speed&r=no&chartType=beeswarm&sort=player_name&sortDir=asc"

OUT_HTML = 'savant_leaderboard.html'
OUT_ABBOTT = 'abbott_from_savant.html'

def main():
    options = webdriver.ChromeOptions()
    # Run with visible browser for debugging (no headless flag)
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--start-maximized')

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    try:
        driver.get(URL)

        # wait for a <table> to appear (the leaderboard table)
        wait = WebDriverWait(driver, 30)
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'table')))

        # give some extra time for JS-rendered content inside the table
        time.sleep(1)

        # extract outerHTML of the table
        table_html = driver.execute_script('return arguments[0].outerHTML;', table)

        # write an HTML file wrapping the extracted table
        with open(OUT_HTML, 'w', encoding='utf-8') as f:
            f.write('<!doctype html>\n<html lang="en">\n<head>\n')
            f.write('  <meta charset="utf-8">\n  <meta name="viewport" content="width=device-width,initial-scale=1">\n')
            f.write('  <title>Baseball Savant — Leaderboard Extract</title>\n')
            f.write('  <style>table{border-collapse:collapse}th,td{border:1px solid #ddd;padding:6px}</style>\n')
            f.write('</head>\n<body>\n')
            f.write('<h1>Extracted leaderboard table</h1>\n')
            f.write(table_html)
            f.write('\n</body>\n</html>')

        # parse rows and headers via selenium elements for robust column extraction
        headers = [th.text for th in table.find_elements(By.TAG_NAME, 'th')]
        rows = []
        for tr in table.find_elements(By.TAG_NAME, 'tr'):
            cells = tr.find_elements(By.TAG_NAME, 'td')
            if not cells:
                continue
            rows.append([c.text for c in cells])

        # filter for Andrew Abbott (both name parts present)
        abbott_rows = [r for r in rows if any('Abbott' in cell for cell in r) and any('Andrew' in cell for cell in r)]
        if abbott_rows:
            with open(OUT_ABBOTT, 'w', encoding='utf-8') as f:
                f.write('<!doctype html>\n<html><head><meta charset="utf-8"><title>Andrew Abbott</title></head><body>\n')
                f.write('<h1>Andrew Abbott rows (from Savannah leaderboard)</h1>\n')
                f.write('<table>\n<thead>\n<tr>')
                for h in headers:
                    f.write('<th>{}</th>'.format(html.escape(h)))
                f.write('</tr>\n</thead>\n<tbody>\n')
                for r in abbott_rows:
                    f.write('<tr>')
                    for c in r:
                        f.write('<td>{}</td>'.format(html.escape(c)))
                    f.write('</tr>\n')
                f.write('</tbody>\n</table>\n</body></html>')

        print('Saved:', OUT_HTML, OUT_ABBOTT)

    finally:
        driver.quit()

if __name__ == '__main__':
    main()
