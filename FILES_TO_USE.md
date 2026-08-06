# UNASHAMED Content Agent - Files Manifest

## 📦 What You Have

All files are ready to use. Copy them to your GitHub repository.

---

## 📋 File Organization

### Root Directory Files
```
scraper.py
generate-metadata.py
dashboard.jsx
download-manager.jsx
SETUP_GUIDE_FINAL.md (READ THIS FIRST!)
```

### GitHub Actions Workflows
```
.github/workflows/
├── scraper.yml (from scraper-workflow.yml)
├── clipper.yml (from clipper-full-workflow.yml)
└── post.yml (from post-workflow.yml)
```

---

## 🚀 Quick Start (5 Steps)

### 1. Create GitHub Repo
```bash
cd your-workspace
git clone https://github.com/YOUR_USERNAME/unashamed-agent.git
cd unashamed-agent
mkdir -p .github/workflows
```

### 2. Copy Python Scripts
- Copy `scraper.py` → repo root
- Copy `generate-metadata.py` → repo root

### 3. Copy Workflows
- Copy `scraper-workflow.yml` → `.github/workflows/scraper.yml`
- Copy `clipper-full-workflow.yml` → `.github/workflows/clipper.yml`
- Copy `post-workflow.yml` → `.github/workflows/post.yml`

### 4. Copy React Components
- Copy `dashboard.jsx` → repo root (or `src/pages/dashboard.jsx` if using Create React App)
- Copy `download-manager.jsx` → repo root (or `src/pages/download-manager.jsx`)

### 5. Push to GitHub
```bash
git add .
git commit -m "Initial UNASHAMED Agent setup"
git push -u origin main
```

---

## 🔑 What Each File Does

### `scraper.py`
**Purpose:** Monitors YouTube channels for new uploads matching your keywords

**When it runs:** Daily at 8 AM UTC (configurable)

**Outputs:** `videos.json` (list of relevant videos)

**API Cost:** FREE (YouTube API has 10K units/day free quota)

---

### `generate-metadata.py`
**Purpose:** Takes clip segments and generates platform-specific captions using Claude

**When it runs:** After clip extraction during clipper workflow

**Outputs:** `clips-with-metadata.json` (captions for TikTok, YouTube, Instagram)

**API Cost:** ~$0.01 per clip (Claude API)

---

### `.github/workflows/scraper.yml`
**Purpose:** GitHub Action that runs scraper.py daily

**Schedule:** 8 AM UTC daily (edit `cron: '0 8 * * *'` to change)

**Can be:** Manually triggered anytime

**Requires secrets:**
- `YOUTUBE_API_KEY`
- `TELEGRAM_TOKEN`
- `TELEGRAM_CHAT_ID`

---

### `.github/workflows/clipper.yml`
**Purpose:** Downloads video → transcribes → extracts clips → generates metadata

**Triggered by:** Manual workflow dispatch from dashboard

**Inputs needed:**
- YouTube URL
- Clip count (default 5)
- Channel name (optional)

**Requires secrets:**
- `DEEPGRAM_API_KEY` (~$0.04 per video)
- `ANTHROPIC_API_KEY` (~$0.01 per clip)
- `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`

**Outputs:**
- `pending-clips.json` (clips + captions ready for approval)
- `clips-with-metadata.json` (full metadata)

---

### `.github/workflows/post.yml`
**Purpose:** Stages approved clips for posting with platform-specific metadata

**Triggered by:** Manual workflow dispatch OR "Approve Clips" button in dashboard

**Outputs:**
- `posting-queue.json` (ready for posting)
- `POSTING_INSTRUCTIONS.md` (download + post guide)

**Requires secrets:**
- `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`

---

### `dashboard.jsx`
**Purpose:** Main approval interface

**Features:**
- 📺 View scraped videos
- 👍 Approve videos to clip
- ✅ Review generated clips
- 👍 Approve clips for posting
- 🔔 Real-time workflow status

**Deployment:** Vercel or local React app

**Requires:**
- GitHub Personal Access Token (for triggering workflows)
- Repo URL

---

### `download-manager.jsx`
**Purpose:** Download & organize clips by platform

**Features:**
- 🎵 TikTok section (3 caption variations + auto-post ready)
- 📺 YouTube Shorts section (copy captions)
- 📱 Instagram section (copy captions)
- 📥 Batch download all metadata
- 📋 Copy individual captions to clipboard

**Deployment:** Same as dashboard

**Usage:** After clips are generated, switch to this tab to get captions for all platforms

---

## 🔧 Deployment Options

### Option A: Vercel (Recommended - 5 minutes)
1. Go to https://vercel.com
2. Import GitHub repo
3. Add environment variables:
   ```
   REACT_APP_GITHUB_REPO=YOUR_USERNAME/unashamed-agent
   REACT_APP_REPO_URL=https://github.com/YOUR_USERNAME/unashamed-agent
   REACT_APP_GITHUB_TOKEN=YOUR_PAT_HERE
   ```
4. Deploy
5. Share live URL → Save on phone

### Option B: Local Development
1. `npx create-react-app unashamed`
2. Copy `dashboard.jsx` → `src/App.js`
3. `npm install lucide-react`
4. `npm start`
5. Access at `http://localhost:3000`

### Option C: GitHub Pages (Static)
1. Convert JSX to static HTML (more complex)
2. Or use GitHub's built-in Pages for simple HTML dashboard

---

## 🎯 Typical Usage Flow

### Day 1: Setup
1. ✅ Complete SETUP_GUIDE_FINAL.md
2. ✅ Get all API keys
3. ✅ Add GitHub Secrets
4. ✅ Deploy dashboard
5. ✅ Test scraper (manual run)

### Day 2: First Video
1. 📬 Scraper runs → finds videos
2. 👍 Approve video in dashboard
3. 🎬 Click "Generate Clips"
4. ⏳ Wait 5-10 min
5. 📬 Telegram: "Clips ready!"
6. 📥 Download Manager → Copy captions
7. 📱 Post to TikTok (auto) + YouTube + Instagram (manual)

### Week 1+: Consistent Posting
1. 📬 Open dashboard each morning
2. 👍 Approve 2-3 videos (30 sec each)
3. 🎬 Trigger clipping (happens while you work)
4. ☀️ At lunch → review clips (2 min)
5. ✅ Approve & queue for posting (1 min)
6. 🌙 Download Manager → post to YouTube/Instagram (5 min)
7. **Total: ~10 min/day for 5+ videos**

---

## 📊 Cost Summary

| Component | Cost | When |
|---|---|---|
| Scraper + Clipper | $5-7/month | Ongoing |
| - Claude API | $3-5/month | Per clip extraction |
| - Deepgram API | $1-2/month | Per video transcript |
| - YouTube/Telegram | FREE | Already counted |
| Dashboard Hosting | FREE (Vercel) | Always |
| GitHub Actions | FREE | 2K min/month included |
| **TOTAL** | **$5-7/month** | ✅ Under $20 budget |

---

## 🚨 Troubleshooting

### Scraper finds 0 videos
- Check YouTube API key in GitHub Secrets
- Verify channel names are exact matches
- Try manual workflow run

### Clips don't generate
- Ensure Deepgram key is valid
- Check Claude API has credits/token valid
- Video must have English audio

### Dashboard won't load videos
- Repo must be PUBLIC
- Verify GitHub PAT scope includes `repo`
- Check repo URL is correct

### Telegram doesn't notify
- Verify TELEGRAM_TOKEN correct
- Verify TELEGRAM_CHAT_ID correct
- Test by sending `/start` to bot in Telegram

### Download Manager missing captions
- Ensure clipper workflow completed successfully
- Check clips-with-metadata.json exists in repo
- Refresh dashboard or clear browser cache

---

## 📞 Commands Reference

### Test Scraper
```
GitHub → Actions → "Daily YouTube Scrape" → Run workflow
```

### Generate Clips
```
Dashboard → Select video → Click "Generate Clips"
```

### View Results
```
GitHub repo → videos.json (scraped videos)
GitHub repo → pending-clips.json (clips ready to review)
GitHub repo → clips-with-metadata.json (all captions/hashtags)
GitHub repo → posting-queue.json (ready to post)
```

### Check Logs
```
GitHub → Actions → Select workflow → View logs
```

---

## ✅ Launch Checklist

- [ ] Files copied to GitHub repo
- [ ] All 5 API keys obtained and verified
- [ ] GitHub Secrets added (6 total)
- [ ] Scraper tested (videos.json created)
- [ ] Dashboard deployed (Vercel or local)
- [ ] Dashboard settings configured
- [ ] First manual scraper run successful
- [ ] First clipping workflow run successful
- [ ] Download Manager displays captions correctly
- [ ] Posted first 3 videos

**Once all checked: YOU'RE LIVE**

---

## 🚀 What Happens Next

Once live:
1. Post 5+ videos/day consistently
2. Hit 10K followers in 60-90 days
3. Qualify for TikTok Partner Program
4. Start earning $500-2K/month
5. Add TikTok Shop for additional revenue

The system handles 90% of the work. Your job: hit that 5/day target.

**Let's go. 🙏**
