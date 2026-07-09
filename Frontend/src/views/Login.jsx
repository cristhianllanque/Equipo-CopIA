import React, { useState } from 'react';
import { ShieldCheck, ArrowRight, Activity, Eye, Zap, Truck } from 'lucide-react';

export default function Login({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setErrorMessage('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/operador/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (response.ok) {
        onLogin();
      } else {
        setErrorMessage(data.detail || 'Credenciales incorrectas');
        setLoading(false);
      }
    } catch (error) {
      setErrorMessage('Error de conexión con el servidor central.');
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative overflow-hidden bg-slate-900 flex">
      {/* Video Background */}
      <video
        autoPlay
        loop
        muted
        playsInline
        className="absolute inset-0 w-full h-full object-cover z-0 opacity-80"
      >
        <source src="/videoCopAI.mp4" type="video/mp4" />
      </video>

      {/* Capa de oscurecimiento súper ligera para que el video destaque pero el texto sea legible */}
      <div className="absolute inset-0 bg-slate-900/40 backdrop-blur-[1px] z-0"></div>

      {/* Elementos decorativos de fondo */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-sky-500/20 rounded-full blur-[100px] z-0 pointer-events-none"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-emerald-500/10 rounded-full blur-[100px] z-0 pointer-events-none"></div>

      {/* Header Fijo con Logo */}
      <div className="absolute top-0 left-0 p-8 z-20 flex items-center">
        <img 
          src="/logoCopAI.png" 
          alt="CopAI Logo" 
          className="w-40 h-auto rounded-3xl border border-sky-400/40 shadow-[0_0_30px_rgba(14,165,233,0.4)] opacity-90 hover:opacity-100 transition-all duration-500 hover:shadow-[0_0_50px_rgba(14,165,233,0.6)]" 
        />
      </div>

      {/* Contenedor Principal Split (Izquierda Marketing / Derecha Login) */}
      <div className="relative z-10 flex w-full h-screen">

        {/* Lado Izquierdo: Textos de Marketing */}
        <div className="hidden lg:flex flex-1 flex-col justify-center px-16 xl:px-24">
          <div className="max-w-2xl">
            <h2 className="text-5xl xl:text-6xl font-bold text-white mb-6 leading-tight drop-shadow-lg">
              El Futuro de la <span className="text-sky-400">Seguridad Vial</span>
            </h2>
            <p className="text-xl text-slate-200 mb-10 leading-relaxed font-light drop-shadow-md">
              Prevención proactiva de accidentes, monitoreo de fatiga en tiempo real y telemetría avanzada para proteger tus activos más valiosos en cada ruta.
            </p>

            <div className="space-y-6">
              <div className="flex items-center gap-4 bg-slate-900/60 border border-slate-700/50 p-4 rounded-xl backdrop-blur-md transition-transform hover:scale-105 cursor-default shadow-lg">
                <div className="w-12 h-12 rounded-full bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
                  <Eye className="w-6 h-6 text-emerald-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Detección de Microsueños</h3>
                  <p className="text-sm text-slate-300">Algoritmos Edge AI que alertan instantáneamente antes del peligro.</p>
                </div>
              </div>

              <div className="flex items-center gap-4 bg-slate-900/60 border border-slate-700/50 p-4 rounded-xl backdrop-blur-md transition-transform hover:scale-105 cursor-default shadow-lg">
                <div className="w-12 h-12 rounded-full bg-amber-500/20 flex items-center justify-center border border-amber-500/30">
                  <Activity className="w-6 h-6 text-amber-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">Análisis de Distracción</h3>
                  <p className="text-sm text-slate-300">Uso de celular, fumar o desvío de mirada reportado a la central.</p>
                </div>
              </div>

              <div className="flex items-center gap-4 bg-slate-900/60 border border-slate-700/50 p-4 rounded-xl backdrop-blur-md transition-transform hover:scale-105 cursor-default shadow-lg">
                <div className="w-12 h-12 rounded-full bg-rose-500/20 flex items-center justify-center border border-rose-500/30">
                  <Zap className="w-6 h-6 text-rose-400" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-white">S.O.S Anti-Robos 4G</h3>
                  <p className="text-sm text-slate-300">Botón de pánico oculto con sincronización cloud y sirenas inmediatas.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Lado Derecho: Panel de Login */}
        <div className="w-full lg:w-[500px] xl:w-[600px] flex items-center justify-center p-8 bg-slate-900/40 backdrop-blur-xl border-l border-white/10 shadow-[-20px_0_50px_rgba(0,0,0,0.5)]">
          <div className="w-full max-w-sm">
            <div className="text-center mb-10">
              <h2 className="text-3xl font-bold text-white tracking-tight mb-2 drop-shadow-md">Acceso a Central</h2>
              <p className="text-slate-300 text-sm">Ingresa tus credenciales de operador para iniciar el monitoreo de la flota.</p>
            </div>

            <form onSubmit={handleLogin} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-2">ID Operador</label>
                <input
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full bg-slate-800/60 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-all shadow-inner"
                  placeholder="OP-001"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-200 mb-2">Contraseña</label>
                <input
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full bg-slate-800/60 border border-slate-600 rounded-lg px-4 py-3 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent transition-all shadow-inner"
                  placeholder="••••••••"
                />
              </div>

              {errorMessage && (
                <div className="bg-rose-500/20 border border-rose-500/50 text-rose-300 p-3 rounded-lg text-sm text-center font-medium shadow-inner animate-pulse">
                  {errorMessage}
                </div>
              )}

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-sky-500 hover:bg-sky-400 text-white font-medium py-3 px-4 rounded-lg flex items-center justify-center gap-2 transition-all shadow-[0_0_15px_rgba(14,165,233,0.4)] hover:shadow-[0_0_25px_rgba(14,165,233,0.6)] disabled:opacity-70 disabled:cursor-not-allowed mt-4"
              >
                {loading ? (
                  <div className="w-6 h-6 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                ) : (
                  <>
                    Iniciar Sesión <ArrowRight className="w-4 h-4" />
                  </>
                )}
              </button>
            </form>

            <div className="mt-12 flex items-center justify-center gap-2 text-slate-400 text-xs">
              <ShieldCheck className="w-4 h-4 text-emerald-400" />
              <span>Conexión cifrada y segura • CopIA AI Engine</span>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
