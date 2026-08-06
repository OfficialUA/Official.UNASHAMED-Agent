#!/usr/bin/env python3
"""
Generate platform-specific captions, titles, and hashtags for clips
Uses Claude to create optimized content for TikTok, YouTube Shorts, and Instagram
"""

import json
import os
from anthropic import Anthropic

client = Anthropic()

def generate_platform_captions(clip_data: dict) -> dict:
    """
    Generate platform-specific metadata for a single clip
    Returns: {
        'tiktok': {'captions': [3 variations], 'hashtags': [...], 'title': '...'},
        'youtube': {'caption': '...', 'hashtags': [...], 'title': '...'},
        'instagram': {'caption': '...', 'hashtags': [...], 'title': '...'}
    }
    """
    
    hook_text = clip_data.get('hook_text', '')
    suggested_title = clip_data.get('suggested_title', '')
    relevance = clip_data.get('relevance', '')
    
    prompt = f"""You are a social media content strategist for a Christian gospel channel (UNASHAMED) focused on Romans 1:16 and End Times eschatology.

CLIP DETAILS:
- Hook: {hook_text}
- Title: {suggested_title}
- Theme: {relevance}

TASK: Generate platform-specific captions, titles, and hashtags for this 30-90 second clip.

REQUIREMENTS:
1. TikTok: Generate 3 caption variations (mix of hook-aggressive and question-based). Each under 150 chars. Include 5-8 relevant hashtags.
2. YouTube Shorts: Adjust the hook slightly longer/more educational angle. Same hashtags but YouTube-optimized.
3. Instagram: Story-focused, engagement angle. Same content angle but Instagram tone. Different hashtag mix.

All should reference Romans 1:16, gospel conviction, or End Times context where relevant.

RETURN ONLY VALID JSON (no other text):
{{
  "tiktok": {{
    "title": "Short punchy title for TikTok",
    "captions": [
      "CAPTION 1 - Hook aggressive style...",
      "CAPTION 2 - Question based style...",
      "CAPTION 3 - Mix of both..."
    ],
    "hashtags": ["#unashamed", "#romans116", "#gospel", "#endtimes", "#prophecy", "#truth", "#jesus"]
  }},
  "youtube": {{
    "title": "Slightly longer title for YouTube Shorts",
    "caption": "Caption with slightly more context...",
    "hashtags": ["#YoutubeShorts", "#Gospel", "#Romans116", "#Unashamed", "#EndTimes", "#Scripture"]
  }},
  "instagram": {{
    "title": "Story-focused title",
    "caption": "Engagement-focused caption with call-to-action...",
    "hashtags": ["#unashamed", "#gospel", "#romans116", "#christianfaith", "#bibletalk", "#endtimes", "#faith", "#jesus"]
  }}
}}

Generate creative, conversion-focused content that drives engagement and shares."""

    try:
        message = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text
        
        # Parse JSON from response
        import re
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            metadata = json.loads(json_match.group())
            return metadata
        else:
            print("Error parsing response")
            return None
    
    except Exception as e:
        print(f"Error generating metadata: {e}")
        return None

def process_all_clips(segments_file: str = "segments.json") -> dict:
    """
    Process all clips and generate platform-specific metadata
    """
    
    if not os.path.exists(segments_file):
        print(f"Error: {segments_file} not found")
        return {}
    
    with open(segments_file, 'r') as f:
        segments_data = json.load(f)
    
    clips = segments_data.get('clips', [])
    all_metadata = {
        'clips': []
    }
    
    for idx, clip in enumerate(clips):
        print(f"Generating metadata for clip {idx + 1}/{len(clips)}...")
        
        metadata = generate_platform_captions(clip)
        
        if metadata:
            clip_with_metadata = {
                **clip,
                'metadata': metadata,
                'clip_index': idx + 1
            }
            all_metadata['clips'].append(clip_with_metadata)
    
    # Save to file
    with open('clips-with-metadata.json', 'w') as f:
        json.dump(all_metadata, f, indent=2)
    
    print(f"Generated metadata for {len(all_metadata['clips'])} clips")
    return all_metadata

if __name__ == "__main__":
    process_all_clips()
