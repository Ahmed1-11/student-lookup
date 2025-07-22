from flask import Flask, request, render_template_string
import sqlite3
import os
import gdown

app = Flask(__name__)

DB_FILE = 'data.db'
DRIVE_FILE_ID = '1sM013T1oIkKvBDoU6aw1f0HF9bfsKroQ'  

def download_db():
    if not os.path.exists(DB_FILE):
        print("📥 Downloading data.db from Google Drive...")
        url = f"https://drive.google.com/uc?id={DRIVE_FILE_ID}"
        gdown.download(url, DB_FILE, quiet=False)
        print("✅ Download complete.")

download_db()

def query_seating(seating_no):
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT arabic_name, total_degree FROM records WHERE seating_no = ?", (seating_no,))
        row = cur.fetchone()
        conn.close()
        return dict(row) if row else None
    except Exception as e:
        print(f"Database error: {e}")
        return None

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Results</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            max-width: 500px;
            width: 100%;
            text-align: center;
        }
        .search-input {
            width: 200px;
            padding: 15px;
            margin: 10px;
            border: 2px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
        }
        .search-btn {
            padding: 15px 30px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-weight: 600;
        }
        .result {
            margin-top: 30px;
            padding: 20px;
            border-radius: 10px;
        }
        .result.success {
            background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
            color: white;
        }
        .result.error {
            background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
            color: #333;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Student Results</h1>
        <form method="POST">
            <input type="text" name="seating_no" class="search-input" placeholder="Enter seating number" value="{{ seating_no or '' }}" required>
            <br>
            <button type="submit" class="search-btn">🔍 Search</button>
        </form>
        
        {% if result %}
            <div class="result success">
                <h3>✅ Student Found!</h3>
                <p><strong>📋 Seating Number:</strong> {{ seating_no }}</p>
                <p><strong>👤 Arabic Name:</strong> {{ result.arabic_name }}</p>
                <p><strong>📊 Total Degree:</strong> {{ result.total_degree }}</p>
            </div>
        {% elif result is not none %}
            <div class="result error">
                <h3>❌ No Match Found</h3>
                <p>No student found with seating number: {{ seating_no }}</p>
            </div>
        {% endif %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    seating_no = None
    if request.method == 'POST':
        seating_no = request.form.get('seating_no', '').strip()
        if seating_no:
            result = query_seating(seating_no)
    return render_template_string(HTML_TEMPLATE, result=result, seating_no=seating_no)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
