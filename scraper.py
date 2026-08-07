#!/usr/bin/env python3
"""
YouTube Channel Scraper for UNASHAMED
Monitors specified channels for new uploads daily
Stores results in JSON for mobile dashboard consumption
"""

import json
import os
from datetime import datetime, timedelta
import requests
from typing import List, Dict

# YouTube channels to monitor
CHANNELS = [
    "2819Church",
    "BryceCrawford",
    "JonathanConricusOfficial",
    "CBNnewsonline",
    "GodLogicApologetics",
    "WesHuff",
    "InspiringPhilosophy",
    "CrossExamined",
    "RealCharlieKirk",
    "JohnLennox",
    "RealLifeJackHibbs",
    "ProphecyPros",
    "BeholdIsrael",
    "BarryStagner",
    "GraceToYou",
    "VoddieBaucham",
    "HeartCryMission",
    "LivingWaters",
    "ThePorch",
    "BecomingSomething",
    "RuslanKD",
    "BryceCrawfordPodcast",
    "LiveOriginal",
    "IsaiahSaldivar",
    "GabePoirot",
    "MarcusRogers",
    "Souljaofgod",
    "PassionCityChurch",
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

    def get_recent_uploads(self, channel_id: str, channel_name: str, days: int = 7) -> List[Dict]:
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
                    videos.append({
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
                    })
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
