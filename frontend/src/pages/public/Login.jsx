import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Recycle, Lock, Mail, ArrowRight, ShieldCheck, UserCheck, AlertCircle } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';

export const Login = () => {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const user = await login(email, password);
      if (user.role === 'seller') navigate('/seller/dashboard');
      else if (user.role === 'buyer') navigate('/buyer/dashboard');
      else if (user.role === 'admin') navigate('/admin/dashboard');
      else navigate('/marketplace');
    } catch (err) {
      setError(err.response?.data?.message || err.response?.data?.detail || 'Invalid email or password');
    } finally {
      setLoading(false);
    }
  };

  const handleDemoLogin = async (demoEmail, demoPassword) => {
    setEmail(demoEmail);
    setPassword(demoPassword);
    setError('');
    setLoading(true);
    try {
      const user = await login(demoEmail, demoPassword);
      if (user.role === 'seller') navigate('/seller/dashboard');
      else if (user.role === 'buyer') navigate('/buyer/dashboard');
      else if (user.role === 'admin') navigate('/admin/dashboard');
      else navigate('/marketplace');
    } catch (err) {
      setError('Demo login failed: ' + (err.response?.data?.message || err.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[80vh] flex items-center justify-center px-4 sm:px-6 lg:px-8 py-12">
      <div className="max-w-md w-full space-y-8 bg-white p-8 rounded-3xl border border-slate-200 shadow-xl">
        <div className="text-center">
          <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-eco-600 to-emerald-400 flex items-center justify-center text-white shadow-sm mx-auto mb-3">
            <Recycle className="w-6 h-6" />
          </div>
          <h2 className="text-2xl font-extrabold text-slate-900 tracking-tight">Welcome Back</h2>
          <p className="text-xs text-slate-500 mt-1">
            Access your AI circular economy marketplace portal
          </p>
        </div>

        {error && (
          <div className="p-3.5 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Demo Account Quick Switch */}
        <div className="bg-slate-50 p-3.5 rounded-2xl border border-slate-200/80">
          <div className="text-[11px] font-bold text-slate-500 uppercase tracking-wider mb-2">
            Quick 1-Click Demo Login:
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              onClick={() => handleDemoLogin('seller@ecotextiles.com', 'Seller@123')}
              className="py-1.5 px-2 rounded-xl bg-white hover:bg-eco-50 hover:text-eco-700 hover:border-eco-300 text-slate-700 font-semibold text-xs border border-slate-200 shadow-2xs transition-colors"
            >
              🌱 Seller
            </button>
            <button
              type="button"
              onClick={() => handleDemoLogin('buyer@greenplast.com', 'Buyer@123')}
              className="py-1.5 px-2 rounded-xl bg-white hover:bg-sky-50 hover:text-sky-700 hover:border-sky-300 text-slate-700 font-semibold text-xs border border-slate-200 shadow-2xs transition-colors"
            >
              🏭 Buyer
            </button>
            <button
              type="button"
              onClick={() => handleDemoLogin('admin@circulareconomy.com', 'Admin@123')}
              className="py-1.5 px-2 rounded-xl bg-white hover:bg-purple-50 hover:text-purple-700 hover:border-purple-300 text-slate-700 font-semibold text-xs border border-slate-200 shadow-2xs transition-colors"
            >
              ⚡ Admin
            </button>
          </div>
        </div>

        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Email Address</label>
            <div className="relative">
              <Mail className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                placeholder="name@company.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Password</label>
            <div className="relative">
              <Lock className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-sm shadow-md shadow-eco-600/20 transition-all flex items-center justify-center gap-2"
          >
            {loading ? 'Authenticating...' : 'Sign In'}
            <ArrowRight className="w-4 h-4" />
          </button>
        </form>

        <div className="text-center text-xs text-slate-500 pt-2 border-t border-slate-100">
          Don't have an account?{' '}
          <Link to="/register" className="font-bold text-eco-600 hover:text-eco-700">
            Register new account
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
