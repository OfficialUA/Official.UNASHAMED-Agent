import React, { useState, useEffect } from 'react';
import { Download, Copy, CheckCircle, Copy as CopyIcon } from 'lucide-react';

export default function DownloadManager() {
  const [clipsData, setClipsData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState({});
  const [settings, setSettings] = useState({});

  useEffect(() => {
    const saved = localStorage.getItem('unashamed-settings');
    if (saved) setSettings(JSON.parse(saved));
    loadClips();
  }, []);

  const loadClips = async () => {
    setLoading(true);
    try {
      const saved = localStorage.getItem('unashamed-settings');
      if (saved) {
        const s = JSON.parse(saved);
        const response = await fetch(`${s.repo_url}/raw/main/pending-clips.json`);
        if (response.ok) {
          const data = await response.json();
          setClipsData(data);
        }
      }
    } catch (err) {
      console.error('Error loading clips:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text, key) => {
    navigator.clipboard.writeText(text);
    setCopied({ ...copied, [key]: true });
    setTimeout(() => setCopied({ ...copied, [key]: false }), 2000);
  };

  const downloadZip = async () => {
    if (!clipsData) return;

    // Note: This is a simplified version. In production, you'd use a library like JSZip
    // For now, we'll create organized text files for download

    const platformFolders = {
      tiktok: [],
      youtube: [],
      instagram: []
    };

    clipsData.clips.forEach((clip, idx) => {
      const meta = clip.metadata;

      // TikTok data
      if (meta.tiktok) {
        platformFolders.tiktok.push({
          filename: `Clip_${idx + 1}_TikTok_Captions.txt`,
          content: `CLIP #${idx + 1}: ${meta.tiktok.title}\n\n${meta.tiktok.captions.map((c, i) => `OPTION ${i + 1}:\n${c}`).join('\n\n')}\n\nHASTAGS:\n${meta.tiktok.hashtags.join(' ')}`
        });
      }

      // YouTube data
      if (meta.youtube) {
        platformFolders.youtube.push({
          filename: `Clip_${idx + 1}_YouTube_Shorts.txt`,
          content: `TITLE: ${meta.youtube.title}\n\nCAPTION:\n${meta.youtube.caption}\n\nHASTAGS:\n${meta.youtube.hashtags.join(' ')}`
        });
      }

      // Instagram data
      if (meta.instagram) {
        platformFolders.instagram.push({
          filename: `Clip_${idx + 1}_Instagram.txt`,
          content: `TITLE: ${meta.instagram.title}\n\nCAPTION:\n${meta.instagram.caption}\n\nHASTAGS:\n${meta.instagram.hashtags.join(' ')}`
        });
      }
    });

    // Create downloadable text files (in production, use JSZip for actual ZIP)
    Object.entries(platformFolders).forEach(([platform, files]) => {
      files.forEach(file => {
        const element = document.createElement('a');
        const fileBlob = new Blob([file.content], { type: 'text/plain' });
        element.href = URL.createObjectURL(fileBlob);
        element.download = `${platform}/${file.filename}`;
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
      });
    });

    alert('✅ All files downloaded! Organize them locally or use the platform-specific sections below.');
  };

  if (!clipsData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white p-4">
        <div className="text-center py-12">
          <p className="text-purple-300">No clips ready yet. Generate clips first.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-gradient-to-r from-purple-900/95 to-black/95 backdrop-blur border-b border-purple-700/30 p-4">
        <h1 className="text-2xl font-black bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent mb-2">
          📥 Download Manager
        </h1>
        <p className="text-sm text-purple-300 mb-4">
          {clipsData.clips_ready_for_review} clips ready for posting
        </p>
        <button
          onClick={downloadZip}
          className="w-full bg-gradient-to-r from-green-600 to-emerald-600 px-4 py-3 rounded font-bold hover:shadow-lg hover:shadow-green-500/50 transition flex items-center justify-center gap-2"
        >
          <Download size={20} /> Download All Metadata (Organized by Platform)
        </button>
      </div>

      {/* Content */}
      <div className="p-4 max-w-4xl mx-auto space-y-8">
        {/* TikTok Section */}
        <section>
          <h2 className="text-xl font-bold text-pink-400 mb-4 pb-2 border-b border-pink-700/30">
            🎵 TikTok (30-60 seconds) — Auto-Post Ready
          </h2>
          <div className="space-y-4">
            {clipsData.clips.map((clip, idx) => {
              const meta = clip.metadata?.tiktok;
              if (!meta) return null;

              return (
                <div
                  key={`tiktok-${idx}`}
                  className="bg-purple-800/30 border border-purple-700/30 rounded-lg p-4"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-xs text-purple-400 mb-1">CLIP #{idx + 1}</p>
                      <h3 className="font-bold text-pink-300">{meta.title}</h3>
                    </div>
                    <span className="text-xs px-2 py-1 rounded bg-pink-900/50 text-pink-200">
                      {clip.start_time.toFixed(1)}s - {clip.end_time.toFixed(1)}s
                    </span>
                  </div>

                  {/* 3 Caption Variations */}
                  <div className="space-y-3 mb-4">
                    {meta.captions.map((caption, capIdx) => (
                      <div key={capIdx} className="bg-black/30 rounded p-3">
                        <p className="text-xs text-purple-400 mb-2 font-bold">
                          OPTION {capIdx + 1}
                          {capIdx === 0 && ' (Hook Aggressive)'}
                          {capIdx === 1 && ' (Question Based)'}
                          {capIdx === 2 && ' (Mixed)'}
                        </p>
                        <p className="text-sm text-white mb-3">{caption}</p>
                        <button
                          onClick={() => copyToClipboard(caption, `tiktok-${idx}-${capIdx}`)}
                          className={`text-xs px-2 py-1 rounded font-bold transition ${
                            copied[`tiktok-${idx}-${capIdx}`]
                              ? 'bg-green-600 text-green-100'
                              : 'bg-purple-700 hover:bg-purple-600 text-purple-100'
                          }`}
                        >
                          {copied[`tiktok-${idx}-${capIdx}`] ? '✓ Copied' : 'Copy Caption'}
                        </button>
                      </div>
                    ))}
                  </div>

                  {/* Hashtags */}
                  <div className="bg-black/30 rounded p-3">
                    <p className="text-xs text-purple-400 mb-2 font-bold">HASHTAGS</p>
                    <button
                      onClick={() => copyToClipboard(meta.hashtags.join(' '), `tiktok-tags-${idx}`)}
                      className={`text-xs px-3 py-2 rounded font-bold w-full transition ${
                        copied[`tiktok-tags-${idx}`]
                          ? 'bg-green-600 text-green-100'
                          : 'bg-purple-700 hover:bg-purple-600 text-purple-100'
                      }`}
                    >
                      {copied[`tiktok-tags-${idx}`] ? '✓ Copied' : 'Copy Hashtags'}
                    </button>
                    <p className="text-xs text-purple-300 mt-2 break-words">
                      {meta.hashtags.join(' ')}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* YouTube Shorts Section */}
        <section>
          <h2 className="text-xl font-bold text-blue-400 mb-4 pb-2 border-b border-blue-700/30">
            📺 YouTube Shorts (Manual Upload)
          </h2>
          <div className="space-y-4">
            {clipsData.clips.map((clip, idx) => {
              const meta = clip.metadata?.youtube;
              if (!meta) return null;

              return (
                <div key={`youtube-${idx}`} className="bg-purple-800/30 border border-purple-700/30 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-xs text-purple-400 mb-1">CLIP #{idx + 1}</p>
                      <h3 className="font-bold text-blue-300">{meta.title}</h3>
                    </div>
                    <span className="text-xs px-2 py-1 rounded bg-blue-900/50 text-blue-200">
                      {clip.start_time.toFixed(1)}s - {clip.end_time.toFixed(1)}s
                    </span>
                  </div>

                  {/* Caption */}
                  <div className="bg-black/30 rounded p-3 mb-4">
                    <p className="text-xs text-purple-400 mb-2 font-bold">CAPTION</p>
                    <p className="text-sm text-white mb-3">{meta.caption}</p>
                    <button
                      onClick={() => copyToClipboard(meta.caption, `youtube-${idx}`)}
                      className={`text-xs px-2 py-1 rounded font-bold transition ${
                        copied[`youtube-${idx}`]
                          ? 'bg-green-600 text-green-100'
                          : 'bg-purple-700 hover:bg-purple-600 text-purple-100'
                      }`}
                    >
                      {copied[`youtube-${idx}`] ? '✓ Copied' : 'Copy Caption'}
                    </button>
                  </div>

                  {/* Hashtags */}
                  <div className="bg-black/30 rounded p-3">
                    <p className="text-xs text-purple-400 mb-2 font-bold">HASHTAGS</p>
                    <button
                      onClick={() => copyToClipboard(meta.hashtags.join(' '), `youtube-tags-${idx}`)}
                      className={`text-xs px-3 py-2 rounded font-bold w-full transition ${
                        copied[`youtube-tags-${idx}`]
                          ? 'bg-green-600 text-green-100'
                          : 'bg-purple-700 hover:bg-purple-600 text-purple-100'
                      }`}
                    >
                      {copied[`youtube-tags-${idx}`] ? '✓ Copied' : 'Copy Hashtags'}
                    </button>
                    <p className="text-xs text-purple-300 mt-2 break-words">
                      {meta.hashtags.join(' ')}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>

        {/* Instagram Section */}
        <section className="pb-12">
          <h2 className="text-xl font-bold text-purple-400 mb-4 pb-2 border-b border-purple-700/30">
            📱 Instagram Reels (Manual Upload)
          </h2>
          <div className="space-y-4">
            {clipsData.clips.map((clip, idx) => {
              const meta = clip.metadata?.instagram;
              if (!meta) return null;

              return (
                <div key={`instagram-${idx}`} className="bg-purple-800/30 border border-purple-700/30 rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <p className="text-xs text-purple-400 mb-1">CLIP #{idx + 1}</p>
                      <h3 className="font-bold text-purple-300">{meta.title}</h3>
                    </div>
                    <span className="text-xs px-2 py-1 rounded bg-purple-900/50 text-purple-200">
                      {clip.start_time.toFixed(1)}s - {clip.end_time.toFixed(1)}s
                    </span>
                  </div>

                  {/* Caption */}
                  <div className="bg-black/30 rounded p-3 mb-4">
                    <p className="text-xs text-purple-400 mb-2 font-bold">CAPTION</p>
                    <p className="text-sm text-white mb-3">{meta.caption}</p>
                    <button
                      onClick={() => copyToClipboard(meta.caption, `instagram-${idx}`)}
                      className={`text-xs px-2 py-1 rounded font-bold transition ${
                        copied[`instagram-${idx}`]
                          ? 'bg-green-600 text-green-100'
                          : 'bg-purple-700 hover:bg-purple-600 text-purple-100'
                      }`}
                    >
                      {copied[`instagram-${idx}`] ? '✓ Copied' : 'Copy Caption'}
                    </button>
                  </div>

                  {/* Hashtags */}
                  <div className="bg-black/30 rounded p-3">
                    <p className="text-xs text-purple-400 mb-2 font-bold">HASHTAGS</p>
                    <button
                      onClick={() => copyToClipboard(meta.hashtags.join(' '), `instagram-tags-${idx}`)}
                      className={`text-xs px-3 py-2 rounded font-bold w-full transition ${
                        copied[`instagram-tags-${idx}`]
                          ? 'bg-green-600 text-green-100'
                          : 'bg-purple-700 hover:bg-purple-600 text-purple-100'
                      }`}
                    >
                      {copied[`instagram-tags-${idx}`] ? '✓ Copied' : 'Copy Hashtags'}
                    </button>
                    <p className="text-xs text-purple-300 mt-2 break-words">
                      {meta.hashtags.join(' ')}
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </section>
      </div>

      {/* Footer Info */}
      <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 to-transparent p-4 text-center text-xs text-purple-400">
        <p>
          ✅ TikTok auto-posts after approval | 📺 YouTube & Instagram: Copy captions → Manual upload in app
        </p>
      </div>
    </div>
  );
}
