import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Sparkles, Building2, MapPin, CheckCircle, Package } from 'lucide-react';
import api from '../../api/client';
import AIAnalysisCard from '../../components/AIAnalysisCard';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';

export const MaterialDetail = () => {
  const { id } = useParams();
  const [material, setMaterial] = useState(null);
  const [recommendedBuyers, setRecommendedBuyers] = useState([]);
  const [pricePrediction, setPricePrediction] = useState(null);
  const [demand, setDemand] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const matRes = await api.get(`/api/materials/${id}`);
        setMaterial(matRes.data);

        // Fetch buyer recommendations
        const recRes = await api.get(`/api/recommendations/buyers/${id}`);
        setRecommendedBuyers(recRes.data);

        // Fetch Price & Demand
        const [pRes, dRes] = await Promise.all([
          api.post('/api/ml/predict-price', {
            material_type: matRes.data.material_type,
            weight_kg: matRes.data.quantity_kg,
            quality: matRes.data.quality,
            location: 'Coimbatore',
            demand_level: 'High',
            historical_price: 180.0,
            processing_cost: 5.0,
            transportation_distance: 20.0,
            month: 9,
            seller_type: 'Business',
            buyer_demand: 0.85,
            material_condition: matRes.data.condition,
          }),
          api.post('/api/ml/predict-demand', {
            material_type: matRes.data.material_type,
          })
        ]);
        setPricePrediction(pRes.data);
        setDemand(dRes.data);
      } catch (err) {
        console.error('Error loading material detail:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [id]);

  if (loading) {
    return <LoadingSpinner text="Generating live AI analysis and matching buyers..." />;
  }

  if (!material) {
    return (
      <div className="text-center py-16 space-y-3">
        <p className="text-sm text-slate-500">Material lot not found.</p>
        <Link to="/seller/materials" className="text-xs font-bold text-eco-600">Back to Inventory</Link>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      <div>
        <Link to="/seller/materials" className="inline-flex items-center gap-1 text-xs font-bold text-slate-500 hover:text-slate-900 mb-4">
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Inventory
        </Link>
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="eco" size="xs">{material.material_type}</Badge>
          <Badge variant="default" size="xs">{material.quality} Grade</Badge>
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          {material.description || `${material.quality} ${material.material_type} Lot`}
        </h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-4 space-y-6">
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
            <div className="aspect-video rounded-2xl overflow-hidden bg-slate-100">
              <img
                src={material.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600'}
                alt={material.material_type}
                className="w-full h-full object-cover"
              />
            </div>
            <div className="space-y-2 text-xs">
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Available Weight</span>
                <span className="font-bold text-slate-900">{material.quantity_kg} kg</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Condition</span>
                <span className="font-bold text-slate-900">{material.condition}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">Intended Purpose</span>
                <span className="font-bold text-slate-900">{material.intended_purpose}</span>
              </div>
              <div className="flex justify-between py-1.5 border-b border-slate-100">
                <span className="text-slate-500">AI Valuation</span>
                <span className="font-bold text-emerald-600">₹{material.predicted_price}/kg</span>
              </div>
              <div className="flex justify-between py-1.5">
                <span className="text-slate-500">Batch Total Est.</span>
                <span className="font-bold text-slate-900">
                  ₹{((material.predicted_price || 40) * material.quantity_kg).toLocaleString('en-IN')}
                </span>
              </div>
            </div>
          </div>
        </div>

        <div className="lg:col-span-8 space-y-6">
          <AIAnalysisCard
            classification={{
              material: material.material_type,
              confidence: 0.94,
            }}
            pricePrediction={pricePrediction}
            demand={demand}
            recommendedBuyers={recommendedBuyers}
          />
        </div>
      </div>
    </div>
  );
};

export default MaterialDetail;
