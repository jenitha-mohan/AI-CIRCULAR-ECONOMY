import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Sparkles,
  Layers,
  ArrowRight,
  CheckCircle,
  AlertCircle,
  HelpCircle,
  Send,
  Loader2,
  Building2,
  Cpu
} from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import FileUploader from '../../components/FileUploader';
import AIAnalysisCard from '../../components/AIAnalysisCard';
import Badge from '../../components/Badge';

export const NewMaterial = () => {
  const { user } = useAuth();
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    material_type: 'Aluminum',
    quantity_kg: 500,
    quality: 'High',
    condition: 'Clean',
    intended_purpose: 'Recycling',
    description: '',
    image_url: '',
    asking_price: '',
  });

  const [selectedFile, setSelectedFile] = useState(null);
  const [imagePreview, setImagePreview] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isPublishing, setIsPublishing] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  // AI Analysis State
  const [classification, setClassification] = useState(null);
  const [pricePrediction, setPricePrediction] = useState(null);
  const [demand, setDemand] = useState(null);
  const [recommendedBuyers, setRecommendedBuyers] = useState([]);

  const MATERIALS = ['Aluminum', 'Copper', 'Steel', 'Plastic', 'Cardboard', 'Paper', 'Glass', 'Textile', 'E-waste', 'Other'];
  const QUALITIES = ['Industrial Grade', 'High', 'Medium', 'Low'];
  const CONDITIONS = ['Clean', 'Sorted', 'Baled', 'Mixed', 'Contaminated'];
  const PURPOSES = ['Recycling', 'Upcycling', 'Direct Reuse', 'Repurposing'];

  const handleFileSelected = (file) => {
    setSelectedFile(file);
    const localUrl = URL.createObjectURL(file);
    setImagePreview(localUrl);
    setError('');
  };

  const handleClearImage = () => {
    setSelectedFile(null);
    setImagePreview('');
    setFormData({ ...formData, image_url: '' });
  };

  const handleAnalyzeWithAI = async () => {
    setError('');
    setIsAnalyzing(true);
    try {
      let uploadedUrl = formData.image_url;
      let detectedClass = null;

      // 1. If image file selected, upload and run Vision Classifier
      if (selectedFile) {
        const uploadForm = new FormData();
        uploadForm.append('file', selectedFile);
        const uploadRes = await api.post('/api/materials/upload-image', uploadForm, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        uploadedUrl = uploadRes.data.file_path;
        detectedClass = uploadRes.data.classification;
        setClassification(detectedClass);
        setFormData((prev) => ({
          ...prev,
          image_url: uploadedUrl,
          material_type: detectedClass?.material || prev.material_type,
        }));
      }

      const activeMaterialType = detectedClass?.material || formData.material_type;

      // 2. Call Price Prediction API
      const priceRes = await api.post('/api/ml/predict-price', {
        material_type: activeMaterialType,
        weight_kg: parseFloat(formData.quantity_kg) || 100,
        quality: formData.quality,
        location: user?.location?.city || 'Coimbatore',
        demand_level: 'High',
        historical_price: 180.0,
        processing_cost: 5.0,
        transportation_distance: 20.0,
        month: new Date().getMonth() + 1,
        seller_type: 'Business',
        buyer_demand: 0.85,
        material_condition: formData.condition,
      });
      setPricePrediction(priceRes.data);

      // Auto-populate asking price with AI price if not set
      if (!formData.asking_price) {
        setFormData((prev) => ({ ...prev, asking_price: priceRes.data.predicted_price_per_kg }));
      }

      // 3. Call Demand Prediction API
      const demandRes = await api.post('/api/ml/predict-demand', {
        material_type: activeMaterialType,
        forecast_period: 'next_month',
        location: user?.location?.city || 'Coimbatore',
      });
      setDemand(demandRes.data);

      // NOTE: Buyer recommendations are fetched from the real recommendation engine
      // after the material listing is published (see handlePublishListing).
      setRecommendedBuyers([]);
    } catch (err) {
      console.error('AI Analysis failed:', err);
      setError('AI Analysis error: ' + (err.response?.data?.message || err.message));
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handlePublishListing = async (e) => {
    e.preventDefault();
    setError('');
    setIsPublishing(true);
    try {
      const payload = {
        material_type: formData.material_type,
        quantity_kg: parseFloat(formData.quantity_kg),
        quality: formData.quality,
        condition: formData.condition,
        intended_purpose: formData.intended_purpose,
        description: formData.description || `${formData.quality} Grade ${formData.material_type}`,
        image_url: formData.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600',
        predicted_price: pricePrediction?.predicted_price_per_kg || 40.0,
      };

      const askPrice = parseFloat(formData.asking_price) || payload.predicted_price;
      const matRes = await api.post(`/api/materials?asking_price=${askPrice}`, payload);
      const createdMaterial = matRes.data;

      // Fetch real buyer recommendations from the recommendation engine
      try {
        const recRes = await api.get(`/api/recommendations/buyers/${createdMaterial.id}?limit=5`);
        setRecommendedBuyers(recRes.data || []);
      } catch (recErr) {
        console.warn('Could not fetch buyer recommendations:', recErr.message);
        setRecommendedBuyers([]);
      }

      setSuccess(true);
      setTimeout(() => {
        navigate('/seller/materials');
      }, 2500);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to publish material listing.');
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="eco" size="sm">AI Material Studio</Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          Upload & Value Circular Materials
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Leverage transfer learning vision classification and machine learning pricing regression before publishing.
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {success && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center gap-2">
          <CheckCircle className="w-4 h-4 flex-shrink-0" />
          <span>Listing successfully analyzed and published to marketplace! Redirecting...</span>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Form & Image Upload */}
        <div className="lg:col-span-6 space-y-6">
          <div className="bg-white rounded-3xl p-6 sm:p-8 border border-slate-200/80 shadow-sm space-y-6">
            <h2 className="text-base font-bold text-slate-900">1. Material Photo & Specs</h2>

            {/* Image Uploader */}
            <FileUploader
              onFileSelected={handleFileSelected}
              previewUrl={imagePreview}
              onClear={handleClearImage}
              isUploading={isUploading}
            />

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Material Type */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Material Type</label>
                <select
                  value={formData.material_type}
                  onChange={(e) => setFormData({ ...formData, material_type: e.target.value })}
                  className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-semibold text-slate-800"
                >
                  {MATERIALS.map((m) => (
                    <option key={m} value={m}>{m}</option>
                  ))}
                </select>
              </div>

              {/* Quantity */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Quantity (kg)</label>
                <input
                  type="number"
                  min="1"
                  step="1"
                  required
                  value={formData.quantity_kg}
                  onChange={(e) => setFormData({ ...formData, quantity_kg: e.target.value })}
                  className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-bold"
                  placeholder="500"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {/* Quality */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Quality Grade</label>
                <select
                  value={formData.quality}
                  onChange={(e) => setFormData({ ...formData, quality: e.target.value })}
                  className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 text-slate-800"
                >
                  {QUALITIES.map((q) => (
                    <option key={q} value={q}>{q}</option>
                  ))}
                </select>
              </div>

              {/* Condition */}
              <div>
                <label className="block text-xs font-bold text-slate-700 mb-1">Physical Condition</label>
                <select
                  value={formData.condition}
                  onChange={(e) => setFormData({ ...formData, condition: e.target.value })}
                  className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 text-slate-800"
                >
                  {CONDITIONS.map((c) => (
                    <option key={c} value={c}>{c}</option>
                  ))}
                </select>
              </div>
            </div>

            {/* Purpose */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Intended Circular Purpose</label>
              <select
                value={formData.intended_purpose}
                onChange={(e) => setFormData({ ...formData, intended_purpose: e.target.value })}
                className="w-full py-2.5 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 text-slate-800"
              >
                {PURPOSES.map((p) => (
                  <option key={p} value={p}>{p}</option>
                ))}
              </select>
            </div>

            {/* Description */}
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">Description / Scrap Specifications</label>
              <textarea
                rows="3"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                className="w-full p-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                placeholder="e.g. 6063 clean aluminum extrusion scrap, cut into 1-meter lengths, degreased."
              ></textarea>
            </div>

            {/* AI Analyze Button */}
            <button
              type="button"
              onClick={handleAnalyzeWithAI}
              disabled={isAnalyzing}
              className="w-full py-3.5 rounded-2xl bg-gradient-to-r from-purple-600 via-purple-700 to-indigo-700 hover:from-purple-700 hover:to-indigo-800 text-white font-bold text-sm shadow-md shadow-purple-600/20 transition-all flex items-center justify-center gap-2"
            >
              {isAnalyzing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Running AI Models & Matchmaker...
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  Analyze with AI
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: AI Analysis & Valuation Display */}
        <div className="lg:col-span-6 space-y-6">
          {pricePrediction || classification ? (
            <div className="space-y-6">
              <AIAnalysisCard
                classification={classification}
                pricePrediction={pricePrediction}
                demand={demand}
                recommendedBuyers={recommendedBuyers}
              />

              {/* Publish Final Confirmation */}
              <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
                <h3 className="text-sm font-bold text-slate-900">2. Confirm Marketplace Pricing</h3>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">
                    Your Asking Price (₹/kg)
                  </label>
                  <input
                    type="number"
                    step="0.5"
                    value={formData.asking_price}
                    onChange={(e) => setFormData({ ...formData, asking_price: e.target.value })}
                    className="w-full py-2.5 px-3 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-extrabold text-emerald-600"
                    placeholder={pricePrediction?.predicted_price_per_kg?.toString() || '40'}
                  />
                  <p className="text-[11px] text-slate-400 mt-1">
                    AI Suggested Fair Market Price: ₹{pricePrediction?.predicted_price_per_kg}/kg
                  </p>
                </div>

                <button
                  type="button"
                  onClick={handlePublishListing}
                  disabled={isPublishing}
                  className="w-full py-3.5 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-sm shadow-md shadow-eco-600/20 transition-all flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  {isPublishing ? 'Publishing Listing...' : 'Publish Listing to Marketplace'}
                </button>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-3xl p-12 text-center border border-slate-200/80 shadow-sm h-full flex flex-col items-center justify-center space-y-4">
              <div className="w-16 h-16 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center">
                <Sparkles className="w-8 h-8 animate-pulse" />
              </div>
              <h3 className="text-base font-bold text-slate-900">AI Valuation Awaiting Input</h3>
              <p className="text-xs text-slate-500 max-w-sm leading-relaxed">
                Upload your recyclable material image on the left and click <strong>"Analyze with AI"</strong> to generate instant vision classification, ML price regression, and buyer matching.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default NewMaterial;
