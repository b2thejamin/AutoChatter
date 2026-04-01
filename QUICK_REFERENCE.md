# Quick Reference: Multi-Channel Setup

## 📝 Configuration Template

```python
# In config.py

CHANNELS = [
    {
        "name": "Channel A",
        "channel_id": "UCxxxxxxxxxxxxxxxxxxxx",
        "token_file": "tokens/channel_a.pickle"
    },
    {
        "name": "Channel B",
        "channel_id": "UCyyyyyyyyyyyyyyyyyyyy",
        "token_file": "tokens/channel_b.pickle"
    }
]
```

## 🔑 Finding Your Channel ID

**Method 1 - From YouTube Studio:**
1. Go to YouTube Studio
2. Settings → Channel → Advanced settings
3. Copy "Channel ID"

**Method 2 - From Channel URL:**
1. Go to your channel
2. Look at URL: `youtube.com/channel/UCxxxxxxxxxxxxxxxxxxxx`
3. Copy everything after `/channel/`

## 🚀 First-Time Setup

```bash
# 1. Create tokens directory
mkdir tokens

# 2. Edit config.py with your channel IDs

# 3. Run the app
python main.py
```

## 🔐 Authentication Process

For **each channel**:
1. Browser opens
2. Sign in with **that channel's Google account**
3. Click "Allow"
4. Token saved to that channel's token file
5. App verifies authentication matches channel ID

## ⚠️ Common Issues

### "AUTHENTICATION MISMATCH!"
**Problem**: Signed in with wrong Google account

**Fix**:
```bash
# Delete the token file
rm tokens/channel_name.pickle

# Run again
python main.py
```

### "No channels were successfully initialized"
**Problem**: All channels failed authentication

**Fix**:
- Check `client_secret.json` exists
- Check channel IDs are correct
- Check token file paths are valid

## 📊 Log Output

```
[Main Channel] Checking for new videos...
[Main Channel] Processing new video: My Latest Upload
[Main Channel] Successfully commented on video
[Gaming Channel] Checking for new videos...
[Gaming Channel] No new videos to process
```

## 🔄 Re-authenticating a Channel

```bash
# Delete token file
rm tokens/channel_name.pickle

# Run app - it will prompt for auth
python main.py
```

## 📂 File Structure

```
AutoChatter/
├── config.py                    ← Edit this
├── client_secret.json           ← Your OAuth credentials
├── tokens/
│   ├── channel_a.pickle         ← Auto-generated
│   └── channel_b.pickle         ← Auto-generated
├── state.json                   ← Auto-generated
└── autochatter.log              ← Check for errors
```

## ✅ Verification Checklist

- [ ] Created `tokens/` directory
- [ ] Updated `CHANNELS` in `config.py`
- [ ] Have `client_secret.json` in project root
- [ ] Know which Google account belongs to which channel
- [ ] Ready to authenticate each channel separately

## 🎯 Expected Behavior

✅ Channel A watches Channel A → comments as Channel A  
✅ Channel B watches Channel B → comments as Channel B  
✅ Each uses own token file  
✅ No cross-channel commenting  
✅ Each verified on startup  

## 📞 Need Help?

Check these files:
- `MULTI_CHANNEL_GUIDE.md` - Detailed setup guide
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- `README.md` - General usage
- `autochatter.log` - Error logs
