from flask import Flask, render_template_string, request, send_file
import requests
import csv
import time
from urllib.parse import quote_plus
import os

# ─── CONFIGURATION ─────────────────────────────────────────────────────
SERPAPI_KEY = "a74c9bfa042543ea769b366227147a51b5487933833d9b3e68956136f7224fe6"

# ─── FLASK APP SETUP ───────────────────────────────────────────────────
app = Flask(__name__)

# ─── HTML FORM TEMPLATE ────────────────────────────────────────────────
HTML_FORM = """
<!DOCTYPE html>
<html>
<head>
    <title>Instagram & Facebook Lead Scraper</title>
    <style>
        body { font-family: Arial; padding: 20px; background-color: #f4f4f4; }
        h2 { color: #333; }
        form { background: white; padding: 20px; border-radius: 8px; max-width: 400px; margin: auto; }
        input, select, button { width: 100%; padding: 10px; margin: 8px 0; }
        button { background-color: #28a745; color: white; border: none; cursor: pointer; }
        button:hover { background-color: #218838; }
    </style>
</head>
<body>
    <h2>Instagram & Facebook Lead Scraper</h2>
    <form method="POST" action="/scrape">
        <label>Keyword</label>
        <input type="text" name="keyword" placeholder="e.g. web designer" required>
        
        <label>Location</label>
        <input type="text" name="location" placeholder="e.g. Mumbai" required>

        <label>Platform</label>
        <select name="platform" required>
            <option value="instagram.com">Instagram</option>
            <option value="facebook.com">Facebook</option>
        </select>

        <button type="submit">Scrape Leads</button>
    </form>
</body>
</html>
"""

# ─── FUNCTIONS ─────────────────────────────────────────────────────────
def search_profiles(query, max_results=50):
    """Search Google for public Instagram or Facebook profiles using SerpAPI."""
    url = (
        f"https://serpapi.com/search.json"
        f"?q={quote_plus(query)}"
        f"&engine=google"
        f"&api_key={SERPAPI_KEY}"
        f"&num={max_results}"
    )
    data = requests.get(url).json()
    return data.get("organic_results", [])

def scrape_meta(url):
    """Extract the <meta name='description'> content from a given URL."""
    try:
        html = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10).text
        start = html.find('<meta name="description" content="')
        if start != -1:
            start += len('<meta name="description" content="')
            end = html.find('"', start)
            return html[start:end]
    except:
        pass
    return ""

# ─── ROUTES ────────────────────────────────────────────────────────────
@app.route("/", methods=["GET"])
def home():
    """Display the form."""
    return render_template_string(HTML_FORM)

@app.route("/scrape", methods=["POST"])
def scrape():
    """Handle form submission, perform scraping, and return CSV."""
    keyword = request.form["keyword"]
    location = request.form["location"]
    platform = request.form["platform"]

    # Build Google search query
    query = f'{keyword} "{location}" site:{platform}'
    results = search_profiles(query)

    # Collect leads
    leads = []
    for r in results:
        link = r.get("link", "")
        title = r.get("title", "")
        snippet = r.get("snippet", "")
        meta_desc = scrape_meta(link)
        leads.append([title, snippet, meta_desc, link])

    # Save leads to CSV
    filename = f"leads_{platform}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    filepath = os.path.join(os.getcwd(), filename)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Google Title", "Google Snippet", "Meta Description", "Profile URL"])
        writer.writerows(leads)

    return send_file(filepath, as_attachment=True)

# ─── MAIN ENTRY POINT ──────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)
