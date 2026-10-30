import React from 'react';

export default function LoadingState({ message = 'Loading electrical data...' }) {
  return (
    <div className="loading-state">
      <div className="spinner"></div>
      <p>{message}</p>
    </div>
  );
}
