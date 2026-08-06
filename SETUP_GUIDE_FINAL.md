# UNASHAMED Content Agent - Complete Setup Guide
## Full Ecosystem: Scrape → Approve → Generate → Download → Post

---

## 🚀 Complete Workflow

```
MORNING (Automated)
├─ 8 AM: Scraper finds 10-15 relevant videos
├─ Dashboard: 📺 Videos available to approve
└─ Telegram: "Found 12 relevant videos!"

YOU (Throughout Day)
├─ Open dashboard
├─ Review video titles + relevance scores
└─ Click "Generate Clips" on 2-3 videos

AFTERNOON (Automated)
├─ Claude extracts 5 best segments per video
├─ Generates 3 TikTok caption variations
├─ Generates YouTube Shorts captions (adjusted hashtags)
├─ Generates Instagram captions (story-focused)
├─ Telegram: "5 clips ready for download!"

YOU (Before Posting)
├─ Open "Download Manager"
├─ See all clips organized by platform
├─ TikTok: Pick best caption variation → Auto-posts
├─ YouTube: Copy caption → Manual upload (2 min)
├─ Instagram: Copy caption → Manual upload (2 min)
└─ Total time: ~10 minutes for 5 videos

THAT NIGHT
└─ Telegram: Engagement stats from TikTok
```

**Total active time: 10 min/day for 5+ videos**

---

## 📋 What You're Getting

### Files to Deploy:
```
unashamed-agent/
├── scraper.py                        # YouTube channel monitor
├── generate-metadata.py               # Claude caption generator
├── .github/workflows/
│   ├── scraper.yml                   # Daily scrape (8 AM UTC)
│   ├── clipper-full.yml              # Generate clips + metadata
│   └── post.yml                       # Auto-post to TikTok
├── dashboard.jsx                      # Main approval UI
├── download-manager.jsx               # Platform-specific metadata UI
└── videos.json                        # Scraped videos (auto-generated)
```

---

## 🔧 Setup (45 min total)

### Step 1: GitHub Repository (10 min)

1. Go to https://github.com/new
2. Create repo: `unashamed-agent`
3. Clone locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/unashamed-agent.git
   cd unashamed-agent
   ```

4. Create file structure:
   ```bash
   mkdir -p .github/workflows
   ```

5. Copy these files:
   - `scraper.py` → repo root
   - `generate-metadata.py` → repo root
   - `scraper-workflow.yml` → `.github/workflows/scraper.yml`
   - `clipper-full-workflow.yml` → `.github/workflows/clipper.yml`
   - `dashboard.jsx` → repo root
   - `download-manager.jsx` → repo root

6. Push to GitHub:
   ```bash
   git add .
   git commit -m "Initial setup"
   git push -u origin main
   ```

### Step 2: API Keys (30 min - Get all 4)

#### YouTube API Key
1. Go to https://console.cloud.google.com
2. Create project: "UNASHAMED Agent"
3. Enable: YouTube Data API v3
4. Credentials → Create API Key
5. Copy key → Save

#### Deepgram API Key
1. Go to https://console.deepgram.com
2. Sign up (free $200/month)
3. Create API key
4. Copy key → Save

#### Claude (Anthropic) API Key
1. Go to https://console.anthropic.com
2. Sign up (free $5 credit)
3. Create API key
4. Copy key → Save

#### Telegram Bot Token & Chat ID
1. Open Telegram → Search "@BotFather"
2. `/start` → `/newbot`
3. Name: "UNASHAMED Agent"
4. Username: "unashamed_agent_bot"
5. Copy token → Save
6. Search "@userinfobot" → `/start`
7. Look for "Id: ..." → Save (this is your CHAT ID)

#### GitHub Personal Access Token
1. GitHub → Settings → Developer settings → Personal access tokens
2. Generate new token (classic)
3. Name: "unashamed"
4. Scopes: `repo`, `workflow`
5. Copy token → Save

### Step 3: Add GitHub Secrets (5 min)

1. Go to repo Settings → Secrets and variables → Actions
2. Create these secrets:

| Name | Value |
|---|---|
| `YOUTUBE_API_KEY` | (from Step 2) |
| `DEEPGRAM_API_KEY` | (from Step 2) |
| `ANTHROPIC_API_KEY` | (from Step 2) |
| `TELEGRAM_TOKEN` | (from Step 2) |
| `TELEGRAM_CHAT_ID` | (from Step 2) |

### Step 4: Test Scraper (5 min)

1. Go to repo → Actions tab
2. Click "Daily YouTube Scrape"
3. Click "Run workflow" → Run workflow
4. Wait 2-3 minutes
5. Check repo → should see `videos.json` updated
6. Check Telegram for notification

### Step 5: Deploy Dashboard (15 min)

**Option A: Use Vercel (Recommended)**
1. Go to https://vercel.com
2. Sign in with GitHub
3. Import project → Select repo
4. Add environment variables:
   ```
   REACT_APP_GITHUB_REPO=YOUR_USERNAME/unashamed-agent
   REACT_APP_REPO_URL=https://github.com/YOUR_USERNAME/unashamed-agent
   REACT_APP_GITHUB_TOKEN=YOUR_TOKEN_HERE
   ```
5. Deploy
6. Save URL → Use on phone

**Option B: Local (Development)**
1. Install Node: https://nodejs.org
2. In repo folder:
   ```bash
   npx create-react-app .
   npm install lucide-react
   # Replace src/App.js with dashboard.jsx content
   npm start
   ```
3. Open http://localhost:3000 on phone

### Step 6: Configure Dashboard (5 min)

1. Open dashboard
2. Settings → Enter:
   - GitHub repo: `YOUR_USERNAME/unashamed-agent`
   - GitHub token: (your PAT from Step 2)
   - Repo URL: `https://github.com/YOUR_USERNAME/unashamed-agent`
   - Telegram Chat ID: (from Step 2)
3. Save

---

## 📱 Daily Usage

### Morning
- ✅ Scraper runs automatically at 8 AM UTC
- 📬 Telegram notifies you
- 📱 Open dashboard → See new videos

### Throughout Day
- 👍 Approve 2-3 videos (30 sec each)
- 🎬 Click "Generate Clips"
- ⏳ Clips generate in background (5-10 min)

### When Ready
- 📬 Telegram: "5 clips ready!"
- 📱 Open dashboard → Switch to "Approval" tab
- ✅ Review clip segments
- 👍 Click "Approve & Post"

### Download & Post
- 📱 Click "Download Manager"
- 🎵 TikTok: Select caption variant → **Auto-posts**
- 📺 YouTube: Copy caption text → Open TikTok → Paste in caption → Upload
- 📱 Instagram: Copy caption text → Open Instagram → Paste → Upload

**Total manual time per 5 videos: ~10 minutes**

---

## 💰 Monthly Cost Breakdown

| Service | Cost | Usage |
|---|---|---|
| GitHub Actions | FREE | 2,000 min/month |
| YouTube API | FREE | 10K units/day |
| Claude API | $3-5 | ~$0.01 per clip |
| Deepgram | $1-2 | ~$0.04 per video |
| Telegram | FREE | Notifications |
| **TOTAL** | **$5-7/month** | ✅ Well under budget |

*Optional: Ayrshare ($20/mo) for full auto-posting to all platforms*

---

## 🎯 Revenue Timeline

| Timeline | Followers | Actions | Revenue |
|---|---|---|---|
| **Week 1-2** | 500-1K | 5 posts/day, establish rhythm | $0 (building) |
| **Week 3-4** | 2-3K | Optimize captions, test variations | $10-20 |
| **Month 1** | 5-7K | Hit 3-5 videos/day consistently | $50-150 |
| **Month 2** | 8-15K | Refine top-performing angles | $200-500 |
| **Month 3** | 15-25K | **Hit Partner Program eligibility** | $500-2K |
| **Month 4+** | 25K+ | Full monetization + Shop | $2K-10K |

**Key: Consistency > Quality. Post 5/day every day. The algorithm rewards frequency.**

---

## 🔍 Troubleshooting

### Scraper finds 0 videos
- **Fix:** Check YouTube API key is valid in GitHub Secrets
- Check channel names are exact

### Clips don't generate
- **Fix:** Verify Deepgram & Claude API keys in GitHub Secrets
- Video must have English audio

### Telegram notifications don't arrive
- **Fix:** Verify TELEGRAM_TOKEN and TELEGRAM_CHAT_ID are correct
- Test: Send `/start` to your bot

### Download Manager won't load
- **Fix:** Ensure repo is PUBLIC
- Verify GitHub PAT has `repo` scope

### Platform-specific captions missing
- **Fix:** Check clips-with-metadata.json exists in repo
- Workflow must complete successfully first

---

## 📞 Quick Reference

**Common Commands:**

Manually trigger scraper:
```
repo → Actions → "Daily YouTube Scrape" → Run workflow
```

Manually trigger clipping:
```
dashboard → Select video → "Generate Clips"
```

View results:
```
repo → videos.json (scraped videos)
repo → pending-clips.json (generated clips)
repo → clips-with-metadata.json (captions + tags)
```

---

## ✅ Launch Checklist

- [ ] GitHub repo created
- [ ] All 5 API keys obtained
- [ ] GitHub Secrets added
- [ ] Scraper tested (videos.json created)
- [ ] Dashboard deployed (Vercel or local)
- [ ] Dashboard configured (settings saved)
- [ ] Telegram bot created & connected
- [ ] First video approved & clipped successfully
- [ ] Download Manager working
- [ ] Posted first 3 videos

**Once checked: YOU'RE LIVE**

---

## 🚀 Post-Launch

**Week 1 Goals:**
- ✅ 5 videos/day minimum
- ✅ Establish posting rhythm
- ✅ Track top-performing angles

**Month 1 Goals:**
- ✅ 10K views/day
- ✅ 2-3K followers
- ✅ Identify winning formats

**Month 2-3 Goals:**
- ✅ 20K+ followers
- ✅ Eligible for TikTok Partner Program
- ✅ Launch TikTok Shop for monetization

**The math is simple:** 5 posts/day × 30 days × 5K avg views per post = 750K views/month → $150-300 from Partner Program alone.

Add Shop links + affiliate revenue = $500-2K/month by Month 3.

---

**You have everything. Post 5+/day. Get paid. Let's go. 🙏**
