import React, { useState, useEffect } from 'react';
import { Activity, AlertTriangle, User, Eye, History, Settings } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

function App() {
  const [status, setStatus] = useState(null);
  const [profile, setProfile] = useState(null);
  const [events, setEvents] = useState([]);
  
  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusRes, profileRes, eventsRes] = await Promise.all([
          fetch('http://localhost:8000/api/status'),
          fetch('http://localhost:8000/api/profile'),
          fetch('http://localhost:8000/api/eventos')
        ]);
        
        setStatus(await statusRes.json());
        setProfile(await profileRes.json());
        setEvents(await eventsRes.json());
      } catch (err) {
        console.error("Error fetching API data", err);
      }
    };
    
    fetchData();
    const interval = setInterval(fetchData, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 font-sans p-6">
      <header className="flex items-center justify-between mb-8 pb-4 border-b border-slate-700">
        <div className="flex items-center gap-3">
          <Activity className="w-8 h-8 text-emerald-400" />
          <h1 className="text-2xl font-bold tracking-tight">CopIA Dashboard</h1>
        </div>
        <div className="flex items-center gap-4">
          <span className="px-3 py-1 bg-slate-800 rounded-full text-sm font-medium border border-slate-700">
            {profile?.initialized ? 'Sistema Calibrado' : 'Calibrando...'}
          </span>
          <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center border border-slate-700">
            <User className="w-5 h-5" />
          </div>
        </div>
      </header>

      <main className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Columna Izquierda: Video y Métricas Base */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-slate-800 rounded-xl overflow-hidden border border-slate-700 shadow-lg relative">
            <div className="absolute top-4 left-4 bg-black/60 px-3 py-1 rounded backdrop-blur-md">
              <span className="text-emerald-400 font-mono font-medium flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                LIVE VIEW
              </span>
            </div>
            {/* Stream image */}
            <img 
              src="http://localhost:8000/video_feed" 
              alt="Live feed" 
              className="w-full aspect-video object-cover bg-black"
              onError={(e) => { e.target.style.display='none'; e.target.parentElement.innerHTML += '<div class="w-full aspect-video flex items-center justify-center bg-black text-slate-500">Video offline (Backend no está corriendo)</div>' }}
            />
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <MetricCard title="EAR (Ojos)" value={status?.ear?.toFixed(3) || '0.000'} icon={<Eye />} />
            <MetricCard title="MAR (Boca)" value={status?.mar?.toFixed(3) || '0.000'} />
            <MetricCard title="PERCLOS" value={`${((status?.perclos || 0)*100).toFixed(1)}%`} />
            <MetricCard title="PITCH (Cabeza)" value={status?.pitch?.toFixed(1) || '0.0'} />
          </div>
        </div>

        {/* Columna Derecha: Alertas y Estado */}
        <div className="space-y-6">
          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <AlertTriangle className={status?.alert_level > 0 ? "text-rose-500" : "text-slate-400"} />
              Estado de Alerta
            </h2>
            <div className="mb-6">
              <div className="flex justify-between items-end mb-2">
                <span className="text-3xl font-bold">{status?.risk_score || 0}</span>
                <span className="text-slate-400 text-sm">/ 100 Riesgo</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all duration-500 ${status?.risk_score > 70 ? 'bg-rose-500' : status?.risk_score > 40 ? 'bg-amber-400' : 'bg-emerald-400'}`}
                  style={{ width: `${Math.min(100, status?.risk_score || 0)}%` }}
                ></div>
              </div>
            </div>
            <div className="p-4 bg-slate-900 rounded-lg border border-slate-700">
              <p className="text-sm font-medium text-slate-300">Último Evento</p>
              <p className="text-lg font-semibold mt-1 capitalize">{status?.event_type || 'Normal'}</p>
              <p className="text-sm text-slate-400 mt-1">{status?.explanation || 'Operación regular'}</p>
            </div>
          </div>

          <div className="bg-slate-800 rounded-xl p-6 border border-slate-700 shadow-lg flex-1">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <History className="w-5 h-5 text-slate-400" />
              Historial de Eventos
            </h2>
            <div className="space-y-3 max-h-[300px] overflow-y-auto pr-2 custom-scrollbar">
              {events.length === 0 && <p className="text-slate-500 text-sm">No hay eventos registrados.</p>}
              {events.map(ev => (
                <div key={ev.id} className="p-3 bg-slate-900 rounded-lg border border-slate-700 flex justify-between items-center">
                  <div>
                    <p className="font-medium capitalize">{ev.tipo_evento}</p>
                    <p className="text-xs text-slate-400">{new Date(ev.timestamp).toLocaleTimeString()}</p>
                  </div>
                  <div className={`px-2 py-1 rounded text-xs font-bold ${ev.nivel_riesgo > 70 ? 'bg-rose-500/20 text-rose-400' : ev.nivel_riesgo > 40 ? 'bg-amber-400/20 text-amber-400' : 'bg-slate-700 text-slate-300'}`}>
                    Riesgo {ev.nivel_riesgo}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

function MetricCard({ title, value, icon }) {
  return (
    <div className="bg-slate-800 p-4 rounded-xl border border-slate-700 shadow-sm flex flex-col justify-between h-28">
      <div className="text-slate-400 text-sm font-medium flex items-center gap-2">
        {icon && <span className="text-slate-500 w-4 h-4">{icon}</span>}
        {title}
      </div>
      <div className="text-2xl font-bold font-mono text-emerald-50">{value}</div>
    </div>
  );
}

export default App;
