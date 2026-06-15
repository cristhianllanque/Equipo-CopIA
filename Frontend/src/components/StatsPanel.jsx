import './StatsPanel.css';

const StatsPanel = ({ status, isOnline }) => {
  if (!isOnline || !status) {
    return (
      <div className="glass-panel stats-panel offline-state">
        <p>Datos no disponibles</p>
      </div>
    );
  }

  const { risk_score, alert_level, ear, mar, pitch, perclos } = status;

  return (
    <div className="glass-panel stats-panel animate-slide-in">
      <h3>Métricas del Conductor</h3>
      
      <div className="stat-card risk-card">
        <div className="stat-header">Nivel de Riesgo Total</div>
        <div className="risk-bar-container">
          <div 
            className="risk-bar-fill transition-all" 
            style={{ 
              width: `${Math.min(risk_score, 100)}%`,
              backgroundColor: risk_score > 75 ? 'var(--risk-critical)' : 
                               risk_score > 50 ? 'var(--risk-high)' : 
                               risk_score > 25 ? 'var(--risk-medium)' : 'var(--risk-low)'
            }}
          ></div>
        </div>
        <div className="risk-value">{risk_score.toFixed(1)} / 100</div>
      </div>

      <div className="stat-grid">
        <div className="stat-item">
          <span className="stat-label">EAR (Ojos)</span>
          <span className="stat-value">{ear.toFixed(3)}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">MAR (Boca)</span>
          <span className="stat-value">{mar.toFixed(3)}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Pitch (Cabeza)</span>
          <span className="stat-value">{pitch.toFixed(1)}°</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">PERCLOS</span>
          <span className="stat-value">{(perclos * 100).toFixed(1)}%</span>
        </div>
      </div>

      <div className="status-summary">
        <div className="summary-label">Estado Actual</div>
        <div className={`summary-value level-${alert_level}`}>
          {alert_level === 0 ? 'Normal / Alerta' : 
           alert_level === 1 ? 'Fatiga Leve' : 
           alert_level === 2 ? 'Fatiga Moderada' : 'Somnolencia Crítica'}
        </div>
      </div>
    </div>
  );
};

export default StatsPanel;
