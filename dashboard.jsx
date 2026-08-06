import React, { useState, useEffect } from 'react';
import { Play, CheckCircle, XCircle, Zap, Clock, Star, Settings } from 'lucide-react';

export default function UnashamedDashboard() {
  const [videos, setVideos] = useState([]);
  const [pendingClips, setPendingClips] = useState(null);
  const [settings, setSettings] = useState({});
  const [showSettings, setShowSettings] = useState(false);
  const [loading, setLoading] = useState(false);
  const [view, setView] = useState('videos'); // 'videos' or 'approval'
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [triggeringClip, setTriggeringClip] = useState(false);

  // Load settings
  useEffect(() => {
    const saved = localStorage.getItem('unashamed-settings');
    if (saved) setSettings(JSON.parse(saved));
    else setShowSettings(true);
  }, []);

  // Fetch videos from GitHub repo
  const loadVideos = async () => {
    setLoading(true);
    try {
      // This assumes videos.json is in your GitHub repo
      const response = await fetch(`${settings.repo_url}/raw/main/videos.json`);
      if (response.ok) {
        const data = await response.json();
        setVideos(data.videos || []);
      }
    } catch (err) {
      console.error('Error loading videos:', err);
    } finally {
      setLoading(false);
    }
  };

  // Load pending clips
  const loadPendingClips = async () => {
    try {
      const response = await fetch(`${settings.repo_url}/raw/main/pending-clips.json`);
      if (response.ok) {
        const data = await response.json();
        setPendingClips(data);
      }
    } catch (err) {
      console.error('Error loading pending clips:', err);
    }
  };

  useEffect(() => {
    if (settings.repo_url) {
      loadVideos();
      loadPendingClips();
      // Refresh every 30 seconds
      const interval = setInterval(() => {
        loadVideos();
        loadPendingClips();
      }, 30000);
      return () => clearInterval(interval);
    }
  }, [settings.repo_url]);

  const triggerClipping = async (video) => {
    if (!settings.github_token) {
      alert('Set GitHub token in settings');
      return;
    }

    setTriggeringClip(true);
    try {
      // Trigger GitHub Actions workflow
      const response = await fetch(
        `https://api.github.com/repos/${settings.github_repo}/actions/workflows/clipper-workflow.yml/dispatches`,
        {
          method: 'POST',
          headers: {
            'Authorization': `token ${settings.github_token}`,
            'Accept': 'application/vnd.github.v3+json',
          },
          body: JSON.stringify({
            ref: 'main',
            inputs: {
              video_url: video.url,
              clip_count: '5',
              channel_name: video.channel_name,
            }
          })
        }
      );

      if (response.ok) {
        alert('✅ Clipping workflow triggered!\nCheck Telegram for updates.');
        setSelectedVideo(null);
      } else {
        alert('Error triggering workflow');
      }
    } catch (err) {
      alert('Error: ' + err.message);
    } finally {
      setTriggeringClip(false);
    }
  };

  const approveClips = async () => {
    if (!settings.github_token) {
      alert('Set GitHub token in settings');
      return;
    }

    try {
      // Trigger posting workflow
      const response = await fetch(
        `https://api.github.com/repos/${settings.github_repo}/actions/workflows/post-workflow.yml/dispatches`,
        {
          method: 'POST',
          headers: {
            'Authorization': `token ${settings.github_token}`,
            'Accept': 'application/vnd.github.v3+json',
          },
          body: JSON.stringify({
            ref: 'main',
            inputs: {
              clips_file: 'pending-clips.json',
            }
          })
        }
      );

      if (response.ok) {
        alert('✅ Clips approved and queued for posting!');
        setPendingClips(null);
        setView('videos');
      } else {
        alert('Error approving clips');
      }
    } catch (err) {
      alert('Error: ' + err.message);
    }
  };

  const saveSettings = () => {
    localStorage.setItem('unashamed-settings', JSON.stringify(settings));
    setShowSettings(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-purple-900 to-black text-white">
      {/* Settings Modal */}
      {showSettings && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="bg-purple-900 rounded-lg p-6 max-w-sm w-full max-h-screen overflow-y-auto">
            <h2 className="text-xl font-bold mb-4">Setup UNASHAMED Agent</h2>
            
            <div className="space-y-4">
              <div>
                <label className="text-sm text-purple-300">GitHub Username/Repo</label>
                <input
                  type="text"
                  placeholder="username/unashamed-agent"
                  value={settings.github_repo || ''}
                  onChange={(e) => setSettings({...settings, github_repo: e.target.value})}
                  className="w-full px-3 py-2 rounded bg-purple-800 text-white text-sm"
                />
              </div>

              <div>
                <label className="text-sm text-purple-300">GitHub Token (Personal Access)</label>
                <input
                  type="password"
                  placeholder="ghp_..."
                  value={settings.github_token || ''}
                  onChange={(e) => setSettings({...settings, github_token: e.target.value})}
                  className="w-full px-3 py-2 rounded bg-purple-800 text-white text-sm"
                />
                <p className="text-xs text-purple-400 mt-1">
                  Get at: github.com/settings/tokens (need: repo, workflow)
                </p>
              </div>

              <div>
                <label className="text-sm text-purple-300">Repository URL</label>
                <input
                  type="text"
                  placeholder="https://github.com/username/unashamed-agent"
                  value={settings.repo_url || ''}
                  onChange={(e) => setSettings({...settings, repo_url: e.target.value})}
                  className="w-full px-3 py-2 rounded bg-purple-800 text-white text-sm"
                />
              </div>

              <div>
                <label className="text-sm text-purple-300">Telegram Chat ID</label>
                <input
                  type="text"
                  placeholder="123456789"
                  value={settings.telegram_chat_id || ''}
                  onChange={(e) => setSettings({...settings, telegram_chat_id: e.target.value})}
                  className="w-full px-3 py-2 rounded bg-purple-800 text-white text-sm"
                />
                <p className="text-xs text-purple-400 mt-1">
                  Get from @userinfobot on Telegram
                </p>
              </div>

              <button
                onClick={saveSettings}
                className="w-full bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-2 rounded font-bold hover:shadow-lg hover:shadow-pink-500/50 transition"
              >
                Save Settings
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="sticky top-0 z-40 bg-gradient-to-r from-purple-900/95 to-black/95 backdrop-blur border-b border-purple-700/30 p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-2xl font-black bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              UNASHAMED
            </h1>
            <p className="text-xs text-purple-400">Content Approval Agent</p>
          </div>
          <button
            onClick={() => setShowSettings(true)}
            className="p-2 bg-purple-800/50 rounded hover:bg-purple-700/50 transition"
          >
            <Settings size={20} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex gap-2">
          <button
            onClick={() => setView('videos')}
            className={`px-4 py-2 rounded text-sm font-bold transition ${
              view === 'videos'
                ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                : 'bg-purple-800/50 hover:bg-purple-700/50'
            }`}
          >
            📺 Videos ({videos.length})
          </button>
          <button
            onClick={() => { setView('approval'); loadPendingClips(); }}
            className={`px-4 py-2 rounded text-sm font-bold transition ${
              view === 'approval'
                ? 'bg-gradient-to-r from-purple-500 to-pink-500'
                : 'bg-purple-800/50 hover:bg-purple-700/50'
            }`}
          >
            ✂️ Clips {pendingClips ? `(${pendingClips.clips_ready_for_review})` : ''}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4 max-w-2xl mx-auto">
        {view === 'videos' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-bold">Discovered Videos</h2>
              <button
                onClick={loadVideos}
                disabled={loading}
                className="px-3 py-2 rounded text-xs font-bold bg-purple-700 hover:bg-purple-600 disabled:opacity-50"
              >
                {loading ? 'Loading...' : 'Refresh'}
              </button>
            </div>

            {videos.length === 0 ? (
              <div className="text-center py-8 text-purple-400">
                <p>No videos discovered yet.</p>
                <p className="text-xs mt-2">Next scrape: Daily at 8 AM UTC</p>
              </div>
            ) : (
              <div className="space-y-3">
                {videos.slice(0, 20).map((video, idx) => (
                  <div
                    key={video.video_id}
                    className={`rounded-lg p-4 border transition cursor-pointer ${
                      selectedVideo?.video_id === video.video_id
                        ? 'bg-purple-800/50 border-purple-500'
                        : 'bg-purple-800/20 border-purple-700/30 hover:border-purple-500/50'
                    }`}
                    onClick={() => setSelectedVideo(selectedVideo?.video_id === video.video_id ? null : video)}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <p className="font-bold text-sm line-clamp-2">{video.title}</p>
                        <p className="text-xs text-purple-300 mt-1">
                          {video.channel_name} • {new Date(video.published_at).toLocaleDateString()}
                        </p>
                      </div>
                      <div className="flex items-center gap-2 ml-2">
                        <Star size={16} className="text-yellow-400" fill="currentColor" />
                        <span className="text-sm font-bold">{video.relevance_score}</span>
                      </div>
                    </div>

                    {selectedVideo?.video_id === video.video_id && (
                      <div className="mt-4 pt-4 border-t border-purple-700/30 space-y-3">
                        <p className="text-xs text-purple-300 line-clamp-3">
                          {video.description}
                        </p>
                        <a
                          href={video.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center gap-2 text-xs text-blue-400 hover:text-blue-300"
                        >
                          <Play size={14} /> Watch on YouTube
                        </a>
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            triggerClipping(video);
                          }}
                          disabled={triggeringClip}
                          className="w-full bg-gradient-to-r from-purple-500 to-pink-500 px-4 py-2 rounded font-bold text-sm hover:shadow-lg hover:shadow-pink-500/50 transition disabled:opacity-50"
                        >
                          {triggeringClip ? 'Triggering...' : '🎬 Generate Clips'}
                        </button>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {view === 'approval' && (
          <div>
            {!pendingClips ? (
              <div className="text-center py-8 text-purple-400">
                <Clock size={32} className="mx-auto mb-2 opacity-50" />
                <p>No clips awaiting approval</p>
                <p className="text-xs mt-2">Videos will appear here after generating clips</p>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="bg-purple-800/50 rounded-lg p-4 border border-purple-700/30">
                  <h3 className="font-bold mb-2">📊 Clips Ready for Review</h3>
                  <p className="text-sm text-purple-300 mb-3">
                    Generated {pendingClips.clips_ready_for_review} clip segments from{' '}
                    <span className="font-bold">{pendingClips.channel_name}</span>
                  </p>

                  {pendingClips.segments && pendingClips.segments.length > 0 && (
                    <div className="space-y-2 max-h-96 overflow-y-auto mb-4">
                      {pendingClips.segments.map((clip, idx) => (
                        <div
                          key={idx}
                          className="bg-black/30 rounded p-3 text-xs border border-purple-700/20"
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-bold">
                              {clip.start_time.toFixed(1)}s - {clip.end_time.toFixed(1)}s
                            </span>
                            <span className="text-purple-400">{(clip.confidence * 100).toFixed(0)}% confident</span>
                          </div>
                          <p className="text-purple-300 mb-1">
                            <span className="font-bold">Hook:</span> "{clip.hook_text}"
                          </p>
                          <p className="text-purple-400">
                            <span className="font-bold">Title:</span> {clip.suggested_title}
                          </p>
                          <p className="text-purple-500 mt-1">
                            {clip.relevance}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}

                  <div className="space-y-2">
                    <button
                      onClick={approveClips}
                      className="w-full bg-gradient-to-r from-green-600 to-emerald-600 px-4 py-3 rounded font-bold hover:shadow-lg hover:shadow-green-500/50 transition flex items-center justify-center gap-2"
                    >
                      <CheckCircle size={18} /> Approve & Queue for Posting
                    </button>
                    <button
                      onClick={() => setPendingClips(null)}
                      className="w-full bg-red-900/50 hover:bg-red-800/50 px-4 py-2 rounded font-bold text-sm transition flex items-center justify-center gap-2"
                    >
                      <XCircle size={16} /> Reject & Regenerate
                    </button>
                  </div>
                </div>

                <div className="text-xs text-purple-400 text-center">
                  ✅ After approval, clips will auto-post to TikTok, YouTube Shorts & Instagram within 5 minutes
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="fixed bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 text-center text-xs text-purple-400">
        <p>Real-time notifications via Telegram • Approve clips on-the-go</p>
      </div>
    </div>
  );
}
