# 🔧 Fix JSON Error in GitHub Secrets

## Error Message
```
json.decoder.JSONDecodeError: Expecting ',' delimiter: line 128 column 7
```

This means your `CLIENTS_JSON` secret in GitHub has invalid JSON.

## ✅ How to Fix

### Step 1: Get Valid JSON Content

Your local `clients.json` file is valid. Get the content:

**Option A: Using the test script**
```bash
python3 test_secrets_local.py
```
This will show you the exact JSON to copy.

**Option B: Using cat command**
```bash
cat clients.json
```
Copy the entire output.

### Step 2: Update GitHub Secret

1. Go to: https://github.com/soulincat/soulin_social_bot/settings/secrets/actions
2. Find `CLIENTS_JSON` secret
3. Click the **pencil icon** (edit) or **delete and recreate**
4. **Delete the old value completely**
5. **Paste the ENTIRE JSON content** from your local file
6. Make sure:
   - No extra characters before/after
   - No missing commas
   - Valid JSON format
7. Click **"Update secret"**

### Step 3: Validate the Secret

1. Go to: https://github.com/soulincat/soulin_social_bot/actions/workflows/test-secrets.yml
2. Click **"Run workflow"**
3. It should now show: `✅ CLIENTS_JSON is valid JSON`

### Step 4: Test the Weekly Report

1. Go to: https://github.com/soulincat/soulin_social_bot/actions/workflows/weekly-report.yml
2. Click **"Run workflow"**
3. It should now work!

## 🐛 Common Mistakes

**❌ Copying only part of the file**
- Make sure you copy the ENTIRE file from `{` to `}`

**❌ Adding extra characters**
- No text before `{`
- No text after `}`
- No extra quotes around the JSON

**❌ Formatting issues**
- The JSON should be exactly as in your local file
- Don't add/remove spaces or newlines

## ✅ Quick Validation

Before pasting to GitHub, validate locally:
```bash
python3 -m json.tool clients.json
```

If this works without errors, the JSON is valid and ready to paste.

## 💡 Pro Tip

Use the test script to get the exact content:
```bash
python3 test_secrets_local.py
```

It will show you the exact JSON to copy-paste, already formatted correctly.

