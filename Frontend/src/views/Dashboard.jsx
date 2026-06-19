import React, { useState, useEffect } from 'react';
import { Users, Truck, AlertTriangle, Shield, History, MapPin, Activity, LayoutDashboard, UserPlus, BarChart2, Map as MapIcon } from 'lucide-react';
import DriverManagement from './DriverManagement';
import Analytics from './Analytics';
import RouteManagement from './RouteManagement';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix leafet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default function Dashboard() {
  const [drivers, setDrivers] = useState([]);
  const [selectedDriver, setSelectedDriver] = useState(null);
  const [status, setStatus] = useState(null);
  const [profile, setProfile] = useState(null);
  const [events, setEvents] = useState([]);
  const [currentView, setCurrentView] = useState('monitor'); // monitor, management, analytics, routes

  useEffect(() => {
    // Polling solo de lista de conductores
    const fetchDrivers = () => {
      fetch('http://localhost:8000/api/conductores')
        .then(res => res.json())
        .then(data => {
          // Mantener mock de status temporal si queremos
          setDrivers(data);
        })
        .catch(err => console.error("Error fetching drivers", err));
    };

    const fetchData = async () => {
      if (currentView !== 'monitor' || !selectedDriver) return;
      try {
        const [statusRes, profileRes, eventsRes] = await Promise.all([
          fetch(`http://localhost:8000/api/status?conductor_id=${selectedDriver}`).catch(() => null),
          fetch(`http://localhost:8000/api/profile?conductor_id=${selectedDriver}`).catch(() => null),
          fetch(`http://localhost:8000/api/eventos?conductor_id=${selectedDriver}`).catch(() => null)
        ]);

        if (statusRes) {
            const statusData = await statusRes.json();
            if (statusData.offline) {
                setStatus(null);
            } else {
                setStatus(statusData);
                // Actualizar risk en la lista localmente
                setDrivers(prev => prev.map(d => 
                    d.id === selectedDriver ? {...d, risk: statusData.log_data.risk_score, status: 'active'} : d
                ));
            }
        }
        if (profileRes && profileRes.ok) setProfile(await profileRes.json());
        if (eventsRes && eventsRes.ok) setEvents(await eventsRes.json());
      } catch (err) {
        console.error("Error fetching data", err);
      }
    };
    
    fetchData();
    // Actualizar el Dashboard web 10 veces por segundo (100ms) para ver métricas fluidas
    const interval = setInterval(fetchData, 100);
    const driversInterval = setInterval(fetchDrivers, 10000);

    return () => {
      clearInterval(interval);
      clearInterval(driversInterval);
    };
  }, [selectedDriver, currentView]);

  return (
    <div className="h-screen bg-[#0f172a] text-slate-200 font-sans flex flex-col overflow-hidden">
      {/* Header Premium */}
      <header className="h-16 border-b border-slate-700/50 bg-slate-900 flex items-center justify-between px-6 z-10 shadow-md">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-sky-500 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(14,165,233,0.5)]">
            <Truck className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-sky-400 to-indigo-400 bg-clip-text text-transparent">
              Transportes Veloz
            </h1>
            <p className="text-[10px] text-slate-400 uppercase tracking-widest font-semibold">Centro de Control Avanzado</p>
          </div>
        </div>
        
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-2 px-3 py-1 rounded-full border border-emerald-500/20 bg-emerald-500/10">
            <div className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_10px_rgba(52,211,153,0.8)]"></div>
            <span className="text-xs font-semibold text-emerald-400">CopIA Engine Activo</span>
          </div>
          <div className="flex items-center gap-3 border-l border-slate-700 pl-6">
            <div className="text-right hidden md:block">
              <p className="text-sm font-semibold text-slate-200">Operador OP-001</p>
              <p className="text-xs text-sky-400 cursor-pointer hover:underline">Cerrar Sesión</p>
            </div>
            <div className="w-10 h-10 bg-slate-700 rounded-full border border-slate-600 flex items-center justify-center">
              <Users className="w-5 h-5 text-slate-300" />
            </div>
          </div>
        </div>
      </header>

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar Principal */}
        <aside className="w-80 border-r border-slate-700/50 bg-slate-800/30 flex flex-col">
          <div className="p-4 border-b border-slate-700/50 space-y-2">
            <button 
                onClick={() => setCurrentView('monitor')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${currentView === 'monitor' ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
                <LayoutDashboard className="w-5 h-5" /> Monitoreo en Vivo
            </button>
            <button 
                onClick={() => setCurrentView('analytics')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${currentView === 'analytics' ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
                <BarChart2 className="w-5 h-5" /> Analíticas de Flota
            </button>
            <button 
                onClick={() => setCurrentView('routes')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${currentView === 'routes' ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
                <MapIcon className="w-5 h-5" /> Gestión de Rutas
            </button>
            <button 
                onClick={() => setCurrentView('management')}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${currentView === 'management' ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/20' : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200'}`}
            >
                <UserPlus className="w-5 h-5" /> Gestión de Conductores
            </button>
          </div>

          {currentView === 'monitor' && (
            <>
                <div className="p-4 border-b border-slate-700/50">
                <h2 className="text-sm font-bold text-slate-400 uppercase tracking-wider">Flota Registrada</h2>
                </div>
                <div className="flex-1 overflow-y-auto custom-scrollbar p-3 space-y-2">
                {drivers.length === 0 ? (
                    <div className="text-slate-500 text-sm text-center py-6">No hay conductores. Ve a Gestión de Flota.</div>
                ) : (
                    drivers.map(driver => (
                        <button 
                            key={driver.id}
                            onClick={() => setSelectedDriver(driver.id)}
                            className={`w-full text-left p-4 rounded-xl border transition-all duration-200 ${selectedDriver === driver.id ? 'bg-sky-500/10 border-sky-500/50 shadow-[0_0_15px_rgba(14,165,233,0.15)]' : 'bg-slate-800/50 border-slate-700/50 hover:bg-slate-800'}`}
                        >
                            <div className="flex justify-between items-start mb-2">
                            <h3 className="font-semibold text-slate-100">{driver.nombre}</h3>
                            <span className={`w-2 h-2 rounded-full mt-1.5 ${driver.status === 'active' ? 'bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.6)]' : 'bg-slate-500'}`}></span>
                            </div>
                            <div className="flex items-center gap-1.5 text-xs text-slate-400 mb-3">
                            <MapPin className="w-3.5 h-3.5" /> {driver.ruta_asignada}
                            </div>
                            <div className="w-full bg-slate-900 rounded-full h-1.5">
                            <div 
                                className={`h-1.5 rounded-full ${(driver.risk || 0) > 70 ? 'bg-rose-500' : (driver.risk || 0) > 40 ? 'bg-amber-400' : 'bg-emerald-400'}`}
                                style={{ width: `${Math.min(100, Math.max(5, driver.risk || 0))}%` }}
                            ></div>
                            </div>
                        </button>
                    ))
                )}
                </div>
            </>
          )}
        </aside>

        {/* Contenido Principal */}
        <main className="flex-1 overflow-y-auto custom-scrollbar bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-slate-800/40 via-slate-900 to-slate-900">
          
          {currentView === 'analytics' ? (
              <Analytics />
          ) : currentView === 'routes' ? (
              <RouteManagement />
          ) : currentView === 'management' ? (
              <DriverManagement />
          ) : selectedDriver ? (
            <div className="p-6 max-w-6xl mx-auto space-y-6">
              
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-2xl font-bold">Monitor de Unidad: {drivers.find(d => d.id === selectedDriver)?.nombre || 'Desconocido'}</h2>
                  <p className="text-slate-400 text-sm flex items-center gap-2 mt-1">
                    <Activity className="w-4 h-4 text-emerald-400" /> Transmisión en tiempo real (CopIA AI)
                  </p>
                </div>
                {profile?.initialized ? (
                    <span className="px-4 py-1.5 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded-full text-sm font-semibold tracking-wide">PERFIL CALIBRADO</span>
                ) : (
                    <span className="px-4 py-1.5 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-full text-sm font-semibold tracking-wide animate-pulse">CALIBRANDO IA...</span>
                )}
              </div>

              <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                
                {/* Visual y Métricas */}
                <div className="xl:col-span-2 space-y-6">
                  
                  {/* Stream de Video (Streaming Nativo MJPEG) */}
                  <div className="glass-panel rounded-2xl overflow-hidden shadow-2xl relative border border-slate-700/60 aspect-video bg-black flex items-center justify-center">
                    <div className="absolute top-4 left-4 z-10 flex gap-2">
                      <span className="bg-rose-500 text-white text-xs font-bold px-2 py-1 rounded shadow-lg flex items-center gap-1">
                        <div className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></div> SATELITAL
                      </span>
                      <span className="bg-black/60 backdrop-blur text-white text-xs px-2 py-1 rounded border border-white/10">{drivers.find(d => d.id === selectedDriver)?.vehiculo || 'Cam 1'}</span>
                    </div>
                    
                    {/* Overlay Moderno de Métricas */}
                    {status && status.log_data && (
                      <div className="absolute bottom-4 left-4 z-10 right-4 flex justify-between items-end">
                        <div className="flex flex-col gap-1.5 bg-black/40 backdrop-blur-md p-3 rounded-xl border border-white/10">
                            <span className="text-white text-xs font-mono">EAR: {status.log_data.ear?.toFixed(3)}</span>
                            <span className="text-white text-xs font-mono">MAR: {status.log_data.mar?.toFixed(3)}</span>
                            <span className="text-white text-xs font-mono">PITCH: {status.log_data.pitch?.toFixed(1)}</span>
                        </div>
                        {status.log_data.alert_level > 0 && (
                            <div className="bg-amber-500/90 text-black px-4 py-2 rounded-xl font-bold uppercase tracking-wider text-sm shadow-lg shadow-amber-500/20 animate-pulse">
                                {status.log_data.event_type} DETECTADA
                            </div>
                        )}
                      </div>
                    )}

                    <img 
                      key={selectedDriver}
                      src={`http://localhost:8000/api/video_feed?conductor_id=${selectedDriver}`} 
                      alt="Telemetría Edge" 
                      className="w-full h-full object-cover"
                      onError={(e) => { e.target.style.display='none'; e.target.parentElement.innerHTML += '<div class="text-slate-500 flex flex-col items-center"><p>Esperando señal de cámara...</p></div>' }}
                    />
                  </div>

                  {/* Tarjetas de Métricas Físicas */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                    <MetricCard title="Apertura Ocular" value={status?.log_data?.ear?.toFixed(3) || '0.000'} subtitle="EAR" highlight={status?.log_data?.ear < 0.20} />
                    <MetricCard title="Apertura Boca" value={status?.log_data?.mar?.toFixed(3) || '0.000'} subtitle="MAR" highlight={status?.log_data?.mar > 0.60} />
                    <MetricCard title="Cierre Proporcional" value={`${((status?.log_data?.perclos || 0)*100).toFixed(1)}%`} subtitle="PERCLOS" highlight={status?.log_data?.perclos > 0.15} />
                    <MetricCard title="Inclinación" value={status?.log_data?.pitch?.toFixed(1) || '0.0'} subtitle="PITCH" />
                  </div>

                  {/* GPS Map */}
                  <div className="glass-panel p-4 rounded-xl relative overflow-hidden h-64 z-0 border border-slate-700/50 shadow-lg">
                     <h3 className="text-slate-300 font-semibold mb-3 flex items-center gap-2">
                        <MapPin className="w-4 h-4 text-sky-400" /> Seguimiento Satelital
                     </h3>
                     {status?.log_data?.lat && status?.log_data?.lng ? (
                         <div className="w-full h-48 rounded-lg overflow-hidden border border-slate-700/50">
                             <MapContainer center={[status.log_data.lat, status.log_data.lng]} zoom={16} style={{ height: '100%', width: '100%', zIndex: 1 }}>
                                 {/* Dark CartoDB Map style to fit the Dashboard */}
                                 <TileLayer 
                                     url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" 
                                     attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a>'
                                 />
                                 <Marker position={[status.log_data.lat, status.log_data.lng]}>
                                    <Popup className="text-slate-800 font-semibold">
                                        {drivers.find(d => d.id === selectedDriver)?.vehiculo}
                                    </Popup>
                                 </Marker>
                             </MapContainer>
                         </div>
                     ) : (
                         <div className="w-full h-48 bg-slate-800/30 rounded-lg flex flex-col items-center justify-center border border-slate-700/50 border-dashed">
                             <MapPin className="w-8 h-8 text-slate-600 mb-2" />
                             <p className="text-slate-500 text-sm">Esperando señal GPS...</p>
                         </div>
                     )}
                  </div>
                </div>

                {/* Panel Derecho: Riesgo e Historial */}
                <div className="space-y-6 flex flex-col">
                  
                  {/* Gauge de Riesgo */}
                  <div className="glass-panel p-6 rounded-2xl relative overflow-hidden">
                    <div className={`absolute -top-20 -right-20 w-40 h-40 rounded-full blur-[80px] ${status?.log_data?.risk_score > 70 ? 'bg-rose-500/30' : status?.log_data?.risk_score > 40 ? 'bg-amber-400/20' : 'bg-emerald-500/10'}`}></div>
                    
                    <h3 className="text-slate-300 font-semibold mb-6 flex items-center gap-2">
                      <AlertTriangle className={status?.log_data?.alert_level > 0 ? "text-rose-400" : "text-slate-400"} />
                      Nivel de Alerta CopIA
                    </h3>
                    
                    <div className="flex flex-col items-center justify-center py-4">
                      <div className="relative flex items-center justify-center">
                        <svg className="w-40 h-40 transform -rotate-90">
                          <circle cx="80" cy="80" r="70" fill="transparent" stroke="#1e293b" strokeWidth="12" />
                          <circle cx="80" cy="80" r="70" fill="transparent" 
                            stroke={status?.log_data?.risk_score > 70 ? '#f43f5e' : status?.log_data?.risk_score > 40 ? '#fbbf24' : '#10b981'} 
                            strokeWidth="12" 
                            strokeDasharray="439.8" 
                            strokeDashoffset={439.8 - (439.8 * Math.min(100, status?.log_data?.risk_score || 0)) / 100}
                            className="transition-all duration-1000 ease-out"
                          />
                        </svg>
                        <div className="absolute flex flex-col items-center">
                          <span className="text-4xl font-bold">{Math.round(status?.log_data?.risk_score || 0)}</span>
                          <span className="text-xs text-slate-400 uppercase tracking-widest mt-1">Score</span>
                        </div>
                      </div>
                      
                      <div className="mt-6 w-full text-center p-3 rounded-lg bg-slate-800/50 border border-slate-700">
                        <p className="text-sm text-slate-400 mb-1">Estado Detectado</p>
                        <p className={`font-bold capitalize ${status?.log_data?.risk_score > 70 ? 'text-rose-400' : status?.log_data?.risk_score > 40 ? 'text-amber-400' : 'text-emerald-400'}`}>
                          {status?.log_data?.event_type || 'Normal'}
                        </p>
                        <p className="text-xs text-slate-500 mt-1">{status?.log_data?.explanation || 'Conducción estable'}</p>
                      </div>
                    </div>
                  </div>

                  {/* Historial de Eventos */}
                  <div className="glass-panel p-5 rounded-2xl flex-1 flex flex-col">
                    <h3 className="text-slate-300 font-semibold mb-4 flex items-center gap-2">
                      <History className="w-4 h-4" />
                      Registro de Eventos
                    </h3>
                    <div className="flex-1 overflow-y-auto custom-scrollbar pr-2 space-y-3 max-h-[350px]">
                      {events.length === 0 ? (
                        <div className="h-full flex flex-col items-center justify-center text-slate-500 py-10">
                          <Shield className="w-8 h-8 mb-2 opacity-20" />
                          <p className="text-sm">Sin eventos críticos recientes</p>
                        </div>
                      ) : (
                        events.map(ev => (
                          <div key={ev.id} className="p-3 bg-slate-800/40 rounded-lg border border-slate-700/50 flex flex-col gap-2">
                            <div className="flex justify-between items-start">
                              <p className="font-medium text-sm text-slate-200 capitalize">{ev.tipo_evento.replace('_', ' ')}</p>
                              <span className="text-[10px] text-slate-400">{new Date(ev.timestamp).toLocaleTimeString()}</span>
                            </div>
                            <div className="flex gap-2">
                              <span className={`text-[10px] px-2 py-0.5 rounded font-bold ${ev.nivel_riesgo > 70 ? 'bg-rose-500/20 text-rose-400' : 'bg-amber-400/20 text-amber-400'}`}>
                                Riesgo: {ev.nivel_riesgo}
                              </span>
                            </div>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                </div>

              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-500 p-6">
              <div className="w-24 h-24 bg-slate-800 rounded-full flex items-center justify-center mb-4 border border-slate-700">
                <Truck className="w-10 h-10 text-slate-600" />
              </div>
              <h2 className="text-xl font-medium text-slate-300 mb-2">Unidad en Descanso</h2>
              <p className="text-sm max-w-md text-center">No has seleccionado un conductor, o no hay conductores transmitiendo en este momento.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

function MetricCard({ title, value, subtitle, highlight }) {
  return (
    <div className={`glass-panel p-4 rounded-xl transition-all duration-300 ${highlight ? 'border-amber-500/50 shadow-[0_0_15px_rgba(245,158,11,0.1)]' : 'border-slate-700/50'}`}>
      <p className="text-xs text-slate-400 font-medium mb-1">{title}</p>
      <div className="flex items-end justify-between">
        <span className={`text-2xl font-bold font-mono ${highlight ? 'text-amber-400' : 'text-slate-100'}`}>{value}</span>
        <span className="text-[10px] font-bold text-slate-500 bg-slate-800 px-1.5 py-0.5 rounded uppercase tracking-wider">{subtitle}</span>
      </div>
    </div>
  );
}
