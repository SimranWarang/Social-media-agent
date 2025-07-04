import React, { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import './App.css';

function App() {
  const [theme, setTheme] = useState('');
  const [calendar, setCalendar] = useState([]);
  const [loading, setLoading] = useState(false);
  const [postContent, setPostContent] = useState(null);
  const [imageUrl, setImageUrl] = useState('');
  const [imagePreview, setImagePreview] = useState('');
  const [posting, setPosting] = useState(false);
  const [scheduleTime, setScheduleTime] = useState('');
  const [darkMode, setDarkMode] = useState(() => localStorage.getItem('darkMode') === 'true');

  useEffect(() => {
    document.body.classList.toggle('dark-mode', darkMode);
    localStorage.setItem('darkMode', darkMode);
  }, [darkMode]);

  useEffect(() => {
    if (postContent) {
      document.body.classList.add('modal-open');
    } else {
      document.body.classList.remove('modal-open');
    }
    return () => document.body.classList.remove('modal-open');
  }, [postContent]);

  const extractKeywords = (text) => {
    return text
      .replace(/[^\w\s]/g, '')
      .split(' ')
      .filter(word =>
        word.length > 3 &&
        !['this', 'that', 'with', 'your', 'just', 'make', 'every', 'about', 'from', 'where', 'what', 'when', 'have', 'been', 'will'].includes(word.toLowerCase())
      )
      .slice(0, 6)
      .join(' ');
  };

  const generateCalendar = async () => {
    if (!theme.trim()) return;
    setLoading(true);
    setPostContent(null);
    try {
      const response = await axios.post('http://127.0.0.1:5000/generate', { theme });
      setCalendar(response.data);
    } catch {
      alert('⚠️ Error generating calendar. Is Flask running?');
    }
    setLoading(false);
  };

  const generatePost = async (item) => {
    setPostContent(null);
    setImagePreview('');
    setImageUrl('');
    try {
      const response = await axios.post('http://127.0.0.1:5000/generate_post', {
        idea: item.post_idea,
        theme
      });
      const content = response.data.CONTENT;
      if (content) {
        const fullContent = { ...response.data, idea: item.post_idea };
        setPostContent(fullContent);
        fetchImageFromServer(theme, content);
      } else {
        alert("Post content is empty.");
      }
    } catch {
      alert('❌ Error generating post content.');
    }
  };

  const fetchImageFromServer = async (themeText, captionText) => {
    try {
      const keywords = extractKeywords(`${themeText} ${captionText}`);
      const res = await axios.post('http://127.0.0.1:5000/search_image', { query: keywords });
      if (res.data.image_url) {
        setImageUrl(res.data.image_url);
        setImagePreview(res.data.image_url);
      } else {
        alert("❌ No image found for the keywords.");
      }
    } catch {
      alert("❌ Failed to fetch image.");
    }
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
      setImageUrl('');
    };
    reader.readAsDataURL(file);
  };

  const autoPostToInstagram = async () => {
    if (!postContent || (!imageUrl && !imagePreview)) {
      alert("❗ Please fill in all fields and generate a post.");
      return;
    }
    setPosting(true);
    try {
      const payload = {
        theme,
        idea: postContent.idea,
        image_url: imageUrl || imagePreview
      };
      const res = await axios.post('http://127.0.0.1:5000/auto_post', payload);
      alert(res.data.message || '⚠️ Post failed');
    } catch {
      alert('❌ Error posting to Instagram.');
    }
    setPosting(false);
  };

  const schedulePostToInstagram = async () => {
    if (!postContent || (!imageUrl && !imagePreview) || !scheduleTime) {
      alert("❗ Please fill in all fields including schedule time.");
      return;
    }
    setPosting(true);
    try {
      const payload = {
        theme,
        idea: postContent.idea,
        image_url: imageUrl || imagePreview,
        schedule_time: scheduleTime
      };
      const res = await axios.post('http://127.0.0.1:5000/schedule_post', payload);
      alert(res.data.message || '⚠️ Scheduling failed');
    } catch {
      alert('❌ Error scheduling the post.');
    }
    setPosting(false);
  };

  return (
    <div className="App">
      <button className="toggle-mode-btn" onClick={() => setDarkMode(!darkMode)}>
        {darkMode ? '☀️ Light Mode' : '🌙 Dark Mode'}
      </button>

      <h1>📅 AI Content Calendar Generator + 📤 Instagram Auto Post</h1>

      <div className="input-group">
        <input
          type="text"
          value={theme}
          onChange={(e) => setTheme(e.target.value)}
          placeholder="Enter a theme (e.g. Football)"
        />
        <button onClick={generateCalendar}>Generate Calendar</button>
      </div>

      {loading && <p>⏳ Generating calendar...</p>}

      {calendar.length > 0 && (
        <table className="calendar-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Date</th>
              <th>Day</th>
              <th>Theme</th>
              <th style={{ maxWidth: '300px' }}>Post Idea</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {calendar.map((item, idx) => (
              <tr key={idx}>
                <td>{idx + 1}</td>
                <td>{item.date}</td>
                <td>{item.day}</td>
                <td>{item.weekly_theme}</td>
                <td style={{
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word',
                  maxWidth: '300px'
                }}>{item.post_idea}</td>
                <td>
                  <button onClick={() => generatePost(item)}>Generate Post</button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {postContent && (
        <>
          <div className="modal-overlay" onClick={() => setPostContent(null)}></div>
          <div className="modal">
            <h3>📝 Generated Post</h3>

            <p><strong>Content:</strong></p>
            <ReactMarkdown>{postContent.CONTENT}</ReactMarkdown>

            <p><strong>Hashtags:</strong></p>
            <ReactMarkdown>{postContent.HASHTAGS}</ReactMarkdown>

            <p><strong>CTA:</strong></p>
            <ReactMarkdown>{postContent.CTA}</ReactMarkdown>

            <hr />

            {imagePreview && (
              <img
                src={imagePreview}
                alt="Preview"
                style={{
                  width: "100%",
                  maxHeight: 300,
                  objectFit: "cover",
                  borderRadius: "8px",
                  marginBottom: "10px"
                }}
              />
            )}

            <input
              type="text"
              value={imageUrl}
              onChange={(e) => {
                setImageUrl(e.target.value);
                setImagePreview(e.target.value);
              }}
              placeholder="Enter Image URL or upload below"
              style={{ width: '100%', marginBottom: '10px' }}
            />

            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              style={{ marginBottom: '10px' }}
            />

            <button
              onClick={() => fetchImageFromServer(theme, postContent.CONTENT)}
              style={{ marginBottom: '10px' }}
            >
              🔁 Fetch Again
            </button>

            <input
              type="datetime-local"
              value={scheduleTime}
              onChange={(e) => setScheduleTime(e.target.value)}
              style={{ width: '100%', marginBottom: '10px' }}
            />

            <button onClick={autoPostToInstagram} disabled={posting}>
              {posting ? "📤 Posting..." : "📤 Post to Instagram Now"}
            </button>

            <button
              onClick={schedulePostToInstagram}
              disabled={posting}
              style={{ marginLeft: '10px' }}
            >
              {posting ? "📆 Scheduling..." : "📆 Schedule Post"}
            </button>

            <br /><br />
            <button onClick={() => setPostContent(null)}>Close</button>
          </div>
        </>
      )}
    </div>
  );
}

export default App;
