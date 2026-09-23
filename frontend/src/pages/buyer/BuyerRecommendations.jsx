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
  const [isPurchasing, setIsPurchasing] = useState(false);
  const [purchaseSuccess, setPurchaseSuccess] = useState(false);

  const fetchRecommendations = async () => {
    if (!user?.id) return;
    setLoading(true);
    try {
      const res = await api.get(`/api/recommendations/materials/${user.id}`);
      setRecommendations(res.data);
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
    setIsModalOpen(true);
    setPurchaseSuccess(false);
  };

  const handleConfirmPurchase = async () => {
    if (!selectedItem) return;
    setIsPurchasing(true);
    try {
      await api.post('/api/transactions', {
        listing_id: selectedItem.material?.listings?.[0]?.id || null,
        seller_id: selectedItem.material?.seller_id || user.id,
        material_type: selectedItem.material_type,
        quantity_kg: selectedItem.quantity_kg,
        agreed_price: selectedItem.predicted_price || selectedItem.asking_price || 40.0,
      });
      setPurchaseSuccess(true);
      fetchRecommendations();
    } catch (err) {
      console.error('Purchase error:', err);
    } finally {
      setIsPurchasing(false);
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
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">AI Valuation</span>
                    <span className="font-extrabold text-emerald-600">₹{item.predicted_price || item.asking_price}/kg</span>
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
                Inspect & Procure <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedItem?.material_type || 'Feedstock Match'}
      >
        {selectedItem && (
          <div className="space-y-6">
            {purchaseSuccess ? (
              <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 text-center space-y-3">
                <CheckCircle2 className="w-10 h-10 text-emerald-600 mx-auto" />
                <h4 className="text-base font-bold text-emerald-900">Procurement Successful!</h4>
                <p className="text-xs text-emerald-700">
                  Transaction registered in ledger with lifecycle CO₂ offset certification.
                </p>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-semibold"
                >
                  Close
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-3 bg-slate-50 p-4 rounded-2xl border border-slate-200/60 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Volume</span>
                    <span className="font-bold text-slate-900 text-sm">{selectedItem.quantity_kg} kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Match Score</span>
                    <span className="font-black text-emerald-600 text-sm">{(selectedItem.match_score * 100).toFixed(0)}%</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Agreed Price</span>
                    <span className="font-bold text-slate-900 text-sm">₹{selectedItem.predicted_price || selectedItem.asking_price}/kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Total Amount</span>
                    <span className="font-bold text-slate-900 text-sm">
                      ₹{((selectedItem.predicted_price || selectedItem.asking_price || 40) * selectedItem.quantity_kg).toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>

                <button
                  onClick={handleConfirmPurchase}
                  disabled={isPurchasing}
                  className="w-full py-3 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-sm shadow-md shadow-eco-600/20"
                >
                  {isPurchasing ? 'Processing Order...' : 'Confirm Circular Order'}
                </button>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BuyerRecommendations;
