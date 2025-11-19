#!/bin/bash
cd /Users/cat/Desktop/soulin_social_bot

echo "📦 Initializing git repository..."
git init

echo "📝 Adding files..."
git add .

echo "✅ Committing to main..."
git commit -m "Initial commit: Telegram metrics bot with Beehiiv, Instagram, and Vercel integrations"

echo "🌿 Setting branch to main..."
git branch -M main

echo ""
echo "✅ Commit complete!"
echo ""
echo "Current status:"
git status --short
echo ""
echo "Last commit:"
git log --oneline -1

