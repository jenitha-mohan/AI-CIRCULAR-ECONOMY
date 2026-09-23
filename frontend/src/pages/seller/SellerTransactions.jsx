import React, { useState, useEffect } from 'react';
import {
  ReceiptText,
  CheckCircle,
  Clock,
  ShieldCheck,
  Leaf,
  MessageSquare,
  Calendar,
  Truck,
  Send,
  Building2,
  RefreshCw,
  AlertCircle
} from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/Badge';
import Modal from '../../components/Modal';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import { useAuth } from '../../context/AuthContext';

export const SellerTransactions = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeChatTx, setActiveChatTx] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(false);

  // Pickup Scheduling Modal
  const [pickupModalOpen, setPickupModalOpen] = useState(false);
  const [pickupTx, setPickupTx] = useState(null);
  const [pickupLocation, setPickupLocation] = useState('');
  const [pickupDate, setPickupDate] = useState('');
  const [pickupInstructions, setPickupInstructions] = useState('');
  const [savingPickup, setSavingPickup] = useState(false);

  // Status Progression Modal
  const [statusModalOpen, setStatusModalOpen] = useState(false);
  const [statusTx, setStatusTx] = useState(null);
  const [selectedStatus, setSelectedStatus] = useState('');
  const [savingStatus, setSavingStatus] = useState(false);

  const [notification, setNotification] = useState({ type: '', text: '' });

  const fetchTxs = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/transactions');
      setTransactions(res.data || []);
    } catch (err) {
      console.error('Error fetching transactions:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTxs();
  }, []);

  // Chat Helpers
  const handleOpenChat = async (tx) => {
    setActiveChatTx(tx);
    setChatLoading(true);
    try {
      const res = await api.get(`/api/transactions/${tx.id}/messages`);
      setChatMessages(res.data || []);
    } catch (err) {
      console.error('Error fetching chat messages:', err);
    } finally {
      setChatLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !activeChatTx) return;
    try {
      const res = await api.post(`/api/transactions/${activeChatTx.id}/messages`, {
        message: newMessage.trim(),
      });
      setChatMessages([...chatMessages, res.data]);
      setNewMessage('');
    } catch (err) {
      alert('Failed to send message: ' + (err.response?.data?.detail || err.message));
    }
  };

  // Pickup Scheduling Helpers
  const handleOpenPickup = (tx) => {
    setPickupTx(tx);
    setPickupLocation(tx.pickup_location || `${user?.organization || 'Seller Warehouse'}, ${user?.city || 'City'}`);
    setPickupDate(tx.pickup_date ? tx.pickup_date.substring(0, 10) : '');
    setPickupInstructions(tx.pickup_instructions || '');
    setPickupModalOpen(true);
  };

  const handleSavePickup = async (e) => {
    e.preventDefault();
    if (!pickupTx) return;
    setSavingPickup(true);
    try {
      await api.post(`/api/transactions/${pickupTx.id}/schedule-pickup`, {
        pickup_location: pickupLocation,
        pickup_date: pickupDate ? new Date(pickupDate).toISOString() : null,
        pickup_instructions: pickupInstructions,
      });
      setNotification({ type: 'success', text: 'Pickup scheduled successfully!' });
      setPickupModalOpen(false);
      fetchTxs();
    } catch (err) {
      setNotification({ type: 'error', text: err.response?.data?.detail || 'Failed to schedule pickup.' });
    } finally {
      setSavingPickup(false);
    }
  };

  // Status Progression
  const handleOpenStatus = (tx) => {
    setStatusTx(tx);
    setSelectedStatus(tx.status);
    setStatusModalOpen(true);
  };

  const handleUpdateStatus = async (e) => {
    e.preventDefault();
    if (!statusTx) return;
    setSavingStatus(true);
    try {
      await api.post(`/api/transactions/${statusTx.id}/update-status`, {
        status: selectedStatus,
      });
      setNotification({ type: 'success', text: `Transaction status changed to ${selectedStatus}` });
      setStatusModalOpen(false);
      fetchTxs();
    } catch (err) {
      setNotification({ type: 'error', text: err.response?.data?.detail || 'Failed to update status.' });
    } finally {
      setSavingStatus(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Confirmed Orders & Shipments</h1>
          <p className="text-xs text-slate-500 mt-1">
            Coordinate dispatches, track circular logistics, and message verified buyers on confirmed orders.
          </p>
        </div>
        <button
          onClick={fetchTxs}
          className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold shadow-sm transition-all"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          Refresh
        </button>
      </div>

      {notification.text && (
        <div
          className={`p-4 rounded-2xl text-xs flex items-center justify-between ${
            notification.type === 'success'
              ? 'bg-emerald-50 border border-emerald-200 text-emerald-700'
              : 'bg-rose-50 border border-rose-200 text-rose-700'
          }`}
        >
          <div className="flex items-center gap-2">
            {notification.type === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertCircle className="w-4 h-4" />}
            <span>{notification.text}</span>
          </div>
          <button onClick={() => setNotification({ type: '', text: '' })} className="font-bold hover:underline">Dismiss</button>
        </div>
      )}

      {loading ? (
        <LoadingSpinner text="Loading transaction records..." />
      ) : transactions.length === 0 ? (
        <EmptyState title="No confirmed orders yet" description="Once a buyer offer is accepted, the confirmed transaction and logistics coordinates appear here." />
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {transactions.map((tx) => (
            <div
              key={tx.id}
              className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-5 sm:p-6 space-y-4 hover:border-slate-300 transition-all"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-emerald-50 flex items-center justify-center text-emerald-600 font-bold">
                    <ReceiptText className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-extrabold text-slate-900 text-sm">
                        {tx.material_type} Shipment
                      </span>
                      <Badge
                        variant={
                          tx.status === 'COMPLETED' || tx.status === 'completed'
                            ? 'success'
                            : tx.status === 'CANCELLED'
                            ? 'error'
                            : tx.status === 'IN_TRANSIT' || tx.status === 'PICKUP_SCHEDULED'
                            ? 'warning'
                            : 'info'
                        }
                        size="xs"
                      >
                        {tx.status}
                      </Badge>
                    </div>
                    <p className="text-[11px] text-slate-500 mt-0.5 flex items-center gap-1.5">
                      <Building2 className="w-3 h-3 text-slate-400" />
                      Buyer: <strong className="text-slate-700">{tx.buyer?.organization || tx.buyer?.name || 'Recycling Mill'}</strong>
                      {tx.buyer?.business_type && <span className="text-slate-400">({tx.buyer.business_type})</span>}
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Transaction ID</span>
                  <span className="font-mono text-xs font-semibold text-slate-600">{tx.id.substring(0, 8)}...</span>
                </div>
              </div>

              {/* Deal Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50/70 p-3.5 rounded-2xl border border-slate-100 text-xs">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Quantity</span>
                  <span className="font-bold text-slate-900 text-sm">{tx.quantity_kg.toLocaleString('en-IN')} kg</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Agreed Settlement Price</span>
                  <span className="font-bold text-slate-900 text-sm">₹{tx.agreed_price}/kg</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Total Order Amount</span>
                  <span className="font-extrabold text-emerald-600 text-sm">₹{tx.total_amount.toLocaleString('en-IN')}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Carbon Avoided</span>
                  <div className="inline-flex items-center gap-1 text-emerald-700 font-bold text-xs bg-emerald-50 px-2 py-0.5 rounded-md mt-0.5">
                    <Leaf className="w-3 h-3 text-emerald-600" />
                    {tx.co2_avoided_kg || 0} kg CO₂
                  </div>
                </div>
              </div>

              {/* Pickup & Logistics Details */}
              {tx.pickup_location && (
                <div className="bg-slate-50 border border-slate-200/60 rounded-xl p-3 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <span className="text-slate-400 font-bold text-[10px] uppercase block">Pickup Location & Instructions</span>
                    <span className="font-medium text-slate-800">{tx.pickup_location}</span>
                    {tx.pickup_instructions && <p className="text-slate-500 text-[11px] mt-0.5 italic">"{tx.pickup_instructions}"</p>}
                  </div>
                  {tx.pickup_date && (
                    <div className="text-right flex-shrink-0">
                      <span className="text-slate-400 font-bold text-[10px] uppercase block">Scheduled Date</span>
                      <span className="font-semibold text-slate-700">{new Date(tx.pickup_date).toLocaleDateString()}</span>
                    </div>
                  )}
                </div>
              )}

              {/* Actions: Pickup, Lifecycle Status, Chat */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleOpenChat(tx)}
                    className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-blue-200 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-bold transition-all"
                  >
                    <MessageSquare className="w-3.5 h-3.5" />
                    Transaction Chat
                  </button>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleOpenPickup(tx)}
                    className="px-3.5 py-2 rounded-xl border border-slate-200 bg-white hover:bg-slate-50 text-slate-700 text-xs font-semibold transition-all flex items-center gap-1.5 shadow-sm"
                  >
                    <Calendar className="w-3.5 h-3.5 text-slate-500" />
                    {tx.pickup_location ? 'Edit Pickup' : 'Schedule Pickup'}
                  </button>

                  <button
                    onClick={() => handleOpenStatus(tx)}
                    className="px-3.5 py-2 rounded-xl border border-eco-200 bg-eco-50 hover:bg-eco-100 text-eco-800 text-xs font-bold transition-all flex items-center gap-1.5"
                  >
                    <Truck className="w-3.5 h-3.5 text-eco-600" />
                    Update Dispatch Status
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Transaction In-Platform Chat Modal */}
      <Modal
        isOpen={!!activeChatTx}
        onClose={() => setActiveChatTx(null)}
        title={`Chat: ${activeChatTx?.material_type} Order`}
        subtitle={`Transaction #${activeChatTx?.id?.substring(0, 8)} with ${activeChatTx?.buyer?.organization || activeChatTx?.buyer?.name || 'Buyer'}`}
        maxWidth="max-w-xl"
      >
        <div className="space-y-4">
          <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-4 h-72 overflow-y-auto space-y-3">
            {chatLoading ? (
              <LoadingSpinner text="Loading message history..." />
            ) : chatMessages.length === 0 ? (
              <div className="text-center py-12 text-slate-400 text-xs">
                No messages yet. Send a note regarding pickup timings, weights, or dispatch logistics.
              </div>
            ) : (
              chatMessages.map((m) => {
                const isMine = m.sender_id === user?.id;
                return (
                  <div key={m.id} className={`flex flex-col ${isMine ? 'items-end' : 'items-start'}`}>
                    <div className="flex items-center gap-1.5 text-[10px] text-slate-400 mb-0.5">
                      <span className="font-semibold">{m.sender_name || (isMine ? 'You' : 'Buyer')}</span>
                      <span>•</span>
                      <span>{new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                    <div
                      className={`px-3.5 py-2 rounded-2xl text-xs max-w-xs ${
                        isMine ? 'bg-eco-600 text-white rounded-br-none shadow-sm' : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none shadow-sm'
                      }`}
                    >
                      {m.message}
                    </div>
                  </div>
                );
              })
            )}
          </div>

          <form onSubmit={handleSendMessage} className="flex items-center gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              placeholder="Type message regarding logistics or payment..."
              className="flex-1 px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-eco-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={!newMessage.trim()}
              className="px-4 py-2.5 rounded-xl bg-eco-600 hover:bg-eco-700 disabled:opacity-50 text-white font-bold text-xs shadow-md flex items-center gap-1.5"
            >
              <Send className="w-3.5 h-3.5" />
              Send
            </button>
          </form>
        </div>
      </Modal>

      {/* Schedule Pickup Modal */}
      <Modal
        isOpen={pickupModalOpen}
        onClose={() => setPickupModalOpen(false)}
        title="Schedule Material Pickup"
        subtitle={`Order #${pickupTx?.id?.substring(0, 8)}`}
        maxWidth="max-w-md"
      >
        <form onSubmit={handleSavePickup} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Pickup Location Address *</label>
            <input
              type="text"
              required
              value={pickupLocation}
              onChange={(e) => setPickupLocation(e.target.value)}
              placeholder="Factory Gate / Warehouse Address"
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Preferred Pickup Date</label>
            <input
              type="date"
              value={pickupDate}
              onChange={(e) => setPickupDate(e.target.value)}
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1">Gate / Contact Instructions</label>
            <textarea
              rows="3"
              value={pickupInstructions}
              onChange={(e) => setPickupInstructions(e.target.value)}
              placeholder="e.g. Weighbridge at Gate 2. Driver must wear safety shoes and helmet."
              className="w-full px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs text-slate-900 focus:ring-2 focus:ring-eco-500 focus:outline-none"
            />
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setPickupModalOpen(false)}
              className="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 text-xs font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={savingPickup}
              className="px-4 py-2 rounded-xl bg-eco-600 hover:bg-eco-700 text-white text-xs font-bold shadow-md"
            >
              {savingPickup ? 'Saving...' : 'Save Pickup Schedule'}
            </button>
          </div>
        </form>
      </Modal>

      {/* Update Lifecycle Status Modal */}
      <Modal
        isOpen={statusModalOpen}
        onClose={() => setStatusModalOpen(false)}
        title="Update Dispatch & Delivery Status"
        subtitle={`Order #${statusTx?.id?.substring(0, 8)}`}
        maxWidth="max-w-sm"
      >
        <form onSubmit={handleUpdateStatus} className="space-y-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-2">Select Current Status</label>
            <div className="space-y-2">
              {['CONFIRMED', 'PICKUP_SCHEDULED', 'IN_TRANSIT', 'DELIVERED', 'COMPLETED', 'CANCELLED'].map((st) => (
                <label
                  key={st}
                  className={`flex items-center gap-3 p-3 rounded-xl border cursor-pointer text-xs font-bold transition-all ${
                    selectedStatus === st ? 'border-eco-600 bg-eco-50/80 text-eco-900' : 'border-slate-200 hover:bg-slate-50 text-slate-700'
                  }`}
                >
                  <input
                    type="radio"
                    name="status"
                    value={st}
                    checked={selectedStatus === st}
                    onChange={(e) => setSelectedStatus(e.target.value)}
                    className="text-eco-600 focus:ring-eco-500"
                  />
                  <span>{st}</span>
                </label>
              ))}
            </div>
          </div>

          <div className="flex items-center justify-end gap-2 pt-2">
            <button
              type="button"
              onClick={() => setStatusModalOpen(false)}
              className="px-4 py-2 rounded-xl border border-slate-200 text-slate-600 text-xs font-semibold hover:bg-slate-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={savingStatus}
              className="px-4 py-2 rounded-xl bg-eco-600 hover:bg-eco-700 text-white text-xs font-bold shadow-md"
            >
              {savingStatus ? 'Updating...' : 'Update Status'}
            </button>
          </div>
        </form>
      </Modal>
    </div>
  );
};

export default SellerTransactions;
