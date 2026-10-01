import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Send,
  Loader2,
  Sparkles,
  CheckCircle,
  AlertCircle,
  RefreshCw,
  ImageIcon,
  ShieldCheck,
} from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';

/* ─── Constants ────────────────────────────────────────────── */
const MATERIALS = [
  'Aluminum', 'Copper', 'Steel', 'Plastic',
  'Cardboard', 'Paper', 'Glass', 'Textile', 'E-waste', 'Other',
];
const CATEGORIES = ['Metal', 'Polymer', 'Fibre', 'Mineral', 'Electronics', 'Mixed'];
const QUALITIES   = ['Industrial Grade', 'High', 'Medium', 'Low'];
const CONDITIONS  = ['Clean', 'Sorted', 'Baled', 'Mixed', 'Contaminated'];
const PURPOSES    = ['Recycling', 'Upcycling', 'Direct Reuse', 'Repurposing'];

/* ─── Badge ─────────────────────────────────────────────────── */
const ConfBadge = ({ value }) => {
  const pct = Math.round(value * 100);
  const color =
    pct >= 85 ? 'bg-emerald-100 text-emerald-700' :
    pct >= 65 ? 'bg-amber-100 text-amber-700' :
                'bg-rose-100 text-rose-600';
  return (
    <span className={`inline-block px-2 py-0.5 rounded-lg text-xs font-bold ${color}`}>
      {pct}%
    </span>
  );
};

/* ─── Component ─────────────────────────────────────────────── */
export const NewMaterial = () => {
  const { user }   = useAuth();
  const navigate   = useNavigate();

  /* form */
  const [formData, setFormData] = useState({
    material_type:     'Aluminum',
    category:          'Metal',
    quantity_kg:       '',
    unit:              'kg',
    quality:           'High',
    condition:         'Clean',
    intended_purpose:  'Recycling',
    description:       '',
    image_url:         '',
    asking_price:      '',
  });

  /* image */
  const [selectedFile,  setSelectedFile]  = useState(null);
  const [imagePreview,  setImagePreview]  = useState('');
  const [isAnalyzing,   setIsAnalyzing]   = useState(false);
  const [aiResult,      setAiResult]      = useState(null);   // classification result
  const [aiApplied,     setAiApplied]     = useState(false);  // did seller accept?

  /* publish */
  const [isPublishing, setIsPublishing] = useState(false);
  const [error,        setError]        = useState('');
  const [success,      setSuccess]      = useState(false);

  /* ── Image selection ───────────────────────────────────────── */
  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const ext  = file.name.split('.').pop().toLowerCase();
    const allowed = ['jpg', 'jpeg', 'png', 'webp'];
    if (!allowed.includes(ext)) {
      setError('Please upload a JPG, PNG, or WEBP image.');
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setError('Image is too large. Maximum allowed size is 10 MB.');
      return;
    }

    setError('');
    setAiResult(null);
    setAiApplied(false);
    setSelectedFile(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleClearImage = () => {
    setSelectedFile(null);
    setImagePreview('');
    setAiResult(null);
    setAiApplied(false);
    setFormData(prev => ({ ...prev, image_url: '' }));
  };

  /* ── AI Analysis ───────────────────────────────────────────── */
  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError('Please upload an image first.');
      return;
    }
    setError('');
    setIsAnalyzing(true);
    setAiResult(null);

    try {
      const form = new FormData();
      form.append('file', selectedFile);

      const res = await api.post('/api/seller/materials/classify', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setAiResult(res.data);
      // Pre-fill image_url from response
      setFormData(prev => ({ ...prev, image_url: res.data.image_url || prev.image_url }));
    } catch (err) {
      const msg =
        err.response?.status === 413 ? 'Image is too large. Maximum allowed size is 10 MB.' :
        err.response?.status === 422 ? (err.response?.data?.detail || 'Please upload a JPG, PNG, or WEBP image.') :
        err.response?.status === 403 ? 'Only sellers can classify materials.' :
        'Material identification failed. Please try another image.';
      setError(msg);
    } finally {
      setIsAnalyzing(false);
    }
  };

  /* Seller accepts AI suggestion */
  const handleApplyAI = () => {
    if (!aiResult) return;
    setFormData(prev => ({
      ...prev,
      material_type: aiResult.material,
      category:      aiResult.category,
    }));
    setAiApplied(true);
  };

  /* Seller overrides manually */
  const handleChangeManually = () => {
    setAiApplied(false);
  };

  /* ── Publish listing ───────────────────────────────────────── */
  const handlePublish = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.image_url) {
      setError('Please upload an image and run AI analysis first.');
      return;
    }
    if (!formData.quantity_kg || Number(formData.quantity_kg) <= 0) {
      setError('Please enter a valid quantity.');
      return;
    }
    if (!formData.asking_price || Number(formData.asking_price) <= 0) {
      setError('Please enter a valid asking price greater than 0.');
      return;
    }

    setIsPublishing(true);
    try {
      await api.post(`/api/materials?asking_price=${formData.asking_price}`, {
        material_type:    formData.material_type,
        description:      formData.description,
        quantity_kg:      parseFloat(formData.quantity_kg),
        quality:          formData.quality,
        condition:        formData.condition,
        intended_purpose: formData.intended_purpose,
        image_url:        formData.image_url,
        status:           'available',
      });

      setSuccess(true);
      setTimeout(() => navigate('/seller/materials'), 1500);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        err.response?.data?.message ||
        'Failed to publish listing. Please try again.'
      );
    } finally {
      setIsPublishing(false);
    }
  };

  /* ─── Success screen ─────────────────────────────────────── */
  if (success) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center text-center space-y-4">
        <div className="w-20 h-20 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600 mx-auto">
          <CheckCircle className="w-10 h-10" />
        </div>
        <h2 className="text-2xl font-extrabold text-slate-900">Listing Published!</h2>
        <p className="text-slate-500 max-w-md">
          Your material is now live on the marketplace.
        </p>
      </div>
    );
  }

  /* ─── Main render ────────────────────────────────────────── */
  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Add Waste Material</h1>
        <p className="text-xs text-slate-500 mt-1">
          Upload an image → AI identifies the material → You verify → Set your price → Publish
        </p>
      </div>

      {/* Global error */}
      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      <form onSubmit={handlePublish} className="grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* ── LEFT COLUMN ───────────────────────────────────── */}
        <div className="lg:col-span-5 space-y-6">

          {/* Image Upload Card */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-5">
            <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider">
              Identify Your Waste
            </h3>

            {/* Drop / Upload zone */}
            <label className="block cursor-pointer">
              <input
                type="file"
                accept=".jpg,.jpeg,.png,.webp"
                className="sr-only"
                onChange={handleFileChange}
              />
              {imagePreview ? (
                <div className="relative rounded-2xl overflow-hidden border border-slate-200 group">
                  <img
                    src={imagePreview}
                    alt="Material preview"
                    className="w-full h-52 object-cover"
                  />
                  <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition flex items-center justify-center text-white text-sm font-bold">
                    Click to change image
                  </div>
                </div>
              ) : (
                <div className="flex flex-col items-center justify-center h-52 rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 hover:bg-eco-50 hover:border-eco-400 transition text-center px-4">
                  <ImageIcon className="w-10 h-10 text-slate-300 mb-3" />
                  <span className="text-sm font-bold text-slate-600">Upload Image</span>
                  <span className="text-xs text-slate-400 mt-1">Supported: JPG, PNG, WEBP · Max 10 MB</span>
                </div>
              )}
            </label>

            {/* Clear */}
            {imagePreview && (
              <button
                type="button"
                onClick={handleClearImage}
                className="text-xs text-slate-400 hover:text-rose-500 flex items-center gap-1 transition"
              >
                <RefreshCw className="w-3 h-3" /> Remove image
              </button>
            )}

            {/* Analyze button */}
            <button
              type="button"
              onClick={handleAnalyze}
              disabled={!selectedFile || isAnalyzing}
              className="w-full py-3 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 text-white font-bold text-sm shadow-md transition flex items-center justify-center gap-2"
            >
              {isAnalyzing ? (
                <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing…</>
              ) : (
                <><Sparkles className="w-4 h-4" /> Analyze Material</>
              )}
            </button>
          </div>

          {/* AI Result Card */}
          {aiResult && (
            <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
              <div className="flex items-center gap-2 text-purple-700 font-extrabold text-sm">
                <Sparkles className="w-4 h-4" /> AI Material Detection
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 rounded-2xl p-3">
                  <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Material</p>
                  <p className="text-base font-extrabold text-slate-900">{aiResult.material}</p>
                </div>
                <div className="bg-slate-50 rounded-2xl p-3">
                  <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Category</p>
                  <p className="text-base font-extrabold text-slate-900">{aiResult.category}</p>
                </div>
                <div className="bg-slate-50 rounded-2xl p-3 col-span-2">
                  <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Confidence</p>
                  <div className="flex items-center gap-3">
                    <ConfBadge value={aiResult.confidence} />
                    <div className="flex-1 bg-slate-200 rounded-full h-1.5">
                      <div
                        className="bg-purple-500 h-1.5 rounded-full transition-all"
                        style={{ width: `${Math.round(aiResult.confidence * 100)}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Verify notice */}
              <div className="flex items-start gap-2 p-3 rounded-xl bg-amber-50 border border-amber-200">
                <ShieldCheck className="w-4 h-4 text-amber-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-amber-700 font-medium">
                  Please verify this result before creating your listing. You can change the material
                  if the detection is incorrect.
                </p>
              </div>

              {/* CTA buttons */}
              {!aiApplied ? (
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={handleApplyAI}
                    className="flex-1 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold transition"
                  >
                    ✓ Use This Result
                  </button>
                  <button
                    type="button"
                    onClick={() => setAiResult(null)}
                    className="flex-1 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition"
                  >
                    Try Another Image
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-between">
                  <span className="text-xs text-emerald-600 font-bold flex items-center gap-1">
                    <CheckCircle className="w-3.5 h-3.5" /> Applied to listing details
                  </span>
                  <button
                    type="button"
                    onClick={handleChangeManually}
                    className="text-xs text-slate-500 hover:text-purple-600 font-semibold transition flex items-center gap-1"
                  >
                    <RefreshCw className="w-3 h-3" /> Change Material
                  </button>
                </div>
              )}

              {/* Model info */}
              <p className="text-[10px] text-slate-300 text-right">
                Model: {aiResult.model_name} v{aiResult.model_version}
              </p>
            </div>
          )}
        </div>

        {/* ── RIGHT COLUMN ─────────────────────────────────── */}
        <div className="lg:col-span-7 space-y-6">

          {/* Material Details */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-5">
            <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider">
              Material Details
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Material type */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Material Type
                  {aiApplied && (
                    <span className="ml-2 text-[10px] text-purple-600 font-semibold bg-purple-50 px-1.5 py-0.5 rounded">
                      AI suggested
                    </span>
                  )}
                </label>
                <select
                  value={formData.material_type}
                  onChange={e => setFormData(p => ({ ...p, material_type: e.target.value }))}
                  className="w-full py-2.5 px-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-semibold"
                >
                  {MATERIALS.map(m => <option key={m}>{m}</option>)}
                </select>
              </div>

              {/* Category */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Category
                  {aiApplied && (
                    <span className="ml-2 text-[10px] text-purple-600 font-semibold bg-purple-50 px-1.5 py-0.5 rounded">
                      AI suggested
                    </span>
                  )}
                </label>
                <select
                  value={formData.category}
                  onChange={e => setFormData(p => ({ ...p, category: e.target.value }))}
                  className="w-full py-2.5 px-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                >
                  {CATEGORIES.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>

              {/* Quantity */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Quantity</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    min="1"
                    step="1"
                    required
                    value={formData.quantity_kg}
                    onChange={e => setFormData(p => ({ ...p, quantity_kg: e.target.value }))}
                    className="flex-1 py-2.5 px-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-bold"
                    placeholder="e.g. 500"
                  />
                  <select
                    value={formData.unit}
                    onChange={e => setFormData(p => ({ ...p, unit: e.target.value }))}
                    className="py-2.5 px-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none font-semibold"
                  >
                    {['kg', 'tonnes', 'litres', 'units'].map(u => <option key={u}>{u}</option>)}
                  </select>
                </div>
              </div>

              {/* Quality */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Quality Grade</label>
                <select
                  value={formData.quality}
                  onChange={e => setFormData(p => ({ ...p, quality: e.target.value }))}
                  className="w-full py-2.5 px-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                >
                  {QUALITIES.map(q => <option key={q}>{q}</option>)}
                </select>
              </div>

              {/* Condition */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Physical Condition</label>
                <select
                  value={formData.condition}
                  onChange={e => setFormData(p => ({ ...p, condition: e.target.value }))}
                  className="w-full py-2.5 px-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                >
                  {CONDITIONS.map(c => <option key={c}>{c}</option>)}
                </select>
              </div>

              {/* Purpose */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Intended Purpose</label>
                <select
                  value={formData.intended_purpose}
                  onChange={e => setFormData(p => ({ ...p, intended_purpose: e.target.value }))}
                  className="w-full py-2.5 px-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                >
                  {PURPOSES.map(p => <option key={p}>{p}</option>)}
                </select>
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Description</label>
              <textarea
                rows={3}
                value={formData.description}
                onChange={e => setFormData(p => ({ ...p, description: e.target.value }))}
                className="w-full p-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                placeholder="e.g. 6063 clean aluminum extrusion scrap, degreased, cut to 1 m lengths."
              />
            </div>
          </div>

          {/* Pricing Card */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-5">
            <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider">
              Your Asking Price
            </h3>
            <p className="text-xs text-slate-500">
              You set the price. Buyers can negotiate. No AI price suggestion is provided.
            </p>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Price (₹ per unit)</label>
              <input
                type="number"
                step="0.5"
                min="0.01"
                required
                value={formData.asking_price}
                onChange={e => setFormData(p => ({ ...p, asking_price: e.target.value }))}
                className="w-full py-3 px-4 rounded-xl text-lg bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-extrabold text-emerald-600"
                placeholder="e.g. 150"
              />
            </div>

            <button
              type="submit"
              disabled={isPublishing}
              className="w-full py-3.5 rounded-2xl bg-eco-600 hover:bg-eco-700 disabled:opacity-50 text-white font-bold text-sm shadow-md transition flex items-center justify-center gap-2"
            >
              <Send className="w-4 h-4" />
              {isPublishing ? 'Publishing…' : 'Publish Listing to Marketplace'}
            </button>
          </div>

        </div>
      </form>
    </div>
  );
};

export default NewMaterial;
