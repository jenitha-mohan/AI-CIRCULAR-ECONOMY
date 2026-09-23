import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Package,
  TrendingUp,
  ReceiptText,
  Users,
  PlusCircle,
  Sparkles,
  ArrowRight,
  ShieldCheck,
  Scale
} from 'lucide-react';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
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

export const SellerDashboard = () => {
  const { user } = useAuth();
  const [materials, setMaterials] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [sellerStats, setSellerStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      setLoading(true);
      try {
        const params = user?.id ? `?seller_id=${user.id}` : '';
        const [matRes, txRes, anaRes] = await Promise.all([
          api.get(`/api/materials${params}`),
          api.get('/api/transactions'),
          api.get('/api/analytics/overview')
        ]);
        setMaterials(matRes.data);
        setTransactions(txRes.data);
        setAnalytics(anaRes.data);

        // Fetch seller-specific stats if we have user id
        if (user?.id) {
          try {
            const statsRes = await api.get(`/api/analytics/seller/${user.id}`);
            setSellerStats(statsRes.data);
          } catch (e) {
            // non-critical, proceed without stats
          }
        }
      } catch (err) {
        console.error('Error loading seller dashboard:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, [user]);

  if (loading) {
    return <LoadingSpinner text="Loading Seller Control Center..." />;
  }

  // Calculate metrics — prefer sellerStats if available
  const totalVolume = sellerStats?.total_volume_kg ?? materials.reduce((acc, m) => acc + (m.quantity_kg || 0), 0);
  const totalValue = sellerStats?.estimated_inventory_value_inr ?? materials.reduce((acc, m) => acc + ((m.predicted_price || 40) * (m.quantity_kg || 0)), 0);
  const soldTxs = transactions.filter((t) => t.status === 'completed');
  const totalSoldVolume = sellerStats?.sold_volume_kg ?? soldTxs.reduce((acc, t) => acc + t.quantity_kg, 0);

  // Chart datasets — computed from real API materials
  const pieAgg = {};
  const PIE_COLORS = ['#10b981', '#f59e0b', '#3b82f6', '#6366f1', '#8b5cf6', '#ef4444', '#14b8a6', '#f97316'];
  materials.forEach((m) => {
    pieAgg[m.material_type] = (pieAgg[m.material_type] || 0) + (m.quantity_kg || 0);
  });
  const materialDistData = Object.entries(pieAgg).map(([name, value], i) => ({
    name,
    value: Math.round(value),
    color: PIE_COLORS[i % PIE_COLORS.length],
  }));

  const priceComparisonData = materials.slice(0, 5).map((m) => ({
    name: m.material_type,
    ai_price: m.predicted_price || 40,
    ask_price: m.listings?.[0]?.asking_price || m.predicted_price || 42,
  }));

  const salesTrendData = analytics?.monthly_trends || [];

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="eco" size="xs">Seller Command Center</Badge>
            <span className="text-xs text-slate-400">• {user?.organization || user?.name}</span>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Inventory & Circular Sales
          </h1>
        </div>

        <Link
          to="/seller/materials/new"
          className="inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-xs sm:text-sm shadow-md shadow-eco-600/20 transition-all hover:scale-[1.02]"
        >
          <PlusCircle className="w-4 h-4" />
          List New Material with AI
        </Link>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Listings"
          value={materials.length}
          unit="lots"
          change="+2 this week"
          changeType="increase"
          icon={Package}
          color="eco"
        />
        <MetricCard
          title="Total Recyclables Sold"
          value={totalSoldVolume.toLocaleString('en-IN')}
          unit="kg"
          change="+18.4% MoM"
          changeType="increase"
          icon={Scale}
          color="blue"
        />
        <MetricCard
          title="Estimated Inventory Value"
          value={`₹${totalValue.toLocaleString('en-IN')}`}
          change="AI Market Valuation"
          changeType="neutral"
          icon={TrendingUp}
          color="amber"
        />
        <MetricCard
          title="Completed Transactions"
          value={soldTxs.length}
          unit="orders"
          change="100% Fulfilled"
          changeType="increase"
          icon={ReceiptText}
          color="purple"
        />
      </div>

      {/* Visual Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Monthly Sales Trend */}
        <div className="lg:col-span-8">
          <ChartCard
            title="Monthly Recyclable Dispatch Trajectory"
            subtitle="Historical volume (kg) recovered through circular exchange"
          >
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={salesTrendData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                  />
                  <Bar dataKey="volume_kg" name="Recovered Volume (kg)" fill="#10b981" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </div>

        {/* Material Distribution Donut */}
        <div className="lg:col-span-4">
          <ChartCard
            title="Material Mix Breakdown"
            subtitle="Composition of listed recyclable feedstocks"
          >
            <div className="h-72 w-full flex items-center justify-center">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={materialDistData}
                    cx="50%"
                    cy="50%"
                    innerRadius={55}
                    outerRadius={85}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {materialDistData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend iconType="circle" wrapperStyle={{ fontSize: '11px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </div>
      </div>

      {/* AI Valuation vs Asking Price Chart */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-6">
          <ChartCard
            title="AI Fair Value vs Asking Price Benchmark"
            subtitle="Comparison of Gradient Boosting prediction against listed ask prices (₹/kg)"
          >
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={priceComparisonData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                  <Bar dataKey="ai_price" name="AI Valuation (₹/kg)" fill="#8b5cf6" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="ask_price" name="Asking Price (₹/kg)" fill="#10b981" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </div>

        {/* Recent Listings Table */}
        <div className="lg:col-span-6">
          <div className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm flex flex-col justify-between h-full">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-base font-bold text-slate-900">Recent Material Listings</h3>
                  <p className="text-xs text-slate-500">Live active inventory items</p>
                </div>
                <Link to="/seller/materials" className="text-xs font-bold text-eco-600 hover:text-eco-700">
                  View All
                </Link>
              </div>

              <div className="divide-y divide-slate-100">
                {materials.slice(0, 4).map((m) => (
                  <div key={m.id} className="py-3 flex items-center justify-between gap-3">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-xl bg-slate-100 overflow-hidden flex-shrink-0">
                        <img
                          src={m.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600'}
                          alt={m.material_type}
                          className="w-full h-full object-cover"
                        />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-slate-900">{m.material_type}</div>
                        <div className="text-[11px] text-slate-500">{m.quantity_kg} kg • {m.quality} Grade</div>
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-xs font-bold text-emerald-600">
                        ₹{m.predicted_price || 40}/kg
                      </div>
                      <Badge variant="eco" size="xs">Active</Badge>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <Link
              to="/seller/materials/new"
              className="mt-4 w-full py-2.5 rounded-xl bg-slate-50 hover:bg-eco-50 hover:text-eco-700 text-slate-700 font-semibold text-xs border border-slate-200 text-center transition-colors block"
            >
              + Upload Another Lot
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SellerDashboard;
