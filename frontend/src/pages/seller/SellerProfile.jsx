import React, { useState, useEffect } from 'react';
import {
  User as UserIcon,
  Building2,
  Mail,
  Phone,
  MapPin,
  ShieldCheck,
  Calendar,
  Layers,
  Save,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/LoadingSpinner';
import Badge from '../../components/Badge';

export const SellerProfile = () => {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [isEditing, setIsEditing] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    phone: '',
    organization: '',
    business_type: '',
    city: '',
    state: ''
  });

  const fetchProfile = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get('/api/users/me');
      setProfile(res.data);
      setFormData({
        phone: res.data.phone || '',
        organization: res.data.organization || '',
        business_type: res.data.business_type || '',
        city: res.data.location?.city || '',
        state: res.data.location?.state || 'Tamil Nadu'
      });
    } catch (err) {
      console.error('Error fetching user profile:', err);
      setError('Failed to load profile details.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const res = await api.put('/api/users/me', {
        phone: formData.phone.trim() || null,
        organization: formData.organization.trim(),
        business_type: formData.business_type.trim() || null,
        city: formData.city.trim() || null,
        state: formData.state.trim() || null
      });
      setProfile(res.data);
      setSuccess('Profile updated successfully.');
      setIsEditing(false);
    } catch (err) {
      console.error('Error updating profile:', err);
      setError(err.response?.data?.message || err.response?.data?.detail || 'Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading verified seller profile..." />;
  }

  const activeUser = profile || user;

  return (
    <div className="max-w-4xl space-y-8 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Seller Account & Credentials</h1>
          <p className="text-xs text-slate-500 mt-1">
            Verified company registration, contact coordinates, and circular marketplace profile
          </p>
        </div>
        {!isEditing && (
          <button
            onClick={() => setIsEditing(true)}
            className="px-4 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold transition-all shadow-sm flex items-center gap-1.5 self-start sm:self-auto"
          >
            Edit Profile
          </button>
        )}
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
          <button onClick={() => setError('')} className="font-bold underline text-rose-800">Dismiss</button>
        </div>
      )}

      {success && (
        <div className="p-4 bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs rounded-2xl flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 flex-shrink-0" />
            <span>{success}</span>
          </div>
          <button onClick={() => setSuccess('')} className="font-bold underline text-emerald-800">Dismiss</button>
        </div>
      )}

      {/* Main Profile Card */}
      <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-6 sm:p-8 space-y-6">
        <div className="flex flex-col sm:flex-row items-start sm:center justify-between gap-4 pb-6 border-b border-slate-100">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-tr from-eco-600 to-emerald-400 text-white font-extrabold text-xl flex items-center justify-center shadow-md shadow-eco-500/20">
              {activeUser?.name?.substring(0, 2).toUpperCase() || 'SE'}
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-extrabold text-slate-900">{activeUser?.name}</h2>
                <Badge variant="eco" size="xs">
                  {activeUser?.role?.toUpperCase()}
                </Badge>
              </div>
              <p className="text-xs text-slate-500 mt-0.5">{activeUser?.organization || 'Circular Partner Enterprise'}</p>
            </div>
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-emerald-50 text-emerald-700 text-xs font-bold border border-emerald-200/60">
            <ShieldCheck className="w-4 h-4" />
            Verified Enterprise
          </div>
        </div>

        {isEditing ? (
          <form onSubmit={handleSave} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Company / Organization *</label>
                <input
                  type="text"
                  required
                  value={formData.organization}
                  onChange={(e) => setFormData({ ...formData, organization: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                  placeholder="e.g. EcoTextiles Pvt Ltd"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Business Type</label>
                <input
                  type="text"
                  value={formData.business_type}
                  onChange={(e) => setFormData({ ...formData, business_type: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                  placeholder="e.g. Manufacturer, Recycler, Scrap Trader"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Contact Phone *</label>
                <input
                  type="text"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                  placeholder="e.g. +91 9876543210"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">City</label>
                <input
                  type="text"
                  value={formData.city}
                  onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                  placeholder="e.g. Coimbatore"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">State</label>
                <input
                  type="text"
                  value={formData.state}
                  onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-semibold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                  placeholder="e.g. Tamil Nadu"
                />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 mb-1">Email (Cannot be modified)</label>
                <input
                  type="email"
                  disabled
                  value={activeUser?.email || ''}
                  className="w-full px-3.5 py-2.5 rounded-xl border border-slate-100 bg-slate-100 text-sm font-semibold text-slate-500 cursor-not-allowed"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-3 pt-4 border-t border-slate-100">
              <button
                type="button"
                onClick={() => {
                  setIsEditing(false);
                  setError('');
                }}
                className="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 text-xs font-bold hover:bg-slate-50 transition-all"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={saving}
                className="px-5 py-2 rounded-xl bg-eco-600 hover:bg-eco-700 text-white text-xs font-bold transition-all shadow-md shadow-eco-600/20 disabled:opacity-50 flex items-center gap-1.5"
              >
                <Save className="w-3.5 h-3.5" />
                {saving ? 'Saving...' : 'Save Profile'}
              </button>
            </div>
          </form>
        ) : (
          /* Profile Details Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
                <Mail className="w-3.5 h-3.5" />
                Email Address
              </div>
              <div className="text-sm font-semibold text-slate-900">{activeUser?.email}</div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
                <Phone className="w-3.5 h-3.5" />
                Contact Phone
              </div>
              <div className="text-sm font-semibold text-slate-900">{activeUser?.phone || 'Not specified'}</div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
                <Building2 className="w-3.5 h-3.5" />
                Business Type
              </div>
              <div className="text-sm font-semibold text-slate-900">{activeUser?.business_type || 'Industrial Scrap Producer'}</div>
            </div>

            <div className="p-4 rounded-2xl bg-slate-50 border border-slate-100 space-y-1">
              <div className="flex items-center gap-2 text-xs font-bold text-slate-400 uppercase tracking-wider">
                <MapPin className="w-3.5 h-3.5" />
                Location
              </div>
              <div className="text-sm font-semibold text-slate-900">
                {activeUser?.location?.city
                  ? `${activeUser.location.city}, ${activeUser.location.state}`
                  : 'Coimbatore, Tamil Nadu'}
              </div>
            </div>
          </div>
        )}

        {/* Security & Verification Notice */}
        <div className="p-4 rounded-2xl bg-blue-50/70 border border-blue-200/60 text-blue-900 text-xs leading-relaxed flex items-start gap-3">
          <ShieldCheck className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
          <div>
            <span className="font-bold">Cryptographically Signed Identity:</span> Your marketplace transactions,
            material listings, and offer negotiations are signed with role-based JWT authentication linked to your verified organization.
          </div>
        </div>
      </div>
    </div>
  );
};

export default SellerProfile;

