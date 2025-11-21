"""
Simple Flask web server to serve dashboard_sample.html as homepage
"""
from flask import Flask, send_file, send_from_directory
import os

# Set up Flask with static files
# Flask will automatically serve files from 'web' folder at '/web' URL
app = Flask(__name__, 
            static_folder='web', 
            static_url_path='/web')

@app.route('/')
def index():
    """Serve dashboard_sample.html as homepage"""
    try:
        return send_file('dashboard_sample.html')
    except FileNotFoundError:
        return "Error: dashboard_sample.html not found", 404

# Export app for Vercel
# Vercel's @vercel/python will automatically detect Flask apps

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    print(f"🌐 Starting web server on http://localhost:{port}")
    print(f"📊 Dashboard available at http://localhost:{port}/")
    print(f"📁 Static files at http://localhost:{port}/web/")
    app.run(host='127.0.0.1', port=port, debug=True)

