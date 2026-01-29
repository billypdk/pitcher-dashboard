import csv
import html

csv_path = r'Test Pitchers - Copy of 2023-2025 pitch mix.csv'
html_output = r'pitcher_pitch_mix_dashboard.html'

# Read CSV data
csv_data_lines = []
with open(csv_path, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    for row in reader:
        # Properly escape the row as a CSV line
        escaped_row = ','.join([f'"{cell}"' if ',' in cell else cell for cell in row])
        csv_data_lines.append(escaped_row)

# Create CSV content string
csv_content = '\n'.join(csv_data_lines)

# HTML template
html_template = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MLB Pitcher Pitch Mix 2023-2025</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1600px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 30px;
        }}
        
        h1 {{
            color: #333;
            margin-bottom: 10px;
            text-align: center;
        }}
        
        .info {{
            text-align: center;
            color: #666;
            margin-bottom: 20px;
            font-size: 14px;
        }}
        
        .controls {{
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
            align-items: center;
        }}
        
        .search-box {{
            flex: 1;
            min-width: 250px;
            padding: 10px 15px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
        }}
        
        .search-box:focus {{
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }}
        
        .team-filter {{
            padding: 10px 15px;
            border: 2px solid #ddd;
            border-radius: 6px;
            font-size: 14px;
            background: white;
            cursor: pointer;
        }}
        
        .team-filter:focus {{
            outline: none;
            border-color: #667eea;
        }}
        
        .btn {{
            padding: 10px 20px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
            transition: background 0.3s;
        }}
        
        .btn:hover {{
            background: #764ba2;
        }}
        
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            text-align: center;
        }}
        
        .stat-card .number {{
            font-size: 28px;
            font-weight: bold;
        }}
        
        .stat-card .label {{
            font-size: 12px;
            opacity: 0.9;
            margin-top: 5px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 13px;
        }}
        
        thead {{
            background: #f5f5f5;
            border-top: 2px solid #667eea;
            border-bottom: 2px solid #667eea;
            position: sticky;
            top: 0;
        }}
        
        th {{
            padding: 10px;
            text-align: left;
            font-weight: 600;
            color: #333;
            cursor: pointer;
            user-select: none;
            white-space: nowrap;
        }}
        
        th:hover {{
            background: #e8e8e8;
        }}
        
        th.sortable::after {{
            content: ' ⇅';
            opacity: 0.5;
        }}
        
        td {{
            padding: 10px;
            border-bottom: 1px solid #eee;
        }}
        
        tbody tr:hover {{
            background: #f9f9f9;
        }}
        
        .team {{
            background: #667eea;
            color: white;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: bold;
            display: inline-block;
        }}
        
        .team.free-agent {{
            background: #999;
        }}
        
        .number {{
            text-align: right;
            font-family: 'Courier New', monospace;
        }}
        
        .no-data {{
            text-align: center;
            padding: 40px;
            color: #999;
        }}
        
        .footer {{
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid #eee;
        }}
        
        .table-wrapper {{
            overflow-x: auto;
            max-height: 800px;
            border: 1px solid #ddd;
            border-radius: 6px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>⚾ MLB Pitcher Pitch Mix</h1>
        <div class="info">2023-2025 Pitch Mix Percentages • All Years Included</div>
        
        <div class="stats" id="statsContainer"></div>
        
        <div class="controls">
            <input type="text" class="search-box" id="searchInput" placeholder="Search by player name...">
            <select class="team-filter" id="teamFilter">
                <option value="">All Teams</option>
            </select>
            <button class="btn" onclick="resetFilters()">Reset</button>
        </div>
        
        <div class="table-wrapper">
            <table id="dataTable">
                <thead>
                    <tr>
                        <th class="sortable" onclick="sortTable('player')">Player Name</th>
                        <th class="sortable" onclick="sortTable('team')">Team</th>
                        <th class="sortable" onclick="sortTable('year')">Year</th>
                        <th class="sortable" onclick="sortTable('pitch_count')">Pitch Count</th>
                        <th class="sortable" onclick="sortTable('FB')">FB %</th>
                        <th class="sortable" onclick="sortTable('SL')">SL %</th>
                        <th class="sortable" onclick="sortTable('CH')">CH %</th>
                        <th class="sortable" onclick="sortTable('CB')">CB %</th>
                        <th class="sortable" onclick="sortTable('SNK')">SNK %</th>
                        <th class="sortable" onclick="sortTable('CUT')">CUT %</th>
                        <th class="sortable" onclick="sortTable('SPLT')">SPLT %</th>
                        <th class="sortable" onclick="sortTable('KN')">KN %</th>
                        <th class="sortable" onclick="sortTable('SWP')">SWP %</th>
                        <th class="sortable" onclick="sortTable('SLV')">SLV %</th>
                        <th class="sortable" onclick="sortTable('FRK')">FRK %</th>
                    </tr>
                </thead>
                <tbody id="tableBody">
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            Data sourced from Baseball Savant (2023-2025) • Pitch Mix Percentages • Updated January 27, 2026
        </div>
    </div>

    <script type="text/csv" id="csvData">{csv_content}</script>
    <script>
        let allData = [];
        let filteredData = [];
        let currentSort = {{ column: 'player', direction: 'asc' }};

        function parseCSV(csv) {{
            const lines = csv.trim().split('\\n');
            const headers = lines[0].split(',').map(h => h.trim());
            const data = [];
            
            for (let i = 1; i < lines.length; i++) {{
                const line = lines[i];
                const values = [];
                let current = '';
                let inQuotes = false;
                
                for (let j = 0; j < line.length; j++) {{
                    const char = line[j];
                    if (char === '\"') {{
                        inQuotes = !inQuotes;
                    }} else if (char === ',' && !inQuotes) {{
                        values.push(current);
                        current = '';
                    }} else {{
                        current += char;
                    }}
                }}
                values.push(current);
                
                // Ensure we have the right number of columns
                while (values.length < headers.length) {{
                    values.push('');
                }}
                
                const obj = {{}};
                headers.forEach((header, index) => {{
                    let val = values[index] ? values[index].trim() : '';
                    // Remove quotes if present
                    if (val.startsWith('\"') && val.endsWith('\"')) {{
                        val = val.slice(1, -1);
                    }}
                    obj[header] = val;
                }});
                data.push(obj);
            }}
            
            return data;
        }}

        function initializeData() {{
            const csvContent = document.querySelector('script#csvData').textContent.trim();
            allData = parseCSV(csvContent);
            filteredData = [...allData];
            
            // Populate team filter
            const teams = [...new Set(allData.map(d => d.Team))].sort();
            const teamFilter = document.getElementById('teamFilter');
            teams.forEach(team => {{
                const option = document.createElement('option');
                option.value = team;
                option.textContent = team;
                teamFilter.appendChild(option);
            }});
            
            updateStats();
            renderTable();
            
            // Add event listeners
            document.getElementById('searchInput').addEventListener('input', applyFilters);
            document.getElementById('teamFilter').addEventListener('change', applyFilters);
        }}

        function updateStats() {{
            const stats = {{
                total: filteredData.length,
                teams: new Set(filteredData.map(d => d.Team)).size,
                avgFastball: (filteredData.reduce((sum, d) => sum + (parseFloat(d.FB) || 0), 0) / filteredData.filter(d => d.FB).length).toFixed(1)
            }};
            
            document.getElementById('statsContainer').innerHTML = `
                <div class="stat-card">
                    <div class="number">${{stats.total}}</div>
                    <div class="label">Pitcher Records</div>
                </div>
                <div class="stat-card">
                    <div class="number">${{stats.teams}}</div>
                    <div class="label">Teams</div>
                </div>
                <div class="stat-card">
                    <div class="number">${{stats.avgFastball}}%</div>
                    <div class="label">Avg FB Mix</div>
                </div>
            `;
        }}

        function applyFilters() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const teamFilter = document.getElementById('teamFilter').value;
            
            filteredData = allData.filter(row => {{
                const playerMatch = row['Player Name'].toLowerCase().includes(searchTerm);
                const teamMatch = !teamFilter || row.Team === teamFilter;
                return playerMatch && teamMatch;
            }});
            
            updateStats();
            renderTable();
        }}

        function sortTable(column) {{
            if (currentSort.column === column) {{
                currentSort.direction = currentSort.direction === 'asc' ? 'desc' : 'asc';
            }} else {{
                currentSort.column = column;
                currentSort.direction = 'asc';
            }}
            
            filteredData.sort((a, b) => {{
                let aVal = column === 'player' ? a['Player Name'] : a[column];
                let bVal = column === 'player' ? b['Player Name'] : b[column];
                
                if (!isNaN(aVal) && !isNaN(bVal) && aVal !== '' && bVal !== '') {{
                    aVal = parseFloat(aVal);
                    bVal = parseFloat(bVal);
                }}
                
                if (currentSort.direction === 'asc') {{
                    return aVal > bVal ? 1 : -1;
                }} else {{
                    return aVal < bVal ? 1 : -1;
                }}
            }});
            
            renderTable();
        }}

        function renderTable() {{
            const tbody = document.getElementById('tableBody');
            
            if (filteredData.length === 0) {{
                tbody.innerHTML = '<tr><td colspan="15" class="no-data">No pitchers found</td></tr>';
                return;
            }}
            
            tbody.innerHTML = filteredData.map(row => {{
                const teamClass = row.Team === 'Free Agent' ? 'free-agent' : '';
                return `
                    <tr>
                        <td>${{row['Player Name']}}</td>
                        <td><span class="team ${{teamClass}}">${{row.Team}}</span></td>
                        <td class="number">${{row.year}}</td>
                        <td class="number">${{row.pitch_count}}</td>
                        <td class="number">${{row.FB || '-'}}</td>
                        <td class="number">${{row.SL || '-'}}</td>
                        <td class="number">${{row.CH || '-'}}</td>
                        <td class="number">${{row.CB || '-'}}</td>
                        <td class="number">${{row.SNK || '-'}}</td>
                        <td class="number">${{row.CUT || '-'}}</td>
                        <td class="number">${{row.SPLT || '-'}}</td>
                        <td class="number">${{row.KN || '-'}}</td>
                        <td class="number">${{row.SWP || '-'}}</td>
                        <td class="number">${{row.SLV || '-'}}</td>
                        <td class="number">${{row.FRK || '-'}}</td>
                    </tr>
                `;
            }}).join('');
        }}

        function resetFilters() {{
            document.getElementById('searchInput').value = '';
            document.getElementById('teamFilter').value = '';
            applyFilters();
        }}

        // Initialize on page load
        window.addEventListener('load', initializeData);
    </script>
</body>
</html>'''

# Write the HTML file
with open(html_output, 'w', encoding='utf-8') as f:
    f.write(html_template)

print(f'Dashboard created successfully: {html_output}')
print(f'Total CSV rows processed: {len(csv_data_lines)}')
