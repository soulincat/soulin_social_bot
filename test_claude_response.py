#!/usr/bin/env python3
"""
Test script to see what Claude API actually returns
"""
import os
from dotenv import load_dotenv
from content.ai_client import ClaudeClient

load_dotenv()

def test_claude_response():
    """Test Claude API response format"""
    try:
        print("🧪 Testing Claude API response...")
        print(f"Model: {os.getenv('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')}")
        print(f"API Key set: {bool(os.getenv('ANTHROPIC_API_KEY'))}")
        print()
        
        client = ClaudeClient()
        print(f"✅ ClaudeClient initialized with model: {client.model}")
        print()
        
        # Test with a simple idea
        test_idea = "How to build better habits"
        test_client = {
            'client_id': 'test',
            'brand': {
                'mission': 'Help people improve their lives',
                'voice': {
                    'tone': 'Friendly and encouraging'
                }
            }
        }
        
        print(f"📝 Testing with idea: '{test_idea}'")
        print("⏳ Calling Claude API...")
        
        result = client.expand_idea(test_idea, test_client)
        
        print()
        print("✅ Success! Claude returned:")
        print(f"   Title: {result.get('title', 'N/A')}")
        print(f"   Content length: {len(result.get('content', ''))} characters")
        print(f"   Word count: {result.get('word_count', 'N/A')}")
        print(f"   Checks: {result.get('checks', {})}")
        
    except Exception as e:
        print()
        print(f"❌ Error: {e}")
        print()
        print("Full error details:")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_claude_response()

