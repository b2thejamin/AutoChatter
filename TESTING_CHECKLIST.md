# Testing Checklist for Multi-Channel Setup

## ✅ Pre-Testing Setup

- [ ] `tokens/` directory created
- [ ] `config.py` has at least one channel configured
- [ ] Each channel has valid `channel_id` (starts with `UC`)
- [ ] Each channel has unique `token_file` path
- [ ] `client_secret.json` exists in project root
- [ ] All Python dependencies installed (`pip install -r requirements.txt`)

## 🧪 Test Scenarios

### Test 1: Single Channel (Backward Compatibility)

**Config:**
```python
CHANNELS = [
    {
        "name": "Test Channel",
        "channel_id": "UCxxxxxxxxxxxxxxxxxxxx",
        "token_file": "token.pickle"
    }
]
```

**Expected:**
- [ ] App starts without errors
- [ ] OAuth browser opens (if first run)
- [ ] After authentication, shows: "Authenticated as: [channel name]"
- [ ] Shows: "✓ Authentication verified for Test Channel"
- [ ] Shows: "Successfully initialized 1 channel(s)"
- [ ] Polling loop starts
- [ ] Logs show: "[Test Channel] Checking for new videos..."

---

### Test 2: Two Channels (New Feature)

**Config:**
```python
CHANNELS = [
    {
        "name": "Channel A",
        "channel_id": "UCaaaaaaaaaaaaaaaaaaa",
        "token_file": "tokens/channel_a.pickle"
    },
    {
        "name": "Channel B",
        "channel_id": "UCbbbbbbbbbbbbbbbbbb",
        "token_file": "tokens/channel_b.pickle"
    }
]
```

**Expected:**
- [ ] App processes Channel A first
- [ ] Browser opens for Channel A authentication (if first run)
- [ ] Shows: "Authenticated as: [Channel A name]"
- [ ] Shows: "✓ Authentication verified for Channel A"
- [ ] App processes Channel B second
- [ ] Browser opens for Channel B authentication (if first run)
- [ ] Shows: "Authenticated as: [Channel B name]"
- [ ] Shows: "✓ Authentication verified for Channel B"
- [ ] Shows: "Successfully initialized 2 channel(s)"
- [ ] Logs show both channels in list
- [ ] Polling loop checks both channels
- [ ] Logs alternate: "[Channel A] ..." then "[Channel B] ..."

---

### Test 3: Authentication Mismatch Detection

**Setup:**
1. Delete `tokens/channel_b.pickle`
2. Run app
3. When Channel B auth opens, sign in with Channel A's account

**Expected:**
- [ ] App detects mismatch
- [ ] Shows error:
  ```
  [Channel B] AUTHENTICATION MISMATCH!
    Expected channel ID: UCbbbbbbbbbbbbbbbbbb
    Authenticated channel ID: UCaaaaaaaaaaaaaaaaaaa
  ```
- [ ] Channel B is skipped
- [ ] Channel A continues to work
- [ ] Shows: "Successfully initialized 1 channel(s)"

**Fix:**
- [ ] Delete `tokens/channel_b.pickle`
- [ ] Restart app
- [ ] Sign in with correct account for Channel B
- [ ] Both channels now work

---

### Test 4: Re-authentication

**Setup:**
1. Stop the app
2. Delete `tokens/channel_a.pickle`
3. Restart app

**Expected:**
- [ ] Browser opens only for Channel A
- [ ] After auth, Channel A works
- [ ] Channel B uses existing token (no browser opens)
- [ ] Both channels start monitoring

---

### Test 5: State Tracking (No Duplicate Comments)

**Setup:**
1. Let app run and comment on a video
2. Stop app
3. Restart app

**Expected:**
- [ ] App loads state from `state.json`
- [ ] Shows: "Loaded state with X tracked videos"
- [ ] Previously commented video is NOT commented again
- [ ] Logs show: "[Channel Name] Video XXX already processed, skipping"

---

### Test 6: Missing Channel Configuration

**Config:**
```python
CHANNELS = [
    {
        "name": "Test",
        # "channel_id": "UCxxxx",  # Missing!
        "token_file": "test.pickle"
    }
]
```

**Expected:**
- [ ] Shows error: "[Test] Missing channel_id, skipping this channel"
- [ ] App continues (doesn't crash)
- [ ] Shows: "ERROR: No channels were successfully initialized!"
- [ ] App exits with error

---

### Test 7: Empty Channels List

**Config:**
```python
CHANNELS = []
```

**Expected:**
- [ ] Shows: "ERROR: No channels configured!"
- [ ] Shows: "Please add at least one channel to the CHANNELS list in config.py"
- [ ] App exits with error

---

### Test 8: File Permissions

**Setup:**
1. Create `tokens/` directory
2. Run app with proper config

**Expected:**
- [ ] App creates token files in `tokens/` directory
- [ ] Token files are created with proper permissions
- [ ] No permission errors in logs

---

## 🔍 What to Check in Logs

### Startup Logs:
```
AutoChatter - YouTube Auto-Comment Bot
Poll interval: 600 seconds
Number of channels configured: 2
Initializing state manager...
Initializing YouTube clients for each channel...
```

### Channel Initialization:
```
============================================================
Initializing channel: Channel A
  Channel ID: UCaaaaaaaaaaaaaaaaaaa
  Token file: tokens/channel_a.pickle
  Authenticated as: Channel A Title (UCaaaaaaaaaaaaaaaaaaa)
  ✓ Authentication verified for Channel A
============================================================
```

### Polling Loop:
```
[Channel A] Checking for new videos on channel UCaaaa...
[Channel A] Fetched 5 videos from channel UCaaaa...
[Channel A] No new videos to process
[Channel B] Checking for new videos on channel UCbbbb...
[Channel B] Processing new video: Video Title (dQw4w9WgXcQ)
[Channel B] Waiting 45 seconds before commenting...
[Channel B] Posting comment on video dQw4w9WgXcQ
[Channel B] Successfully commented on video: Video Title
```

---

## 🐛 Debugging Tips

### Check autochatter.log:
```bash
tail -f autochatter.log
```

### Check state.json:
```bash
cat state.json
```
Should show entries like:
```json
{
  "last_seen_videos": [
    "UCaaaa:video123",
    "UCbbbb:video456"
  ]
}
```

### Verify token files exist:
```bash
ls -la tokens/
```

### Test OAuth separately:
```python
from yt_client import YouTubeClient
client = YouTubeClient(token_file="tokens/test.pickle")
info = client.get_authenticated_channel_info()
print(info)
```

---

## ✅ Success Criteria

Your multi-channel setup is working correctly if:

- ✅ Each channel initializes without errors
- ✅ Authentication verification passes for all channels
- ✅ Each channel uses its own token file
- ✅ Logs clearly show which channel is being processed
- ✅ Each channel monitors only its own uploads
- ✅ Comments appear on correct videos
- ✅ No duplicate comments on same video
- ✅ State is tracked correctly per channel
- ✅ Authentication mismatches are detected and logged
- ✅ App handles missing/invalid config gracefully

---

## 📊 Performance Expectations

With 2 channels and default settings:

- **Startup time**: 5-10 seconds (after auth)
- **First auth**: 30-60 seconds per channel (user interaction)
- **Subsequent starts**: Instant (uses saved tokens)
- **Poll interval**: Every 10 minutes (configurable)
- **Memory usage**: ~50-100 MB per channel
- **API quota**: ~400 units/day (2 channels, 144 checks, ~5 comments)

---

## 🎉 Ready to Go!

If all tests pass, your AutoChatter is ready for production use with multiple channels!
