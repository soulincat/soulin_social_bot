# Socials Dashboard - Backend Logic Review

## ✅ Current Functionality

### 1. **Social Profile Fetching** (`/api/dashboard/socials`)
- **Status**: ✅ Functional
- **Logic Flow**:
  1. Gets client_id from request
  2. Loads client from `clients.json`
  3. Checks `brand.socials` for enabled platforms
  4. Defaults to enabled if socials is empty (matches settings behavior)
  5. For each enabled platform:
     - Creates profile_data structure
     - Checks `connected_accounts` for connection status
     - **Instagram**: Fetches real data via Facebook Graph API if connected
       - Gets: followers_count, profile_picture_url, biography, username
       - Uses: `user_id` and `access_token` from connected_accounts
     - **Other platforms**: Placeholders (LinkedIn, X, Threads, Substack, Telegram)
  6. Sums total followers from all platforms
  7. Returns profiles array + total_followers

### 2. **Follower Crawling**
- **Instagram**: ✅ **WORKING** - Fetches real-time data when:
  - Platform is enabled in settings
  - Account is connected in `connected_accounts.instagram`
  - Has valid `user_id` and `access_token`
- **Other Platforms**: ⚠️ **NOT YET IMPLEMENTED** - Show 0 followers (placeholders)

### 3. **Connection Status**
- **Current**: Checks `connected_accounts[platform].connected`
- **Issue**: Settings page doesn't show connection status yet (needs UI update)

## 🔧 Issues Found & Fixed

### Issue 1: Icons Duplicated ✅ FIXED
- **Problem**: Icon shown in both profile pic area AND name
- **Fix**: Removed icon from name, only show in profile pic area (or use platform icon if no profile pic)

### Issue 2: Platform Icons ✅ FIXED
- **Problem**: Using emoji icons
- **Fix**: Using Simple Icons CDN for actual platform logos
  - LinkedIn: Blue LinkedIn icon
  - X: Black X icon
  - Threads: Black Threads icon
  - Instagram: Pink Instagram icon
  - Substack: Orange Substack icon
  - Telegram: Blue Telegram icon

### Issue 3: OAuth Connection ✅ ADDED
- **Added**: "Connect Account" button when platform is enabled
- **Status**: Placeholder alert (OAuth flow needs full implementation)
- **Endpoint**: `POST /api/clients/<client_id>/connect/<platform>` ready for OAuth callback

## 📋 Backend Logic Flow

```
Dashboard Load
  ↓
loadDashboardData()
  ↓
loadSocialProfiles(clientId)
  ↓
GET /api/dashboard/socials?client_id=...
  ↓
Backend:
  1. Load client from clients.json
  2. Get brand.socials (enabled platforms)
  3. Get connected_accounts (connection status)
  4. For each enabled platform:
     - Check if connected
     - If Instagram + connected: Fetch from Facebook Graph API
     - Else: Return placeholder (0 followers)
  5. Sum total followers
  6. Return profiles + total_followers
  ↓
Frontend renders cards with:
  - Platform icon (or profile pic if available)
  - Platform name (no duplicate icon)
  - Username (if available)
  - Follower count (real if connected, 0 if not)
  - Description/bio (if available)
```

## 🐛 Known Issues

1. **OAuth Not Fully Implemented**
   - "Connect Account" button shows alert
   - Need to implement actual OAuth flows for each platform
   - Need OAuth callback handlers

2. **Only Instagram Fetches Real Data**
   - LinkedIn, X, Threads, Substack, Telegram need API implementations
   - Currently return 0 followers

3. **Connection Status Not Visible in Settings**
   - Added connection status display but needs to check actual connected_accounts
   - Need to update checkAllConnectionStatuses() to use new endpoint

## ✅ What's Working

- ✅ Instagram follower count fetching (if connected)
- ✅ Instagram profile pic, bio, username fetching
- ✅ Total followers calculation
- ✅ Platform icons (using Simple Icons)
- ✅ No duplicate icons
- ✅ Enabled platforms show on dashboard
- ✅ Connection status checking endpoint added

