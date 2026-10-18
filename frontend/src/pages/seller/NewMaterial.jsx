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
  AlertTriangle,
  Info,
} from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import FileUploader from '../../components/FileUploader';

/* ─── Constants ────────────────────────────────────────────── */
// Marketplace materials for listings
const ALL_MATERIALS = [
  'Plastic', 'Cardboard', 'Paper', 'Glass', 'Textile', 'E-waste', 'Other',
  'Aluminum', 'Copper', 'Steel',
];

// Dedicated classes supported by MobileNetV2 7-Class AI model
const AI_SUPPORTED_CLASSES = [
  'Cardboard', 'E-waste', 'Glass', 'Other', 'Paper', 'Plastic', 'Textile',
];

const CATEGORIES = ['Polymer', 'Fibre', 'Mineral', 'Electronics', 'Metal', 'Mixed'];
const QUALITIES   = ['Industrial Grade', 'High', 'Medium', 'Low'];
const CONDITIONS  = ['Clean', 'Sorted', 'Baled', 'Mixed', 'Contaminated'];
const PURPOSES    = ['Recycling', 'Upcycling', 'Direct Reuse', 'Repurposing'];

/* ─── Confidence Badge ───────────────────────────────────────── */
const ConfBadge = ({ value }) => {
  const pct = Math.round((value ?? 0) * 100);
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

  /* form state */
  const [formData, setFormData] = useState({
    material_type:     'Plastic',
    category:          'Polymer',
    quantity_kg:       '',
    unit:              'kg',
    quality:           'High',
    condition:         'Clean',
    intended_purpose:  'Recycling',
    description:       '',
    image_url:         '',
    asking_price:      '',
  });

  /* image & upload state */
  const [selectedFile,  setSelectedFile]  = useState(null);
  const [imagePreview,  setImagePreview]  = useState('');
  const [isAnalyzing,   setIsAnalyzing]   = useState(false);
  const [aiResult,      setAiResult]      = useState(null);   // real classification result
  const [aiApplied,     setAiApplied]     = useState(false);  // did seller apply result?
  const [uploadError,   setUploadError]   = useState('');

  /* publish state */
  const [isPublishing, setIsPublishing] = useState(false);
  const [error,        setError]        = useState('');
  const [success,      setSuccess]      = useState(false);

  /* ── Image selection & frontend validation ─────────────────── */
  const handleFileSelected = (file) => {
    if (!file) return;

    const ext = file.name.split('.').pop().toLowerCase();
    const allowed = ['jpg', 'jpeg', 'png', 'webp'];
    if (!allowed.includes(ext)) {
      setUploadError(`Unsupported format .${ext}. Please upload a JPG, PNG, or WEBP image.`);
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setUploadError('Image exceeds 10 MB limit. Please select a smaller file.');
      return;
    }
    if (file.size === 0) {
      setUploadError('Uploaded file is empty.');
      return;
    }

    setUploadError('');
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
    setUploadError('');
    setFormData(prev => ({ ...prev, image_url: '' }));
  };

  /* ── AI Analysis via Real Backend Endpoint ─────────────────── */
  const handleAnalyze = async () => {
    if (!selectedFile) {
      setUploadError('Please select or drop an image first.');
      return;
    }
    setUploadError('');
    setError('');
    setIsAnalyzing(true);
    setAiResult(null);

    try {
      const form = new FormData();
      // Exact field name expected by backend: "file"
      form.append('file', selectedFile);

      // Dedicated authenticated seller classification endpoint
      const res = await api.post('/api/seller/materials/classify', form, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });

      setAiResult(res.data);
      // Pre-fill image_url from real uploaded storage path
      if (res.data.image_url) {
        setFormData(prev => ({ ...prev, image_url: res.data.image_url }));
      }
    } catch (err) {
      let msg = 'Material identification failed. Please try another image.';
      if (err.response?.status === 413) {
        msg = 'File size exceeds maximum allowed 10 MB limit.';
      } else if (err.response?.status === 422) {
        msg = err.response?.data?.message || err.response?.data?.detail || 'Invalid or corrupted image file.';
      } else if (err.response?.status === 401) {
        msg = 'Authentication session expired. Please log in again.';
      } else if (err.response?.status === 403) {
        msg = 'Access denied. Only registered sellers can classify waste materials.';
      } else if (err.response?.status === 503) {
        msg = 'AI Classification service temporarily unavailable.';
      } else if (err.response?.data?.detail) {
        msg = err.response.data.detail;
      }
      setUploadError(msg);
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
      category:      aiResult.category || prev.category,
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
      setError('Please upload an image and run AI analysis before publishing.');
      return;
    }
    if (!formData.quantity_kg || Number(formData.quantity_kg) <= 0) {
      setError('Please enter a valid quantity greater than 0.');
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
          Your waste material has been verified and posted to the marketplace at your asking price.
        </p>
      </div>
    );
  }

  /* ─── Main render ────────────────────────────────────────── */
  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div>
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Add Waste Material</h1>
            <p className="text-xs text-slate-500 mt-1">
              Upload an image → Real MobileNetV2 Vision AI classification → Verify or override → Set asking price → Publish
            </p>
          </div>
          <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-purple-50 text-purple-700 border border-purple-200 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5" /> MobileNetV2 7-Class AI Prototype
          </div>
        </div>
      </div>

      {/* Global Error Banner */}
      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-sm flex items-center gap-2">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      <form onSubmit={handlePublish} className="grid grid-cols-1 lg:grid-cols-12 gap-8">

        {/* ── LEFT COLUMN: Image & AI Vision ────────────────── */}
        <div className="lg:col-span-5 space-y-6">

          {/* Upload Card */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-5">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider">
                1. Upload Waste Image
              </h3>
              {selectedFile && (
                <span className="text-[11px] text-slate-400 font-medium">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </span>
              )}
            </div>

            {/* Reusable drag-and-drop file uploader with live preview */}
            <FileUploader
              onFileSelected={handleFileSelected}
              previewUrl={imagePreview}
              onClear={handleClearImage}
              isUploading={isAnalyzing}
            />

            {/* Local upload validation error */}
            {uploadError && (
              <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {uploadError}
              </div>
            )}

            {/* AI Analyze Action Button */}
            <button
              type="button"
              onClick={handleAnalyze}
              disabled={!selectedFile || isAnalyzing}
              className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50 text-white font-bold text-sm shadow-md transition flex items-center justify-center gap-2"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Running MobileNetV2 Vision Classifier…
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Classify Material with AI Vision
                </>
              )}
            </button>
          </div>

          {/* Real AI Result Card */}
          {aiResult && (
            <div className="bg-white rounded-3xl p-6 border border-purple-200 shadow-md space-y-5">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-purple-700 font-extrabold text-sm">
                  <Sparkles className="w-4 h-4" /> Real AI Classification Output
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">
                  7-Class Prototype
                </span>
              </div>

              {/* Primary Prediction Details */}
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-50 rounded-2xl p-3 border border-slate-100">
                  <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Predicted Material</p>
                  <p className="text-lg font-black text-slate-900">{aiResult.material}</p>
                </div>
                <div className="bg-slate-50 rounded-2xl p-3 border border-slate-100">
                  <p className="text-[10px] uppercase font-bold text-slate-400 mb-1">Broad Category</p>
                  <p className="text-lg font-black text-slate-900">{aiResult.category}</p>
                </div>
                <div className="bg-slate-50 rounded-2xl p-3 col-span-2 border border-slate-100">
                  <div className="flex items-center justify-between mb-1.5">
                    <p className="text-[10px] uppercase font-bold text-slate-400">Confidence Score</p>
                    <ConfBadge value={aiResult.confidence} />
                  </div>
                  <div className="w-full bg-slate-200 rounded-full h-2">
                    <div
                      className="bg-purple-600 h-2 rounded-full transition-all duration-500"
                      style={{ width: `${Math.round((aiResult.confidence || 0) * 100)}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Top-3 Ranked Predictions */}
              {aiResult.top_predictions && aiResult.top_predictions.length > 0 && (
                <div className="bg-slate-50/70 rounded-2xl p-3.5 border border-slate-100 space-y-2">
                  <p className="text-[10px] uppercase font-bold text-slate-500 tracking-wider">
                    Top-3 Ranked Predictions
                  </p>
                  <div className="space-y-1.5">
                    {aiResult.top_predictions.map((p, idx) => (
                      <div key={idx} className="flex items-center justify-between text-xs font-semibold">
                        <span className="text-slate-700 flex items-center gap-1.5">
                          <span className="w-4 h-4 rounded-full bg-slate-200 text-[10px] flex items-center justify-center font-bold text-slate-600">
                            {idx + 1}
                          </span>
                          {p.material}
                        </span>
                        <span className="text-slate-500 font-mono">
                          {(p.confidence * 100).toFixed(2)}%
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Low Confidence / Ambiguity Warning */}
              {aiResult.is_uncertain && (
                <div className="p-3.5 rounded-2xl bg-amber-500/10 border border-amber-300 text-xs text-amber-900 space-y-1">
                  <div className="flex items-center gap-1.5 font-bold text-amber-950">
                    <AlertTriangle className="w-4 h-4 text-amber-600 flex-shrink-0" />
                    Low Confidence Warning — Manual Review Recommended
                  </div>
                  <p className="text-[11px] leading-relaxed text-amber-800">
                    {aiResult.uncertainty_warning ||
                      `Prediction confidence is low (${Math.round((aiResult.confidence || 0) * 100)}% < 60%). The visual appearance matches multiple materials. Please inspect and manually select the correct material below.`}
                  </p>
                </div>
              )}

              {/* Prototype Limitations Disclosure */}
              <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200 text-xs text-slate-700 space-y-1">
                <div className="flex items-center gap-1.5 font-bold text-slate-800">
                  <AlertTriangle className="w-4 h-4 text-slate-500 flex-shrink-0" />
                  7-Class Prototype Notice
                </div>
                <p className="text-[11px] leading-relaxed text-slate-600">
                  {aiResult.limitations || (
                    'Supported classes: Cardboard, E-waste, Glass, Other, Paper, Plastic, Textile. Aluminum, Copper, and Steel are excluded from dedicated AI output classes due to training data unavailability.'
                  )}
                </p>
              </div>

              {/* Verification & Manual Review Prompt */}
              <div className="flex items-start gap-2 p-3 rounded-xl bg-slate-50 border border-slate-200">
                <ShieldCheck className="w-4 h-4 text-slate-600 mt-0.5 flex-shrink-0" />
                <p className="text-xs text-slate-600">
                  Please review the AI detection before publishing. You have full authority to override the material type if needed.
                </p>
              </div>

              {/* Action Buttons */}
              {!aiApplied ? (
                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={handleApplyAI}
                    className="flex-1 py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white text-xs font-bold transition flex items-center justify-center gap-1.5 shadow-sm"
                  >
                    ✓ Accept AI Classification
                  </button>
                  <button
                    type="button"
                    onClick={() => setAiResult(null)}
                    className="py-2.5 px-4 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-bold transition"
                  >
                    Reset
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-between p-2.5 rounded-xl bg-emerald-50 border border-emerald-200">
                  <span className="text-xs text-emerald-700 font-bold flex items-center gap-1.5">
                    <CheckCircle className="w-4 h-4 text-emerald-600" /> Applied to listing form
                  </span>
                  <button
                    type="button"
                    onClick={handleChangeManually}
                    className="text-xs text-slate-600 hover:text-purple-700 font-semibold transition flex items-center gap-1"
                  >
                    <RefreshCw className="w-3 h-3" /> Edit in Form
                  </button>
                </div>
              )}

              {/* Model Provenance */}
              <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-100">
                <span>Model: {aiResult.model_name || 'MobileNetV2'}</span>
                <span>Version: {aiResult.model_version || '7class-mobilenetv2-v1'}</span>
              </div>
            </div>
          )}
        </div>

        {/* ── RIGHT COLUMN: Listing Details & Pricing ──────── */}
        <div className="lg:col-span-7 space-y-6">

          {/* Material Details Card */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-5">
            <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider">
              2. Review Material Details
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Material Type Selection */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Material Type
                  {aiApplied && (
                    <span className="ml-2 text-[10px] text-purple-600 font-semibold bg-purple-50 px-1.5 py-0.5 rounded">
                      AI Applied
                    </span>
                  )}
                </label>
                <select
                  value={formData.material_type}
                  onChange={e => setFormData(p => ({ ...p, material_type: e.target.value }))}
                  className="w-full py-2.5 px-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-bold text-slate-900"
                >
                  <optgroup label="AI Supported Classes (7-Class Prototype)">
                    {AI_SUPPORTED_CLASSES.map(m => <option key={m} value={m}>{m}</option>)}
                  </optgroup>
                  <optgroup label="Other Marketplace Materials (Manual Entry Only)">
                    {ALL_MATERIALS.filter(m => !AI_SUPPORTED_CLASSES.includes(m)).map(m => (
                      <option key={m} value={m}>{m} (Manual)</option>
                    ))}
                  </optgroup>
                </select>
              </div>

              {/* Category */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">
                  Category
                  {aiApplied && (
                    <span className="ml-2 text-[10px] text-purple-600 font-semibold bg-purple-50 px-1.5 py-0.5 rounded">
                      AI Applied
                    </span>
                  )}
                </label>
                <select
                  value={formData.category}
                  onChange={e => setFormData(p => ({ ...p, category: e.target.value }))}
                  className="w-full py-2.5 px-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                >
                  {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                </select>
              </div>

              {/* Quantity */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Quantity</label>
                <div className="flex gap-2">
                  <input
                    type="number"
                    min="1"
                    step="any"
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
                    {['kg', 'tonnes', 'litres', 'units'].map(u => <option key={u} value={u}>{u}</option>)}
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
                  {QUALITIES.map(q => <option key={q} value={q}>{q}</option>)}
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
                  {CONDITIONS.map(c => <option key={c} value={c}>{c}</option>)}
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
                  {PURPOSES.map(p => <option key={p} value={p}>{p}</option>)}
                </select>
              </div>
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Description & Notes</label>
              <textarea
                rows={3}
                value={formData.description}
                onChange={e => setFormData(p => ({ ...p, description: e.target.value }))}
                className="w-full p-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                placeholder="e.g. Clean sorted PET plastic bottles, baled and free from contaminants."
              />
            </div>
          </div>

          {/* Pricing Card: Strictly Seller-Entered */}
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-5">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-extrabold text-slate-900 uppercase tracking-wider">
                3. Seller Asking Price
              </h3>
              <span className="text-[11px] font-semibold text-slate-400 bg-slate-100 px-2.5 py-0.5 rounded-full">
                No AI Price Suggestion
              </span>
            </div>
            <p className="text-xs text-slate-500">
              The seller decides the asking price per unit. The AI does not set, suggest, or predict prices on this page.
            </p>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Asking Price (₹ per {formData.unit})</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                required
                value={formData.asking_price}
                onChange={e => setFormData(p => ({ ...p, asking_price: e.target.value }))}
                className="w-full py-3.5 px-4 rounded-xl text-xl bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-black text-emerald-600"
                placeholder="e.g. 150.00"
              />
            </div>

            <button
              type="submit"
              disabled={isPublishing}
              className="w-full py-4 rounded-2xl bg-eco-600 hover:bg-eco-700 disabled:opacity-50 text-white font-extrabold text-sm shadow-md transition flex items-center justify-center gap-2"
            >
              {isPublishing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Publishing Listing to Marketplace…
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  Publish Verified Listing to Marketplace
                </>
              )}
            </button>
          </div>

        </div>
      </form>
    </div>
  );
};

export default NewMaterial;
