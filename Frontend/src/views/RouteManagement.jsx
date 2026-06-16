import React, { useState, useEffect } from 'react';
import { Map, Plus, Trash2, MapPin } from 'lucide-react';

export default function RouteManagement() {
    const [rutas, setRutas] = useState([]);
    const [origen, setOrigen] = useState('');
    const [destino, setDestino] = useState('');
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchRutas();
    }, []);

    const fetchRutas = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/rutas');
            const data = await res.json();
            setRutas(data);
        } catch (error) {
            console.error(error);
        }
    };

    const handleCrearRuta = async (e) => {
        e.preventDefault();
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/api/rutas', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ origen, destino })
            });
            if (res.ok) {
                setOrigen('');
                setDestino('');
                fetchRutas();
            }
        } catch (error) {
            console.error(error);
        }
        setLoading(false);
    };

    return (
        <div className="max-w-4xl mx-auto p-6 animate-in fade-in duration-300">
            <div className="flex items-center gap-3 mb-8">
                <div className="w-12 h-12 bg-indigo-500/20 rounded-xl flex items-center justify-center border border-indigo-500/30">
                    <Map className="w-6 h-6 text-indigo-400" />
                </div>
                <div>
                    <h2 className="text-2xl font-bold text-white">Gestión de Rutas Oficiales</h2>
                    <p className="text-slate-400 text-sm">Administra los destinos disponibles para los conductores.</p>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                <div className="md:col-span-1">
                    <div className="glass-panel p-6 rounded-2xl border border-slate-700/50 bg-slate-800/50">
                        <h3 className="text-lg font-semibold text-white mb-4">Nueva Ruta</h3>
                        <form onSubmit={handleCrearRuta} className="space-y-4">
                            <div>
                                <label className="block text-xs font-medium text-slate-400 mb-1">Origen</label>
                                <input
                                    type="text"
                                    value={origen}
                                    onChange={e => setOrigen(e.target.value)}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
                                    placeholder="Ej: Lima"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-xs font-medium text-slate-400 mb-1">Destino</label>
                                <input
                                    type="text"
                                    value={destino}
                                    onChange={e => setDestino(e.target.value)}
                                    className="w-full bg-slate-900 border border-slate-700 rounded-lg px-4 py-2 text-white focus:outline-none focus:border-indigo-500"
                                    placeholder="Ej: Arequipa"
                                    required
                                />
                            </div>
                            <button
                                type="submit"
                                disabled={loading}
                                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-2 rounded-lg flex items-center justify-center gap-2 transition-colors disabled:opacity-50"
                            >
                                <Plus className="w-4 h-4" /> {loading ? 'Guardando...' : 'Añadir Ruta'}
                            </button>
                        </form>
                    </div>
                </div>

                <div className="md:col-span-2">
                    <div className="glass-panel rounded-2xl border border-slate-700/50 bg-slate-800/30 overflow-hidden">
                        <div className="p-4 border-b border-slate-700/50 bg-slate-800/50">
                            <h3 className="font-semibold text-slate-200">Rutas Disponibles</h3>
                        </div>
                        <div className="p-4">
                            {rutas.length === 0 ? (
                                <div className="text-center py-8 text-slate-500">
                                    No hay rutas registradas. Crea una a la izquierda.
                                </div>
                            ) : (
                                <div className="space-y-3">
                                    {rutas.map(ruta => (
                                        <div key={ruta.id} className="flex items-center justify-between p-4 bg-slate-900/50 rounded-xl border border-slate-700/50 hover:border-slate-600 transition-colors">
                                            <div className="flex items-center gap-4">
                                                <div className="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center border border-slate-700">
                                                    <MapPin className="w-4 h-4 text-slate-400" />
                                                </div>
                                                <div>
                                                    <p className="text-slate-200 font-medium">{ruta.origen} <span className="text-slate-500 mx-2">→</span> {ruta.destino}</p>
                                                    <span className="text-xs text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full border border-emerald-500/20">{ruta.estado}</span>
                                                </div>
                                            </div>
                                            <button className="text-slate-500 hover:text-rose-400 transition-colors p-2">
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
