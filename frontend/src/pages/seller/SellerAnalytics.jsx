import React, { useState, useEffect } from 'react';
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
import {
  Leaf,
  Scale,
  TrendingUp,
  Layers,
  Award,
  Package,
  ReceiptText,
  DollarSign,
  AlertCircle
} from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import MetricCard from '../../components/MetricCard';
import ChartCard from '../../components/ChartCard';
import LoadingSpinner from '../../components/LoadingSpinner';

export const SellerAnalytics = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [materials, setMaterials] = useState([]);
  const [transactions, setTransactions] = useState([]);
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchSellerAnalytics = async () => {
      setLoading(true);
      setError('');
      try {
        const [statsRes, matRes, txRes, ovRes] = await Promise.all([
          api.get('/api/analytics/seller/me').catch(() => {
            return user?.id ? api.get(`/api/analytics/seller/${user.id}`) : Promise.resolve({ data: null });
          }),
          api.get('/api/materials' + (user?.id ? `?seller_id=${user.id}` : '')),
          api.get('/api/transactions'),
          api.get('/api/analytics/overview'),
        ]);

        setStats(statsRes?.data || null);
        setMaterials(matRes.data || []);
        // Filter seller transactions
        const myTxs = (txRes.data || []).filter(
          (t) => t.seller_id === user?.id || t.seller?.id === user?.id
        );
        setTransactions(myTxs);
        setOverview(ovRes.data || null);
      } catch (err) {
        console.error('Error fetching seller analytics:', err);
        setError('Failed to load server analytics. Please verify network connectivity or try again.');
      } finally {
        setLoading(false);
      }
    };

    fetchSellerAnalytics();
  }, [user]);

  if (loading) {
    return <LoadingSpinner text="Computing seller circular metrics & performance analytics..." />;
  }

  if (error) {
    return (
      <div className="p-6 bg-white rounded-3xl border border-rose-200 text-rose-700 space-y-3">
        <div className="flex items-center gap-3">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </div>
        <button
          onClick={() => window.location.reload()}
          className="px-4 py-2 rounded-xl bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold transition-all"
        >
          Retry Analytics
        </button>
      </div>
    );
  }

  // Aggregate material breakdown
  const pieAgg = {};
  const PIE_COLORS = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#ef4444', '#06b6d4', '#14b8a6'];
  materials.forEach((m) => {
    pieAgg[m.material_type] = (pieAgg[m.material_type] || 0) + (m.quantity_kg || 0);
  });
  const materialDistData = Object.entries(pieAgg).map(([name, value], i) => ({
    name,
    value: Math.round(value),
    color: PIE_COLORS[i % PIE_COLORS.length],
  }));

  // Build monthly sales trend from completed seller transactions
  const monthlyAgg = {};
  transactions
    .filter((t) => t.status === 'completed' || t.status === 'COMPLETED')
    .forEach((t) => {
      const month = t.created_at ? new Date(t.created_at).toLocaleString('default', { month: 'short' }) : 'Recent';
      monthlyAgg[month] = (monthlyAgg[month] || 0) + (t.quantity_kg || 0);
    });

  const salesTrendData = Object.keys(monthlyAgg).length > 0
    ? Object.entries(monthlyAgg).map(([month, volume_kg]) => ({ month, volume_kg: Math.round(volume_kg) }))
    : [
        { month: 'Jan', volume_kg: 0 },
        { month: 'Feb', volume_kg: 0 },
        { month: 'Mar', volume_kg: 0 },
      ];

  const totalVolume = stats?.total_volume_kg ?? materials.reduce((acc, m) => acc + (m.quantity_kg || 0), 0);
  const totalRevenue = stats?.total_revenue_inr ?? transactions.reduce((acc, t) => acc + (t.total_amount || 0), 0);
  const completedTxs = stats?.completed_transactions ?? transactions.filter((t) => t.status === 'completed' || t.status === 'COMPLETED').length;

  return (
    <div className="space-y-8 pb-16">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Seller Circular Analytics</h1>
        <p className="text-xs text-slate-500 mt-1">
          Real-time circular performance, recovered volume, inventory valuation, and dispatch metrics
        </p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Listed Volume"
          value={totalVolume}
          unit="kg"
          change=""
          changeType="neutral"
          icon={Package}
          color="eco"
        />
        <MetricCard
          title="Recovered Revenue"
          value={`₹${Math.round(totalRevenue).toLocaleString()}`}
          unit=""
          change=""
          changeType="neutral"
          icon={TrendingUp}
          color="blue"
        />
        <MetricCard
          title="Completed Dispatches"
          value={completedTxs}
          unit="deals"
          change=""
          changeType="neutral"
          icon={ReceiptText}
          color="amber"
        />
        <MetricCard
          title="Avoided CO₂ Equivalent"
          value={Math.round(totalVolume * 2.2)}
          unit="kg CO₂e"
          change=""
          changeType="neutral"
          icon={Leaf}
          color="purple"
        />
      </div>

      {/* Visual Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8">
          <ChartCard
            title="Monthly Recyclable Dispatch Trajectory"
            subtitle="Volume (kg) diverted through confirmed circular sales"
          >
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={salesTrendData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                  <Bar dataKey="volume_kg" name="Recovered Volume (kg)" fill="#10b981" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </div>

        <div className="lg:col-span-4">
          <ChartCard
            title="Material Mix Distribution"
            subtitle="Breakdown of listed recyclable feedstocks"
          >
            <div className="h-72 w-full flex items-center justify-center">
              {materialDistData.length === 0 ? (
                <p className="text-xs text-slate-400">No material listings yet</p>
              ) : (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={materialDistData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={75}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {materialDistData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }} />
                    <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                  </PieChart>
                </ResponsiveContainer>
              )}
            </div>
          </ChartCard>
        </div>
      </div>
    </div>
  );
};

export default SellerAnalytics;
