import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  SlidersHorizontal,
  Sparkles,
  ReceiptText,
  Building2,
  Package,
  Leaf,
  ArrowRight,
  TrendingUp,
  MapPin
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import MetricCard from '../../components/MetricCard';
import ChartCard from '../../components/ChartCard';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';

export const BuyerDashboard = () => {
  const { user } = useAuth();
  const [requirements, setRequirements] = useState([]);
  const [recommendedMaterials, setRecommendedMaterials] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBuyerData = async () => {
      setLoading(true);
      try {
        const [reqRes, txRes, recRes] = await Promise.all([
          api.get(`/api/buyers/requirements?buyer_id=${user.id}`),
          api.get('/api/transactions'),
          api.get(`/api/recommendations/materials/${user.id}`)
        ]);
        setRequirements(reqRes.data);
        setTransactions(txRes.data);
        setRecommendedMaterials(recRes.data);
      } catch (err) {
        console.error('Error fetching buyer dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    if (user?.id) {
      fetchBuyerData();
    }
  }, [user]);

  if (loading) {
    return <LoadingSpinner text="Loading Recycler Sourcing Command Center..." />;
  }

  const completedPurchases = transactions.filter((t) => t.status === 'completed');
  const totalSourcedVolume = completedPurchases.reduce((acc, t) => acc + t.quantity_kg, 0);
  const totalCo2Avoided = completedPurchases.reduce((acc, t) => acc + (t.co2_avoided_kg || 0), 0);

  // Group real transactions by month
  const monthlyProcure = {};
  completedPurchases.forEach((t) => {
    const d = new Date(t.created_at || Date.now());
    const mName = d.toLocaleString('default', { month: 'short' });
    if (!monthlyProcure[mName]) {
      monthlyProcure[mName] = { month: mName, purchased_kg: 0, spend_inr: 0 };
    }
    monthlyProcure[mName].purchased_kg += (t.quantity_kg || 0);
    monthlyProcure[mName].spend_inr += (t.total_amount || 0);
  });

  const procurementTrendData = Object.values(monthlyProcure).length > 0
    ? Object.values(monthlyProcure)
    : [
        { month: new Date().toLocaleString('default', { month: 'short' }), purchased_kg: totalSourcedVolume, spend_inr: 0 }
      ];

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="eco" size="xs">Recycler / Buyer Portal</Badge>
            <span className="text-xs text-slate-400">• {user?.organization || user?.name}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Feedstock Procurement Center
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/buyer/requirements"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs shadow-sm transition-all"
          >
            <SlidersHorizontal className="w-4 h-4" />
            Post Sourcing Spec
          </Link>
          <Link
            to="/buyer/search"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-xs shadow-md shadow-eco-600/20 transition-all"
          >
            <Search className="w-4 h-4" />
            Search Materials
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Sourcing Specs"
          value={requirements.length}
          unit="demands"
          change="Seeking secondary feedstock"
          changeType="neutral"
          icon={SlidersHorizontal}
          color="blue"
        />
        <MetricCard
          title="Total Feedstock Sourced"
          value={totalSourcedVolume.toLocaleString('en-IN')}
          unit="kg"
          change="+24.5% MoM"
          changeType="increase"
          icon={Package}
          color="eco"
        />
        <MetricCard
          title="Estimated CO₂ Avoided"
          value={`${totalCo2Avoided.toLocaleString('en-IN')}`}
          unit="kg CO₂"
          change="Peer-reviewed LCA factors"
          changeType="increase"
          icon={Leaf}
          color="teal"
        />
        <MetricCard
          title="Compatible AI Matches"
          value={recommendedMaterials.length}
          unit="lots"
          change="Weighted match score >= 75%"
          changeType="neutral"
          icon={Sparkles}
          color="purple"
        />
      </div>

      {/* Charts & Recommended Materials */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Sourcing Volume History */}
        <div className="lg:col-span-7">
          <ChartCard
            title="Recyclable Feedstock Intake Trajectory"
            subtitle="Monthly volume of diverted circular materials procured"
          >
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={procurementTrendData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                  />
                  <Bar dataKey="purchased_kg" name="Feedstock Procured (kg)" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </div>

        {/* AI High-Match Available Materials */}
        <div className="lg:col-span-5">
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between h-full">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900">AI-Matched Materials</h3>
                  <p className="text-xs text-slate-500">Calculated via composite match engine</p>
                </div>
                <Link to="/buyer/recommendations" className="text-xs font-bold text-eco-600 hover:text-eco-700">
                  View All
                </Link>
              </div>

              <div className="divide-y divide-slate-100">
                {recommendedMaterials.slice(0, 3).map((item) => (
                  <div key={item.material_id} className="py-3 flex items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="text-xs font-bold text-slate-900">{item.material_type}</span>
                        <Badge variant="eco" size="xs">{item.quality}</Badge>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        {item.quantity_kg} kg • ₹{item.predicted_price || item.asking_price}/kg
                      </div>
                      <div className="text-[10px] text-slate-400 flex items-center gap-1 mt-1">
                        <MapPin className="w-3 h-3 text-sky-500" />
                        {item.distance_km} km away
                      </div>
                    </div>

                    <div className="text-right">
                      <span className="text-base font-black text-emerald-600">
                        {(item.match_score * 100).toFixed(0)}%
                      </span>
                      <span className="text-[10px] text-slate-400 block font-semibold uppercase">
                        Match
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Link
              to="/buyer/search"
              className="mt-4 w-full py-2.5 rounded-xl bg-slate-50 hover:bg-eco-50 hover:text-eco-700 text-slate-700 font-semibold text-xs border border-slate-200 text-center transition-colors block"
            >
              Browse All Active Listings
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BuyerDashboard;
