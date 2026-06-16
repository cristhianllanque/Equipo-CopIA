import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingUp, Users, AlertTriangle, Activity } from 'lucide-react';

const COLORS = ['#10b981', '#f59e0b', '#f97316', '#ef4444'];

export default function Analytics() {
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch('http://localhost:8000/api/analytics')
            .then(res => res.json())
            .then(data => {
                setData(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="p-8 text-center text-slate-400">Cargando analíticas...</div>;
    if (!data) return <div className="p-8 text-center text-slate-400">Error cargando analíticas</div>;

    const barData = data.ranking_conductores.map(c => ({
        name: c.nombre,
        "Total Eventos": c.total_eventos,
        "Riesgo Promedio": c.riesgo_promedio
    }));

    return (
        <div className="p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-500">
            <div className="flex items-center justify-between">
                <div>
                    <h2 className="text-3xl font-bold text-white tracking-tight">Business Intelligence</h2>
                    <p className="text-slate-400 mt-2 text-lg">Métricas de seguridad y rendimiento de la flota</p>
                </div>
            </div>

            {/* KPIs */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="glass-panel p-6 rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-800 to-slate-900 shadow-xl">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-sky-500/20 flex items-center justify-center border border-sky-500/30">
                            <Users className="w-6 h-6 text-sky-400" />
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm font-medium">Conductores Activos</p>
                            <h3 className="text-3xl font-bold text-white">{data.ranking_conductores.length}</h3>
                        </div>
                    </div>
                </div>

                <div className="glass-panel p-6 rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-800 to-slate-900 shadow-xl">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-rose-500/20 flex items-center justify-center border border-rose-500/30">
                            <AlertTriangle className="w-6 h-6 text-rose-400" />
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm font-medium">Eventos Hoy</p>
                            <h3 className="text-3xl font-bold text-white">{data.total_eventos_hoy}</h3>
                        </div>
                    </div>
                </div>

                <div className="glass-panel p-6 rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-800 to-slate-900 shadow-xl">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-amber-500/20 flex items-center justify-center border border-amber-500/30">
                            <TrendingUp className="w-6 h-6 text-amber-400" />
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm font-medium">Riesgo Promedio</p>
                            <h3 className="text-3xl font-bold text-white">
                                {(data.ranking_conductores.reduce((acc, c) => acc + c.riesgo_promedio, 0) / (data.ranking_conductores.length || 1)).toFixed(1)}
                            </h3>
                        </div>
                    </div>
                </div>
                
                <div className="glass-panel p-6 rounded-2xl border border-slate-700/50 bg-gradient-to-br from-slate-800 to-slate-900 shadow-xl">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-emerald-500/20 flex items-center justify-center border border-emerald-500/30">
                            <Activity className="w-6 h-6 text-emerald-400" />
                        </div>
                        <div>
                            <p className="text-slate-400 text-sm font-medium">Estado General</p>
                            <h3 className="text-2xl font-bold text-emerald-400 mt-1">ESTABLE</h3>
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Gráfico 1 */}
                <div className="glass-panel p-6 rounded-2xl border border-slate-700/50 bg-slate-800/30">
                    <h3 className="text-xl font-semibold text-slate-200 mb-6">Total de Eventos Críticos por Conductor</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                <XAxis dataKey="name" stroke="#94a3b8" tick={{fill: '#94a3b8'}} axisLine={false} tickLine={false} />
                                <YAxis stroke="#94a3b8" tick={{fill: '#94a3b8'}} axisLine={false} tickLine={false} />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Bar dataKey="Total Eventos" fill="#f43f5e" radius={[4, 4, 0, 0]} maxBarSize={50} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Gráfico 2 */}
                <div className="glass-panel p-6 rounded-2xl border border-slate-700/50 bg-slate-800/30">
                    <h3 className="text-xl font-semibold text-slate-200 mb-6">Nivel de Riesgo Promedio Histórico</h3>
                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={barData} layout="vertical" margin={{ top: 10, right: 30, left: 10, bottom: 0 }}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" horizontal={false} />
                                <XAxis type="number" stroke="#94a3b8" tick={{fill: '#94a3b8'}} axisLine={false} tickLine={false} />
                                <YAxis dataKey="name" type="category" stroke="#94a3b8" tick={{fill: '#94a3b8'}} axisLine={false} tickLine={false} width={100} />
                                <Tooltip 
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff', borderRadius: '8px' }}
                                />
                                <Bar dataKey="Riesgo Promedio" fill="#0ea5e9" radius={[0, 4, 4, 0]} maxBarSize={30}>
                                    {barData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry["Riesgo Promedio"] > 50 ? '#f43f5e' : entry["Riesgo Promedio"] > 30 ? '#f59e0b' : '#10b981'} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}
