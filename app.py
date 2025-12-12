"""
Flask web server for dashboard and content management
"""
from flask import Flask, send_file, send_from_directory, request, jsonify, render_template_string
import os
import json
import requests
from datetime import datetime

# Set up Flask with static files and templates
app = Flask(__name__, 
            static_folder='web', 
            static_url_path='/web',
            template_folder='web/templates')

# Content API routes - lazy imports to avoid crashing if ANTHROPIC_API_KEY is missing
# These will be imported inside the route handlers when needed

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
    from content.center_post import list_posts
    client_id = request.args.get('client_id')
    status = request.args.get('status')
    posts = list_posts(client_id=client_id, status=status)
    return jsonify({"posts": posts})

@app.route('/api/content/posts', methods=['POST'])
def api_create_post():
    """Create a new center post"""
    from content.center_post import create_center_post
    data = request.json
    try:
        print(f"Creating post for client: {data.get('client_id')}, idea: {data.get('raw_idea')[:50]}...")
        post = create_center_post(
            client_id=data.get('client_id'),
            raw_idea=data.get('raw_idea', ''),
            auto_expand=data.get('auto_expand', True),
            pillar_id=data.get('pillar_id'),
            include_cta=data.get('include_cta', False)
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
    from content.center_post import get_post
    post = get_post(post_id)
    if not post:
        return jsonify({"error": "Post not found"}), 404
    return jsonify(post)

@app.route('/api/content/posts/<post_id>', methods=['PUT'])
def api_update_post(post_id):
    """Update a post (status, pillar_id, etc.)"""
    from content.center_post import update_post
    try:
        updates = request.json
        if not updates:
            return jsonify({"error": "No update data provided"}), 400
        
        post = update_post(post_id, updates)
        return jsonify(post)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/content/posts/<post_id>/branch', methods=['POST'])
def api_generate_branches(post_id):
    """Generate archive and blog versions"""
    from content.branch_generator import generate_branches
    try:
        post = generate_branches(post_id)
        return jsonify(post)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/content/posts/<post_id>/generate', methods=['POST'])
def api_generate_derivatives(post_id):
    """Generate derivatives for selected platforms"""
    from content.center_post import get_post
    from content.derivative_generator import generate_derivatives
    data = request.json or {}
    platforms = data.get('platforms', ['linkedin', 'x', 'threads', 'instagram', 'substack', 'telegram'])
    try:
        # Get client_id from post
        post = get_post(post_id)
        client_id = post.get('client_id') if post else None
        
        derivatives = generate_derivatives(
            post_id,
            include_podcast=data.get('include_podcast', False),
            platforms=platforms,
            client_id=client_id
        )
        return jsonify({"derivatives": derivatives})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/content/posts/<post_id>/schedule', methods=['POST'])
def api_schedule_derivatives(post_id):
    """Schedule derivatives for publishing"""
    from content.publisher import schedule_derivatives
    schedule_config = request.json
    try:
        derivatives = schedule_derivatives(post_id, schedule_config)
        return jsonify({"derivatives": derivatives})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/content/derivatives', methods=['GET'])
def api_list_derivatives():
    """List derivatives"""
    from content.derivative_generator import get_derivatives
    post_id = request.args.get('post_id')
    status = request.args.get('status')
    derivatives = get_derivatives(post_id=post_id, status=status)
    return jsonify({"derivatives": derivatives})

@app.route('/api/content/derivatives/<deriv_id>/approve', methods=['POST'])
def api_approve_derivative(deriv_id):
    """Approve a derivative (change status from draft to approved)"""
    try:
        from content.derivative_generator import load_derivatives, save_derivatives
        data = load_derivatives()
        derivative = None
        for i, d in enumerate(data.get('derivatives', [])):
            if d.get('id') == deriv_id:
                derivative = d
                if d.get('metadata', {}).get('status') == 'draft':
                    data['derivatives'][i]['metadata']['status'] = 'approved'
                    save_derivatives(data)
                    return jsonify({"message": "Approved", "derivative": data['derivatives'][i]})
                else:
                    return jsonify({"error": "Derivative is not in draft status"}), 400
        if not derivative:
            return jsonify({"error": "Derivative not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/content/derivatives/<deriv_id>', methods=['PUT'])
def api_update_derivative(deriv_id):
    """Update a derivative (content, etc.)"""
    try:
        from content.derivative_generator import update_derivative, load_derivatives
        updates = request.json
        if not updates:
            return jsonify({"error": "No update data provided"}), 400
        
        derivative = update_derivative(deriv_id, updates)
        return jsonify(derivative)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/content/derivatives/<deriv_id>/regenerate', methods=['POST'])
def api_regenerate_derivative(deriv_id):
    """Regenerate a specific derivative"""
    try:
        from content.derivative_generator import load_derivatives, save_derivatives, get_derivatives
        from content.center_post import get_post
        from content.ai_client import ClaudeClient
        
        data = load_derivatives()
        derivative = None
        deriv_index = None
        for i, d in enumerate(data.get('derivatives', [])):
            if d.get('id') == deriv_id:
                derivative = d
                deriv_index = i
                break
        
        if not derivative:
            return jsonify({"error": "Derivative not found"}), 404
        
        # Get the original post
        post = get_post(derivative.get('post_id'))
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        source_content = post.get('center_post', {}).get('content', '')
        if not source_content:
            return jsonify({"error": "Post has no content"}), 400
        
        # Load brand settings for regeneration
        client_id = post.get('client_id')
        brand_socials = {}
        cta_info = None
        if client_id:
            try:
                try:
                    with open('clients.json', 'r') as f:
                        clients_data = json.load(f)
                except FileNotFoundError:
                    print("⚠️ clients.json not found, skipping brand settings")
                    clients_data = {"clients": []}
                
                for client in clients_data.get('clients', []):
                    if client.get('client_id') == client_id:
                        brand_socials = client.get('brand', {}).get('socials', {})
                        # Get CTA info if post has include_cta flag
                        if post.get('include_cta'):
                            main_product = client.get('brand', {}).get('main_product', {})
                            if main_product.get('cta_text') and main_product.get('cta_url'):
                                cta_info = {
                                    'text': main_product['cta_text'],
                                    'url': main_product['cta_url']
                                }
                        break
            except Exception as e:
                print(f"Warning: Could not load brand settings: {e}")
        
        platform = derivative.get('type', '').lower()
        ai_client = ClaudeClient()
        
        # Regenerate based on platform
        if platform in ['linkedin', 'x', 'threads', 'instagram', 'substack']:
            social_posts = ai_client.generate_social_posts(
                source_content, 
                [platform],
                brand_socials=brand_socials,
                cta_info=cta_info
            )
            platform_posts = social_posts.get(platform, [])
            if platform_posts:
                new_content = platform_posts[0].get('content', '')
                if platform_posts[0].get('type') == 'thread' and platform_posts[0].get('thread_parts'):
                    new_content = '\n\n---\n\n'.join(platform_posts[0].get('thread_parts', []))
                data['derivatives'][deriv_index]['content'] = new_content
                data['derivatives'][deriv_index]['metadata']['status'] = 'draft'
        elif platform == 'telegram':
            new_content = ai_client.generate_telegram_announcement(source_content)
            data['derivatives'][deriv_index]['content'] = new_content
            data['derivatives'][deriv_index]['metadata']['status'] = 'draft'
        else:
            return jsonify({"error": f"Regeneration not supported for platform: {platform}"}), 400
        
        save_derivatives(data)
        return jsonify({"message": "Regenerated", "derivative": data['derivatives'][deriv_index]})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/content/derivatives/<deriv_id>/publish', methods=['POST'])
def api_publish_derivative(deriv_id):
    """Publish a derivative to its platform (Beehiiv for newsletters, etc.)"""
    try:
        from content.derivative_generator import load_derivatives, save_derivatives, get_derivatives
        from content.center_post import get_post
        
        data = load_derivatives()
        derivative = None
        deriv_index = None
        
        for i, d in enumerate(data.get('derivatives', [])):
            if d.get('id') == deriv_id:
                derivative = d
                deriv_index = i
                break
        
        if not derivative:
            return jsonify({"error": "Derivative not found"}), 404
        
        deriv_type = derivative.get('type')
        
        # Get client_id from post
        post = get_post(derivative.get('post_id'))
        if not post:
            return jsonify({"error": "Post not found"}), 404
        
        client_id = post.get('client_id')
        
        # Publish based on type
        if deriv_type == 'newsletter':
            from content.publisher import publish_to_beehiiv
            result = publish_to_beehiiv(derivative, client_id)
            
            if result.get('success'):
                # Update derivative status and add published info
                data['derivatives'][deriv_index]['metadata']['status'] = 'published'
                data['derivatives'][deriv_index]['published_at'] = datetime.now().isoformat()
                if result.get('published_url'):
                    data['derivatives'][deriv_index]['published_url'] = result['published_url']
                if result.get('post_id'):
                    data['derivatives'][deriv_index]['beehiiv_post_id'] = result['post_id']
                save_derivatives(data)
                
                return jsonify({
                    "message": result.get('message', 'Published successfully'),
                    "published_url": result.get('published_url'),
                    "derivative": data['derivatives'][deriv_index]
                })
            else:
                return jsonify({
                    "error": result.get('message', 'Failed to publish')
                }), 400
        else:
            return jsonify({"error": f"Publishing not yet implemented for type: {deriv_type}"}), 400
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/content/pillars', methods=['GET'])
def api_list_pillars():
    """List content pillars"""
    from content.pillar_tracker import get_pillars
    client_id = request.args.get('client_id')
    pillars = get_pillars(client_id=client_id)
    return jsonify({"pillars": pillars})

@app.route('/api/content/pillars', methods=['POST'])
def api_create_pillar():
    """Create a new pillar"""
    from content.pillar_tracker import create_pillar
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
    from content.pillar_tracker import get_pillar_performance
    days = request.args.get('days', 30, type=int)
    try:
        performance = get_pillar_performance(pillar_id, date_range_days=days)
        return jsonify(performance)
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/content/posts/<post_id>/performance', methods=['POST'])
def api_track_performance(post_id):
    """Track content performance"""
    from content.pillar_tracker import track_content_performance
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
        try:
            with open('clients.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("⚠️ clients.json not found, returning dummy client")
            # Return a dummy client so dashboard can still load
            return jsonify({
                "clients": [{
                    "client_id": "client_e7d73194",
                    "name": "Demo Client",
                    "status": "active"
                }]
            })
        clients = data.get('clients', [])
        # If no clients found, return dummy client
        if not clients:
            print("⚠️ No clients found, returning dummy client")
            return jsonify({
                "clients": [{
                    "client_id": "client_e7d73194",
                    "name": "Demo Client",
                    "status": "active"
                }]
            })
        return jsonify({"clients": clients})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Client Routes
@app.route('/api/clients/<client_id>', methods=['GET'])
def api_get_client(client_id):
    """Get a specific client"""
    try:
        try:
            with open('clients.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("⚠️ clients.json not found, returning 404")
            return jsonify({"error": "Client not found"}), 404
        
        client = None
        for c in data.get('clients', []):
            if c.get('client_id') == client_id:
                client = c
                break
        
        if not client:
            return jsonify({"error": "Client not found"}), 404
        
        return jsonify({"client": client})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Settings Routes
@app.route('/settings')
def settings_page():
    """Settings page"""
    return send_file('web/templates/settings.html')

@app.route('/product')
def product_page():
    """Product management page"""
    return send_file('web/templates/product.html')

@app.route('/api/clients/<client_id>/brand', methods=['GET'])
def api_get_brand(client_id):
    """Get brand settings for a client"""
    try:
        try:
            with open('clients.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("⚠️ clients.json not found, returning empty brand")
            return jsonify({"brand": {}})
        
        client = None
        for c in data.get('clients', []):
            if c.get('client_id') == client_id:
                client = c
                break
        
        if not client:
            return jsonify({"brand": {}})
        
        brand = client.get('brand', {})
        return jsonify({"brand": brand})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/socials', methods=['GET'])
def api_get_social_profiles():
    """Get social media profiles for enabled platforms"""
    try:
        client_id = request.args.get('client_id')
        if not client_id:
            return jsonify({"error": "client_id required"}), 400
        
        # Try to load clients.json, fallback to dummy data if not found (e.g., on Vercel)
        try:
            with open('clients.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("⚠️ clients.json not found, using dummy data for socials")
            data = {"clients": []}
        
        client = None
        for c in data.get('clients', []):
            if c.get('client_id') == client_id:
                client = c
                break
        
        # If client not found, use dummy client structure
        if not client:
            print(f"⚠️ Client {client_id} not found, using dummy data")
            client = {
                'client_id': client_id,
                'brand': {
                    'socials': {}
                },
                'connected_accounts': {}
            }
        
        brand = client.get('brand', {})
        socials = brand.get('socials', {})
        connected_accounts = client.get('connected_accounts', {})
        
        profiles = []
        total_followers = 0
        
        # Check each platform
        platform_configs = {
            'linkedin': {'name': 'LinkedIn', 'icon': '💼'},
            'x': {'name': 'X (Twitter)', 'icon': '🐦'},
            'threads': {'name': 'Threads', 'icon': '🧵'},
            'instagram': {'name': 'Instagram', 'icon': '📷'},
            'substack': {'name': 'Substack', 'icon': '📰'},
            'telegram': {'name': 'Telegram', 'icon': '✈️'}
        }
        
        # If socials is empty or missing, default all platforms to enabled
        # (matches settings page behavior where platforms default to enabled)
        socials_empty = not socials or len(socials) == 0
        
        for platform_id, platform_info in platform_configs.items():
            platform_settings = socials.get(platform_id, {})
            # Default to enabled if:
            # 1. socials is empty/missing (user hasn't configured yet)
            # 2. platform not in socials
            # 3. enabled is not explicitly set to false
            if socials_empty:
                is_enabled = True
            elif platform_id not in socials:
                is_enabled = True  # Platform not configured yet, default to enabled
            else:
                is_enabled = platform_settings.get('enabled', True)  # Default to True if key missing
            
            if is_enabled:
                # Try to get profile data
                profile_data = {
                    'platform': platform_id,
                    'name': platform_info['name'],
                    'icon': platform_info['icon'],
                    'followers': 0,
                    'profile_pic': None,
                    'description': '',
                    'username': ''
                }
                
                # Fetch real data using web scraper or API
                profile_url = platform_settings.get('profile_url', '')
                
                # Try Instagram API first (if connected via OAuth - fallback for existing setups)
                connected = connected_accounts.get(platform_id, {})
                if platform_id == 'instagram' and connected.get('connected'):
                    try:
                        user_id = connected.get('user_id')
                        access_token = connected.get('access_token') or os.getenv('INSTAGRAM_ACCESS_TOKEN')
                        if user_id and access_token:
                            url = f"https://graph.facebook.com/v18.0/{user_id}"
                            params = {
                                'fields': 'username,biography,profile_picture_url,followers_count',
                                'access_token': access_token
                            }
                            response = requests.get(url, params=params)
                            if response.status_code == 200:
                                instagram_data = response.json()
                                profile_data['followers'] = instagram_data.get('followers_count', 0)
                                profile_data['profile_pic'] = instagram_data.get('profile_picture_url')
                                profile_data['description'] = instagram_data.get('biography', '')
                                profile_data['username'] = instagram_data.get('username', '')
                                print(f"✅ Fetched Instagram profile via API: {profile_data['followers']} followers")
                            else:
                                print(f"⚠️ Instagram API error: {response.status_code} - {response.text}")
                                # Fall through to scraper if API fails
                                profile_url = profile_url or f"https://instagram.com/{connected.get('username', '')}"
                    except Exception as e:
                        print(f"❌ Error fetching Instagram profile via API: {e}")
                        # Fall through to scraper
                        profile_url = profile_url or f"https://instagram.com/{connected.get('username', '')}"
                
                # Use web scraper if profile URL is provided
                if profile_url:
                    try:
                        from social_scraper import get_followers_from_url
                        scraped_data = get_followers_from_url(platform_id, profile_url)
                        if scraped_data and scraped_data.get('followers', 0) > 0:
                            profile_data['followers'] = scraped_data.get('followers', 0)
                            profile_data['profile_pic'] = scraped_data.get('profile_pic')
                            profile_data['description'] = scraped_data.get('description', '')
                            profile_data['username'] = scraped_data.get('username', '')
                            print(f"✅ Scraped {platform_info['name']} profile: {profile_data['followers']} followers")
                        else:
                            print(f"⚠️ Could not scrape {platform_info['name']} from {profile_url}, using dummy data")
                            # Fall through to dummy data
                            profile_data['followers'] = 0
                    except Exception as e:
                        print(f"❌ Error scraping {platform_info['name']}: {e}, using dummy data")
                        # Fall through to dummy data
                        profile_data['followers'] = 0
                
                # Always provide dummy data if no real data was fetched
                if not profile_data['followers'] or profile_data['followers'] == 0:
                    print(f"ℹ️ {platform_info['name']} using dummy data for testing")
                    dummy_followers = {
                        'linkedin': 1250,
                        'x': 3200,
                        'threads': 890,
                        'instagram': 5600,
                        'substack': 450,
                        'telegram': 1200
                    }
                    profile_data['followers'] = dummy_followers.get(platform_id, 0)
                    if not profile_data['username']:
                        profile_data['username'] = f'@{platform_id}_example'
                    if not profile_data['description']:
                        profile_data['description'] = f'Professional {platform_info["name"]} profile'
                
                total_followers += profile_data['followers']
                profiles.append(profile_data)
        
        return jsonify({
            'profiles': profiles,
            'total_followers': total_followers
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/products', methods=['GET'])
def api_get_products():
    """Get products with sales/buyers data"""
    try:
        client_id = request.args.get('client_id')
        if not client_id:
            return jsonify({"error": "client_id required"}), 400
        
        # Try to load clients.json, fallback to dummy data if not found
        try:
            with open('clients.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("⚠️ clients.json not found, using dummy data for products")
            data = {"clients": []}
        
        client = None
        for c in data.get('clients', []):
            if c.get('client_id') == client_id:
                client = c
                break
        
        # If client not found, use dummy client structure
        if not client:
            print(f"⚠️ Client {client_id} not found, using dummy data")
            client = {
                'client_id': client_id,
                'brand': {
                    'main_product': {}
                }
            }
        
        brand = client.get('brand', {})
        main_product = brand.get('main_product', {})
        
        products = []
        if main_product.get('product_id'):
            # Return the main product with dummy sales data for testing
            products.append({
                'product_id': main_product.get('product_id'),
                'name': main_product.get('cta_text', 'Main Product') or 'Main Product',
                'monthly_sales': 12,  # Dummy data for testing
                'monthly_buyers': 8,  # Dummy data for testing
                'revenue': 9600  # Dummy data: 8 buyers × $1,200 average
            })
        else:
            # If no product configured, show dummy data for testing
            products.append({
                'product_id': 'product_dummy_001',
                'name': 'Coaching Program',
                'monthly_sales': 15,
                'monthly_buyers': 12,
                'revenue': 14400
            })
            products.append({
                'product_id': 'product_dummy_002',
                'name': 'Discovery Call',
                'monthly_sales': 8,
                'monthly_buyers': 8,
                'revenue': 0  # Free product
            })
        
        return jsonify({'products': products})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/growth', methods=['GET'])
def api_get_growth_data():
    """Get monthly growth data for earnings and followers"""
    try:
        client_id = request.args.get('client_id')
        if not client_id:
            return jsonify({"error": "client_id required"}), 400
        
        from datetime import datetime, timedelta
        from calendar import month_abbr
        
        # Get current month data - try to load clients.json, fallback to dummy data
        try:
            with open('clients.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            print("⚠️ clients.json not found, using dummy data for growth")
            data = {"clients": []}
        
        client = None
        for c in data.get('clients', []):
            if c.get('client_id') == client_id:
                client = c
                break
        
        # If client not found, use dummy client structure
        if not client:
            print(f"⚠️ Client {client_id} not found, using dummy data")
            client = {
                'client_id': client_id,
                'brand': {
                    'main_product': {},
                    'socials': {}
                },
                'connected_accounts': {}
            }
        
        # Get current earnings (from products)
        brand = client.get('brand', {})
        main_product = brand.get('main_product', {})
        current_earnings = 0
        if main_product.get('product_id'):
            # Use dummy data for now (would come from Stripe API in production)
            current_earnings = 9600  # Dummy: 8 buyers × $1,200
        else:
            # Sum dummy products
            current_earnings = 14400  # Dummy data
        
        # Get current followers (from social profiles)
        socials = brand.get('socials', {})
        connected_accounts = client.get('connected_accounts', {})
        current_followers = 0
        
        # Calculate total followers from connected accounts
        if connected_accounts.get('instagram', {}).get('connected'):
            try:
                user_id = connected_accounts['instagram'].get('user_id')
                access_token = connected_accounts['instagram'].get('access_token') or os.getenv('INSTAGRAM_ACCESS_TOKEN')
                if user_id and access_token:
                    url = f"https://graph.facebook.com/v18.0/{user_id}"
                    params = {
                        'fields': 'followers_count',
                        'access_token': access_token
                    }
                    response = requests.get(url, params=params)
                    if response.status_code == 200:
                        instagram_data = response.json()
                        current_followers += instagram_data.get('followers_count', 0)
            except Exception as e:
                print(f"Error fetching Instagram followers: {e}")
        
        # Generate last 12 months of data
        months = []
        earnings = []
        followers = []
        
        now = datetime.now()
        
        # Use dummy data for testing - clear growth trend
        # Earnings: Start at $5,000, grow to current (or $14,400 if no current)
        # Followers: Start at 5,000, grow to current (or 12,000 if no current)
        base_earnings = current_earnings if current_earnings > 0 else 14400
        base_followers = current_followers if current_followers > 0 else 12000
        
        for i in range(11, -1, -1):  # Last 12 months
            month_date = now - timedelta(days=30 * i)
            month_label = f"{month_abbr[month_date.month]} '{str(month_date.year)[2:]}"
            months.append(month_label)
            
            # For historical data, use metrics_history.json if available
            # Otherwise, generate dummy data with growth trend
            month_key = month_date.strftime('%Y-%m')
            
            # Try to load from metrics_history
            historical_earnings = None
            historical_followers = None
            try:
                if os.path.exists('metrics_history.json'):
                    with open('metrics_history.json', 'r') as f:
                        history = json.load(f)
                    # Look for data matching this month
                    for scope_id, metrics in history.items():
                        if scope_id == client_id or scope_id.startswith(client_id):
                            metric_date_str = metrics.get('date', '')
                            if metric_date_str:
                                try:
                                    metric_date = datetime.fromisoformat(metric_date_str.replace('Z', '+00:00'))
                                    if metric_date.strftime('%Y-%m') == month_key:
                                        historical_earnings = metrics.get('monthly_revenue', 0)
                                        historical_followers = metrics.get('fans_total', 0)
                                        break
                                except:
                                    pass
            except Exception as e:
                print(f"Error loading historical data: {e}")
            
            # Use historical data if available, otherwise generate dummy trend
            if historical_earnings is not None:
                earnings.append(historical_earnings)
            else:
                # Generate trend: start at 60% of base and grow linearly to base
                progress = (12 - i) / 12
                # Add some variation for realism
                variation = (i % 3 - 1) * 0.05  # ±5% variation
                month_earnings = int(base_earnings * (0.6 + 0.4 * progress) * (1 + variation))
                earnings.append(max(1000, month_earnings))  # Minimum $1,000
            
            if historical_followers is not None:
                followers.append(historical_followers)
            else:
                # Generate trend: start at 70% of base and grow linearly to base
                progress = (12 - i) / 12
                # Add some variation for realism
                variation = (i % 2) * 0.03  # ±3% variation
                month_followers = int(base_followers * (0.7 + 0.3 * progress) * (1 + variation))
                followers.append(max(1000, month_followers))  # Minimum 1,000 followers
        
        # Ensure current month matches actual values (or use dummy if no actual)
        earnings[-1] = current_earnings if current_earnings > 0 else base_earnings
        followers[-1] = current_followers if current_followers > 0 else base_followers
        
        return jsonify({
            'months': months,
            'earnings': earnings,
            'followers': followers
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/posts', methods=['GET'])
def api_get_weekly_posts():
    """Get this week's posts with scheduling info"""
    try:
        client_id = request.args.get('client_id')
        if not client_id:
            return jsonify({"error": "client_id required"}), 400
        
        from datetime import datetime, timedelta
        from content.center_post import load_content_posts
        from content.derivative_generator import load_derivatives
        
        # Get current week (Monday to Sunday)
        now = datetime.now()
        day_of_week = now.weekday()  # 0 = Monday, 6 = Sunday
        monday = now - timedelta(days=day_of_week)
        sunday = monday + timedelta(days=6)
        
        # Load posts - fallback to dummy data if files don't exist
        try:
            posts_data = load_content_posts()
            if not posts_data.get('posts'):
                print("⚠️ No posts found, using dummy data")
                posts_data = {"posts": []}
        except Exception as e:
            print(f"⚠️ Error loading posts: {e}, using dummy data")
            posts_data = {"posts": []}
        
        try:
            derivatives_data = load_derivatives()
            if not derivatives_data.get('derivatives'):
                print("⚠️ No derivatives found, using dummy data")
                derivatives_data = {"derivatives": []}
        except Exception as e:
            print(f"⚠️ Error loading derivatives: {e}, using dummy data")
            derivatives_data = {"derivatives": []}
        
        # Load client config for default schedule and special events - fallback to dummy data
        try:
            with open('clients.json', 'r') as f:
                clients_data = json.load(f)
        except FileNotFoundError:
            print("⚠️ clients.json not found, using dummy data for weekly posts")
            clients_data = {"clients": []}
        
        client = None
        for c in clients_data.get('clients', []):
            if c.get('client_id') == client_id:
                client = c
                break
        
        # If client not found, use empty brand structure
        if not client:
            print(f"⚠️ Client {client_id} not found, using default schedule")
            client = {
                'client_id': client_id,
                'brand': {}
            }
        
        # Get default schedule from brand settings
        brand = client.get('brand', {})
        default_schedule = brand.get('default_schedule', {})
        newsletter_default_time = default_schedule.get('newsletter_time', '09:00')
        newsletter_default_day = default_schedule.get('newsletter_day', 'friday')
        
        # Format default schedule string
        day_map = {
            'monday': 'Monday',
            'tuesday': 'Tuesday',
            'wednesday': 'Wednesday',
            'thursday': 'Thursday',
            'friday': 'Friday',
            'saturday': 'Saturday',
            'sunday': 'Sunday',
            'weekly': 'Weekly',
            'biweekly': 'Bi-weekly'
        }
        default_schedule_str = f"{newsletter_default_time} UTC (Every {day_map.get(newsletter_default_day, 'Friday')})"
        
        # Get special events
        special_events = brand.get('special_events', [])
        # Filter events for this week and upcoming
        upcoming_events = []
        for event in special_events:
            event_date_str = event.get('date')
            if event_date_str:
                try:
                    event_date = datetime.fromisoformat(event_date_str)
                    # Show events from this week onwards
                    if event_date >= monday:
                        upcoming_events.append(event)
                except:
                    pass
        
        # Aggregate data for this week
        main_topic = None
        topic_post_id = None
        newsletter_scheduled = None
        has_drafted = False
        has_scheduled = False
        social_counts = {
            'linkedin': 0,
            'x': 0,
            'threads': 0,
            'instagram': 0,
            'substack': 0,
            'telegram': 0
        }
        
        # Find posts from this week and aggregate their derivatives
        for post in posts_data.get('posts', []):
            if post.get('client_id') != client_id:
                continue
            
            try:
                created_at_str = post.get('created_at', '')
                if not created_at_str:
                    continue
                # Handle timezone-aware and naive datetimes
                if 'Z' in created_at_str:
                    created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                elif '+' in created_at_str or created_at_str.count('-') > 2:
                    created_at = datetime.fromisoformat(created_at_str)
                else:
                    created_at = datetime.fromisoformat(created_at_str)
                
                # Make both timezone-naive for comparison
                if created_at.tzinfo:
                    created_at = created_at.replace(tzinfo=None)
                monday_naive = monday.replace(tzinfo=None) if monday.tzinfo else monday
                sunday_naive = sunday.replace(tzinfo=None) if sunday.tzinfo else sunday
                
                # Check if post was created this week
                if monday_naive <= created_at <= sunday_naive + timedelta(days=1):  # Include Sunday
                    # Check if post is drafted (idea, drafted, branched, approved)
                    post_status = post.get('status', 'draft')
                    if post_status in ['idea', 'drafted', 'branched', 'approved']:
                        has_drafted = True
                    
                    # Get main topic (use the most recent post's title)
                    if not main_topic:
                        center_post = post.get('center_post', {})
                        main_topic = center_post.get('title', post.get('raw_idea', 'Untitled')[:50])
                        topic_post_id = post.get('id')
                    
                    # Find derivatives for this post and aggregate
                    post_id = post.get('id')
                    for deriv in derivatives_data.get('derivatives', []):
                        if deriv.get('post_id') != post_id:
                            continue
                        
                        deriv_type = deriv.get('type')
                        status = deriv.get('metadata', {}).get('status', deriv.get('status', 'draft'))
                        
                        # Check if queued (scheduled)
                        if status == 'queued' and deriv.get('scheduled_for'):
                            has_scheduled = True
                            if deriv_type == 'newsletter':
                                # Use the first/earliest newsletter scheduled time
                                if not newsletter_scheduled:
                                    newsletter_scheduled = deriv.get('scheduled_for')
                            else:
                                # Map derivative types to platform IDs
                                platform_map = {
                                    'x': 'x',
                                    'social_x': 'x',
                                    'linkedin': 'linkedin',
                                    'social_linkedin': 'linkedin',
                                    'threads': 'threads',
                                    'social_threads': 'threads',
                                    'instagram': 'instagram',
                                    'social_ig': 'instagram',
                                    'ig': 'instagram',
                                    'substack': 'substack',
                                    'social_substack': 'substack',
                                    'telegram': 'telegram',
                                    'social_telegram': 'telegram'
                                }
                                platform_id = platform_map.get(deriv_type)
                                if platform_id and platform_id in social_counts:
                                    social_counts[platform_id] += 1
            except Exception as e:
                print(f"Error processing post {post.get('id', 'unknown')}: {e}")
                continue
        
        # If no data found, return dummy data for testing
        if not main_topic and not has_drafted and not has_scheduled:
            print("ℹ️ No posts found for this week, returning dummy data")
            return jsonify({
                'topic': 'Building Your Personal Brand',
                'topic_post_id': None,
                'newsletter_scheduled': None,
                'newsletter_default_time': '09:00 UTC',
                'social_counts': {
                    'x': 5,
                    'linkedin': 3,
                    'threads': 2,
                    'instagram': 4,
                    'substack': 1,
                    'telegram': 1
                },
                'has_drafted': False,
                'has_scheduled': False,
                'special_events': [],
                'week_start': monday.isoformat(),
                'week_end': sunday.isoformat()
            })
        
        return jsonify({
            'topic': main_topic,
            'topic_post_id': topic_post_id,
            'newsletter_scheduled': newsletter_scheduled,
            'newsletter_default_time': default_schedule_str,
            'social_counts': social_counts,
            'has_drafted': has_drafted,
            'has_scheduled': has_scheduled,
            'special_events': upcoming_events[:5],  # Limit to 5 upcoming events
            'week_start': monday.isoformat(),
            'week_end': sunday.isoformat()
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/dashboard/analysis', methods=['GET'])
def api_get_dashboard_analysis():
    """Get analysis for a specific dashboard area"""
    try:
        client_id = request.args.get('client_id')
        area = request.args.get('area')
        
        if not client_id or not area:
            return jsonify({"error": "client_id and area required"}), 400
        
        # Load client config - fallback to dummy data if not found
        try:
            with open('clients.json', 'r') as f:
                clients_data = json.load(f)
        except FileNotFoundError:
            print("⚠️ clients.json not found, using dummy data for analysis")
            clients_data = {"clients": []}
        
        client = None
        for c in clients_data.get('clients', []):
            if c.get('client_id') == client_id:
                client = c
                break
        
        # If client not found, use dummy client structure
        if not client:
            print(f"⚠️ Client {client_id} not found, using dummy data")
            client = {
                'client_id': client_id,
                'brand': {},
                'funnel_structure': {}
            }
        
        # Try to get real metrics (from existing endpoints or calculate)
        # For now, use static analysis with fallback logic
        from report_formatter import identify_bottleneck, generate_action_plan
        
        # Calculate basic metrics from client structure
        funnel_structure = client.get('funnel_structure', {})
        awareness_channels = funnel_structure.get('awareness', {}).get('channels', [])
        capture_config = funnel_structure.get('capture', {})
        nurture_config = funnel_structure.get('nurture', {})
        conversion_touchpoints = funnel_structure.get('conversion', {}).get('touchpoints', [])
        
        # Build metrics dict (simplified - in production would fetch from APIs)
        # Calculate total impressions from all awareness channels
        total_impressions = 1234 + 5678 + 890  # Blog + Instagram + LinkedIn (would come from APIs)
        
        metrics = {
            'blog_visitors': 1234,  # Would come from Vercel API
            'new_subscribers': 23,  # Would come from Beehiiv API
            'total_subscribers': 456,  # Would come from Beehiiv API
            'open_rate': 45.2,  # Would come from Beehiiv API
            'click_rate': 8.3,  # Would come from Beehiiv API
            'inquiries': 2,  # Manual entry
            'calls_booked': 1,  # Manual entry
            'close_rate': 50.0,  # Calculated
            'capture_rate': (23 / total_impressions * 100) if total_impressions > 0 else 0,  # Calculated
            'inquiry_rate': (2 / 456 * 100) if 456 > 0 else 0,  # Calculated
            'total_reach': total_impressions,
            'total_impressions': total_impressions
        }
        
        # Identify bottleneck
        bottleneck_name, bottleneck_desc = identify_bottleneck(metrics)
        action_plan = generate_action_plan(bottleneck_name, metrics)
        
        # Generate analysis for the requested area
        analysis = generate_area_analysis(area, metrics, bottleneck_name, action_plan)
        
        return jsonify({"analysis": analysis})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def generate_area_analysis(area, metrics, bottleneck_name, action_plan):
    """Generate analysis for a specific dashboard area"""
    
    area_map = {
        'blog_visitors': {
            'area_name': 'Blog Visitors',
            'current_value': metrics.get('blog_visitors', 0),
            'target_value': 5000,
            'status': 'good' if metrics.get('blog_visitors', 0) >= 3000 else 'warning' if metrics.get('blog_visitors', 0) >= 1000 else 'critical',
            'what_is_good': 'Your blog is getting consistent traffic' if metrics.get('blog_visitors', 0) >= 1000 else None,
            'what_is_bad': 'Traffic is below target of 5,000 weekly visitors' if metrics.get('blog_visitors', 0) < 5000 else None,
            'improvements': [
                'Increase content frequency to 3-4 posts/week',
                'Optimize SEO for high-intent keywords',
                'Promote posts on social media'
            ],
            'suggestions': [
                'Focus on long-form content (2,000+ words)',
                'Add internal linking between posts',
                'Create topic clusters around main themes'
            ]
        },
        'new_subscribers': {
            'area_name': 'New Subscribers',
            'current_value': metrics.get('new_subscribers', 0),
            'target_value': int(metrics.get('blog_visitors', 0) * 0.04),
            'status': 'good' if metrics.get('capture_rate', 0) >= 4 else 'warning' if metrics.get('capture_rate', 0) >= 2 else 'critical',
            'what_is_good': 'You have a growing email list' if metrics.get('new_subscribers', 0) > 0 else None,
            'what_is_bad': f"Capture rate is {metrics.get('capture_rate', 0):.1f}% vs target 4%. You're losing {100 - metrics.get('capture_rate', 0):.1f}% of visitors" if metrics.get('capture_rate', 0) < 4 else None,
            'improvements': (
                [action_plan.get('LEAD CAPTURE', {}).get('priority_1', {}).get('title'), action_plan.get('LEAD CAPTURE', {}).get('priority_2', {}).get('title', 'Add lead magnet to every post')]
                if action_plan.get('LEAD CAPTURE', {}).get('priority_1', {}).get('title')
                else [
                    'Add ebook popup to blog',
                    'Create exit-intent popup',
                    'Add lead magnet to every post'
                ]
            ),
            'suggestions': [
                'Test different lead magnet offers',
                'Simplify signup form (fewer fields)',
                'Add social proof to signup page'
            ]
        },
        'open_rate': {
            'area_name': 'Open Rate',
            'current_value': metrics.get('open_rate', 0),
            'target_value': 40,
            'status': 'good' if metrics.get('open_rate', 0) >= 40 else 'warning' if metrics.get('open_rate', 0) >= 30 else 'critical',
            'what_is_good': 'Your open rate is above target! Content resonates well' if metrics.get('open_rate', 0) >= 40 else None,
            'what_is_bad': f"Open rate is {metrics.get('open_rate', 0):.1f}% vs target 40%" if metrics.get('open_rate', 0) < 40 else None,
            'improvements': (
                [action_plan.get('ENGAGEMENT', {}).get('priority_1', {}).get('title'), action_plan.get('ENGAGEMENT', {}).get('priority_2', {}).get('title', 'Test send times')]
                if action_plan.get('ENGAGEMENT', {}).get('priority_1', {}).get('title')
                else [
                    'Improve email subject lines',
                    'Test send times for better engagement'
                ]
            ),
            'suggestions': [
                'Segment list for more targeted content',
                'A/B test subject lines',
                'Personalize email content'
            ]
        },
        'inquiries_clients': {
            'area_name': 'Inquiries → Clients',
            'current_value': metrics.get('close_rate', 0),
            'target_value': 40,
            'status': 'good' if metrics.get('close_rate', 0) >= 40 else 'warning' if metrics.get('close_rate', 0) >= 30 else 'critical',
            'what_is_good': 'Excellent close rate! You convert well' if metrics.get('close_rate', 0) >= 40 else None,
            'what_is_bad': f"Low inquiry volume (only {metrics.get('inquiries', 0)} per week)" if metrics.get('inquiries', 0) < 5 else f"Close rate is {metrics.get('close_rate', 0):.0f}% vs target 40%" if metrics.get('close_rate', 0) < 40 else None,
            'improvements': (
                [action_plan.get('INQUIRIES', {}).get('priority_1', {}).get('title'), action_plan.get('INQUIRIES', {}).get('priority_2', {}).get('title', 'Create clear call-to-action')]
                if action_plan.get('INQUIRIES', {}).get('priority_1', {}).get('title')
                else [
                    'Add case studies to newsletter',
                    'Include testimonials in every email',
                    'Create clear call-to-action'
                ]
            ),
            'suggestions': [
                'Add inquiry form to website',
                'Make booking process easier',
                'Show social proof on landing pages'
            ]
        },
        'funnel_flow': {
            'area_name': 'Funnel Flow Overview',
            'status': 'warning' if bottleneck_name in ['LEAD CAPTURE', 'INQUIRIES'] else 'good',
            'what_is_good': 'Your funnel is working end-to-end',
            'what_is_bad': f"Bottleneck identified: {bottleneck_name}" if bottleneck_name != 'UNKNOWN' else None,
            'improvements': [
                f"Focus on fixing {bottleneck_name.lower()} first",
                'Optimize each stage sequentially',
                'Track conversion rates between stages'
            ],
            'suggestions': [
                'Set up funnel tracking',
                'A/B test each stage',
                'Monitor drop-off points'
            ]
        },
        'funnel_awareness': {
            'area_name': 'Awareness Stage',
            'status': 'good' if metrics.get('total_impressions', 0) >= 5000 else 'warning',
            'current_value': metrics.get('total_impressions', 0),
            'target_value': 5000,
            'what_is_good': 'Good reach across multiple channels' if metrics.get('total_impressions', 0) >= 3000 else None,
            'what_is_bad': f"Total impressions is {metrics.get('total_impressions', 0):,} vs target 5,000" if metrics.get('total_impressions', 0) < 5000 else None,
            'improvements': (
                [action_plan.get('AWARENESS', {}).get('priority_1', {}).get('title'), action_plan.get('AWARENESS', {}).get('priority_2', {}).get('title', 'Increase content frequency')]
                if action_plan.get('AWARENESS', {}).get('priority_1', {}).get('title')
                else [
                    'Post 3x per week on Instagram',
                    'Guest post on relevant blogs',
                    'Increase content frequency'
                ]
            ),
            'suggestions': [
                'Focus on high-intent keywords',
                'Collaborate with other creators',
                'Repurpose content across platforms'
            ]
        },
        'funnel_capture': {
            'area_name': 'Email Capture Stage',
            'status': 'critical' if metrics.get('capture_rate', 0) < 2 else 'warning' if metrics.get('capture_rate', 0) < 4 else 'good',
            'current_value': metrics.get('new_subscribers', 0),
            'target_value': int(metrics.get('total_impressions', 0) * 0.04),
            'what_is_good': 'Good capture rate' if metrics.get('capture_rate', 0) >= 4 else None,
            'what_is_bad': f"Capture rate is {metrics.get('capture_rate', 0):.1f}% vs target 4%" if metrics.get('capture_rate', 0) < 4 else None,
            'improvements': (
                [action_plan.get('LEAD CAPTURE', {}).get('priority_1', {}).get('title'), action_plan.get('LEAD CAPTURE', {}).get('priority_2', {}).get('title', 'Add exit-intent popup')]
                if action_plan.get('LEAD CAPTURE', {}).get('priority_1', {}).get('title')
                else [
                    'Add ebook popup to blog',
                    'Create exit-intent popup',
                    'Add lead magnet to every post'
                ]
            ),
            'suggestions': [
                'Test different lead magnet offers',
                'Simplify signup form',
                'Add social proof'
            ]
        },
        'funnel_nurture': {
            'area_name': 'Inquiry Stage',
            'status': 'warning' if metrics.get('inquiry_rate', 0) < 1 else 'good',
            'current_value': metrics.get('inquiries', 0),
            'target_value': int(metrics.get('total_subscribers', 0) * 0.015),
            'what_is_good': 'Good inquiry rate' if metrics.get('inquiry_rate', 0) >= 1 else None,
            'what_is_bad': f"Inquiry rate is {metrics.get('inquiry_rate', 0):.1f}% vs target 1%" if metrics.get('inquiry_rate', 0) < 1 else None,
            'improvements': (
                [action_plan.get('INQUIRIES', {}).get('priority_1', {}).get('title'), action_plan.get('INQUIRIES', {}).get('priority_2', {}).get('title', 'Add testimonials')]
                if action_plan.get('INQUIRIES', {}).get('priority_1', {}).get('title')
                else [
                    'Add case studies to newsletter',
                    'Include testimonials in emails',
                    'Create clear call-to-action'
                ]
            ),
            'suggestions': [
                'Add inquiry form to website',
                'Make booking process easier',
                'Show social proof on landing pages'
            ]
        },
        'funnel_conversion': {
            'area_name': 'Conversion Stage',
            'status': 'good' if metrics.get('close_rate', 0) >= 40 else 'warning',
            'current_value': metrics.get('calls_booked', 0),
            'target_value': metrics.get('inquiries', 0),
            'what_is_good': 'Excellent close rate' if metrics.get('close_rate', 0) >= 40 else None,
            'what_is_bad': f"Close rate is {metrics.get('close_rate', 0):.0f}% vs target 40%" if metrics.get('close_rate', 0) < 40 else None,
            'improvements': (
                [action_plan.get('CLOSE RATE', {}).get('priority_1', {}).get('title'), action_plan.get('CLOSE RATE', {}).get('priority_2', {}).get('title', 'Create call checklist')]
                if action_plan.get('CLOSE RATE', {}).get('priority_1', {}).get('title')
                else [
                    'Record and analyze sales calls',
                    'Create call preparation checklist',
                    'Follow up with warm leads'
                ]
            ),
            'suggestions': [
                'Improve discovery call process',
                'Address common objections',
                'Follow up within 24 hours'
            ]
        },
        'stage_awareness': {
            'area_name': 'Awareness Stage',
            'status': 'good' if metrics.get('total_reach', 0) >= 5000 else 'warning',
            'what_is_good': 'Good reach across multiple channels' if metrics.get('total_reach', 0) >= 3000 else None,
            'what_is_bad': f"Total reach is {metrics.get('total_reach', 0):,} vs target 5,000" if metrics.get('total_reach', 0) < 5000 else None,
            'improvements': (
                [action_plan.get('AWARENESS', {}).get('priority_1', {}).get('title'), action_plan.get('AWARENESS', {}).get('priority_2', {}).get('title', 'Increase content frequency')]
                if action_plan.get('AWARENESS', {}).get('priority_1', {}).get('title')
                else [
                    'Post 3x per week on Instagram',
                    'Guest post on relevant blogs',
                    'Increase content frequency'
                ]
            ),
            'suggestions': [
                'Focus on high-intent keywords',
                'Collaborate with other creators',
                'Repurpose content across platforms'
            ]
        },
        'stage_capture': {
            'area_name': 'Lead Capture Stage',
            'status': 'critical' if metrics.get('capture_rate', 0) < 2 else 'warning' if metrics.get('capture_rate', 0) < 4 else 'good',
            'what_is_good': 'Good capture rate' if metrics.get('capture_rate', 0) >= 4 else None,
            'what_is_bad': f"Capture rate is {metrics.get('capture_rate', 0):.1f}% vs target 4%" if metrics.get('capture_rate', 0) < 4 else None,
            'improvements': action_plan.get('LEAD CAPTURE', {}).get('priority_1', {}).get('title') and [
                action_plan['LEAD CAPTURE']['priority_1']['title'],
                action_plan['LEAD CAPTURE'].get('priority_2', {}).get('title', 'Add exit-intent popup')
            ] or [
                'Add ebook popup to blog',
                'Create exit-intent popup',
                'Add lead magnet to every post'
            ],
            'suggestions': [
                'Test different lead magnet offers',
                'Simplify signup form',
                'Add social proof'
            ]
        },
        'stage_nurture': {
            'area_name': 'Nurture Stage',
            'status': 'good' if metrics.get('open_rate', 0) >= 40 else 'warning',
            'what_is_good': 'Strong email engagement' if metrics.get('open_rate', 0) >= 40 else None,
            'what_is_bad': f"Open rate is {metrics.get('open_rate', 0):.1f}% vs target 40%" if metrics.get('open_rate', 0) < 40 else None,
            'improvements': action_plan.get('ENGAGEMENT', {}).get('priority_1', {}).get('title') and [
                action_plan['ENGAGEMENT']['priority_1']['title'],
                action_plan['ENGAGEMENT'].get('priority_2', {}).get('title', 'Add clear CTAs')
            ] or [
                'Improve email subject lines',
                'Add clear CTAs in emails',
                'Test send times'
            ],
            'suggestions': [
                'Segment list for targeted content',
                'A/B test subject lines',
                'Personalize email content'
            ]
        },
        'stage_conversion': {
            'area_name': 'Conversion Stage',
            'status': 'good' if metrics.get('close_rate', 0) >= 40 else 'warning',
            'what_is_good': 'Excellent close rate' if metrics.get('close_rate', 0) >= 40 else None,
            'what_is_bad': f"Close rate is {metrics.get('close_rate', 0):.0f}% vs target 40%" if metrics.get('close_rate', 0) < 40 else f"Low inquiry volume ({metrics.get('inquiries', 0)} per week)" if metrics.get('inquiries', 0) < 5 else None,
            'improvements': action_plan.get('INQUIRIES', {}).get('priority_1', {}).get('title') and [
                action_plan['INQUIRIES']['priority_1']['title'],
                action_plan['INQUIRIES'].get('priority_2', {}).get('title', 'Add testimonials')
            ] or [
                'Add case studies to newsletter',
                'Include testimonials in emails',
                'Create clear call-to-action'
            ],
            'suggestions': [
                'Record and analyze sales calls',
                'Create call preparation checklist',
                'Follow up with warm leads'
            ]
        }
    }
    
    return area_map.get(area, {
        'area_name': area.replace('_', ' ').title(),
        'status': 'good',
        'what_is_good': 'This area is performing well',
        'improvements': ['Continue monitoring performance']
    })

@app.route('/api/clients/<client_id>/connect/<platform>', methods=['POST'])
def api_connect_platform(client_id, platform):
    """Handle OAuth callback and save connection details"""
    try:
        data = request.json or {}
        access_token = data.get('access_token')
        user_id = data.get('user_id')
        username = data.get('username')
        
        with open('clients.json', 'r') as f:
            clients_data = json.load(f)
        
        client_index = None
        for i, c in enumerate(clients_data.get('clients', [])):
            if c.get('client_id') == client_id:
                client_index = i
                break
        
        if client_index is None:
            return jsonify({"error": "Client not found"}), 404
        
        # Initialize connected_accounts if it doesn't exist
        if 'connected_accounts' not in clients_data['clients'][client_index]:
            clients_data['clients'][client_index]['connected_accounts'] = {}
        
        # Update connection for this platform
        clients_data['clients'][client_index]['connected_accounts'][platform] = {
            'connected': True,
            'user_id': user_id,
            'access_token': access_token or 'env_var',
            'username': username,
            'status': 'active',
            'connected_at': datetime.now().isoformat()
        }
        
        with open('clients.json', 'w') as f:
            json.dump(clients_data, f, indent=2)
        
        return jsonify({"message": f"{platform} connected successfully"})
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

