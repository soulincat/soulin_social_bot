# 🚀 How to Trigger the Test Secrets Workflow (First Time)

Since the workflow has never been run, here's exactly how to trigger it:

## Step-by-Step with Screenshots Guide

### Step 1: Go to the Workflow Page
Visit: https://github.com/soulincat/soulin_social_bot/actions/workflows/test-secrets.yml

You should see:
- "This workflow has no runs yet"
- A button that says **"Run workflow"** on the right side

### Step 2: Click "Run workflow"
- Look for the **"Run workflow"** dropdown button on the right side of the page
- It's usually in the top-right area, next to "Filter workflow runs"

### Step 3: Select Branch and Run
- A dropdown will appear
- Make sure **"Use workflow from"** shows `main` branch
- Click the green **"Run workflow"** button at the bottom of the dropdown

### Step 4: Watch It Run
- The page will refresh
- You'll see a new workflow run appear
- Click on it to see the progress and results

## Visual Guide

```
┌─────────────────────────────────────────┐
│  test-secrets.yml                       │
│                                          │
│  [Filter workflow runs]  [Run workflow ▼] ← Click here!
│                                          │
│  This workflow has no runs yet.         │
└─────────────────────────────────────────┘
```

After clicking "Run workflow":
```
┌─────────────────────────────────────────┐
│  [Run workflow ▼]                        │
│  ┌───────────────────────────────────┐ │
│  │ Use workflow from: [main ▼]       │ │
│  │                                    │ │
│  │         [Run workflow] ← Click!    │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

## Alternative: If You Don't See "Run workflow" Button

If the button doesn't appear, it might be because:

1. **Actions might be disabled:**
   - Go to: Settings → Actions → General
   - Make sure "Allow all actions and reusable workflows" is selected
   - Or at minimum, "Allow local actions and reusable workflows"

2. **You might not have write access:**
   - Make sure you're logged in as the repository owner
   - Or you have write permissions to the repo

3. **Try refreshing the page:**
   - Sometimes it takes a moment to load
   - Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

## What Happens After You Run It

1. The workflow will start running (you'll see a yellow circle)
2. It will check your secrets
3. You'll see output showing:
   - ✅ Which secrets are set
   - ❌ Which secrets are missing
4. The workflow will complete (green checkmark if secrets are set, red X if missing)

## Troubleshooting

**Still can't see the button?**
- Make sure you're on the correct page: `/actions/workflows/test-secrets.yml`
- Check that the workflow file exists: `.github/workflows/test-secrets.yml`
- Try going to the main Actions page first: `/actions`

**Button is grayed out?**
- You might need to enable Actions in repository settings
- Check repository permissions

## Quick Direct Link

Just go here and click "Run workflow":
https://github.com/soulincat/soulin_social_bot/actions/workflows/test-secrets.yml

