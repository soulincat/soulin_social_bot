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
        # Allow model to be configured via environment variable
        # Default to claude-sonnet-4-20250514 (current recommended model)
        # Other valid models: claude-opus-4-20250514, claude-3-7-sonnet-20250219, claude-3-5-haiku-20241022
        self.model = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-20250514')
    
    def expand_idea(self, raw_idea, client_config, cta_info=None):
        """
        Expand raw idea into full center post (800-1200 words)
        Returns: {content, checks: {mission, persona, tone, goal, identity, novelty}}
        
        Args:
            raw_idea: The raw idea text
            client_config: Client configuration dict
            cta_info: Optional dict with 'text' and 'url' for CTA to include
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
{f"CTA: End the content with this call-to-action: {cta_info['text']} ({cta_info['url']})" if cta_info and cta_info.get('text') and cta_info.get('url') else ""}

Check alignment with:
- Mission: Does this align with the business mission?
- Persona: Does this resonate with the target audience?
- Tone: Is the tone appropriate for the brand?
- Goal: Does this serve the content goal?
- Identity: Does this reflect brand identity?
- Novelty: Does this bring fresh perspective?

CRITICAL: You MUST return ONLY valid JSON. Do not include any markdown, explanations, or text outside the JSON object.

Return JSON format (no markdown, no code blocks, just the raw JSON):
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
}}

Remember: Return ONLY the JSON object, nothing else."""
        
        try:
            print(f"[ClaudeClient] Calling Claude API with model: {self.model}")
            print(f"[ClaudeClient] Prompt length: {len(prompt)} characters")
            
            try:
                message = self.client.messages.create(
                    model=self.model,
                    max_tokens=4000,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
            except Exception as api_err:
                error_str = str(api_err)
                if "model" in error_str.lower() and ("not found" in error_str.lower() or "404" in error_str):
                    raise Exception(
                        f"Model '{self.model}' not found or not available.\n"
                        f"Valid models include: claude-sonnet-4-20250514, claude-opus-4-20250514, claude-3-7-sonnet-20250219, claude-3-5-haiku-20241022\n"
                        f"Set ANTHROPIC_MODEL in your .env file to use a different model.\n"
                        f"Error: {error_str}"
                    )
                raise
            
            # Check for stop reason
            if hasattr(message, 'stop_reason') and message.stop_reason:
                print(f"[ClaudeClient] Stop reason: {message.stop_reason}")
                if message.stop_reason == 'max_tokens':
                    print("[ClaudeClient] ⚠️ Response was truncated due to max_tokens limit")
                elif message.stop_reason == 'content_filter':
                    print("[ClaudeClient] ⚠️ Response was filtered by content policy")
                    raise Exception("Claude API filtered the response due to content policy. Please adjust your prompt.")
            # Check if response has content
            if not message.content or len(message.content) == 0:
                raise Exception("Claude API returned empty response. This might indicate an API issue. Please check your ANTHROPIC_API_KEY and try again.")
            
            # Get response text - handle different response formats
            if hasattr(message.content[0], 'text'):
                response_text = message.content[0].text
            elif isinstance(message.content[0], dict) and 'text' in message.content[0]:
                response_text = message.content[0]['text']
            elif isinstance(message.content[0], str):
                response_text = message.content[0]
            else:
                raise Exception(f"Unexpected response format from Claude API. Content type: {type(message.content[0])}")
            
            print(f"[ClaudeClient] API response received, length: {len(response_text) if response_text else 0}")
            if response_text:
                print(f"[ClaudeClient] Response text preview: {response_text[:500]}...")
            else:
                print(f"[ClaudeClient] ⚠️ Response text is None or empty")
            
            if not response_text or len(response_text.strip()) == 0:
                raise Exception(
                    "Claude API returned empty response text.\n"
                    "This could mean:\n"
                    "1. The API call was interrupted\n"
                    "2. The model hit a safety filter\n"
                    "3. There's an issue with the API key\n"
                    "Please check the server logs and try again."
                )
            
            # Try to extract JSON from response (might be wrapped in markdown code blocks)
            original_text = response_text
            json_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if "```json" in json_text:
                json_start = json_text.find("```json") + 7
                json_end = json_text.find("```", json_start)
                if json_end == -1:
                    json_end = len(json_text)
                json_text = json_text[json_start:json_end].strip()
            elif "```" in json_text:
                json_start = json_text.find("```") + 3
                json_end = json_text.find("```", json_start)
                if json_end == -1:
                    json_end = len(json_text)
                json_text = json_text[json_start:json_end].strip()
            
            # Try to find JSON object in the text (look for { ... })
            if not json_text.startswith('{'):
                # Try to find the first { and last }
                first_brace = json_text.find('{')
                last_brace = json_text.rfind('}')
                if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
                    json_text = json_text[first_brace:last_brace + 1]
            
            # Validate we have something to parse
            if not json_text or len(json_text.strip()) == 0:
                # Log the full response for debugging
                print(f"[ClaudeClient] ❌ Empty JSON text after extraction")
                print(f"[ClaudeClient] Original response (first 1000 chars): {original_text[:1000]}")
                print(f"[ClaudeClient] Original response length: {len(original_text)}")
                raise Exception(
                    f"Could not extract JSON from Claude response.\n"
                    f"Response was empty or contained no JSON.\n"
                    f"Response preview (first 500 chars): {original_text[:500]}\n"
                    f"Full response length: {len(original_text)} characters\n"
                    f"This might mean:\n"
                    f"1. Claude returned an error message instead of JSON\n"
                    f"2. The response was filtered or blocked\n"
                    f"3. The API call was interrupted\n"
                    f"Please check server logs for full response details."
                )
            
            try:
                result = json.loads(json_text)
                print(f"[ClaudeClient] Successfully parsed JSON. Title: {result.get('title', 'N/A')[:50]}...")
                return result
            except json.JSONDecodeError as json_err:
                # Try to extract JSON more aggressively
                import re
                # Look for JSON object pattern (more robust regex)
                json_match = re.search(r'\{.*\}', json_text, re.DOTALL)
                if json_match:
                    try:
                        extracted_json = json_match.group(0)
                        result = json.loads(extracted_json)
                        print(f"[ClaudeClient] Successfully parsed JSON using regex extraction. Title: {result.get('title', 'N/A')[:50]}...")
                        return result
                    except Exception as regex_err:
                        print(f"[ClaudeClient] Regex extraction also failed: {regex_err}")
                
                # Save the actual response for debugging
                error_details = f"Error parsing Claude response as JSON: {str(json_err)}\n\n"
                error_details += f"Response received (first 1000 chars):\n{original_text[:1000]}\n\n"
                error_details += f"JSON extraction attempted (first 500 chars):\n{json_text[:500]}\n\n"
                error_details += f"This usually means:\n"
                error_details += f"1. Claude returned text instead of JSON\n"
                error_details += f"2. The response was truncated or incomplete\n"
                error_details += f"3. The prompt needs adjustment\n\n"
                error_details += f"Full response length: {len(original_text)} characters"
                
                print(f"[ClaudeClient] ❌ JSON Parse Error:")
                print(f"   Error: {str(json_err)}")
                print(f"   Response length: {len(original_text)}")
                print(f"   Response preview: {original_text[:500]}")
                print(f"   JSON text attempted: {json_text[:500]}")
                
                raise Exception(error_details)
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
    
    def generate_social_posts(self, center_post_content, platforms=['linkedin', 'x', 'threads', 'instagram', 'substack'], brand_socials=None, cta_info=None):
        """
        Generate social media posts for multiple platforms
        Returns: Dict with posts per platform
        
        Args:
            center_post_content: The source content to generate from
            platforms: List of platforms to generate for
            brand_socials: Optional dict of platform-specific brand settings from brand.socials
            cta_info: Optional dict with 'text' and 'url' for CTA to include
        """
        # Default platform requirements
        default_requirements = {
            'linkedin': 'Professional, 1200 chars max, can include line breaks for readability',
            'x': '280 chars max, can be threads (multiple posts), concise and punchy',
            'threads': 'Similar to X but slightly more casual, 500 chars per post, can be threads',
            'instagram': 'Carousel concept with 6-8 slides, each slide description, engaging captions',
            'substack': 'Newsletter-style feed post, 300-500 words, engaging hook'
        }
        
        # Build platform-specific requirements using brand settings
        platform_requirements = []
        for p in platforms:
            platform_settings = brand_socials.get(p, {}) if brand_socials else {}
            enabled = platform_settings.get('enabled', True)
            
            if not enabled:
                continue  # Skip disabled platforms
            
            req_parts = []
            
            # Use custom voice if specified
            if platform_settings.get('voice'):
                req_parts.append(f"Voice: {platform_settings['voice']}")
            
            # Use custom tone if specified
            if platform_settings.get('tone'):
                req_parts.append(f"Tone: {platform_settings['tone']}")
            
            # Use length limits if specified
            min_len = platform_settings.get('minLength')
            max_len = platform_settings.get('maxLength')
            if min_len or max_len:
                length_desc = f"{min_len or 'no min'}-{max_len or 'no max'} chars"
                req_parts.append(length_desc)
            else:
                req_parts.append(default_requirements.get(p, 'Platform-appropriate format'))
            
            # Add format preferences
            if platform_settings.get('format'):
                req_parts.append(f"Format: {platform_settings['format']}")
            
            req_text = ', '.join(req_parts) if req_parts else default_requirements.get(p, 'Platform-appropriate format')
            platform_requirements.append(f"- {p.upper()}: {req_text}")
        
        reqs = '\n'.join(platform_requirements)
        
        # Build post count requirements
        post_count_reqs = []
        for p in platforms:
            platform_settings = brand_socials.get(p, {}) if brand_socials else {}
            enabled = platform_settings.get('enabled', True)
            if enabled:
                post_count = platform_settings.get('postCount', 1)
                post_count_reqs.append(f"- {p.upper()}: Generate {post_count} post(s)")
        
        post_count_text = '\n'.join(post_count_reqs) if post_count_reqs else ''
        
        prompt = f"""Generate social media posts from this content:

{center_post_content}

Generate posts for these platforms: {', '.join([p.upper() for p in platforms])}

Requirements:
- Hook-first, value-dense
- CTA at end (where appropriate)
{f"- Use this specific CTA at the end: {cta_info['text']} ({cta_info['url']})" if cta_info and cta_info.get('text') and cta_info.get('url') else "- CTA at end (where appropriate)"}
- Platform-appropriate format
{reqs}
{post_count_text if post_count_text else ''}

Return JSON format:
{{
  "linkedin": [
    {{"content": "LinkedIn post...", "type": "single_post"}}
  ],
  "x": [
    {{"content": "X post 1...", "type": "single_post"}},
    {{"content": "X post 2...", "type": "thread", "thread_parts": ["part 1", "part 2"]}}
  ],
  "threads": [
    {{"content": "Threads post 1...", "type": "single_post"}},
    {{"content": "Threads post 2...", "type": "thread", "thread_parts": ["part 1", "part 2"]}}
  ],
  "instagram": [
    {{"content": "IG carousel concept...", "type": "carousel", "slides": ["slide 1 description", "slide 2 description", ...]}}
  ],
  "substack": [
    {{"content": "Substack feed post...", "type": "feed_post"}}
  ]
}}

IMPORTANT: Generate the exact number of posts specified for each platform above."""
        
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

