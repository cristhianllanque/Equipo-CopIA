import React, { useState, useEffect } from 'react';
import { UserPlus, Truck, Map, Shield, CheckCircle } from 'lucide-react';

export default function DriverManagement() {
  const [drivers, setDrivers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [formData, setFormData] = useState({
    nombre: '',
    username: '',
    password: '',
    vehiculo: '',
    foto_url: '',
    vehiculo_foto_url: ''
  });

  const fetchDrivers = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/conductores');
      const data = await res.json();
      setDrivers(data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchDrivers();
  }, []);

  const handleChange = (e) => {
    setFormData({...formData, [e.target.name]: e.target.value});
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/conductores', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (res.ok) {
        setSuccess(true);
        setFormData({ nombre: '', username: '', password: '', vehiculo: '', foto_url: '', vehiculo_foto_url: '' });
        fetchDrivers();
        setTimeout(() => setSuccess(false), 3000);
      }
    } catch (e) {
      console.error(e);
    }
    setLoading(false);
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-2xl font-bold text-white">Gestión de Flota</h2>
          <p className="text-slate-400 mt-1">Registra nuevos conductores y asigna vehículos.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Formulario de Registro */}
        <div className="lg:col-span-1">
          <div className="glass-panel p-6 rounded-2xl border border-slate-700/50">
            <h3 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
              <UserPlus className="w-5 h-5 text-sky-400" /> Nuevo Conductor
            </h3>
            
            {success && (
              <div className="mb-6 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 p-3 rounded-lg flex items-center gap-2 text-sm">
                <CheckCircle className="w-4 h-4" /> Conductor registrado con éxito.
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Nombre Completo</label>
                <input type="text" name="nombre" value={formData.nombre} onChange={handleChange} required
                  className="w-full bg-slate-800/50 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-sky-500" placeholder="Ej. Juan Pérez" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Usuario (Para la Raspberry Pi)</label>
                <input type="text" name="username" value={formData.username} onChange={handleChange} required
                  className="w-full bg-slate-800/50 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-sky-500" placeholder="Ej. jperez" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Contraseña</label>
                <input type="password" name="password" value={formData.password} onChange={handleChange} required
                  className="w-full bg-slate-800/50 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-sky-500" placeholder="••••••••" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">Vehículo Asignado</label>
                <input type="text" name="vehiculo" value={formData.vehiculo} onChange={handleChange} required
                  className="w-full bg-slate-800/50 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-sky-500" placeholder="Volvo FH16 - A1B-234" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">URL Foto del Conductor (Opcional)</label>
                <input type="url" name="foto_url" value={formData.foto_url} onChange={handleChange}
                  className="w-full bg-slate-800/50 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-sky-500" placeholder="https://ejemplo.com/foto.jpg" />
              </div>
              <div>
                <label className="block text-xs font-medium text-slate-400 mb-1">URL Foto del Vehículo (Opcional)</label>
                <input type="url" name="vehiculo_foto_url" value={formData.vehiculo_foto_url} onChange={handleChange}
                  className="w-full bg-slate-800/50 border border-slate-600 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-sky-500" placeholder="https://ejemplo.com/camion.jpg" />
              </div>

              <button type="submit" disabled={loading} className="w-full mt-4 bg-sky-500 hover:bg-sky-400 text-white text-sm font-semibold py-2.5 rounded-lg transition-colors">
                {loading ? 'Guardando...' : 'Registrar Conductor'}
              </button>
            </form>
          </div>
        </div>

        {/* Lista de Conductores Registrados */}
        <div className="lg:col-span-2">
          <div className="glass-panel rounded-2xl border border-slate-700/50 overflow-hidden">
            <div className="p-6 border-b border-slate-700/50">
              <h3 className="text-lg font-semibold text-white">Directorio de Personal</h3>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-300">
                <thead className="text-xs text-slate-400 uppercase bg-slate-800/50 border-b border-slate-700/50">
                  <tr>
                    <th className="px-6 py-4 font-semibold">Conductor</th>
                    <th className="px-6 py-4 font-semibold">Vehículo</th>
                    <th className="px-6 py-4 font-semibold">Ruta</th>
                    <th className="px-6 py-4 font-semibold">Estado</th>
                  </tr>
                </thead>
                <tbody>
                  {drivers.length === 0 ? (
                    <tr>
                      <td colSpan="4" className="px-6 py-10 text-center text-slate-500">
                        No hay conductores registrados. Crea el primero.
                      </td>
                    </tr>
                  ) : (
                    drivers.map(driver => (
                      <tr key={driver.id} className="border-b border-slate-700/30 hover:bg-slate-800/30 transition-colors">
                        <td className="px-6 py-4 flex items-center gap-3">
                          {driver.foto_url ? (
                            <img src={driver.foto_url} alt={driver.nombre} className="w-10 h-10 rounded-full object-cover border border-slate-600" />
                          ) : (
                            <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-slate-400 font-bold border border-slate-600">
                              {driver.nombre.charAt(0)}
                            </div>
                          )}
                          <div>
                            <p className="font-medium text-white">{driver.nombre}</p>
                            <p className="text-xs text-slate-500">@{driver.username}</p>
                          </div>
                        </td>
                        <td className="px-6 py-4 flex items-center gap-2">
                          <Truck className="w-4 h-4 text-slate-500" /> {driver.vehiculo}
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-2">
                            <Map className="w-4 h-4 text-slate-500" /> {driver.ruta_asignada || 'Sin ruta activa'}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className="bg-slate-700/50 text-slate-300 px-2.5 py-1 rounded-full text-xs border border-slate-600">
                            {driver.estado}
                          </span>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
