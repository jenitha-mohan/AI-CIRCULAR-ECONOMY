import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Search,
  MapPin,
  Building2,
  Handshake,
  Sparkles,
  Filter,
  CheckCircle,
  AlertCircle,
  Tag
} from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import Modal from '../../components/Modal';

export const BuyerSearch = () => {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedQuality, setSelectedQuality] = useState('All');
  const [selectedMaterial, setSelectedMaterial] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Offer submission state
  const [offeredQuantity, setOfferedQuantity] = useState('');
  const [offeredPrice, setOfferedPrice] = useState('');
  const [offerMessage, setOfferMessage] = useState('');
  const [isSubmittingOffer, setIsSubmittingOffer] = useState(false);
  const [offerSuccess, setOfferSuccess] = useState(false);
  const [offerError, setOfferError] = useState('');

  const CATEGORIES = ['All', 'Aluminum', 'Copper', 'Steel', 'Plastic', 'Cardboard', 'Paper', 'Glass', 'Textile', 'E-waste', 'Other'];

  const fetchMaterials = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/materials?status=available');
      setMaterials(res.data || []);
    } catch (err) {
      console.error('Error searching materials:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMaterials();
  }, []);

  const filtered = materials.filter((m) => {
    const matchSearch =
      m.material_type.toLowerCase().includes(search.toLowerCase()) ||
      (m.description && m.description.toLowerCase().includes(search.toLowerCase())) ||
      (m.seller?.organization && m.seller.organization.toLowerCase().includes(search.toLowerCase()));
    const matchCat = selectedCategory === 'All' || m.material_type.toLowerCase() === selectedCategory.toLowerCase();
    const matchQual = selectedQuality === 'All' || m.quality === selectedQuality;
    return matchSearch && matchCat && matchQual;
  });

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
    if (!selectedMaterial) return;

    const listingId = selectedMaterial.listings?.[0]?.id;
    if (!listingId) {
      setOfferError('No active listing ID found for this material lot.');
      return;
    }

    setIsSubmittingOffer(true);
    setOfferError('');
    try {
      await api.post('/api/offers', {
        listing_id: listingId,
        offered_quantity: parseFloat(offeredQuantity),
        offered_price: parseFloat(offeredPrice),
        message: offerMessage || 'Offer placed via Material Search.'
      });
      setOfferSuccess(true);
    } catch (err) {
      setOfferError(err.response?.data?.detail || 'Failed to submit offer.');
    } finally {
      setIsSubmittingOffer(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Geospatial Material Sourcing</h1>
        <p className="text-xs text-slate-500 mt-1">Search proximate industrial recyclables, view AI price ranges, and place bids directly.</p>
      </div>

      {/* Filter Bar */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by alloy, polymer, keyword..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
            />
          </div>

          <div>
            <select
              value={selectedQuality}
              onChange={(e) => setSelectedQuality(e.target.value)}
              className="w-full py-2 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-medium text-slate-700"
            >
              <option value="All">All Quality Grades</option>
              <option value="Industrial Grade">Industrial Grade</option>
              <option value="High">High Purity</option>
              <option value="Medium">Medium</option>
              <option value="Low">Low</option>
            </select>
          </div>

          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full py-2 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-medium text-slate-700"
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{c}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Results */}
      {loading ? (
        <LoadingSpinner text="Searching proximate batches..." />
      ) : filtered.length === 0 ? (
        <EmptyState title="No material lots matched your criteria" description="Try adjusting search terms or grades." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {filtered.map((mat) => {
            const askPrice = mat.listings?.[0]?.asking_price || mat.predicted_price || 0;
            const aiMin = mat.listings?.[0]?.ai_estimated_min_price || Math.round(askPrice * 0.95);
            const aiMax = mat.listings?.[0]?.ai_estimated_max_price || Math.round(askPrice * 1.05);

            return (
              <div
                key={mat.id}
                onClick={() => handleOpenDetail(mat)}
                className="bg-white rounded-3xl border border-slate-200/80 shadow-sm hover:shadow-md transition-all overflow-hidden flex flex-col cursor-pointer group"
              >
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

                <div className="p-5 flex-1 flex flex-col justify-between space-y-4">
                  <div className="space-y-1.5">
                    <h3 className="font-bold text-slate-900 text-sm group-hover:text-eco-600 transition-colors">
                      {mat.description || `${mat.quality} Grade ${mat.material_type}`}
                    </h3>
                    <p className="text-[11px] text-slate-500 flex items-center gap-1">
                      <Building2 className="w-3.5 h-3.5 text-slate-400" />
                      {mat.seller?.organization || mat.seller?.name || 'Verified Generator'}
                    </p>
                  </div>

                  <div className="pt-3 border-t border-slate-100 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 font-semibold">Available Lot:</span>
                      <span className="font-bold text-slate-800">{mat.quantity_kg.toLocaleString('en-IN')} kg</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 font-semibold">Asking Price:</span>
                      <span className="font-extrabold text-slate-900">₹{askPrice}/kg</span>
                    </div>
                    <div className="bg-purple-50 border border-purple-100 rounded-xl px-2.5 py-1 text-[10px] text-purple-800 flex items-center justify-between">
                      <span>🤖 AI Market Range:</span>
                      <span className="font-bold">₹{aiMin} – ₹{aiMax}/kg</span>
                    </div>

                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleOpenDetail(mat);
                      }}
                      className="w-full py-2.5 rounded-xl bg-slate-900 hover:bg-eco-600 text-white font-bold text-xs transition-colors flex items-center justify-center gap-1.5 mt-2"
                    >
                      <Handshake className="w-3.5 h-3.5" />
                      Make Circular Offer
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Make Offer Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedMaterial?.material_type || 'Material Lot'}
        subtitle={`Listing: ${selectedMaterial?.id?.substring(0, 8)}`}
        maxWidth="max-w-2xl"
      >
        {selectedMaterial && (
          <div className="space-y-6">
            {offerSuccess ? (
              <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 text-center space-y-3">
                <CheckCircle className="w-10 h-10 text-emerald-600 mx-auto" />
                <h4 className="text-base font-bold text-emerald-900">Offer Placed Successfully!</h4>
                <p className="text-xs text-emerald-700 max-w-sm mx-auto">
                  Your bid of <strong>₹{offeredPrice}/kg</strong> for <strong>{offeredQuantity} kg</strong> was sent to the seller.
                </p>
                <div className="flex items-center justify-center gap-3 pt-2">
                  <button
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2 rounded-xl border border-emerald-300 text-emerald-800 text-xs font-semibold"
                  >
                    Close Window
                  </button>
                  <Link
                    to="/buyer/offers"
                    className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-bold"
                  >
                    Go to Negotiations Portal →
                  </Link>
                </div>
              </div>
            ) : (
              <form onSubmit={handleMakeOffer} className="space-y-4">
                {offerError && (
                  <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center gap-2">
                    <AlertCircle className="w-4 h-4 flex-shrink-0" />
                    <span>{offerError}</span>
                  </div>
                )}

                <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-xl text-xs">
                  <div><span className="text-slate-400 block text-[10px]">Seller Asking Price</span><span className="font-bold text-slate-900">₹{selectedMaterial.listings?.[0]?.asking_price || selectedMaterial.predicted_price}/kg</span></div>
                  <div><span className="text-slate-400 block text-[10px]">AI Estimate Range</span><span className="font-bold text-purple-700">₹{selectedMaterial.listings?.[0]?.ai_estimated_min_price || 0} – ₹{selectedMaterial.listings?.[0]?.ai_estimated_max_price || 0}/kg</span></div>
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Offered Quantity (kg) *</label>
                  <input
                    type="number"
                    required
                    step="1"
                    max={selectedMaterial.quantity_kg}
                    value={offeredQuantity}
                    onChange={(e) => setOfferedQuantity(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Offered Price (₹ per kg) *</label>
                  <input
                    type="number"
                    required
                    step="0.1"
                    value={offeredPrice}
                    onChange={(e) => setOfferedPrice(e.target.value)}
                    className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs font-bold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                  />
                </div>

                <div>
                  <label className="block text-xs font-bold text-slate-700 mb-1">Message for Seller (Optional)</label>
                  <textarea
                    rows="2"
                    value={offerMessage}
                    onChange={(e) => setOfferMessage(e.target.value)}
                    placeholder="e.g. Seeking immediate dispatch to our Coimbatore processing facility."
                    className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-xs text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                  />
                </div>

                <div className="p-3 rounded-xl bg-slate-50 border border-slate-200 text-xs flex items-center justify-between">
                  <span>Total Bid Value:</span>
                  <strong className="text-emerald-700 text-sm">
                    ₹{((parseFloat(offeredQuantity) || 0) * (parseFloat(offeredPrice) || 0)).toLocaleString('en-IN')}
                  </strong>
                </div>

                <button
                  type="submit"
                  disabled={isSubmittingOffer}
                  className="w-full py-3 rounded-xl bg-eco-600 hover:bg-eco-700 disabled:opacity-50 text-white font-bold text-xs shadow-md transition-all flex items-center justify-center gap-2"
                >
                  <Handshake className="w-4 h-4" />
                  {isSubmittingOffer ? 'Submitting...' : 'Submit Offer'}
                </button>
              </form>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BuyerSearch;
