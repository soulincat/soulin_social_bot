"""
Simple Flask web server to serve dashboard_sample.html as homepage
"""
from flask import Flask, send_from_directory, send_file
import os

app = Flask(__name__, static_folder='web', static_url_path='/web')

@app.route('/')
def index():
    """Serve dashboard_sample.html as homepage"""
    return send_file('dashboard_sample.html')

@app.route('/web/<path:path>')
def serve_web(path):
    """Serve static files from web directory"""
    return send_from_directory('web', path)

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🌐 Starting web server on http://localhost:{port}")
    print(f"📊 Dashboard available at http://localhost:{port}/")
    app.run(host='0.0.0.0', port=port, debug=True)

