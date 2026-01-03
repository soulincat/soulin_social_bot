# Center Post Not Created - Issue & Fix

## Problem

Posts are being saved to Supabase (7 posts saved), but they don't have `center_post` because **AI expansion is failing**.

## Root Causes

Looking at the error messages in `content_posts.json`, the issues are:

1. **Missing API Key**: `"ANTHROPIC_API_KEY not found in environment"`
2. **Invalid API Key**: `"Error code: 401 - invalid x-api-key"`
3. **Wrong Model Name**: `"Error code: 404 - model: claude-3-5-sonnet-20241022 not found"`

## What Happens When AI Expansion Fails

When `auto_expand=True` but AI expansion fails:
- ✅ Post **IS saved** to Supabase
- ❌ Post **does NOT have** `center_post` field
- ⚠️ Post has `status: 'idea'` (or sometimes incorrectly 'draft')
- ⚠️ Post has `error: "..."` field with the error message

## How to Fix

### 1. Set ANTHROPIC_API_KEY

Add to your `.env` file:
```bash
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Get your key from: https://console.anthropic.com/

### 2. Check Model Name (Optional)

The default model is `claude-sonnet-4-20250514`. If you need a different model, set:
```bash
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022
```

**Note**: Make sure the model name is correct. The error shows `claude-3-5-sonnet-20241022` doesn't exist. Valid models include:
- `claude-sonnet-4-20250514` (default, recommended)
- `claude-3-5-sonnet-20250620`
- `claude-3-opus-20240229`

### 3. Restart Flask Server

After updating `.env`, restart your Flask server:
```bash
python3 app.py
# or
npm run dev
```

## UI Updates

The content detail page now shows:
- ⚠️ Warning message when `center_post` is missing
- ❌ Specific error message (API key issue, model issue, etc.)
- 🔘 "Expand with AI" button to retry expansion

## Fixing Existing Posts

Posts that were saved without `center_post` can be fixed by:

1. **Option 1**: Click "Expand with AI" button on the post detail page
2. **Option 2**: Fix your API key and create new posts (old posts will remain as 'idea' status)

## Verification

After fixing the API key, create a new post and check:
- ✅ Post should have `status: 'drafted'` (not 'idea')
- ✅ Post should have `center_post` object with `title`, `content`, `word_count`, `checks`
- ✅ No `error` field in the post

## Summary

**The posts ARE being saved correctly to Supabase.** The issue is that `center_post` is only created when AI expansion succeeds. Since AI expansion is failing due to missing/invalid API key, posts are saved without `center_post`.

Fix: Set `ANTHROPIC_API_KEY` in `.env` and restart the server.

