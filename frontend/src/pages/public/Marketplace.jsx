import React, { useState, useEffect } from 'react';
import {
  Search,
  Filter,
  ArrowUpDown,
  MapPin,
  Building2,
  Sparkles,
  CheckCircle,
  Tag,
  ShieldCheck,
  ShoppingBag,
  ExternalLink
} from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/Badge';
import Modal from '../../components/Modal';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import { useAuth } from '../../context/AuthContext';

export const Marketplace = () => {
  const { user, isAuthenticated } = useAuth();
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedMaterial, setSelectedMaterial] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isBuying, setIsBuying] = useState(false);
  const [buySuccess, setBuySuccess] = useState(false);

  // Filters
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('All');
  const [qualityFilter, setQualityFilter] = useState('All');
  const [sortBy, setSortBy] = useState('newest');

  const CATEGORIES = ['All', 'Aluminum', 'Copper', 'Steel', 'Plastic', 'Cardboard', 'Paper', 'Glass', 'Textile', 'E-waste', 'Other'];

  const fetchMaterials = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/materials?status=available');
      setMaterials(res.data);
    } catch (err) {
      console.error('Error fetching materials:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMaterials();
  }, []);

  const filteredMaterials = materials
    .filter((m) => {
      const matchSearch =
        m.material_type.toLowerCase().includes(search.toLowerCase()) ||
        (m.description && m.description.toLowerCase().includes(search.toLowerCase())) ||
        (m.seller?.organization && m.seller.organization.toLowerCase().includes(search.toLowerCase()));
      const matchCategory = categoryFilter === 'All' || m.material_type.toLowerCase() === categoryFilter.toLowerCase();
      const matchQuality = qualityFilter === 'All' || m.quality === qualityFilter;
      return matchSearch && matchCategory && matchQuality;
    })
    .sort((a, b) => {
      if (sortBy === 'price-asc') return (a.predicted_price || 0) - (b.predicted_price || 0);
      if (sortBy === 'price-desc') return (b.predicted_price || 0) - (a.predicted_price || 0);
      if (sortBy === 'qty-desc') return b.quantity_kg - a.quantity_kg;
      return new Date(b.created_at) - new Date(a.created_at);
    });

  const handleOpenDetail = (mat) => {
    setSelectedMaterial(mat);
    setIsModalOpen(true);
    setBuySuccess(false);
  };

  const handlePurchase = async () => {
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }
    if (!selectedMaterial) return;

    setIsBuying(true);
    try {
      await api.post('/api/transactions', {
        listing_id: selectedMaterial.listings?.[0]?.id || null,
        seller_id: selectedMaterial.seller_id,
        material_type: selectedMaterial.material_type,
        quantity_kg: selectedMaterial.quantity_kg,
        agreed_price: selectedMaterial.predicted_price || 40.0
      });
      setBuySuccess(true);
      fetchMaterials();
    } catch (err) {
      console.error('Error creating transaction:', err);
    } finally {
      setIsBuying(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
            Circular Materials Marketplace
          </h1>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Browse verified industrial recyclables, upcyclable scrap lots, and circular feedstocks
          </p>
        </div>
      </div>

      {/* Search & Filter Bar */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 md:grid-cols-4 gap-3">
          {/* Search Input */}
          <div className="relative sm:col-span-2">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search materials, polymer grades, alloys..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
            />
          </div>

          {/* Quality Filter */}
          <div>
            <select
              value={qualityFilter}
              onChange={(e) => setQualityFilter(e.target.value)}
              className="w-full py-2 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-medium text-slate-700"
            >
              <option value="All">All Quality Grades</option>
              <option value="Industrial Grade">Industrial Grade</option>
              <option value="High">High Grade</option>
              <option value="Medium">Medium Grade</option>
              <option value="Low">Low Grade</option>
            </select>
          </div>

          {/* Sort By */}
          <div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full py-2 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-medium text-slate-700"
            >
              <option value="newest">Sort: Newest First</option>
              <option value="price-asc">Price: Low to High</option>
              <option value="price-desc">Price: High to Low</option>
              <option value="qty-desc">Quantity: High to Low</option>
            </select>
          </div>
        </div>

        {/* Category Filter Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 pt-1 text-xs">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-xl font-semibold whitespace-nowrap transition-colors ${
                categoryFilter === cat
                  ? 'bg-eco-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200/80'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Materials Grid */}
      {loading ? (
        <LoadingSpinner text="Loading verified circular materials..." />
      ) : filteredMaterials.length === 0 ? (
        <EmptyState
          title="No materials match your filters"
          description="Try broadening your search term or clearing quality filters."
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredMaterials.map((mat) => (
            <div
              key={mat.id}
              onClick={() => handleOpenDetail(mat)}
              className="bg-white rounded-3xl overflow-hidden border border-slate-200/80 shadow-sm hover:shadow-md transition-all hover:translate-y-[-2px] cursor-pointer flex flex-col justify-between group"
            >
              <div className="aspect-video bg-slate-100 relative overflow-hidden">
                <img
                  src={mat.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600'}
                  alt={mat.material_type}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
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
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                    {mat.quality} • {mat.condition}
                  </div>
                  <h3 className="text-sm font-bold text-slate-900 line-clamp-1 mb-1.5">
                    {mat.description || `${mat.quality} ${mat.material_type}`}
                  </h3>
                  <div className="text-xs text-slate-500 flex items-center gap-1">
                    <Building2 className="w-3.5 h-3.5 text-slate-400" />
                    <span className="truncate">{mat.seller?.organization || mat.seller?.name || 'Verified Seller'}</span>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100 flex items-center justify-between mt-4">
                  <div>
                    <div className="text-[10px] text-slate-400 font-semibold uppercase">AI Price</div>
                    <div className="text-base font-extrabold text-emerald-600">
                      ₹{mat.predicted_price?.toFixed(2) || '40.00'}/kg
                    </div>
                  </div>
                  <button className="px-3.5 py-1.5 rounded-xl bg-eco-50 text-eco-700 font-bold text-xs group-hover:bg-eco-600 group-hover:text-white transition-colors">
                    View
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Material Detail Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedMaterial?.material_type || 'Material Details'}
        subtitle={`Listing ID: ${selectedMaterial?.id?.substring(0, 8)}`}
        maxWidth="max-w-3xl"
      >
        {selectedMaterial && (
          <div className="space-y-6">
            {buySuccess ? (
              <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 text-center space-y-3">
                <CheckCircle className="w-10 h-10 text-emerald-600 mx-auto" />
                <h4 className="text-base font-bold text-emerald-900">Purchase Transaction Recorded!</h4>
                <p className="text-xs text-emerald-700 max-w-sm mx-auto">
                  The order has been created, materials allocated, and sustainability impact credits calculated.
                </p>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-semibold"
                >
                  Close Window
                </button>
              </div>
            ) : (
              <>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="rounded-2xl overflow-hidden border border-slate-200 bg-slate-100 aspect-video">
                    <img
                      src={selectedMaterial.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600'}
                      alt={selectedMaterial.material_type}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  <div className="space-y-4">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Badge variant="eco" size="xs">{selectedMaterial.material_type}</Badge>
                        <Badge variant="default" size="xs">{selectedMaterial.quality}</Badge>
                      </div>
                      <h3 className="text-lg font-bold text-slate-900">
                        {selectedMaterial.description || `${selectedMaterial.quality} Grade Lot`}
                      </h3>
                      <p className="text-xs text-slate-500 mt-1 flex items-center gap-1">
                        <Building2 className="w-3.5 h-3.5" />
                        Seller: {selectedMaterial.seller?.organization || selectedMaterial.seller?.name}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3.5 rounded-2xl border border-slate-200/60 text-xs">
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Quantity</span>
                        <span className="font-bold text-slate-900 text-sm">{selectedMaterial.quantity_kg} kg</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Condition</span>
                        <span className="font-bold text-slate-900 text-sm">{selectedMaterial.condition}</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">AI Valuation</span>
                        <span className="font-extrabold text-emerald-600 text-sm">₹{selectedMaterial.predicted_price}/kg</span>
                      </div>
                      <div>
                        <span className="text-slate-400 block text-[10px] uppercase font-semibold">Est. Total</span>
                        <span className="font-bold text-slate-900 text-sm">
                          ₹{(selectedMaterial.predicted_price * selectedMaterial.quantity_kg).toLocaleString('en-IN')}
                        </span>
                      </div>
                    </div>

                    {/* AI Circular Assurance */}
                    <div className="p-3.5 rounded-2xl bg-purple-50 border border-purple-200 text-xs text-purple-900 space-y-1">
                      <div className="font-bold flex items-center gap-1.5 text-purple-800">
                        <Sparkles className="w-4 h-4 text-purple-600" />
                        AI Quality & Pricing Certified
                      </div>
                      <p className="text-[11px] text-purple-700">
                        Evaluated with MobileNetV2 vision classification & Gradient Boosting pricing regression model.
                      </p>
                    </div>

                    <button
                      onClick={handlePurchase}
                      disabled={isBuying}
                      className="w-full py-3 rounded-xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-sm shadow-md shadow-eco-600/20 transition-all flex items-center justify-center gap-2"
                    >
                      <ShoppingBag className="w-4 h-4" />
                      {isBuying ? 'Processing Purchase...' : 'Confirm Circular Purchase'}
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default Marketplace;
