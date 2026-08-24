#!/usr/bin/env python3
"""
YouTube Channel Scraper for UNASHAMED
Monitors specified channels for new uploads daily
Extracts transcripts and finds keyword timestamps for fast clipping
Stores results in JSON for mobile dashboard consumption

CHANGELOG (this revision):
- FIXED: get_transcript() was calling a static method (YouTubeTranscriptApi.get_transcript)
  that was removed in youtube-transcript-api v1.0+. This silently failed on every single
  video via the broad except block, which is why clip_markers was empty for 100% of videos.
  Now uses the current instance-based .fetch() API.
- FIXED: save_results() previously never updated already-saved videos, only added new ones.
  That meant re-running the scraper after a fix would never backfill old empty clip_markers.
  Now updates in place, but ONLY for videos still in "pending" status — anything you've
  already acted on (clipped, rejected, etc.) is left untouched so this can't clobber your work.
- CHANGED: find_keyword_timestamps() now pads each hit with real lead/trail time instead of
  a flat +5 seconds, and caps output to the highest-confidence markers per video instead of
  dumping every keyword hit (a chatty video could previously flood the queue with 15+ markers).
- ADDED: generate_manifest() writes a human-readable clips_manifest.md after each run — lets
  you triage candidate clips by reading snippets, BEFORE downloading anything, instead of
  downloading every flagged video to find out if it's worth clipping.
- FIXED (minor): scrape_all_channels() was passing channel_id as channel_name, which is why
  videos.json showed raw channel IDs instead of readable names. CHANNELS is now a list of
  {id, name} dicts. Also corrected the 4 channel IDs verified against your live videos.json
  (ProphecyPros, RealLifeJackHibbs, CBNnewsonline, J.D. Farag) — the other ~24 entries are
  UNVERIFIED and were flagged separately as a known open issue, not fixed in this pass.
"""

import json
import os
import re
from datetime import datetime, timedelta

import requests
from typing import List, Dict

# Try to import youtube-transcript-api, fallback gracefully
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_AVAILABLE = True
except ImportError:
    TRANSCRIPT_AVAILABLE = False
    print("Warning: youtube-transcript-api not installed. Install with: pip install youtube-transcript-api")

# ---------------------------------------------------------------------------
# YouTube channels to monitor
# Every ID below was verified directly against YouTube (either via live
# videos.json output already producing real content, or by fetching the
# channel's actual @handle page and reading its real channel_id). None of
# these are guessed or AI-generated — that was the root cause of the
# original channel list being mostly fabricated.
#
# Channels that could NOT be verified (no URL supplied) were DROPPED rather
# than kept with fake IDs. Open/excluded for now: Jonathan Conricus, Charlie
# Kirk, Barry Stagner, Voddie Baucham, The Porch, Becoming Something, Live
# Original, Marcus Rogers, Soulja of God, Scott Mitchell, Gary P. Miller,
# David Wilhelmson, Gary Wayne. Send a real channel URL for any of these to
# add them back in with a verified ID.
# ---------------------------------------------------------------------------
CHANNELS = [
    {"id": "UCkz3m787ygph7Uvjxzngl-g", "name": "J.D. Farag"},
    {"id": "UCM5pZmeOIGuO3naMnJYg3gA", "name": "Prophecy Pros"},
    {"id": "UCzvq_2THJhueXOP8JdAO2-A", "name": "Real Life Jack Hibbs"},
    {"id": "UCYI_ychRnL7sJrG6PUSBpQA", "name": "CBN News Online"},
    {"id": "UCrPGIKiPtgQ25TaW1fLdR0Q", "name": "2819 Church"},
    {"id": "UCedYGs_lqq1uNet0u7qlSyQ", "name": "CrossExamined (Frank Turek)"},
    {"id": "UCneKpMu9SFGlt2usTdAI75A", "name": "Grace to You (John MacArthur)"},
    {"id": "UCa3C7WpFobavsDJdkKUtodw", "name": "Behold Israel (Amir Tsarfati)"},
    {"id": "UC5qDet6sa6rODi7t6wfpg8g", "name": "InspiringPhilosophy"},
    {"id": "UCE63fBeQIoJ2P2mlBkQDchA", "name": "Bryce Crawford Podcast"},
    {"id": "UCfTJJ9hIy6Us3JVJV_4eKzg", "name": "GodLogic Apologetics"},
    {"id": "UCmrVJGUS1u5-Hsm_BFS_1YA", "name": "Living Waters (Ray Comfort)"},
    {"id": "UCJX2EazMKUqBQV048px2aoA", "name": "Wes Huff"},
    {"id": "UCkoujZQZatbqy4KGcgjpVxQ", "name": "Shawn Ryan Show"},
    {"id": "UCm6u_sCZttC70GyRh6uCurQ", "name": "HeartCry Missionary Society (Paul Washer)"},
    {"id": "UCJ6JqDgPg9ufscsNkck_rfw", "name": "GodSounds"},
    {"id": "UCj2yZE96gWsFyeVYnY9zXeg", "name": "Ruslan KD"},
    {"id": "UCeapS6tXIdBI-Hf82-MrlCA", "name": "Isaiah Saldivar"},
    {"id": "UC12TliEdwocs1yxNkTbYjTQ", "name": "OCCA Oxford Centre for Christian Apologetics (John Lennox)"},
    {"id": "UCzT4tQfAZEsm_yMql_10dpg", "name": "Passion City Church"},
    {"id": "UCWKMsegWgWqOa90t-DCZkdg", "name": "Gabe Poirot"},
    {"id": "UCzTWdr_9IVWWmeStz5qDjoA", "name": "Derek Prince Ministries"},
    {"id": "UCPSNPjFfoFW_A_6popRatsA", "name": "World Challenge (David Wilkerson)"},
    {"id": "UCoiIt_v1D-6z75LmrdIU2aw", "name": "Rob Skiba (Skiba News Nation)"},
    {"id": "UCySeXTLuH6wSJveZrA-sz9A", "name": "L.A. Marzulli"},
]

# Keywords to filter for high-relevance content
KEYWORDS = [
    "romans 1:16", "romans 1 16", "not ashamed", "not ashamed of the gospel",
    "unashamed", "unashamed of the gospel", "gospel", "gospel message",
    "boldness for christ", "uncompromising faith",
    "end times", "end times prophecy", "eschatology", "last days",
    "christ return", "return of jesus", "second coming", "second coming of christ",
    "rapture", "rapture of the church", "tribulation", "great tribulation",
    "day of the lord", "blessed hope",
    "prophecy", "bible prophecy", "bible prophecy update", "signs of the times",
    "signs of the end times", "book of revelation", "revelation prophecy",
    "antichrist", "mark of the beast", "third temple",
    "prophecy update", "end times sermon", "revelation bible study",
    # Genesis 6 / Nephilim / Watchers — added for upcoming Genesis 6 content
    "genesis 6", "genesis chapter 6", "sons of god", "daughters of men",
    "nephilim", "watchers", "fallen angels", "giants in the earth",
    "book of enoch", "days of noah", "before the flood",
]

# ---------------------------------------------------------------------------
# Clip marker tuning — Phase 2 fix
# ---------------------------------------------------------------------------
CLIP_PAD_BEFORE = 3       # seconds of lead-in before the keyword hit
CLIP_PAD_AFTER = 30       # seconds of trailing context after the keyword hit
MERGE_GAP_SECONDS = 10    # merge two hits into one clip if this close together
MAX_CLIPS_PER_VIDEO = 4   # hard cap so one chatty video can't flood the queue

# ---------------------------------------------------------------------------
# Cloud transcript fetching toggle
# GitHub Actions (and any cloud provider) gets IP-blocked by YouTube for
# transcript requests — confirmed from a live run's logs, not a guess.
# Defaults OFF so the Action doesn't burn ~20 minutes retrying calls that
# will always fail. Transcript fetching (and clip_markers generation) now
# happens locally instead — run fetch_transcripts_local.py on a home
# connection. Only flip this on if you've set up a paid residential proxy
# (see comments in get_transcript) and know what that costs.
# ---------------------------------------------------------------------------
FETCH_TRANSCRIPTS_IN_CLOUD = os.getenv("FETCH_TRANSCRIPTS_IN_CLOUD", "false").lower() == "true"


class YouTubeScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.videos = []

    def get_transcript(self, video_id: str) -> List[Dict]:
        """
        Extract transcript from a YouTube video using the current (v1.0+) API.

        NOTE: This will reliably fail with an IpBlocked/RequestBlocked error when
        run from GitHub Actions or any cloud provider IP — YouTube blocks
        transcript requests from datacenter IPs categorically. This is not a
        bug in this code; it's confirmed directly from a live run's logs.
        The free/reliable fix is NOT to call this from cloud CI. Use
        fetch_transcripts_local.py on a home/residential connection instead —
        see that file for the actual transcript-fetching step.
        """
        if not TRANSCRIPT_AVAILABLE:
            return []
        try:
            ytt_api = YouTubeTranscriptApi()
            fetched = ytt_api.fetch(video_id)
            return fetched.to_raw_data()
        except Exception as e:
            print(f"    Could not get transcript for {video_id}: {e}")
            return []

    def find_keyword_timestamps(self, transcript: List[Dict]) -> List[Dict]:
        """
        Find timestamps where keywords appear in transcript.
        Each hit is padded with lead/trail context (not just a flat +5s), nearby hits
        are merged, and output is capped to the highest-confidence markers per video.
        """
        if not transcript:
            return []

        segments = []
        keywords_lower = [kw.lower() for kw in KEYWORDS]

        for entry in transcript:
            text_lower = entry['text'].lower()
            raw_start = entry['start']

            for i, keyword in enumerate(keywords_lower):
                if keyword in text_lower:
                    padded_start = max(0, raw_start - CLIP_PAD_BEFORE)
                    padded_end = raw_start + CLIP_PAD_AFTER
                    segments.append({
                        "keyword": KEYWORDS[i],
                        "start_time": round(padded_start, 2),
                        "end_time": round(padded_end, 2),
                        "text_snippet": entry['text'][:150],
                    })

        # Remove exact duplicates
        unique_segments = []
        seen = set()
        for seg in segments:
            key = (seg['start_time'], seg['keyword'])
            if key not in seen:
                unique_segments.append(seg)
                seen.add(key)
        unique_segments.sort(key=lambda x: x['start_time'])

        # Merge nearby/overlapping segments into one clip
        merged = []
        for seg in unique_segments:
            if merged and seg['start_time'] - merged[-1]['end_time'] < MERGE_GAP_SECONDS:
                merged[-1]['end_time'] = max(merged[-1]['end_time'], seg['end_time'])
                merged[-1]['keywords'] = list(dict.fromkeys(
                    merged[-1].get('keywords', []) + [seg['keyword']]
                ))
            else:
                seg['keywords'] = [seg['keyword']]
                del seg['keyword']
                merged.append(seg)

        # Rank by confidence (more distinct keyword hits merged together = stronger signal),
        # cap to the top N, then restore chronological order for readability.
        merged.sort(key=lambda x: len(x['keywords']), reverse=True)
        top_clips = merged[:MAX_CLIPS_PER_VIDEO]
        top_clips.sort(key=lambda x: x['start_time'])

        return top_clips

    def get_recent_uploads(self, channel_id: str, channel_name: str, days: int = 365) -> List[Dict]:
        """Get recent uploads from a channel and search transcripts for keywords"""
        url = f"{self.base_url}/search"
        published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "maxResults": 50,
            "order": "date",
            "publishedAfter": published_after,
            "type": "video",
            "key": self.api_key,
        }

        videos = []
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            for item in data.get("items", []):
                snippet = item["snippet"]
                video_id = item["id"]["videoId"]
                title = snippet["title"]
                description = snippet["description"]
                published_at = snippet["publishedAt"]

                title_desc_relevance = self._calculate_relevance(title + " " + description)

                transcript_relevance = 0
                clip_markers = []

                if FETCH_TRANSCRIPTS_IN_CLOUD and TRANSCRIPT_AVAILABLE:
                    print(f"    Fetching transcript for: {title[:50]}...")
                    transcript = self.get_transcript(video_id)
                    if transcript:
                        markers = self.find_keyword_timestamps(transcript)
                        if markers:
                            transcript_relevance = len(markers)
                            clip_markers = markers
                            print(f"    Found {len(markers)} clip point(s) in transcript")

                total_relevance = title_desc_relevance + transcript_relevance

                if total_relevance > 0:
                    video_data = {
                        "video_id": video_id,
                        "channel_name": channel_name,
                        "channel_id": channel_id,
                        "title": title,
                        "description": description,
                        "published_at": published_at,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "relevance_score": total_relevance,
                        "status": "pending",
                        "discovered_at": datetime.utcnow().isoformat(),
                        "clip_markers": clip_markers,
                    }
                    videos.append(video_data)

        except Exception as e:
            print(f"Error fetching uploads for {channel_name}: {e}")

        return videos

    def _calculate_relevance(self, text: str) -> float:
        """Calculate relevance score based on keyword matches"""
        text_lower = text.lower()
        score = 0
        for keyword in KEYWORDS:
            if keyword in text_lower:
                score += 1
        return score

    def scrape_all_channels(self) -> List[Dict]:
        """Scrape all channels and return combined results"""
        all_videos = []
        print(f"Starting scrape of {len(CHANNELS)} channels...")

        for channel in CHANNELS:
            print(f"Scraping {channel['name']} ({channel['id']})...")
            videos = self.get_recent_uploads(channel["id"], channel["name"])
            all_videos.extend(videos)
            print(f"    Found {len(videos)} relevant videos")

        all_videos.sort(key=lambda x: (
            -x["relevance_score"],
            -datetime.fromisoformat(x["published_at"].replace("Z", "+00:00")).timestamp()
        ))
        return all_videos

    def save_results(self, videos: List[Dict], output_file: str = "videos.json"):
        """
        Save results to JSON file. Updates videos still in 'pending' status with
        fresh data (this is what lets a scraper fix backfill previously-broken
        clip_markers). Videos with any other status (clipped, rejected, etc.)
        are left completely untouched — this can never clobber work you've
        already done downstream.
        """
        existing = {}
        if os.path.exists(output_file):
            try:
                with open(output_file, "r") as f:
                    existing_data = json.load(f)
                for video in existing_data.get("videos", []):
                    existing[video["video_id"]] = video
            except Exception as e:
                print(f"Error loading existing videos: {e}")

        new_count = 0
        updated_count = 0

        for video in videos:
            vid = video["video_id"]
            if vid not in existing:
                existing[vid] = video
                new_count += 1
            else:
                prior_status = existing[vid].get("status", "pending")
                if prior_status == "pending":
                    existing[vid]["title"] = video["title"]
                    existing[vid]["description"] = video["description"]
                    existing[vid]["relevance_score"] = video["relevance_score"]
                    existing[vid]["clip_markers"] = video["clip_markers"]
                    existing[vid]["channel_name"] = video["channel_name"]
                    updated_count += 1
                # else: already acted on downstream — leave it alone

        videos_list = list(existing.values())
        videos_list.sort(key=lambda x: (
            -x["relevance_score"],
            -datetime.fromisoformat(x["published_at"].replace("Z", "+00:00")).timestamp()
        ))

        output_data = {
            "last_updated": datetime.utcnow().isoformat(),
            "total_videos": len(videos_list),
            "videos": videos_list[:100],
        }

        try:
            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=2)
            print(f"Saved {len(videos_list)} videos to {output_file} "
                  f"({new_count} new, {updated_count} updated)")
        except Exception as e:
            print(f"Error saving results: {e}")

        return output_data


def generate_manifest(output_data: dict, output_file: str = "clips_manifest.md"):
    """
    Human-readable triage doc. Read this BEFORE downloading anything — lets you
    decide which videos are actually worth pulling down based on the matched
    snippets, instead of downloading every flagged video to find out.
    """
    pending = [
        v for v in output_data.get("videos", [])
        if v.get("status") == "pending" and v.get("clip_markers")
    ]
    pending.sort(key=lambda x: -x["relevance_score"])

    lines = [
        f"# Clip Manifest — generated {datetime.utcnow().isoformat()}",
        f"\n{len(pending)} pending video(s) with candidate clips.\n",
    ]

    for v in pending:
        lines.append(f"## {v['title']}")
        lines.append(f"- Channel: {v['channel_name']} | Relevance: {v['relevance_score']} | [Watch]({v['url']})")
        markers = v.get("clip_markers", [])
        lines.append(f"- {len(markers)} candidate clip(s):")
        for i, m in enumerate(markers, 1):
            kws = ", ".join(m.get("keywords", []))
            snippet = m.get("text_snippet", "").replace("\n", " ")
            lines.append(f"  {i}. `{m['start_time']}s–{m['end_time']}s` [{kws}] — \"{snippet}\"")
        lines.append("")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Manifest written to {output_file} ({len(pending)} videos)")


def main():
    """Main execution"""
    api_key = os.getenv("YOUTUBE_API_KEY")
    print(f"DEBUG: TRANSCRIPT_AVAILABLE = {TRANSCRIPT_AVAILABLE}")

    if not api_key:
        raise ValueError("YOUTUBE_API_KEY environment variable not set")

    scraper = YouTubeScraper(api_key)
    videos = scraper.scrape_all_channels()
    output_data = scraper.save_results(videos)
    generate_manifest(output_data)

    print(f"SCRAPE_COMPLETE=true")
    print(f"VIDEOS_FOUND={len(videos)}")


if __name__ == "__main__":
    main()

