import React, { useState, useEffect } from 'react';
import { Sparkles, MapPin, Building2, CheckCircle2, ShoppingBag, ArrowRight } from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import Modal from '../../components/Modal';

export const BuyerRecommendations = () => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [offeredQuantity, setOfferedQuantity] = useState('');
  const [offeredPrice, setOfferedPrice] = useState('');
  const [offerMessage, setOfferMessage] = useState('');
  const [isSubmittingOffer, setIsSubmittingOffer] = useState(false);
  const [offerSuccess, setOfferSuccess] = useState(false);
  const [offerError, setOfferError] = useState('');

  const fetchRecommendations = async () => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const res = await api.get(`/api/recommendations/materials/${user.id}`);
      setRecommendations(res.data || []);
    } catch (err) {
      console.error('Error fetching buyer recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchRecommendations();
  }, [user]);

  const handleOpenDetail = (item) => {
    setSelectedItem(item);
    const defaultAsk = item.asking_price ?? (item.material?.listings?.[0]?.asking_price ?? '');
    setOfferedQuantity(item.quantity_kg || '');
    setOfferedPrice(defaultAsk);
    setOfferMessage('');
    setOfferError('');
    setOfferSuccess(false);
    setIsModalOpen(true);
  };

  const handleSubmitOffer = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    if (!selectedItem) return;

    const listingId = selectedItem.material?.listings?.[0]?.id;
    if (!listingId) {
      setOfferError('No active listing found for this recommended material lot. The seller may have closed or paused it.');
      return;
    }

    const qty = parseFloat(offeredQuantity);
    const price = parseFloat(offeredPrice);

    if (!qty || qty <= 0) {
      setOfferError('Offered quantity must be greater than zero.');
      return;
    }
    if (!price || price <= 0) {
      setOfferError('Offered price must be greater than zero.');
      return;
    }

    const maxAvailable = selectedItem.material?.listings?.[0]?.quantity_available ?? selectedItem.quantity_kg;
    if (qty > maxAvailable) {
      setOfferError(`Offered quantity (${qty} kg) exceeds available stock (${maxAvailable} kg).`);
      return;
    }

    setIsSubmittingOffer(true);
    setOfferError('');
    try {
      await api.post('/api/offers', {
        listing_id: listingId,
        offered_quantity: qty,
        offered_price: price,
        message: offerMessage || 'Offer initiated from AI Recommendations feed.',
      });
      setOfferSuccess(true);
      fetchRecommendations();
    } catch (err) {
      console.error('Offer submission error:', err);
      setOfferError(err.response?.data?.detail || err.response?.data?.message || 'Failed to submit offer to seller.');
    } finally {
      setIsSubmittingOffer(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="ai" size="xs">AI Matchmaking Feed</Badge>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          Personalized Feedstock Recommendations
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Algorithmic matchmaking based on material compatibility, volume specs, quality grades, and Haversine proximity
        </p>
      </div>

      {loading ? (
        <LoadingSpinner text="Computing weighted compatibility matrices..." />
      ) : recommendations.length === 0 ? (
        <EmptyState title="No matching recommendations found" />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {recommendations.map((item) => (
            <div
              key={item.material_id}
              className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3 mb-3">
                  <div>
                    <Badge variant="eco" size="xs">{item.material_type}</Badge>
                    <h3 className="text-base font-bold text-slate-900 mt-1">
                      {item.seller_organization || item.seller_name || 'Verified Eco Seller'}
                    </h3>
                  </div>
                  <div className="text-right">
                    <span className="text-lg font-black text-emerald-600">
                      {(item.match_score * 100).toFixed(0)}%
                    </span>
                    <span className="text-[10px] text-slate-400 block font-semibold uppercase">
                      Match
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-2xl border border-slate-200/60 text-xs mb-4">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Available Lot</span>
                    <span className="font-bold text-slate-900">{item.quantity_kg} kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Quality Grade</span>
                    <span className="font-bold text-slate-900">{item.quality}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Seller Asking Price</span>
                    <span className="font-extrabold text-emerald-600">
                      {item.asking_price ? `₹${item.asking_price}/kg` : 'Negotiable'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Proximity</span>
                    <span className="font-bold text-slate-900 flex items-center gap-1">
                      <MapPin className="w-3 h-3 text-sky-500" />
                      {item.distance_km} km
                    </span>
                  </div>
                </div>

                {/* Reasons */}
                {item.reasons && item.reasons.length > 0 && (
                  <div className="space-y-1.5 mb-4">
                    {item.reasons.slice(0, 2).map((r, rIdx) => (
                      <div key={rIdx} className="text-[11px] text-slate-600 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                        <span>{r}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <button
                onClick={() => handleOpenDetail(item)}
                className="w-full py-2.5 rounded-xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-xs shadow-sm shadow-eco-600/20 transition-all flex items-center justify-center gap-1.5"
              >
                Inspect & Make Offer <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedItem?.material_type ? `Make Offer — ${selectedItem.material_type}` : 'Feedstock Offer'}
        subtitle={`Seller: ${selectedItem?.seller_organization || selectedItem?.seller_name || 'Verified Generator'}`}
        maxWidth="max-w-md"
      >
        {selectedItem && (
          <div className="space-y-4">
            {offerSuccess ? (
              <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 text-center space-y-3">
                <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
                <h4 className="text-base font-bold text-emerald-900">Offer Submitted Successfully!</h4>
                <p className="text-xs text-emerald-700">
                  Your purchase offer has been sent to the seller for review. You can track rounds and negotiate terms under My Offers.
                </p>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-semibold hover:bg-emerald-700 transition-colors"
                >
                  Done
                </button>
              </div>
            ) : (
              <form onSubmit={handleSubmitOffer} className="space-y-4">
                {offerError && (
                  <div className="p-3 bg-rose-50 border border-rose-200 rounded-xl text-xs text-rose-700 flex items-center gap-2">
                    <span className="font-bold">Error:</span> {offerError}
                  </div>
                )}

                <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3 rounded-2xl border border-slate-200/60 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Available Lot</span>
                    <span className="font-bold text-slate-900 text-sm">{selectedItem.quantity_kg} kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Match Score</span>
                    <span className="font-black text-emerald-600 text-sm">{(selectedItem.match_score * 100).toFixed(0)}%</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Seller Asking Price</span>
                    <span className="font-bold text-slate-900 text-sm">
                      {selectedItem.asking_price ? `₹${selectedItem.asking_price}/kg` : 'Open to Bids'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Proximity</span>
                    <span className="font-bold text-slate-900 text-sm">{selectedItem.distance_km} km</span>
                  </div>
                </div>

                <div className="space-y-3">
                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Offer Quantity (kg) *
                    </label>
                    <input
                      type="number"
                      step="any"
                      min="1"
                      required
                      value={offeredQuantity}
                      onChange={(e) => setOfferedQuantity(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-bold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                      placeholder="e.g. 500"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Bid Price (₹ per kg) *
                    </label>
                    <input
                      type="number"
                      step="any"
                      min="0.1"
                      required
                      value={offeredPrice}
                      onChange={(e) => setOfferedPrice(e.target.value)}
                      className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-bold text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
                      placeholder="e.g. 35.0"
                    />
                  </div>

                  <div>
                    <label className="block text-xs font-bold text-slate-700 mb-1">
                      Note to Seller (Optional)
                    </label>
                    <textarea
                      rows="2"
                      value={offerMessage}
                      onChange={(e) => setOfferMessage(e.target.value)}
                      className="w-full px-3.5 py-2 rounded-xl border border-slate-200 text-xs text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none resize-none"
                      placeholder="Include logistics preferences, delivery window, or spec questions..."
                    />
                  </div>
                </div>

                {offeredQuantity && offeredPrice && (
                  <div className="bg-eco-50/60 border border-eco-200/80 p-3 rounded-xl flex items-center justify-between text-xs">
                    <span className="text-slate-600 font-semibold">Total Bid Value:</span>
                    <span className="text-sm font-extrabold text-eco-800">
                      ₹{(parseFloat(offeredQuantity || 0) * parseFloat(offeredPrice || 0)).toLocaleString('en-IN')}
                    </span>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isSubmittingOffer}
                  className="w-full py-3 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-sm shadow-md shadow-eco-600/20 disabled:opacity-50 transition-all flex items-center justify-center gap-2"
                >
                  {isSubmittingOffer ? 'Submitting Bid...' : 'Submit Purchase Offer'}
                </button>
              </form>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BuyerRecommendations;
