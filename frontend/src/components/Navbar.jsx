import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Recycle, PlusCircle, User, LogOut, LayoutDashboard, ShoppingBag, ShieldCheck, Sparkles } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import Badge from './Badge';

export const Navbar = () => {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const getDashboardLink = () => {
    if (!user) return '/marketplace';
    if (user.role === 'seller') return '/seller/dashboard';
    if (user.role === 'buyer') return '/buyer/dashboard';
    if (user.role === 'admin') return '/admin/dashboard';
    return '/marketplace';
  };

  return (
    <header className="sticky top-0 z-40 bg-white/90 backdrop-blur-md border-b border-slate-200/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-8">
            <Link to="/" className="flex items-center gap-2.5 group">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-eco-600 to-emerald-400 flex items-center justify-center text-white shadow-sm shadow-eco-500/20 group-hover:scale-105 transition-transform">
                <Recycle className="w-6 h-6 animate-spin-slow" />
              </div>
              <div>
                <span className="font-extrabold text-slate-900 text-lg tracking-tight block leading-tight">
                  Circul<span className="text-eco-600">AI</span>
                </span>
                <span className="text-[10px] text-slate-400 font-semibold tracking-wider uppercase block">
                  Circular Marketplace
                </span>
              </div>
            </Link>

            {/* Navigation links */}
            <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-600">
              <Link to="/marketplace" className="hover:text-eco-600 transition-colors">
                Explore Materials
              </Link>
              <Link to="/about" className="hover:text-eco-600 transition-colors">
                Sustainability & AI
              </Link>
              {isAuthenticated && (
                <Link to={getDashboardLink()} className="hover:text-eco-600 transition-colors flex items-center gap-1.5">
                  <LayoutDashboard className="w-4 h-4" />
                  Dashboard
                </Link>
              )}
            </nav>
          </div>

          {/* Right Action Area */}
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                {user.role === 'seller' && (
                  <Link
                    to="/seller/materials/new"
                    className="hidden sm:inline-flex items-center gap-2 px-4 py-2 rounded-xl bg-eco-600 hover:bg-eco-700 text-white text-sm font-semibold shadow-sm shadow-eco-600/20 transition-all hover:shadow-md"
                  >
                    <PlusCircle className="w-4 h-4" />
                    List Recyclables with AI
                  </Link>
                )}

                {user.role === 'admin' && (
                  <Link
                    to="/admin/ml-performance"
                    className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-purple-50 text-purple-700 border border-purple-200 text-xs font-semibold"
                  >
                    <Sparkles className="w-3.5 h-3.5" />
                    ML Registry
                  </Link>
                )}

                {/* User Pill */}
                <div className="flex items-center gap-3 pl-3 border-l border-slate-200">
                  <div className="hidden lg:block text-right">
                    <div className="text-xs font-bold text-slate-900">{user.name}</div>
                    <div className="flex items-center justify-end gap-1 mt-0.5">
                      <Badge variant={user.role === 'admin' ? 'dark' : user.role === 'seller' ? 'eco' : 'info'} size="xs">
                        {user.role?.toUpperCase()}
                      </Badge>
                    </div>
                  </div>

                  <button
                    onClick={handleLogout}
                    title="Logout"
                    className="p-2 text-slate-400 hover:text-rose-600 hover:bg-rose-50 rounded-xl transition-colors"
                  >
                    <LogOut className="w-5 h-5" />
                  </button>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-3">
                <Link
                  to="/login"
                  className="px-4 py-2 rounded-xl text-sm font-semibold text-slate-700 hover:text-slate-900 hover:bg-slate-100 transition-colors"
                >
                  Log In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 rounded-xl text-sm font-semibold bg-eco-600 hover:bg-eco-700 text-white shadow-sm shadow-eco-600/20 transition-all"
                >
                  Join Marketplace
                </Link>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};

export default Navbar;
