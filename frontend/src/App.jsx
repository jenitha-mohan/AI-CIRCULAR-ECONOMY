import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, Outlet, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';

// Components
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Footer from './components/Footer';

// Public Pages
import Home from './pages/public/Home';
import About from './pages/public/About';
import Marketplace from './pages/public/Marketplace';
import Login from './pages/public/Login';
import Register from './pages/public/Register';

// Seller Pages
import SellerDashboard from './pages/seller/SellerDashboard';
import SellerMaterials from './pages/seller/SellerMaterials';
import NewMaterial from './pages/seller/NewMaterial';
import MaterialDetail from './pages/seller/MaterialDetail';
import SellerRecommendations from './pages/seller/SellerRecommendations';
import SellerOffers from './pages/seller/SellerOffers';
import SellerTransactions from './pages/seller/SellerTransactions';

// Buyer Pages
import BuyerDashboard from './pages/buyer/BuyerDashboard';
import BuyerSearch from './pages/buyer/BuyerSearch';
import BuyerRequirements from './pages/buyer/BuyerRequirements';
import BuyerRecommendations from './pages/buyer/BuyerRecommendations';
import BuyerOffers from './pages/buyer/BuyerOffers';
import BuyerTransactions from './pages/buyer/BuyerTransactions';

// Admin Pages
import AdminDashboard from './pages/admin/AdminDashboard';
import AdminUsers from './pages/admin/AdminUsers';
import AdminMaterials from './pages/admin/AdminMaterials';
import AdminTransactions from './pages/admin/AdminTransactions';
import AdminAnalytics from './pages/admin/AdminAnalytics';
import AdminMLPerformance from './pages/admin/AdminMLPerformance';

// Public Layout
const PublicLayout = () => {
  return (
    <div className="min-h-screen flex flex-col bg-[#f8fafc]">
      <Navbar />
      <main className="flex-grow">
        <Outlet />
      </main>
      <Footer />
    </div>
  );
};

// Dashboard Layout (with Sidebar)
const DashboardLayout = () => {
  const { isAuthenticated, loading, user } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#f8fafc]">
        <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-eco-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  // Role-based route protection
  const path = location.pathname;
  const role = user?.role;

  if (path.startsWith('/seller') && role !== 'seller' && role !== 'admin') {
    return <Navigate to={`/${role}/dashboard`} replace />;
  }
  if (path.startsWith('/buyer') && role !== 'buyer' && role !== 'admin') {
    return <Navigate to={`/${role}/dashboard`} replace />;
  }
  if (path.startsWith('/admin') && role !== 'admin') {
    return <Navigate to={`/${role}/dashboard`} replace />;
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#f8fafc]">
      <Navbar />
      <div className="flex flex-1 max-w-7xl w-full mx-auto">
        <Sidebar />
        <main className="flex-1 p-4 sm:p-6 lg:p-8 min-w-0">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public Routes */}
          <Route element={<PublicLayout />}>
            <Route path="/" element={<Home />} />
            <Route path="/about" element={<About />} />
            <Route path="/marketplace" element={<Marketplace />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
          </Route>

          {/* Seller Routes */}
          <Route path="/seller" element={<DashboardLayout />}>
            <Route path="dashboard" element={<SellerDashboard />} />
            <Route path="materials" element={<SellerMaterials />} />
            <Route path="materials/new" element={<NewMaterial />} />
            <Route path="materials/:id" element={<MaterialDetail />} />
            <Route path="offers" element={<SellerOffers />} />
            <Route path="recommendations" element={<SellerRecommendations />} />
            <Route path="transactions" element={<SellerTransactions />} />
          </Route>

          {/* Buyer Routes */}
          <Route path="/buyer" element={<DashboardLayout />}>
            <Route path="dashboard" element={<BuyerDashboard />} />
            <Route path="search" element={<BuyerSearch />} />
            <Route path="offers" element={<BuyerOffers />} />
            <Route path="requirements" element={<BuyerRequirements />} />
            <Route path="recommendations" element={<BuyerRecommendations />} />
            <Route path="transactions" element={<BuyerTransactions />} />
          </Route>

          {/* Admin Routes */}
          <Route path="/admin" element={<DashboardLayout />}>
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="users" element={<AdminUsers />} />
            <Route path="materials" element={<AdminMaterials />} />
            <Route path="transactions" element={<AdminTransactions />} />
            <Route path="analytics" element={<AdminAnalytics />} />
            <Route path="ml-performance" element={<AdminMLPerformance />} />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}
