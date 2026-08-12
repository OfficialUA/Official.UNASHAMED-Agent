#!/usr/bin/env python3
"""
YouTube Channel Scraper for UNASHAMED
Monitors specified channels for new uploads daily
Extracts transcripts and finds keyword timestamps for fast clipping
Stores results in JSON for mobile dashboard consumption
"""

import json
import os
from datetime import datetime, timedelta
import requests
from typing import List, Dict, Tuple
from urllib.parse import urlparse, parse_qs

# Try to import youtube-transcript-api, fallback gracefully
try:
    from youtube_transcript_api import YouTubeTranscriptApi
    TRANSCRIPT_AVAILABLE = True
except ImportError:
    TRANSCRIPT_AVAILABLE = False
    print("Warning: youtube-transcript-api not installed. Install with: pip install youtube-transcript-api")

# YouTube channels to monitor
CHANNELS = [
    "UC6T34aIevA1qW_RjE_Xl28w",  # 2819 Church
    "UCX9K37bE2gGf9d3b2W4hZlw",  # Bryce Crawford
    "UC0_L2tA1kG8vX6w5T_v3c2g",  # Jonathan Conricus Official
    "UCATGPOQp9m-1iC7VvDk_kZQ",  # CBN News Online
    "UC8z3e0bTz1_g2Fw4Y1Z6q7A",  # GodLogic Apologetics
    "UCqT8oX9z1X6tZ7vY8xQ4w9g",  # Wes Huff
    "UC52LiukMgMrcH5r8Q_tZz2Q",  # InspiringPhilosophy
    "UCDqgkkA5A5J2xRz0z8v1g4w",  # CrossExamined
    "UCZsYlW72sM4n2d8S5d1K08A",  # Real Charlie Kirk
    "UCb3_G00A23sZ5w3p8qV0w6A",  # John Lennox
    "UC4vD12K0u_p-jO-0vK3q89g",  # Real Life Jack Hibbs
    "UC9w6zX3Y8w2K0r7s9L3v1aA",  # Prophecy Pros
    "UCxP9c4T2Z5l0q3k1n2w0R7A",  # Behold Israel
    "UC2x4q8Y1w0m3v6l9z7pK5A",  # Barry Stagner
    "UC7y7-21w5x6_b0z8v1K3r5g",  # Grace to You
    "UCqZ1_tXk-vK5z1w3v2z8R7w",  # Voddie Baucham
    "UCgH24J1sK0m8v5x1z7w2L9Q",  # HeartCry Missionary Society
    "UC1bJ5n2Z8w1v0x7l6K3m5A",  # Living Waters
    "UC2y7x5w0v1z8_K3m6l9p2A",  # The Porch
    "UC3v1z8l6K5m7w2x0y4p9A",  # Becoming Something
    "UCqX6l2w0v5z8m1K3l7p4A",  # Ruslan KD
    "UC7k0m5v2w1z8x6L3p9q4A",  # Bryce Crawford Podcast
    "UC5m2w1z8x6L3p9q4K7k0A",  # Live Original
    "UC6L3p9q4K7k0m5v2w1z8A",  # Isaiah Saldivar
    "UC8x6L3p9q4K7k0m5v2w1Z",  # Gabe Poirot
    "UC9q4K7k0m5v2w1z8x6L3A",  # Marcus Rogers
    "UC4K7k0m5v2w1z8x6L3p9A",  # Soulja of God
    "UC7k0m5v2w1z8x6L3p9q4B",  # Passion City Church
]

# Keywords to filter for high-relevance content
KEYWORDS = [
    "romans 1:16",
    "not ashamed",
    "gospel",
    "end times",
    "eschatology",
    "christ return",
    "second coming",
    "rapture",
    "tribulation",
    "prophecy",
    "unashamed",
]

class YouTubeScraper:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://www.googleapis.com/youtube/v3"
        self.videos = []
        self.channels_data = {}

    def get_channel_id(self, channel_name: str) -> str:
        """Get YouTube channel ID from channel name"""
        url = f"{self.base_url}/search"
        params = {
            "part": "snippet",
            "q": channel_name,
            "type": "channel",
            "key": self.api_key,
            "maxResults": 1,
        }
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            if data.get("items"):
                return data["items"][0]["snippet"]["channelId"]
        except Exception as e:
            print(f"Error getting channel ID for {channel_name}: {e}")
        return None

    def get_transcript(self, video_id: str) -> List[Dict]:
        """Extract transcript from a YouTube video"""
        if not TRANSCRIPT_AVAILABLE:
            return []
        
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            print(f"  Could not get transcript for {video_id}: {e}")
            return []

    def find_keyword_timestamps(self, transcript: List[Dict]) -> List[Dict]:
        """
        Find timestamps where keywords appear in transcript
        Returns list of segments with start/end times and matched keywords
        """
        if not transcript:
            return []
        
        segments = []
        keywords_lower = [kw.lower() for kw in KEYWORDS]
        
        for entry in transcript:
            text_lower = entry['text'].lower()
            start_time = entry['start']
            
            # Check if any keyword is in this snippet
            for i, keyword in enumerate(keywords_lower):
                if keyword in text_lower:
                    # Find the end time (next entry or +5 seconds if last)
                    end_time = start_time + 5
                    
                    segments.append({
                        "keyword": KEYWORDS[i],  # Use original capitalization
                        "start_time": round(start_time, 2),
                        "end_time": round(end_time, 2),
                        "text_snippet": entry['text'][:100],  # First 100 chars
                    })
        
        # Remove duplicates and sort by start time
        unique_segments = []
        seen = set()
        for seg in segments:
            key = (seg['start_time'], seg['keyword'])
            if key not in seen:
                unique_segments.append(seg)
                seen.add(key)
        
        unique_segments.sort(key=lambda x: x['start_time'])
        
        # Merge nearby segments (within 10 seconds)
        merged = []
        for seg in unique_segments:
            if merged and seg['start_time'] - merged[-1]['end_time'] < 10:
                # Extend the previous segment
                merged[-1]['end_time'] = max(merged[-1]['end_time'], seg['end_time'])
                merged[-1]['keywords'] = list(set(merged[-1].get('keywords', []) + [seg['keyword']]))
            else:
                seg['keywords'] = [seg['keyword']]
                del seg['keyword']  # Remove single keyword, use keywords list
                merged.append(seg)
        
        return merged

    def format_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS format"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"

    def get_recent_uploads(self, channel_id: str, channel_name: str, days: int = 365) -> List[Dict]:
        """Get recent uploads from a channel (last N days)"""
        url = f"{self.base_url}/search"
        published_after = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
        
        params = {
            "part": "snippet",
            "channelId": channel_id,
            "maxResults": 15,
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
                
                # Check if video matches keywords
                relevance_score = self._calculate_relevance(title + " " + description)
                
                if relevance_score > 0:  # Only include if matches keywords
                    video_data = {
                        "video_id": video_id,
                        "channel_name": channel_name,
                        "channel_id": channel_id,
                        "title": title,
                        "description": description,
                        "published_at": published_at,
                        "url": f"https://www.youtube.com/watch?v={video_id}",
                        "relevance_score": relevance_score,
                        "status": "pending",
                        "discovered_at": datetime.utcnow().isoformat(),
                        "clip_markers": [],  # Will populate with transcript data
                    }
                    
                    # Try to get transcript and find timestamps
                    if TRANSCRIPT_AVAILABLE:
                        print(f"    Fetching transcript for: {title[:50]}...")
                        transcript = self.get_transcript(video_id)
                        if transcript:
                            markers = self.find_keyword_timestamps(transcript)
                            if markers:
                                video_data["clip_markers"] = markers
                                print(f"    Found {len(markers)} clip points")
                    
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
        
        for channel_name in CHANNELS:
            print(f"Scraping {channel_name}...")
            channel_id = self.get_channel_id(channel_name)
            
            if channel_id:
                videos = self.get_recent_uploads(channel_id, channel_name)
                all_videos.extend(videos)
                print(f"  Found {len(videos)} relevant videos")
            else:
                print(f"  Could not find channel")
        
        # Sort by relevance and publish date
        all_videos.sort(key=lambda x: (-x["relevance_score"], -datetime.fromisoformat(x["published_at"].replace("Z", "+00:00")).timestamp()))
        
        return all_videos

    def save_results(self, videos: List[Dict], output_file: str = "videos.json"):
        """Save results to JSON file"""
        # Load existing videos to avoid duplicates
        existing = {}
        if os.path.exists(output_file):
            try:
                with open(output_file, "r") as f:
                    existing_data = json.load(f)
                    for video in existing_data.get("videos", []):
                        existing[video["video_id"]] = video
            except Exception as e:
                print(f"Error loading existing videos: {e}")
        
        # Add new videos
        for video in videos:
            if video["video_id"] not in existing:
                existing[video["video_id"]] = video
        
        # Convert back to list and sort
        videos_list = list(existing.values())
        videos_list.sort(key=lambda x: (-x["relevance_score"], -datetime.fromisoformat(x["published_at"].replace("Z", "+00:00")).timestamp()))
        
        output_data = {
            "last_updated": datetime.utcnow().isoformat(),
            "total_videos": len(videos_list),
            "videos": videos_list[:100],  # Keep last 100
        }
        
        try:
            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=2)
            print(f"Saved {len(videos_list)} videos to {output_file}")
        except Exception as e:
            print(f"Error saving results: {e}")

def main():
    """Main execution"""
    api_key = os.getenv("YOUTUBE_API_KEY")
    print(f"DEBUG: TRANSCRIPT_AVAILABLE = {TRANSCRIPT_AVAILABLE}")
    if not api_key:
        raise ValueError("YOUTUBE_API_KEY environment variable not set")
    
    scraper = YouTubeScraper(api_key)
    videos = scraper.scrape_all_channels()
    scraper.save_results(videos)
    
    # Return JSON for GitHub Actions output
    print(f"SCRAPE_COMPLETE=true")
    print(f"VIDEOS_FOUND={len(videos)}")

if __name__ == "__main__":
    main()

