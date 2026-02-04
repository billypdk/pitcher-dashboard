#!/usr/bin/env python3
"""
Update pitch mix data in combined_pitcher_dashboard_final.html
using rows from test pitcher mix.csv (matching by Player Name, Team, year).
"""
from pathlib import Path
import csv
import io

workspace = Path(__file__).parent
html_path = workspace / "combined_pitcher_dashboard_final.html"
test_csv_path = workspace / "Test Pitchers - Copy of 2023-2025 pitch mix TABLE FINAL.csv"

# Load test CSV rows into dict
with open(test_csv_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    test_rows = list(reader)

if not test_rows:
    raise SystemExit("Test CSV is empty.")

header = test_rows[0]

def make_key(row):
    return (row[0], row[1], row[2])

test_map = {make_key(row): row for row in test_rows[1:]}

# Read HTML
html_text = html_path.read_text(encoding="utf-8")
start_tag = '<script type="text/csv" id="mix-csvData">'
start_idx = html_text.find(start_tag)
if start_idx == -1:
    raise SystemExit("mix-csvData block not found.")

start_idx += len(start_tag)
end_tag = "</script>"
end_idx = html_text.find(end_tag, start_idx)
if end_idx == -1:
    raise SystemExit("End of mix-csvData block not found.")

# Replace entire CSV block with test CSV data
output = io.StringIO()
writer = csv.writer(output, lineterminator='\n')
writer.writerows(test_rows)
new_csv_block = output.getvalue()

# Replace block in HTML
new_html = html_text[:start_idx] + "\n" + new_csv_block + html_text[end_idx:]
html_path.write_text(new_html, encoding="utf-8")

print(f"Replaced entire pitch mix data with {len(test_rows)-1} rows from {test_csv_path.name}.")
