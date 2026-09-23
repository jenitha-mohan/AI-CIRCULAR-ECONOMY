import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
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
  Handshake,
  ExternalLink,
  Info,
  AlertCircle
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
  
  // Offer Submission Form State
  const [offeredQuantity, setOfferedQuantity] = useState('');
  const [offeredPrice, setOfferedPrice] = useState('');
  const [offerMessage, setOfferMessage] = useState('');
  const [isSubmittingOffer, setIsSubmittingOffer] = useState(false);
  const [offerSuccess, setOfferSuccess] = useState(false);
  const [offerError, setOfferError] = useState('');

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
      setMaterials(res.data || []);
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
      const aPrice = mPrice(a);
      const bPrice = mPrice(b);
      if (sortBy === 'price-asc') return aPrice - bPrice;
      if (sortBy === 'price-desc') return bPrice - aPrice;
      if (sortBy === 'qty-desc') return b.quantity_kg - a.quantity_kg;
      return new Date(b.created_at) - new Date(a.created_at);
    });

  function mPrice(mat) {
    return mat.listings?.[0]?.asking_price || mat.predicted_price || 0;
  }

  const handleOpenDetail = (mat) => {
    setSelectedMaterial(mat);
    const defaultAsk = mat.listings?.[0]?.asking_price || mat.predicted_price || 40.0;
    setOfferedQuantity(mat.quantity_kg);
    setOfferedPrice(defaultAsk);
    setOfferMessage('');
    setOfferError('');
    setOfferSuccess(false);
    setIsModalOpen(true);
  };

  const handleMakeOffer = async (e) => {
    e.preventDefault();
    if (!isAuthenticated) {
      window.location.href = '/login';
      return;
    }
    if (!selectedMaterial) return;

    const listingId = selectedMaterial.listings?.[0]?.id;
    if (!listingId) {
      setOfferError('No active listing ID associated with this material lot.');
      return;
    }

    setIsSubmittingOffer(true);
    setOfferError('');
    try {
      await api.post('/api/offers', {
        listing_id: listingId,
        offered_quantity: parseFloat(offeredQuantity),
        offered_price: parseFloat(offeredPrice),
        message: offerMessage || 'Initial offer submitted via Circular Marketplace.'
      });
      setOfferSuccess(true);
    } catch (err) {
      setOfferError(err.response?.data?.detail || 'Failed to submit offer.');
    } finally {
      setIsSubmittingOffer(false);
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
            Browse verified industrial recyclables, view AI price benchmarks, and negotiate directly with sellers.
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
              <option value="High">High Purity</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          {/* Sort By */}
          <div>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="w-full py-2 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-medium text-slate-700"
            >
              <option value="newest">Newest Lots First</option>
              <option value="price-asc">Price: Low to High</option>
              <option value="price-desc">Price: High to Low</option>
              <option value="qty-desc">Quantity: High to Low</option>
            </select>
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 scrollbar-none">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setCategoryFilter(cat)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                categoryFilter === cat
                  ? 'bg-eco-600 text-white shadow-sm shadow-eco-600/30'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200/70'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Grid of Materials */}
      {loading ? (
        <LoadingSpinner text="Querying active circular lots..." />
      ) : filteredMaterials.length === 0 ? (
        <EmptyState
          title="No materials matched your filters"
          description="Try broadening your category filter or search keywords."
        />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredMaterials.map((mat) => {
            const askPrice = mat.listings?.[0]?.asking_price || mat.predicted_price || 0;
            const aiMin = mat.listings?.[0]?.ai_estimated_min_price || round(askPrice * 0.95, 1);
            const aiMax = mat.listings?.[0]?.ai_estimated_max_price || round(askPrice * 1.05, 1);

            return (
              <div
                key={mat.id}
                onClick={() => handleOpenDetail(mat)}
                className="bg-white rounded-3xl border border-slate-200/80 shadow-sm hover:shadow-md hover:border-slate-300 transition-all overflow-hidden flex flex-col cursor-pointer group"
              >
                {/* Image */}
                <div className="relative aspect-video bg-slate-100 overflow-hidden">
                  <img
                    src={mat.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600'}
                    alt={mat.material_type}
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                  />
                  <div className="absolute top-3 left-3 flex gap-1.5">
                    <Badge variant="eco" size="xs">{mat.material_type}</Badge>
                    <Badge variant="default" size="xs">{mat.quality}</Badge>
                  </div>
                </div>

                {/* Body */}
                <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                  <div className="space-y-2">
                    <h3 className="font-bold text-slate-900 text-sm line-clamp-1 group-hover:text-eco-600 transition-colors">
                      {mat.description || `${mat.quality} Grade ${mat.material_type}`}
                    </h3>

                    <div className="flex items-center gap-1 text-slate-500 text-[11px]">
                      <Building2 className="w-3.5 h-3.5 text-slate-400" />
                      <span className="truncate">{mat.seller?.organization || mat.seller?.name || 'Verified Generator'}</span>
                    </div>

                    <div className="flex items-center gap-1 text-slate-400 text-[11px]">
                      <MapPin className="w-3.5 h-3.5 text-slate-400" />
                      <span>{mat.seller?.city || 'Coimbatore'}, {mat.seller?.state || 'Tamil Nadu'}</span>
                    </div>
                  </div>

                  {/* Pricing & Valuation Section */}
                  <div className="pt-3 border-t border-slate-100 space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-[10px] uppercase font-bold text-slate-400">Available Stock</span>
                      <span className="text-xs font-bold text-slate-800">{mat.quantity_kg.toLocaleString('en-IN')} kg</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="text-[10px] uppercase font-bold text-slate-400">Asking Price</span>
                      <span className="text-sm font-extrabold text-slate-900">₹{askPrice}/kg</span>
                    </div>

                    {/* AI Estimate Range Pill */}
                    <div className="bg-purple-50 border border-purple-100 rounded-xl px-2.5 py-1 text-[10px] text-purple-800 flex items-center justify-between">
                      <span className="flex items-center gap-1">
                        <Sparkles className="w-3 h-3 text-purple-600" />
                        AI Estimate:
                      </span>
                      <span className="font-bold">₹{aiMin} – ₹{aiMax}/kg</span>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenDetail(mat);
                      }}
                      className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-eco-600 text-white text-xs font-bold transition-colors flex items-center justify-center gap-1.5 mt-2"
                    >
                      <Handshake className="w-3.5 h-3.5" />
                      Make Offer / Negotiate
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Make Offer / Material Detail Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedMaterial?.material_type || 'Material Details'}
        subtitle={`Listing ID: ${selectedMaterial?.id?.substring(0, 8)}`}
        maxWidth="max-w-3xl"
      >
        {selectedMaterial && (
          <div className="space-y-6">
            {offerSuccess ? (
              <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 text-center space-y-3">
                <CheckCircle className="w-10 h-10 text-emerald-600 mx-auto" />
                <h4 className="text-base font-bold text-emerald-900">Circular Offer Submitted to Seller!</h4>
                <p className="text-xs text-emerald-700 max-w-sm mx-auto">
                  Your bid of <strong>₹{offeredPrice}/kg</strong> for <strong>{offeredQuantity} kg</strong> has been delivered. The seller can accept or submit a counter-proposal.
                </p>
                <div className="flex items-center justify-center gap-3 pt-2">
                  <button
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2 rounded-xl border border-emerald-300 text-emerald-800 text-xs font-semibold"
                  >
                    Close Window
                  </button>
                  {isAuthenticated && user?.role === 'buyer' && (
                    <Link
                      to="/buyer/offers"
                      className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-bold"
                    >
                      View My Offers & Negotiations →
                    </Link>
                  )}
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <div className="rounded-2xl overflow-hidden border border-slate-200 bg-slate-100 aspect-video">
                    <img
                      src={selectedMaterial.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600'}
                      alt={selectedMaterial.material_type}
                      className="w-full h-full object-cover"
                    />
                  </div>

                  <div className="bg-slate-50 p-4 rounded-2xl border border-slate-200/60 text-xs space-y-2">
                    <div className="font-bold text-slate-800">Lot Specifications</div>
                    <div className="grid grid-cols-2 gap-2 text-[11px]">
                      <div><span className="text-slate-400">Condition:</span> <strong>{selectedMaterial.condition}</strong></div>
                      <div><span className="text-slate-400">Quality:</span> <strong>{selectedMaterial.quality}</strong></div>
                      <div><span className="text-slate-400">Total Lot:</span> <strong>{selectedMaterial.quantity_kg} kg</strong></div>
                      <div><span className="text-slate-400">Seller:</span> <strong>{selectedMaterial.seller?.organization || selectedMaterial.seller?.name}</strong></div>
                    </div>
                  </div>

                  {/* AI Disclaimer */}
                  <div className="p-3 rounded-2xl bg-purple-50 border border-purple-200 text-xs text-purple-900 space-y-1">
                    <div className="font-bold flex items-center gap-1.5 text-purple-800">
                      <Sparkles className="w-4 h-4 text-purple-600" />
                      AI Price Advisory Range: ₹{selectedMaterial.listings?.[0]?.ai_estimated_min_price || 0} – ₹{selectedMaterial.listings?.[0]?.ai_estimated_max_price || 0}/kg
                    </div>
                    <p className="text-[11px] text-purple-700">
                      Notice: AI provides market guidance only. The final transaction price is established strictly by mutual agreement between seller and buyer.
                    </p>
                  </div>
                </div>

                {/* Offer Submission Form */}
                <form onSubmit={handleMakeOffer} className="space-y-4">
                  <div className="border-b border-slate-100 pb-2">
                    <h4 className="font-bold text-slate-900 text-sm">Submit Purchase Bid & Terms</h4>
                    <p className="text-[11px] text-slate-500">Seller Asking Price: <strong>₹{selectedMaterial.listings?.[0]?.asking_price || selectedMaterial.predicted_price}/kg</strong></p>
                  </div>

                  {offerError && (
                    <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                      <AlertCircle className="w-4 h-4 flex-shrink-0" />
                      <span>{offerError}</span>
                    </div>
                  )}

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Offered Quantity (kg) *
                    </label>
                    <input
                      type="number"
                      step="1"
                      required
                      max={selectedMaterial.quantity_kg}
                      value={offeredQuantity}
                      onChange={(e) => setOfferedQuantity(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Offered Price (₹ per kg) *
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      required
                      value={offeredPrice}
                      onChange={(e) => setOfferedPrice(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Initial Message / Terms (Optional)
                    </label>
                    <textarea
                      rows="2"
                      value={offerMessage}
                      onChange={(e) => setOfferMessage(e.target.value)}
                      placeholder="e.g. Can arrange immediate truck pickup from Coimbatore."
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-xs text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                    />
                  </div>

                  <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-700 flex items-center justify-between">
                    <span>Total Deal Value:</span>
                    <strong className="text-emerald-700 text-sm">
                      ₹{((parseFloat(offeredQuantity) || 0) * (parseFloat(offeredPrice) || 0)).toLocaleString('en-IN')}
                    </strong>
                  </div>

                  <button
                    type="submit"
                    disabled={isSubmittingOffer}
                    className="w-full py-3 rounded-xl bg-eco-600 hover:bg-eco-700 disabled:opacity-50 text-white font-bold text-xs shadow-md shadow-eco-600/20 transition-all flex items-center justify-center gap-2"
                  >
                    <Handshake className="w-4 h-4" />
                    {isSubmittingOffer ? 'Transmitting Offer...' : 'Send Offer to Seller'}
                  </button>
                </form>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

function round(val, dec) {
  return Number(Math.round(val + 'e' + dec) + 'e-' + dec);
}

export default Marketplace;
