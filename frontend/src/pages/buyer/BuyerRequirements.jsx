import React, { useState, useEffect } from 'react';
import { PlusCircle, Trash2, SlidersHorizontal, CheckCircle2, AlertCircle } from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import Modal from '../../components/Modal';

export const BuyerRequirements = () => {
  const [requirements, setRequirements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [formData, setFormData] = useState({
    material_type: 'Plastic',
    min_quantity: 500,
    max_quantity: 2500,
    quality: 'High',
    purpose: 'Recycling',
    max_price_per_kg: 42.0,
  });
  const [submitting, setSubmitting] = useState(false);

  const MATERIALS = ['Aluminum', 'Copper', 'Steel', 'Plastic', 'Cardboard', 'Paper', 'Glass', 'Textile', 'E-waste', 'Other'];
  const QUALITIES = ['Any', 'Industrial Grade', 'High', 'Medium', 'Low'];
  const PURPOSES = ['Recycling', 'Upcycling', 'Direct Reuse', 'Repurposing'];

  const fetchRequirements = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/buyers/requirements');
      setRequirements(res.data);
    } catch (err) {
      console.error('Error fetching buyer requirements:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRequirements();
  }, []);

  const handleCreateRequirement = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post('/api/buyers/requirements', {
        ...formData,
        min_quantity: parseFloat(formData.min_quantity),
        max_quantity: parseFloat(formData.max_quantity),
        max_price_per_kg: parseFloat(formData.max_price_per_kg),
      });
      setIsModalOpen(false);
      fetchRequirements();
    } catch (err) {
      alert('Failed to post requirement: ' + (err.response?.data?.message || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Delete this sourcing requirement?')) return;
    try {
      await api.delete(`/api/buyers/requirements/${id}`);
      setRequirements(requirements.filter((r) => r.id !== id));
    } catch (err) {
      alert('Failed to delete requirement: ' + (err.response?.data?.message || err.message));
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Sourcing Specifications</h1>
          <p className="text-xs text-slate-500 mt-1">
            Specify raw recyclable feedstocks needed by your processing plant or recycling mill
          </p>
        </div>
        <button
          onClick={() => setIsModalOpen(true)}
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-xs shadow-md shadow-eco-600/20"
        >
          <PlusCircle className="w-4 h-4" />
          Post Sourcing Demand
        </button>
      </div>

      {loading ? (
        <LoadingSpinner text="Loading sourcing specifications..." />
      ) : requirements.length === 0 ? (
        <EmptyState
          title="No sourcing requirements posted"
          description="Create your first specification to automatically match incoming seller batches."
          action={
            <button
              onClick={() => setIsModalOpen(true)}
              className="px-4 py-2 rounded-xl bg-eco-600 text-white text-xs font-semibold"
            >
              Post Sourcing Demand
            </button>
          }
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {requirements.map((req) => (
            <div
              key={req.id}
              className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <Badge variant="eco" size="xs">{req.material_type}</Badge>
                  <button
                    onClick={() => handleDelete(req.id)}
                    className="p-1.5 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Target Range</span>
                    <span className="font-bold text-slate-900">{req.min_quantity} - {req.max_quantity} kg</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Required Grade</span>
                    <span className="font-bold text-slate-900">{req.quality}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Intended Purpose</span>
                    <span className="font-bold text-slate-900">{req.purpose}</span>
                  </div>
                  <div className="flex justify-between py-1">
                    <span className="text-slate-500">Max Unit Budget</span>
                    <span className="font-bold text-emerald-600">₹{req.max_price_per_kg}/kg</span>
                  </div>
                </div>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                <span className="flex items-center gap-1 text-emerald-600 font-semibold">
                  <CheckCircle2 className="w-3.5 h-3.5" /> Actively Matching
                </span>
                <span>Active</span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal for new requirement */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Post Feedstock Sourcing Specification"
        subtitle="Our AI engine will continuously match incoming seller listings"
      >
        <form onSubmit={handleCreateRequirement} className="space-y-4">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Target Material</label>
              <select
                value={formData.material_type}
                onChange={(e) => setFormData({ ...formData, material_type: e.target.value })}
                className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-semibold"
              >
                {MATERIALS.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Quality Grade</label>
              <select
                value={formData.quality}
                onChange={(e) => setFormData({ ...formData, quality: e.target.value })}
                className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
              >
                {QUALITIES.map((q) => (
                  <option key={q} value={q}>{q}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Min Batch Size (kg)</label>
              <input
                type="number"
                required
                value={formData.min_quantity}
                onChange={(e) => setFormData({ ...formData, min_quantity: e.target.value })}
                className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Max Batch Capacity (kg)</label>
              <input
                type="number"
                required
                value={formData.max_quantity}
                onChange={(e) => setFormData({ ...formData, max_quantity: e.target.value })}
                className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Max Purchase Price (₹/kg)</label>
              <input
                type="number"
                step="0.5"
                required
                value={formData.max_price_per_kg}
                onChange={(e) => setFormData({ ...formData, max_price_per_kg: e.target.value })}
                className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-bold text-emerald-600"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Processing Purpose</label>
              <select
                value={formData.purpose}
                onChange={(e) => setFormData({ ...formData, purpose: e.target.value })}
                className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
              >
                {PURPOSES.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-3 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-sm shadow-md shadow-eco-600/20 transition-all"
          >
            {submitting ? 'Saving...' : 'Publish Sourcing Demand'}
          </button>
        </form>
      </Modal>
    </div>
  );
};

export default BuyerRequirements;
