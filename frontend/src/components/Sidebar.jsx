import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  PlusCircle,
  Package,
  Users,
  Search,
  Sparkles,
  ReceiptText,
  BarChart3,
  Cpu,
  SlidersHorizontal,
  Leaf
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

export const Sidebar = () => {
  const { user } = useAuth();
  if (!user) return null;

  const role = user.role || 'seller';

  const sellerLinks = [
    { to: '/seller/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/seller/materials/new', label: 'AI Material Studio', icon: PlusCircle, highlight: true },
    { to: '/seller/materials', label: 'My Materials', icon: Package },
    { to: '/seller/recommendations', label: 'Buyer Matches', icon: Sparkles },
    { to: '/seller/transactions', label: 'Transactions', icon: ReceiptText },
  ];

  const buyerLinks = [
    { to: '/buyer/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/buyer/search', label: 'Material Search', icon: Search },
    { to: '/buyer/requirements', label: 'Sourcing Specs', icon: SlidersHorizontal },
    { to: '/buyer/recommendations', label: 'AI Recommended', icon: Sparkles, highlight: true },
    { to: '/buyer/transactions', label: 'Purchases', icon: ReceiptText },
  ];

  const adminLinks = [
    { to: '/admin/dashboard', label: 'Control Center', icon: LayoutDashboard },
    { to: '/admin/users', label: 'User Management', icon: Users },
    { to: '/admin/materials', label: 'Materials & Listings', icon: Package },
    { to: '/admin/transactions', label: 'Transactions', icon: ReceiptText },
    { to: '/admin/analytics', label: 'Circular Analytics', icon: BarChart3 },
    { to: '/admin/ml-performance', label: 'ML Performance Registry', icon: Cpu, highlight: true },
  ];

  const links = role === 'admin' ? adminLinks : role === 'buyer' ? buyerLinks : sellerLinks;

  return (
    <aside className="w-64 bg-white border-r border-slate-200/80 min-h-[calc(100vh-4rem)] p-4 flex flex-col justify-between hidden md:flex">
      <div className="space-y-6">
        <div>
          <div className="px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">
            {role} Portal
          </div>
          <nav className="space-y-1">
            {links.map((link) => {
              const Icon = link.icon;
              return (
                <NavLink
                  key={link.to}
                  to={link.to}
                  className={({ isActive }) =>
                    `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-semibold transition-all ${
                      isActive
                        ? link.highlight
                          ? 'bg-purple-600 text-white shadow-sm shadow-purple-600/30'
                          : 'bg-eco-600 text-white shadow-sm shadow-eco-600/30'
                        : link.highlight
                        ? 'text-purple-700 bg-purple-50/70 hover:bg-purple-100/70'
                        : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100/80'
                    }`
                  }
                >
                  <Icon className="w-4 h-4" />
                  <span>{link.label}</span>
                </NavLink>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Sustainable Circular Tip */}
      <div className="bg-gradient-to-br from-emerald-50 to-eco-100/60 p-4 rounded-2xl border border-emerald-200/60">
        <div className="flex items-center gap-2 text-eco-800 text-xs font-bold mb-1">
          <Leaf className="w-4 h-4 text-eco-600" />
          Circular Tip
        </div>
        <p className="text-[11px] text-slate-600 leading-relaxed">
          High purity sorted non-ferrous metals reduce carbon emissions by up to 95% compared to virgin extraction.
        </p>
      </div>
    </aside>
  );
};

export default Sidebar;
