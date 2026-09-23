import React, { useState, useEffect } from 'react';
import { Package, Trash2, ShieldCheck, Building2, Sparkles } from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';

export const AdminMaterials = () => {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMaterials = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/materials');
      setMaterials(res.data);
    } catch (err) {
      console.error('Error loading materials:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMaterials();
  }, []);

  const handleDelete = async (id) => {
    if (!window.confirm('Moderation: Remove this material from marketplace?')) return;
    try {
      await api.delete(`/api/materials/${id}`);
      setMaterials(materials.filter((m) => m.id !== id));
    } catch (err) {
      alert('Error deleting material: ' + (err.response?.data?.message || err.message));
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Marketplace Material Moderation</h1>
        <p className="text-xs text-slate-500 mt-1">Audit active circular listings, purity classifications, and seller offerings</p>
      </div>

      {loading ? (
        <LoadingSpinner text="Loading marketplace material lots..." />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/80 text-slate-500 font-bold uppercase text-[10px] tracking-wider">
                  <th className="py-3.5 px-6">Material Lot</th>
                  <th className="py-3.5 px-6">Seller Organization</th>
                  <th className="py-3.5 px-6">Quantity</th>
                  <th className="py-3.5 px-6">AI Valuation</th>
                  <th className="py-3.5 px-6">Status</th>
                  <th className="py-3.5 px-6 text-right">Moderation</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {materials.map((m) => (
                  <tr key={m.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-4 px-6">
                      <div className="font-bold text-slate-900 text-sm">{m.material_type}</div>
                      <div className="text-[11px] text-slate-400">{m.quality} Grade • {m.condition}</div>
                    </td>
                    <td className="py-4 px-6 text-slate-700">
                      {m.seller?.organization || m.seller?.name}
                    </td>
                    <td className="py-4 px-6 font-bold text-slate-900">
                      {m.quantity_kg.toLocaleString('en-IN')} kg
                    </td>
                    <td className="py-4 px-6 font-extrabold text-emerald-600 text-sm">
                      ₹{m.predicted_price || 40}/kg
                    </td>
                    <td className="py-4 px-6">
                      <Badge variant={m.status === 'available' ? 'eco' : 'default'} size="xs">
                        {m.status}
                      </Badge>
                    </td>
                    <td className="py-4 px-6 text-right">
                      <button
                        onClick={() => handleDelete(m.id)}
                        className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
                        title="Delete Listing"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminMaterials;
