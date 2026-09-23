import React, { useState, useEffect } from 'react';
import {
  Handshake,
  CheckCircle,
  XCircle,
  MessageSquare,
  ArrowRight,
  TrendingUp,
  Clock,
  Building2,
  AlertCircle,
  RefreshCw,
  History,
  ShieldCheck,
  Send
} from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/Badge';
import Modal from '../../components/Modal';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export const BuyerOffers = () => {
  const [offers, setOffers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOffer, setSelectedOffer] = useState(null);
  const [historyModalOpen, setHistoryModalOpen] = useState(false);
  const [counterModalOpen, setCounterModalOpen] = useState(false);
  const [counterPrice, setCounterPrice] = useState('');
  const [counterMessage, setCounterMessage] = useState('');
  const [actionLoading, setActionLoading] = useState(false);
  const [successMsg, setSuccessMsg] = useState('');
  const [errorMsg, setErrorMsg] = useState('');

  const fetchOffers = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/offers/buyer/me');
      setOffers(res.data || []);
    } catch (err) {
      console.error('Error fetching buyer offers:', err);
      setErrorMsg('Failed to load your submitted offers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchOffers();
  }, []);

  const handleOpenHistory = async (offer) => {
    try {
      const res = await api.get(`/api/offers/${offer.id}/history`);
      setSelectedOffer({ ...offer, fullHistory: res.data });
      setHistoryModalOpen(true);
    } catch (err) {
      console.error('Error fetching history:', err);
      setSelectedOffer(offer);
      setHistoryModalOpen(true);
    }
  };

  const handleOpenCounter = (offer) => {
    setSelectedOffer(offer);
    setCounterPrice(offer.offered_price || '');
    setCounterMessage('');
    setCounterModalOpen(true);
    setErrorMsg('');
  };

  const handleCancelOffer = async (offerId) => {
    if (!window.confirm('Are you sure you want to withdraw/cancel this offer?')) return;
    setActionLoading(true);
    setErrorMsg('');
    try {
      await api.post(`/api/offers/${offerId}/cancel`);
      setSuccessMsg('Offer successfully cancelled.');
      fetchOffers();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to cancel offer.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleAcceptSellerCounter = async (offerId) => {
    if (!window.confirm('Accept this price and proceed to confirmed transaction?')) return;
    setActionLoading(true);
    setErrorMsg('');
    try {
      await api.post(`/api/offers/${offerId}/accept`);
      setSuccessMsg('Counter-offer accepted! Transaction confirmed.');
      fetchOffers();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to accept offer.');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSendCounter = async (e) => {
    e.preventDefault();
    if (!counterPrice || parseFloat(counterPrice) <= 0) {
      setErrorMsg('Please enter a valid counter price.');
      return;
    }
    setActionLoading(true);
    setErrorMsg('');
    try {
      await api.post(`/api/offers/${selectedOffer.id}/counter`, {
        counter_price: parseFloat(counterPrice),
        message: counterMessage || 'Counter offer submitted by buyer.'
      });
      setSuccessMsg('Counter-bid submitted to seller!');
      setCounterModalOpen(false);
      fetchOffers();
    } catch (err) {
      setErrorMsg(err.response?.data?.detail || 'Failed to send counter-offer.');
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">My Circular Bids & Negotiations</h1>
          <p className="text-xs text-slate-500 mt-1">
            Track material offers, seller counter-proposals, and negotiated price agreements.
          </p>
        </div>
        <button
          onClick={fetchOffers}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-sm transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {successMsg && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-700 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 flex-shrink-0" />
            <span>{successMsg}</span>
          </div>
          <button onClick={() => setSuccessMsg('')} className="text-emerald-800 font-bold hover:underline">Dismiss</button>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{errorMsg}</span>
          </div>
          <button onClick={() => setErrorMsg('')} className="text-rose-800 font-bold hover:underline">Dismiss</button>
        </div>
      )}

      {loading ? (
        <LoadingSpinner text="Loading your circular offers..." />
      ) : offers.length === 0 ? (
        <EmptyState
          title="No active offers placed yet"
          description="Browse the Circular Materials Marketplace and submit offers on recyclable lots that fit your sourcing specs."
        />
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {offers.map((offer) => {
            const askingPrice = offer.listing?.asking_price || 0;
            const lastRound = offer.history && offer.history.length > 0 ? offer.history[offer.history.length - 1] : null;
            const sellerCountered = lastRound?.created_by === 'seller';

            return (
              <div
                key={offer.id}
                className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-5 sm:p-6 space-y-4 hover:border-slate-300 transition-all"
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 font-bold">
                      <Handshake className="w-5 h-5" />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-extrabold text-slate-900 text-sm">
                          {offer.listing?.material?.material_type || 'Recyclable'} Lot
                        </span>
                        <Badge
                          variant={
                            offer.status === 'ACCEPTED'
                              ? 'success'
                              : offer.status === 'REJECTED'
                              ? 'error'
                              : offer.status === 'CANCELLED'
                              ? 'default'
                              : sellerCountered
                              ? 'warning'
                              : 'info'
                          }
                          size="xs"
                        >
                          {offer.status === 'COUNTERED' && sellerCountered ? 'SELLER COUNTERED' : offer.status}
                        </Badge>
                      </div>
                      <p className="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1.5">
                        <Building2 className="w-3 h-3 text-slate-400" />
                        Seller: <strong className="text-slate-700">{offer.listing?.material?.seller?.organization || offer.listing?.material?.seller?.name || 'Verified Generator'}</strong>
                      </p>
                    </div>
                  </div>

                  <div className="text-right">
                    <span className="text-[10px] uppercase font-bold text-slate-400 block">Submitted</span>
                    <span className="text-xs font-semibold text-slate-600">
                      {new Date(offer.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* Offer Metrics Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50/70 p-3.5 rounded-2xl border border-slate-100 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Quantity</span>
                    <span className="font-bold text-slate-900 text-sm">{offer.offered_quantity.toLocaleString('en-IN')} kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Seller Asking Price</span>
                    <span className="font-bold text-slate-600 text-sm">₹{askingPrice}/kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Current Active Price</span>
                    <span className="font-extrabold text-emerald-700 text-sm">₹{offer.offered_price}/kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Estimated Value</span>
                    <span className="font-extrabold text-slate-900 text-sm">
                      ₹{(offer.offered_price * offer.offered_quantity).toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>

                {/* Latest History Note */}
                {lastRound && (
                  <div className={`p-3 rounded-xl text-xs space-y-1 ${sellerCountered ? 'bg-amber-50 border border-amber-200' : 'bg-slate-50 border border-slate-200/60'}`}>
                    <div className="flex items-center justify-between font-semibold text-[11px]">
                      <span className={sellerCountered ? 'text-amber-900 font-bold' : 'text-slate-600'}>
                        {sellerCountered ? '⚡ Seller Counter Proposal:' : 'Your Latest Note:'}
                      </span>
                      <span className="text-slate-400">Round {offer.history.length}</span>
                    </div>
                    <p className="text-slate-800 italic">"{lastRound.message || 'No additional note'}"</p>
                  </div>
                )}

                {/* Actions */}
                <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                  <button
                    onClick={() => handleOpenHistory(offer)}
                    className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-600 hover:text-slate-900 transition-colors"
                  >
                    <History className="w-3.5 h-3.5 text-slate-400" />
                    Negotiation History ({offer.history?.length || 1} rounds)
                  </button>

                  {offer.status !== 'ACCEPTED' && offer.status !== 'REJECTED' && offer.status !== 'CANCELLED' && (
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handleCancelOffer(offer.id)}
                        disabled={actionLoading}
                        className="px-3.5 py-2 rounded-xl border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-semibold transition-all"
                      >
                        Cancel Offer
                      </button>

                      <button
                        onClick={() => handleOpenCounter(offer)}
                        disabled={actionLoading}
                        className="px-3.5 py-2 rounded-xl border border-blue-300 bg-blue-50 hover:bg-blue-100 text-blue-800 font-bold text-xs transition-all flex items-center gap-1.5"
                      >
                        <TrendingUp className="w-3.5 h-3.5" />
                        Counter-Bid
                      </button>

                      {sellerCountered && (
                        <button
                          onClick={() => handleAcceptSellerCounter(offer.id)}
                          disabled={actionLoading}
                          className="px-4 py-2 rounded-xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-xs shadow-md shadow-eco-600/20 transition-all flex items-center gap-1.5"
                        >
                          <CheckCircle className="w-3.5 h-3.5" />
                          Accept Seller's ₹{offer.offered_price}/kg
                        </button>
                      )}
                    </div>
                  )}

                  {offer.status === 'ACCEPTED' && (
                    <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-xl border border-emerald-200">
                      ✓ Deal Confirmed at ₹{offer.agreed_price}/kg
                    </span>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* History Audit Trail Modal */}
      <Modal
        isOpen={historyModalOpen}
        onClose={() => setHistoryModalOpen(false)}
        title="Negotiation Audit Trail"
        subtitle={`Offer ID: ${selectedOffer?.id?.substring(0, 8)}`}
        maxWidth="max-w-2xl"
      >
        <div className="space-y-4">
          <div className="space-y-3">
            {(selectedOffer?.fullHistory || selectedOffer?.history || []).map((step, idx) => (
              <div
                key={idx}
                className={`p-3.5 rounded-2xl border text-xs space-y-1.5 ${
                  step.created_by === 'seller'
                    ? 'bg-amber-50/60 border-amber-200/80 ml-6'
                    : 'bg-blue-50/60 border-blue-200/80 mr-6'
                }`}
              >
                <div className="flex items-center justify-between font-bold">
                  <span className={step.created_by === 'seller' ? 'text-amber-900' : 'text-blue-900'}>
                    Round {idx + 1}: {step.created_by === 'seller' ? 'Seller Counter' : 'Buyer Bid (You)'}
                  </span>
                  <span className="text-slate-900 font-extrabold text-sm">₹{step.price}/kg</span>
                </div>
                {step.message && (
                  <p className="text-slate-700 italic">"{step.message}"</p>
                )}
                <div className="text-[10px] text-slate-400 flex items-center justify-between pt-1 border-t border-slate-200/40">
                  <span>Action: {step.action || 'COUNTER'}</span>
                  <span>{new Date(step.created_at).toLocaleString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </Modal>

      {/* Counter Offer Modal */}
      <Modal
        isOpen={counterModalOpen}
        onClose={() => setCounterModalOpen(false)}
        title="Submit New Counter-Bid"
        subtitle={`Lot: ${selectedOffer?.listing?.material?.material_type} (${selectedOffer?.offered_quantity} kg)`}
        maxWidth="max-w-md"
      >
        <form onSubmit={handleSendCounter} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Your Counter Bid (₹ per kg) *
            </label>
            <input
              type="number"
              step="0.1"
              required
              value={counterPrice}
              onChange={(e) => setCounterPrice(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-sm font-bold text-slate-900 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="e.g. 190.0"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">
              Note for Seller (Optional)
            </label>
            <textarea
              rows="3"
              value={counterMessage}
              onChange={(e) => setCounterMessage(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs text-slate-800 focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="e.g. Can do ₹190/kg with guaranteed prompt payment upon dispatch."
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setCounterModalOpen(false)}
              className="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 text-xs font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={actionLoading}
              className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-bold shadow-md transition-all"
            >
              {actionLoading ? 'Submitting...' : 'Send Counter Bid'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default BuyerOffers;
