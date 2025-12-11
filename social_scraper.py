"""
Web scraper for social media follower counts
Scrapes public profile pages to get follower counts without OAuth
"""
import requests
import re
import json
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import time


def get_followers_from_url(platform, url):
    """
    Get follower count from a social media profile URL
    
    Args:
        platform: 'linkedin', 'x', 'threads', 'instagram', 'substack', 'telegram'
        url: Full profile URL
    
    Returns:
        dict with 'followers', 'username', 'description', 'profile_pic' or None on error
    """
    if not url:
        return None
    
    try:
        # Normalize URL
        url = url.strip()
        if not url.startswith('http'):
            url = 'https://' + url
        
        # Set headers to mimic a browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse based on platform
        if platform == 'linkedin':
            return _scrape_linkedin(response.text, url)
        elif platform == 'x':
            return _scrape_x(response.text, url)
        elif platform == 'threads':
            return _scrape_threads(response.text, url)
        elif platform == 'instagram':
            return _scrape_instagram(response.text, url)
        elif platform == 'substack':
            return _scrape_substack(response.text, url)
        elif platform == 'telegram':
            return _scrape_telegram(response.text, url)
        else:
            return None
            
    except Exception as e:
        print(f"❌ Error scraping {platform} from {url}: {e}")
        return None


def _scrape_linkedin(html, url):
    """Scrape LinkedIn profile"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract username from URL
        username = url.split('/in/')[-1].split('/')[0] if '/in/' in url else None
        
        # LinkedIn stores follower count in various places
        # Try to find it in meta tags or JSON-LD
        followers = None
        
        # Method 1: Look for JSON-LD structured data
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict) and 'mainEntity' in data:
                    # LinkedIn structured data
                    pass
            except:
                pass
        
        # Method 2: Look for follower count in text
        # LinkedIn shows "XXX followers" or "XXX connections"
        follower_patterns = [
            r'(\d+(?:,\d+)*)\s+followers',
            r'(\d+(?:,\d+)*)\s+connections',
        ]
        
        page_text = soup.get_text()
        for pattern in follower_patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                followers_str = match.group(1).replace(',', '')
                try:
                    followers = int(followers_str)
                    break
                except:
                    pass
        
        # Method 3: Look in meta tags
        if not followers:
            meta_followers = soup.find('meta', {'property': 'og:description'})
            if meta_followers:
                desc = meta_followers.get('content', '')
                match = re.search(r'(\d+(?:,\d+)*)\s+followers', desc, re.IGNORECASE)
                if match:
                    followers = int(match.group(1).replace(',', ''))
        
        # Get profile picture
        profile_pic = None
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image:
            profile_pic = og_image.get('content')
        
        # Get description
        description = None
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc:
            description = og_desc.get('content', '')[:200]  # Limit length
        
        return {
            'followers': followers or 0,
            'username': username,
            'description': description,
            'profile_pic': profile_pic
        }
    except Exception as e:
        print(f"Error parsing LinkedIn: {e}")
        return None


def _scrape_x(html, url):
    """Scrape X (Twitter) profile"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract username from URL
        username = url.split('x.com/')[-1].split('/')[0] if 'x.com/' in url else url.split('twitter.com/')[-1].split('/')[0] if 'twitter.com/' in url else None
        
        # X/Twitter stores data in JSON in script tags
        followers = None
        
        # Look for data in script tags (X uses React, data is in JSON)
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and 'followers_count' in script.string:
                # Try to extract from JSON
                try:
                    # X embeds data in various formats
                    match = re.search(r'"followers_count":\s*(\d+)', script.string)
                    if match:
                        followers = int(match.group(1))
                        break
                except:
                    pass
        
        # Alternative: Look for follower count in text
        if not followers:
            page_text = soup.get_text()
            # Look for patterns like "1.2K Followers" or "1,234 Followers"
            patterns = [
                r'([\d.]+[KMB]?)\s+[Ff]ollowers',
                r'(\d+(?:,\d+)*)\s+[Ff]ollowers',
            ]
            for pattern in patterns:
                match = re.search(pattern, page_text)
                if match:
                    count_str = match.group(1)
                    followers = _parse_count(count_str)
                    if followers:
                        break
        
        # Get profile picture
        profile_pic = None
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image:
            profile_pic = og_image.get('content')
        
        # Get description
        description = None
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc:
            description = og_desc.get('content', '')[:200]
        
        return {
            'followers': followers or 0,
            'username': username,
            'description': description,
            'profile_pic': profile_pic
        }
    except Exception as e:
        print(f"Error parsing X: {e}")
        return None


def _scrape_threads(html, url):
    """Scrape Threads profile"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract username from URL
        username = url.split('threads.net/@')[-1].split('/')[0] if 'threads.net/@' in url else None
        
        # Threads is similar to Instagram (Meta)
        followers = None
        
        # Look for JSON data in script tags
        scripts = soup.find_all('script')
        for script in scripts:
            if script.string and ('follower_count' in script.string or 'followers' in script.string):
                try:
                    match = re.search(r'"follower_count":\s*(\d+)', script.string)
                    if not match:
                        match = re.search(r'"followers":\s*(\d+)', script.string)
                    if match:
                        followers = int(match.group(1))
                        break
                except:
                    pass
        
        # Get profile picture
        profile_pic = None
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image:
            profile_pic = og_image.get('content')
        
        # Get description
        description = None
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc:
            description = og_desc.get('content', '')[:200]
        
        return {
            'followers': followers or 0,
            'username': username,
            'description': description,
            'profile_pic': profile_pic
        }
    except Exception as e:
        print(f"Error parsing Threads: {e}")
        return None


def _scrape_instagram(html, url):
    """Scrape Instagram profile (fallback if API fails)"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract username from URL
        username = url.split('instagram.com/')[-1].split('/')[0] if 'instagram.com/' in url else None
        
        # Instagram stores data in JSON in script tags
        followers = None
        
        scripts = soup.find_all('script', type='text/javascript')
        for script in scripts:
            if script.string and 'edge_followed_by' in script.string:
                try:
                    # Instagram embeds data in window._sharedData
                    match = re.search(r'"edge_followed_by":\s*{\s*"count":\s*(\d+)', script.string)
                    if match:
                        followers = int(match.group(1))
                        break
                except:
                    pass
        
        # Alternative: Look in meta tags
        if not followers:
            meta_followers = soup.find('meta', {'property': 'og:description'})
            if meta_followers:
                desc = meta_followers.get('content', '')
                # Pattern: "123K Followers, 456 Following, 789 Posts"
                match = re.search(r'([\d.]+[KMB]?)\s+Followers', desc, re.IGNORECASE)
                if match:
                    followers = _parse_count(match.group(1))
        
        # Get profile picture
        profile_pic = None
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image:
            profile_pic = og_image.get('content')
        
        # Get description
        description = None
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc:
            description = og_desc.get('content', '')[:200]
        
        return {
            'followers': followers or 0,
            'username': username,
            'description': description,
            'profile_pic': profile_pic
        }
    except Exception as e:
        print(f"Error parsing Instagram: {e}")
        return None


def _scrape_substack(html, url):
    """Scrape Substack profile/publication"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract username/publication name from URL
        parsed = urlparse(url)
        username = parsed.netloc.replace('.substack.com', '') if '.substack.com' in parsed.netloc else None
        
        # Substack shows subscriber count
        followers = None
        
        # Look for subscriber count in various places
        page_text = soup.get_text()
        
        # Pattern: "1,234 subscribers" or "1.2K subscribers"
        patterns = [
            r'([\d.]+[KMB]?)\s+subscribers',
            r'(\d+(?:,\d+)*)\s+subscribers',
        ]
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                followers = _parse_count(match.group(1))
                if followers:
                    break
        
        # Get profile picture (publication logo)
        profile_pic = None
        og_image = soup.find('meta', {'property': 'og:image'})
        if og_image:
            profile_pic = og_image.get('content')
        
        # Get description
        description = None
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc:
            description = og_desc.get('content', '')[:200]
        
        return {
            'followers': followers or 0,
            'username': username,
            'description': description,
            'profile_pic': profile_pic
        }
    except Exception as e:
        print(f"Error parsing Substack: {e}")
        return None


def _scrape_telegram(html, url):
    """Scrape Telegram channel/group"""
    try:
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract username from URL
        username = url.split('t.me/')[-1].split('/')[0] if 't.me/' in url else None
        
        # Telegram web shows member count
        followers = None
        
        page_text = soup.get_text()
        
        # Pattern: "1,234 members" or "1.2K members" or "1,234 subscribers"
        patterns = [
            r'([\d.]+[KMB]?)\s+members',
            r'(\d+(?:,\d+)*)\s+members',
            r'([\d.]+[KMB]?)\s+subscribers',
            r'(\d+(?:,\d+)*)\s+subscribers',
        ]
        for pattern in patterns:
            match = re.search(pattern, page_text, re.IGNORECASE)
            if match:
                followers = _parse_count(match.group(1))
                if followers:
                    break
        
        # Get description
        description = None
        og_desc = soup.find('meta', {'property': 'og:description'})
        if og_desc:
            description = og_desc.get('content', '')[:200]
        
        # Telegram doesn't have profile pics in the same way
        profile_pic = None
        
        return {
            'followers': followers or 0,
            'username': username,
            'description': description,
            'profile_pic': profile_pic
        }
    except Exception as e:
        print(f"Error parsing Telegram: {e}")
        return None


def _parse_count(count_str):
    """Parse count string like '1.2K', '1M', '1,234' into integer"""
    if not count_str:
        return None
    
    count_str = count_str.strip().replace(',', '')
    
    try:
        if count_str.upper().endswith('K'):
            return int(float(count_str[:-1]) * 1000)
        elif count_str.upper().endswith('M'):
            return int(float(count_str[:-1]) * 1000000)
        elif count_str.upper().endswith('B'):
            return int(float(count_str[:-1]) * 1000000000)
        else:
            return int(float(count_str))
    except:
        return None

