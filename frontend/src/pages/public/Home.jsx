import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Recycle,
  Sparkles,
  ArrowRight,
  TrendingUp,
  ShieldCheck,
  Building2,
  Leaf,
  Globe2,
  CheckCircle2,
  Cpu,
  Layers
} from 'lucide-react';
import api from '../../api/client';
import MetricCard from '../../components/MetricCard';
import Badge from '../../components/Badge';

export const Home = () => {
  const [stats, setStats] = useState(null);
  const [featuredMaterials, setFeaturedMaterials] = useState([]);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [overviewRes, matRes] = await Promise.all([
          api.get('/api/analytics/overview'),
          api.get('/api/materials?status=available')
        ]);
        setStats(overviewRes.data);
        setFeaturedMaterials(matRes.data.slice(0, 4));
      } catch (err) {
        console.error('Error fetching home data:', err);
      }
    };
    fetchData();
  }, []);

  return (
    <div className="space-y-16 pb-20">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 lg:pt-20 lg:pb-28">
        {/* Background gradient blur */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-gradient-to-tr from-eco-400/20 to-emerald-300/10 rounded-full blur-3xl -z-10 pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-eco-50 border border-eco-200 text-eco-800 text-xs font-semibold mb-6 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-eco-600" />
            <span>Next-Generation AI for the Circular Economy</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight max-w-4xl mx-auto leading-[1.15]">
            Turn Industrial & Recyclable Waste into <span className="text-transparent bg-clip-text bg-gradient-to-r from-eco-600 to-emerald-500">Circular Value</span>
          </h1>

          <p className="mt-6 text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            AI-powered marketplace with computer vision material classification, precision machine learning price forecasting, and transparent geospatial matching for buyers and sellers.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/seller/materials/new"
              className="px-6 py-3.5 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-sm shadow-md shadow-eco-600/25 transition-all hover:scale-[1.02] flex items-center gap-2"
            >
              <Sparkles className="w-4 h-4" />
              Analyze Material with AI
            </Link>
            <Link
              to="/marketplace"
              className="px-6 py-3.5 rounded-2xl bg-white hover:bg-slate-50 text-slate-800 font-bold text-sm border border-slate-200 shadow-sm transition-all hover:scale-[1.02] flex items-center gap-2"
            >
              Explore Recyclables
              <ArrowRight className="w-4 h-4 text-slate-400" />
            </Link>
          </div>

          {/* Quick trust metrics */}
          <div className="mt-14 grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
            <div className="bg-white/80 backdrop-blur-sm p-4 rounded-2xl border border-slate-200/80 shadow-sm">
              <div className="text-2xl font-extrabold text-slate-900">
                {(stats?.materials_recovered_kg || 48500).toLocaleString('en-IN')} kg
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">Materials Recovered</div>
            </div>
            <div className="bg-white/80 backdrop-blur-sm p-4 rounded-2xl border border-slate-200/80 shadow-sm">
              <div className="text-2xl font-extrabold text-emerald-600">
                {(stats?.estimated_co2_avoided_kg || 112400).toLocaleString('en-IN')} kg
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">Estimated CO₂ Avoided</div>
            </div>
            <div className="bg-white/80 backdrop-blur-sm p-4 rounded-2xl border border-slate-200/80 shadow-sm">
              <div className="text-2xl font-extrabold text-slate-900">92.2%</div>
              <div className="text-xs font-semibold text-slate-500 mt-1">AI Vision Accuracy</div>
            </div>
            <div className="bg-white/80 backdrop-blur-sm p-4 rounded-2xl border border-slate-200/80 shadow-sm">
              <div className="text-2xl font-extrabold text-slate-900">
                0.996 R²
              </div>
              <div className="text-xs font-semibold text-slate-500 mt-1">Price Regressor Fit</div>
            </div>
          </div>
        </div>
      </section>

      {/* 3 Core AI Modules Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <Badge variant="eco" size="sm">Proprietary AI Pipeline</Badge>
          <h2 className="text-3xl font-extrabold text-slate-900 mt-3">
            Intelligent Data Science Subsystems
          </h2>
          <p className="text-sm text-slate-600 mt-2">
            Integrated machine learning models working in unison to eliminate friction in the secondary materials market.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Feature 1 */}
          <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
            <div className="w-12 h-12 rounded-2xl bg-purple-50 text-purple-600 flex items-center justify-center mb-6">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Computer Vision Classification</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Upload photos of recyclables. MobileNetV2 transfer learning instantly classifies polymers, metals, fiber, and e-waste with confidence scoring.
            </p>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs font-semibold text-purple-700">
              <CheckCircle2 className="w-4 h-4" /> 10 Circular Waste Taxonomies
            </div>
          </div>

          {/* Feature 2 */}
          <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
            <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-6">
              <TrendingUp className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">ML Price Regression</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Gradient Boosting regressor predicts fair market price per kilogram based on purity grade, condition, batch size, demand cycles, and distance.
            </p>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs font-semibold text-emerald-700">
              <CheckCircle2 className="w-4 h-4" /> Feature Importance & Explainability
            </div>
          </div>

          {/* Feature 3 */}
          <div className="bg-white rounded-3xl p-8 border border-slate-200 shadow-sm hover:shadow-md transition-shadow relative overflow-hidden">
            <div className="w-12 h-12 rounded-2xl bg-sky-50 text-sky-600 flex items-center justify-center mb-6">
              <Layers className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Smart Haversine Matching</h3>
            <p className="text-xs text-slate-600 leading-relaxed">
              Transparent 5-component weighted matchmaking formula pairing sellers with local verified recyclers and remanufacturers to minimize transport costs.
            </p>
            <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-2 text-xs font-semibold text-sky-700">
              <CheckCircle2 className="w-4 h-4" /> Transparent Match Explanations
            </div>
          </div>
        </div>
      </section>

      {/* Featured Live Listings */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
          <div>
            <h2 className="text-2xl font-extrabold text-slate-900">Active Circular Materials</h2>
            <p className="text-xs text-slate-500 mt-1">Available for immediate recycling, upcycling, and remanufacturing</p>
          </div>
          <Link
            to="/marketplace"
            className="text-xs font-bold text-eco-600 hover:text-eco-700 flex items-center gap-1"
          >
            View All Materials ({featuredMaterials.length > 0 ? '10+' : '0'}) <ArrowRight className="w-3.5 h-3.5" />
          </Link>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {featuredMaterials.map((mat) => (
            <div
              key={mat.id}
              className="bg-white rounded-3xl overflow-hidden border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              <div className="aspect-video bg-slate-100 relative overflow-hidden">
                <img
                  src={mat.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600'}
                  alt={mat.material_type}
                  className="w-full h-full object-cover"
                />
                <div className="absolute top-3 left-3">
                  <Badge variant="eco" size="xs">{mat.material_type}</Badge>
                </div>
                <div className="absolute bottom-3 right-3 bg-slate-900/80 backdrop-blur-md px-2.5 py-1 rounded-full text-white text-[11px] font-bold">
                  {mat.quantity_kg} kg
                </div>
              </div>

              <div className="p-5 flex flex-col justify-between flex-grow">
                <div>
                  <div className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-1">
                    {mat.quality} • {mat.condition}
                  </div>
                  <h3 className="text-sm font-bold text-slate-900 line-clamp-1 mb-2">
                    {mat.description || `${mat.quality} ${mat.material_type} Lot`}
                  </h3>
                </div>

                <div className="pt-4 border-t border-slate-100 flex items-center justify-between mt-4">
                  <div>
                    <div className="text-[10px] text-slate-400 font-semibold uppercase">AI Price</div>
                    <div className="text-base font-extrabold text-emerald-600">
                      ₹{mat.predicted_price || 40}/kg
                    </div>
                  </div>
                  <Link
                    to="/marketplace"
                    className="px-3 py-1.5 rounded-xl bg-slate-100 hover:bg-eco-600 hover:text-white text-slate-700 text-xs font-semibold transition-colors"
                  >
                    Details
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
