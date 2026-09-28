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
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[650px] h-[650px] bg-gradient-to-tr from-eco-400/20 to-emerald-300/10 rounded-full blur-3xl -z-10 pointer-events-none"></div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-eco-50 border border-eco-200 text-eco-800 text-xs font-semibold mb-6 shadow-sm">
            <Sparkles className="w-3.5 h-3.5 text-eco-600" />
            <span>AI Circular Economy Marketplace</span>
          </div>

          <h1 className="text-4xl sm:text-6xl font-extrabold text-slate-900 tracking-tight max-w-4xl mx-auto leading-[1.15]">
            Turn Waste Into <span className="text-transparent bg-clip-text bg-gradient-to-r from-eco-600 to-emerald-500">Value</span>
          </h1>

          <p className="mt-6 text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            An AI-powered marketplace that connects sellers of recyclable materials with buyers who need them.
          </p>

          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/register/seller"
              className="px-6 py-3.5 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-sm shadow-md shadow-eco-600/25 transition-all hover:scale-[1.02] flex items-center gap-2"
            >
              Register as Seller
            </Link>
            <Link
              to="/register/buyer"
              className="px-6 py-3.5 rounded-2xl bg-sky-600 hover:bg-sky-700 text-white font-bold text-sm shadow-md shadow-sky-600/25 transition-all hover:scale-[1.02] flex items-center gap-2"
            >
              Register as Buyer
            </Link>
            <Link
              to="/login"
              className="px-6 py-3.5 rounded-2xl bg-white text-slate-700 hover:bg-slate-50 font-bold text-sm border border-slate-200 shadow-sm transition-all hover:scale-[1.02] flex items-center gap-2"
            >
              Login
            </Link>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 bg-slate-50 py-16 rounded-3xl">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <h2 className="text-3xl font-extrabold text-slate-900">
            How It Works
          </h2>
          <p className="text-sm text-slate-600 mt-3">
            A simple, transparent process to list and sell recyclable materials.
          </p>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
            <div className="text-4xl font-extrabold text-eco-100 mb-4">01</div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Add Your Waste</h3>
            <p className="text-sm text-slate-600">Seller uploads recyclable material details and images.</p>
          </div>
          
          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100 relative">
            <div className="text-4xl font-extrabold text-eco-100 mb-4">02</div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">AI Analysis</h3>
            <p className="text-sm text-slate-600">AI identifies the material and provides estimated market price guidance.</p>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
            <div className="text-4xl font-extrabold text-eco-100 mb-4">03</div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Find Buyers</h3>
            <p className="text-sm text-slate-600">AI matches the material with suitable buyers based on distance and needs.</p>
          </div>

          <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-100">
            <div className="text-4xl font-extrabold text-eco-100 mb-4">04</div>
            <h3 className="text-lg font-bold text-slate-900 mb-2">Sell & Negotiate</h3>
            <p className="text-sm text-slate-600">Buyer and seller negotiate and confirm the final deal.</p>
          </div>
        </div>

        <div className="mt-8 text-center">
          <p className="text-sm font-bold text-eco-700 bg-eco-50 inline-block px-4 py-2 rounded-lg border border-eco-200">
            IMPORTANT: AI provides price guidance. The seller decides the asking price.
          </p>
        </div>
      </section>

      {/* AI Features Section */}
      <section id="features" className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mt-16">
        <div className="text-center max-w-2xl mx-auto mb-12">
          <Badge variant="eco" size="sm">Powered by AI</Badge>
          <h2 className="text-3xl font-extrabold text-slate-900 mt-3">
            AI Features
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center mb-4">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-2">AI Material Identification</h3>
            <p className="text-sm text-slate-600">Identify recyclable materials automatically from uploaded images.</p>
          </div>

          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4">
              <TrendingUp className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-2">AI Price Guidance</h3>
            <p className="text-sm text-slate-600">Estimate the market value using historical and material data.</p>
          </div>

          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center mb-4">
              <Layers className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-2">Smart Buyer Matching</h3>
            <p className="text-sm text-slate-600">Find buyers based on material, quantity, quality and location.</p>
          </div>
          
          <div className="bg-white rounded-3xl p-6 border border-slate-200 shadow-sm">
            <div className="w-10 h-10 rounded-xl bg-amber-50 text-amber-600 flex items-center justify-center mb-4">
              <Globe2 className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-slate-900 mb-2">Demand Insights</h3>
            <p className="text-sm text-slate-600">Understand demand trends for recyclable materials.</p>
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
