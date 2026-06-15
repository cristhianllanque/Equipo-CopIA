import './VideoFeed.css';

const VideoFeed = ({ isOnline }) => {
  return (
    <div className="glass-panel video-container">
      <div className="video-header">
        <h2>Cámara en Vivo</h2>
        <span className="live-indicator">LIVE</span>
      </div>
      
      <div className="video-frame">
        {isOnline ? (
          <img 
            src="http://localhost:8000/video_feed" 
            alt="CopIA Live Feed" 
            className="video-stream"
          />
        ) : (
          <div className="offline-placeholder">
            <p>Esperando conexión con el vehículo...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default VideoFeed;
