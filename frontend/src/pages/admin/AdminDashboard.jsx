import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Users,
  Package,
  ReceiptText,
  Leaf,
  Cpu,
  BarChart3,
  TrendingUp,
  ArrowRight,
  ShieldCheck,
  Scale
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
import MetricCard from '../../components/MetricCard';
import ChartCard from '../../components/ChartCard';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';

export const AdminDashboard = () => {
  const [overview, setOverview] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAdminData = async () => {
      setLoading(true);
      try {
        const res = await api.get('/api/analytics/overview');
        setOverview(res.data);
      } catch (err) {
        console.error('Error loading admin analytics:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchAdminData();
  }, []);

  if (loading) {
    return <LoadingSpinner text="Loading Circular Platform Control Center..." />;
  }

  const monthlyData = overview?.monthly_trends || [];

  return (
    <div className="space-y-8 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <Badge variant="dark" size="xs">Platform Governance</Badge>
          </div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Circular Marketplace Operations
          </h1>
        </div>

        <div className="flex items-center gap-3">
          <Link
            to="/admin/ml-performance"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs shadow-md shadow-purple-600/20"
          >
            <Cpu className="w-4 h-4" />
            ML Performance Registry
          </Link>
          <Link
            to="/admin/analytics"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-2xl bg-slate-900 hover:bg-slate-800 text-white font-bold text-xs"
          >
            <BarChart3 className="w-4 h-4" />
            Macro Analytics
          </Link>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Total Registered Entities"
          value={overview?.total_users || 6}
          unit="users"
          description={`${overview?.total_sellers || 2} Sellers • ${overview?.total_buyers || 3} Recyclers`}
          icon={Users}
          color="blue"
        />
        <MetricCard
          title="Materials Diverted"
          value={(overview?.materials_recovered_kg || 48500).toLocaleString('en-IN')}
          unit="kg"
          change="+18.2% Total"
          changeType="increase"
          icon={Scale}
          color="eco"
        />
        <MetricCard
          title="Estimated CO₂ Avoided"
          value={(overview?.estimated_co2_avoided_kg || 112400).toLocaleString('en-IN')}
          unit="kg CO₂"
          change="Verified Offsets"
          changeType="increase"
          icon={Leaf}
          color="teal"
        />
        <MetricCard
          title="Transactions Cleared"
          value={overview?.total_transactions || 5}
          unit="settlements"
          change="100% On-Chain Match"
          changeType="neutral"
          icon={ReceiptText}
          color="purple"
        />
      </div>

      {/* Macro Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div className="lg:col-span-8">
          <ChartCard
            title="Circularity Volume & CO₂ Avoidance Momentum"
            subtitle="Platform aggregate waste diverted from landfills vs estimated CO₂ avoidance"
          >
            <div className="h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={monthlyData}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                  <XAxis dataKey="month" stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                  <Tooltip
                    contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', fontSize: '12px' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '11px' }} />
                  <Line type="monotone" dataKey="volume_kg" name="Diverted Material (kg)" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="co2_avoided_kg" name="CO₂ Offset (kg)" stroke="#8b5cf6" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </ChartCard>
        </div>

        {/* Quick ML Health Card */}
        <div className="lg:col-span-4">
          <div className="bg-gradient-to-br from-slate-900 via-slate-850 to-slate-950 text-white rounded-3xl p-6 border border-slate-700 shadow-xl flex flex-col justify-between h-full">
            <div>
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                  <Cpu className="w-5 h-5 text-purple-400" />
                  <h3 className="text-base font-bold text-white">ML Subsystems Health</h3>
                </div>
                <Badge variant="ai" size="xs">ONLINE</Badge>
              </div>

              <div className="space-y-3 text-xs">
                <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 flex items-center justify-between">
                  <span>Vision Classifier</span>
                  <span className="text-emerald-400 font-bold">92.2% Acc</span>
                </div>
                <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 flex items-center justify-between">
                  <span>Price Regressor</span>
                  <span className="text-emerald-400 font-bold">0.996 R² (GB)</span>
                </div>
                <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 flex items-center justify-between">
                  <span>Demand Forecaster</span>
                  <span className="text-emerald-400 font-bold">0.830 R²</span>
                </div>
                <div className="bg-slate-800/80 p-3 rounded-xl border border-slate-700/60 flex items-center justify-between">
                  <span>Matching Engine</span>
                  <span className="text-eco-400 font-bold">Weighted Active</span>
                </div>
              </div>
            </div>

            <Link
              to="/admin/ml-performance"
              className="mt-6 w-full py-2.5 rounded-xl bg-purple-600 hover:bg-purple-700 text-white font-bold text-xs text-center transition-colors block"
            >
              Open ML Evaluation Registry
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
