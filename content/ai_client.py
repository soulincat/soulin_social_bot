"""
Claude API client for content generation
"""
import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

class ClaudeClient:
    """Wrapper for Anthropic Claude API"""
    
    def __init__(self):
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment")
        
        # Trim whitespace from API key
        api_key = api_key.strip()
        
        # Validate key format
        if api_key.startswith('sk-or-'):
            raise ValueError(
                "❌ Wrong API key type! You're using an OpenAI key (starts with 'sk-or-').\n"
                "This system requires an Anthropic (Claude) API key.\n\n"
                "To fix:\n"
                "1. Go to https://console.anthropic.com/\n"
                "2. Sign in or create an account\n"
                "3. Navigate to 'API Keys' section\n"
                "4. Create a new API key (it will start with 'sk-ant-api03-')\n"
                "5. Update your .env file: ANTHROPIC_API_KEY=sk-ant-api03-your-key-here\n"
                "6. Restart the Flask server"
            )
        elif not api_key.startswith('sk-ant-'):
            raise ValueError(
                f"❌ ANTHROPIC_API_KEY format appears invalid.\n"
                f"Anthropic keys should start with 'sk-ant-'.\n"
                f"Your key starts with: '{api_key[:15]}...'\n\n"
                "Please check your .env file and ensure you're using an Anthropic API key from:\n"
                "https://console.anthropic.com/"
            )
        
        self.client = Anthropic(api_key=api_key)
        # Allow model to be configured via environment variable, default to Claude Sonnet 4
        self.model = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
    
    def expand_idea(self, raw_idea, client_config):
        """
        Expand raw idea into full center post (800-1200 words)
        Returns: {content, checks: {mission, persona, tone, goal, identity, novelty}}
        """
        business = client_config.get('business', {})
        funnel = client_config.get('funnel_structure', {})
        brand = client_config.get('brand', {})
        
        # Build brand context section
        brand_context = ""
        if brand:
            brand_context = "\n\nBRAND GUIDELINES:\n"
            
            if brand.get('mission'):
                brand_context += f"Mission: {brand['mission']}\n"
            
            if brand.get('positioning'):
                brand_context += f"Positioning: {brand['positioning']}\n"
            
            voice = brand.get('voice', {})
            if voice.get('tone'):
                brand_context += f"Tone: {voice['tone']}\n"
            if voice.get('style'):
                brand_context += f"Writing Style: {voice['style']}\n"
            if voice.get('personality'):
                brand_context += f"Personality Traits: {', '.join(voice['personality'])}\n"
            
            if brand.get('values'):
                brand_context += f"Core Values: {', '.join(brand['values'])}\n"
            
            if brand.get('content_goals'):
                brand_context += f"Content Goals: {', '.join(brand['content_goals'])}\n"
            
            if brand.get('do_not_use'):
                brand_context += f"Avoid: {', '.join(brand['do_not_use'])}\n"
            
            examples = brand.get('examples', {})
            if examples.get('good_content'):
                brand_context += f"\nGood Content Example:\n{examples['good_content']}\n"
            if examples.get('bad_content'):
                brand_context += f"\nBad Content Example (avoid this style):\n{examples['bad_content']}\n"
        
        prompt = f"""Raw idea: {raw_idea}

Expand this into a full center post (800-1200 words).

Business context:
- Type: {business.get('type', 'business')}
- Target audience: {business.get('target_audience', 'general')}
{brand_context}
IMPORTANT: The content must align with the brand guidelines above. Use the specified tone, style, and personality. Follow the content goals and avoid the listed elements.

Check alignment with:
- Mission: Does this align with the business mission?
- Persona: Does this resonate with the target audience?
- Tone: Is the tone appropriate for the brand?
- Goal: Does this serve the content goal?
- Identity: Does this reflect brand identity?
- Novelty: Does this bring fresh perspective?

Return JSON format:
{{
  "content": "full expanded content here...",
  "title": "compelling title",
  "checks": {{
    "mission": true/false,
    "persona": true/false,
    "tone": true/false,
    "goal": true/false,
    "identity": true/false,
    "novelty": true/false
  }},
  "word_count": 1200
}}"""
        
        try:
            print(f"[ClaudeClient] Calling Claude API with model: {self.model}")
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            print(f"[ClaudeClient] API response received, length: {len(message.content[0].text) if message.content else 0}")
            
            # Extract JSON from response
            response_text = message.content[0].text
            print(f"[ClaudeClient] Response text preview: {response_text[:200]}...")
            
            # Try to parse JSON (might be wrapped in markdown code blocks)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            print(f"[ClaudeClient] Successfully parsed JSON. Title: {result.get('title', 'N/A')[:50]}...")
            return result
        except json.JSONDecodeError as e:
            raise Exception(f"Error parsing Claude response as JSON: {str(e)}")
        except Exception as e:
            error_str = str(e)
            # Check for authentication errors
            if "401" in error_str or "authentication" in error_str.lower() or "invalid x-api-key" in error_str.lower():
                raise Exception(
                    "Authentication failed with Claude API. Please check your ANTHROPIC_API_KEY:\n"
                    "1. Go to https://console.anthropic.com/\n"
                    "2. Create or copy your API key (should start with 'sk-ant-')\n"
                    "3. Add it to your .env file: ANTHROPIC_API_KEY=your_key_here\n"
                    "4. Restart the Flask server\n"
                    f"Error details: {error_str}"
                )
            elif "429" in error_str or "rate limit" in error_str.lower():
                raise Exception(f"Rate limit exceeded. Please try again later. Error: {error_str}")
            else:
                raise Exception(f"Error expanding idea with Claude: {error_str}")
    
    def generate_archive_version(self, center_post_content):
        """
        Rewrite in first-person narrative, unfiltered personal voice
        This will become a chapter in a book. Raw, authentic, no marketing polish.
        """
        prompt = f"""Rewrite this content in first-person narrative, unfiltered personal voice.

Original content:
{center_post_content}

This will become a chapter in my book. Make it:
- Raw and authentic
- Personal and vulnerable
- No marketing polish
- Narrative style, like storytelling
- First-person perspective

Return the rewritten content directly (no JSON wrapper)."""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text.strip()
        except Exception as e:
            raise Exception(f"Error generating archive version: {str(e)}")
    
    def generate_blog_version(self, center_post_content):
        """
        Rewrite as definitive guide optimized for AI citation
        - Clear structure with H2/H3 headers
        - Definitive statements
        - Data/examples where relevant
        - Comprehensive but scannable
        """
        prompt = f"""Rewrite this content as a definitive guide optimized for AI citation and search.

Original content:
{center_post_content}

Requirements:
- Clear structure with H2/H3 headers (use ## and ###)
- Definitive statements ("X is Y" not "X might be Y")
- Data/examples where relevant
- Comprehensive but scannable
- SEO-friendly
- Include schema.org Article structured data suggestions

Return JSON format:
{{
  "content": "rewritten content with markdown headers...",
  "structured_data": {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "...",
    "author": {{"@type": "Person", "name": "..."}},
    "datePublished": "...",
    "description": "..."
  }}
}}"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            return result
        except Exception as e:
            raise Exception(f"Error generating blog version: {str(e)}")
    
    def generate_social_posts(self, center_post_content, platforms=['x', 'linkedin', 'instagram']):
        """
        Generate 3-5 social post variations
        Returns: List of posts per platform
        """
        prompt = f"""Generate social media posts from this content:

{center_post_content}

Generate posts for these platforms: {', '.join(platforms)}

Requirements:
- Hook-first, value-dense
- CTA at end
- Platform-appropriate format
- For X: 280 chars max, can be threads
- For LinkedIn: 1200 chars max
- For Instagram: Carousel concept (8 slides with descriptions)

Return JSON format:
{{
  "x": [
    {{"content": "post 1...", "type": "single_post"}},
    {{"content": "post 2...", "type": "thread", "thread_parts": ["part 1", "part 2"]}}
  ],
  "linkedin": [
    {{"content": "LinkedIn post...", "type": "single_post"}}
  ],
  "instagram": [
    {{"content": "IG carousel concept...", "type": "carousel", "slides": ["slide 1", "slide 2", ...]}}
  ]
}}"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            return result
        except Exception as e:
            raise Exception(f"Error generating social posts: {str(e)}")
    
    def generate_newsletter_version(self, center_post_content):
        """
        Convert to email format with wrapper
        """
        prompt = f"""Convert this content into a newsletter email format:

{center_post_content}

Requirements:
- Email-friendly format
- Engaging subject line
- Clear intro hook
- Scannable sections
- Strong CTA at end
- Newsletter wrapper (greeting, sign-off)

Return JSON format:
{{
  "subject": "Email subject line",
  "content": "Full email content with greeting and sign-off..."
}}"""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            response_text = message.content[0].text
            # Extract JSON
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            elif "```" in response_text:
                json_start = response_text.find("```") + 3
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end].strip()
            
            result = json.loads(response_text)
            return result
        except Exception as e:
            raise Exception(f"Error generating newsletter version: {str(e)}")
    
    def generate_telegram_announcement(self, center_post_content):
        """
        Create Telegram announcement (200 chars max)
        """
        prompt = f"""Create a short Telegram announcement from this content:

{center_post_content}

Requirements:
- 200 characters maximum
- Hook-first
- Include link placeholder: [Read more]
- Engaging and concise

Return just the announcement text (no JSON)."""
        
        try:
            message = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            
            return message.content[0].text.strip()
        except Exception as e:
            raise Exception(f"Error generating Telegram announcement: {str(e)}")

