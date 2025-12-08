"""
Flask web server for dashboard and content management
"""
from flask import Flask, send_file, send_from_directory, request, jsonify, render_template_string
import os
import json

# Set up Flask with static files and templates
app = Flask(__name__, 
            static_folder='web', 
            static_url_path='/web',
            template_folder='web/templates')

# Content API routes
from content.center_post import create_center_post, get_post, list_posts, update_post, delete_post
from content.branch_generator import generate_branches
from content.derivative_generator import generate_derivatives, get_derivatives
from content.publisher import schedule_derivatives, publish_queued_derivatives
from content.pillar_tracker import create_pillar, get_pillars, get_pillar_performance, track_content_performance

@app.route('/')
def index():
    """Serve dashboard_sample.html as homepage"""
    try:
        return send_file('dashboard_sample.html')
    except FileNotFoundError:
        return "Error: dashboard_sample.html not found", 404

# Content Management Routes
@app.route('/api/content/posts', methods=['GET'])
def api_list_posts():
    """List all content posts"""
    client_id = request.args.get('client_id')
    status = request.args.get('status')
    posts = list_posts(client_id=client_id, status=status)
    return jsonify({"posts": posts})

@app.route('/api/content/posts', methods=['POST'])
def api_create_post():
    """Create a new center post"""
    data = request.json
    try:
        print(f"Creating post for client: {data.get('client_id')}, idea: {data.get('raw_idea')[:50]}...")
        post = create_center_post(
            client_id=data.get('client_id'),
            raw_idea=data.get('raw_idea', ''),
            auto_expand=data.get('auto_expand', True),
            pillar_id=data.get('pillar_id')
        )
        print(f"Post created successfully: {post.get('id')}, status: {post.get('status')}")
        return jsonify(post), 201
    except Exception as e:
        print(f"Error creating post: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 400

@app.route('/api/content/posts/<post_id>', methods=['GET'])
def api_get_post(post_id):
    """Get a specific post"""
    post = get_post(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post)

@app.route('/api/content/posts/<post_id>/branch', methods=['POST'])
def api_generate_branches(post_id):
    """Generate archive and blog versions"""
    try:
        post = generate_branches(post_id)
        return jsonify(post)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/content/posts/<post_id>/generate', methods=['POST'])
def api_generate_derivatives(post_id):
    """Generate all derivatives"""
    data = request.json or {}
    try:
        derivatives = generate_derivatives(
            post_id,
            include_podcast=data.get('include_podcast', False)
        )
        return jsonify({"derivatives": derivatives})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/content/posts/<post_id>/schedule', methods=['POST'])
def api_schedule_derivatives(post_id):
    """Schedule derivatives for publishing"""
    schedule_config = request.json
    try:
        derivatives = schedule_derivatives(post_id, schedule_config)
        return jsonify({"derivatives": derivatives})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/content/derivatives', methods=['GET'])
def api_list_derivatives():
    """List derivatives"""
    post_id = request.args.get('post_id')
    status = request.args.get('status')
    derivatives = get_derivatives(post_id=post_id, status=status)
    return jsonify({"derivatives": derivatives})

@app.route('/api/content/pillars', methods=['GET'])
def api_list_pillars():
    """List content pillars"""
    client_id = request.args.get('client_id')
    pillars = get_pillars(client_id=client_id)
    return jsonify({"pillars": pillars})

@app.route('/api/content/pillars', methods=['POST'])
def api_create_pillar():
    """Create a new pillar"""
    data = request.json
    try:
        pillar = create_pillar(
            client_id=data.get('client_id'),
            name=data.get('name'),
            color=data.get('color', '#3b82f6'),
            channels=data.get('channels', []),
            target_audience=data.get('target_audience')
        )
        return jsonify(pillar), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/content/pillars/<pillar_id>/performance', methods=['GET'])
def api_get_pillar_performance(pillar_id):
    """Get pillar performance metrics"""
    days = request.args.get('days', 30, type=int)
    try:
        performance = get_pillar_performance(pillar_id, date_range_days=days)
        return jsonify(performance)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/content/posts/<post_id>/performance', methods=['POST'])
def api_track_performance(post_id):
    """Track content performance"""
    metrics = request.json
    try:
        result = track_content_performance(post_id, metrics)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

# Web UI Routes
@app.route('/content')
def content_list_page():
    """Content list page"""
    return send_file('web/templates/content_list.html')

@app.route('/content/create')
def content_create_page():
    """Content creation page"""
    return send_file('web/templates/content_create.html')

@app.route('/content/<post_id>')
def content_detail_page(post_id):
    """Content detail page"""
    return send_file('web/templates/content_detail.html')

@app.route('/api/clients', methods=['GET'])
def api_list_clients():
    """List all clients"""
    try:
        with open('clients.json', 'r') as f:
            data = json.load(f)
        return jsonify({"clients": data.get('clients', [])})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Settings Routes
@app.route('/settings')
def settings_page():
    """Settings page"""
    return send_file('web/templates/settings.html')

@app.route('/api/clients/<client_id>/brand', methods=['GET'])
def api_get_brand(client_id):
    """Get brand settings for a client"""
    try:
        with open('clients.json', 'r') as f:
            data = json.load(f)
        
        client = None
        for c in data.get('clients', []):
            if c.get('client_id') == client_id:
                client = c
                break
        
        if not client:
            return jsonify({"error": "Client not found"}), 404
        
        brand = client.get('brand', {})
        return jsonify({"brand": brand})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/clients/<client_id>/brand', methods=['PUT'])
def api_update_brand(client_id):
    """Update brand settings for a client"""
    try:
        with open('clients.json', 'r') as f:
            data = json.load(f)
        
        client_index = None
        for i, c in enumerate(data.get('clients', [])):
            if c.get('client_id') == client_id:
                client_index = i
                break
        
        if client_index is None:
            return jsonify({"error": "Client not found"}), 404
        
        # Update brand section
        brand_data = request.json.get('brand', {})
        if 'brand' not in data['clients'][client_index]:
            data['clients'][client_index]['brand'] = {}
        
        # Merge brand data
        data['clients'][client_index]['brand'].update(brand_data)
        
        # Save back to file
        with open('clients.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        return jsonify({"brand": data['clients'][client_index]['brand']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Export app for Vercel
# Vercel's @vercel/python will automatically detect Flask apps

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3000))
    print(f"🌐 Starting web server on http://localhost:{port}")
    print(f"📊 Dashboard available at http://localhost:{port}/")
    print(f"📝 Content management at http://localhost:{port}/content")
    print(f"📁 Static files at http://localhost:{port}/web/")
    app.run(host='127.0.0.1', port=port, debug=True)

