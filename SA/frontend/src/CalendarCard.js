import React from 'react';
import './CalendarCard.css'; // Optional

const CalendarCard = ({ item }) => {
  return (
    <div className="calendar-card">
      <h3>{item.date} ({item.day})</h3>
      <p><strong>Theme:</strong> {item.weekly_theme}</p>
      <p><strong>Idea:</strong> {item.post_idea}</p>
      <p><strong>Content:</strong> {item.content}</p>
      <p><strong>Hashtags:</strong> {item.hashtags}</p>
      <p><strong>CTA:</strong> {item.cta}</p>
    </div>
  );
};

export default CalendarCard;
