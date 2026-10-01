import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { PlusCircle, Trash2, Edit, Sparkles, MapPin, Building2, Layers } from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export const SellerMaterials = () => {
  const { user } = useAuth();
  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchListings = async () => {
    setLoading(true);
    try {
      const res = await api.get(`/api/listings/seller/me`);
      setListings(res.data);
    } catch (err) {
      console.error('Error fetching seller listings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchListings();
  }, [user]);

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to remove this listing?')) return;
    try {
      await api.delete(`/api/listings/${id}`);
      setListings(listings.filter((l) => l.id !== id));
    } catch (err) {
      alert('Failed to delete listing: ' + (err.response?.data?.message || err.message));
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">My Recyclable Inventory</h1>
          <p className="text-xs text-slate-500 mt-1">Manage active listings and stock availability</p>
        </div>
        <Link
          to="/seller/materials/new"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-xs shadow-md shadow-eco-600/20"
        >
          <PlusCircle className="w-4 h-4" />
          Add Material Lot
        </Link>
      </div>

      {loading ? (
        <LoadingSpinner text="Loading your inventory lots..." />
      ) : listings.length === 0 ? (
        <EmptyState
          title="No materials listed yet"
          description="Upload your first recyclable batch to start selling."
          action={
            <Link
              to="/seller/materials/new"
              className="px-4 py-2 rounded-xl bg-eco-600 text-white text-xs font-semibold"
            >
              List Material Now
            </Link>
          }
        />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/80 text-slate-500 font-bold uppercase text-[10px] tracking-wider">
                  <th className="py-3.5 px-6">Material Lot</th>
                  <th className="py-3.5 px-6">Quantity</th>
                  <th className="py-3.5 px-6">Quality & Condition</th>
                  <th className="py-3.5 px-6">Asking Price</th>
                  <th className="py-3.5 px-6">Status</th>
                  <th className="py-3.5 px-6 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {listings.map((l) => (
                  <tr key={l.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-4 px-6">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-xl bg-slate-100 overflow-hidden flex-shrink-0">
                          <img
                            src={l.material?.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600'}
                            alt={l.material?.material_type}
                            className="w-full h-full object-cover"
                          />
                        </div>
                        <div>
                          <div className="text-sm font-bold text-slate-900">{l.material?.material_type}</div>
                          <div className="text-[11px] text-slate-400 line-clamp-1 max-w-xs">
                            {l.material?.description || 'Verified recycled lot'}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="py-4 px-6 font-bold text-slate-900">
                      {l.quantity_available.toLocaleString('en-IN')} {l.unit}
                    </td>
                    <td className="py-4 px-6">
                      <div className="flex flex-col gap-1">
                        <span className="font-semibold text-slate-900">{l.material?.quality} Grade</span>
                        <span className="text-[11px] text-slate-500">{l.material?.condition}</span>
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <div className="font-extrabold text-emerald-600 text-sm">
                        ₹{l.asking_price}/kg
                      </div>
                      <div className="text-[10px] text-slate-400">
                        Total: ₹{(l.asking_price * l.quantity_available).toLocaleString('en-IN')}
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <Badge variant={l.status === 'active' ? 'eco' : 'default'} size="xs">
                        {l.status}
                      </Badge>
                    </td>
                    <td className="py-4 px-6 text-right space-x-2">
                      <button
                        onClick={() => handleDelete(l.id)}
                        className="inline-flex p-2 rounded-xl bg-rose-50 text-rose-600 hover:bg-rose-100 transition-colors"
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

export default SellerMaterials;
