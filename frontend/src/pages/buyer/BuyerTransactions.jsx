import React, { useState, useEffect } from 'react';
import {
  ReceiptText,
  CheckCircle,
  Clock,
  ShieldCheck,
  Leaf,
  MessageSquare,
  Building2,
  RefreshCw,
  AlertCircle,
  Send,
  Calendar,
  Truck
} from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/Badge';
import Modal from '../../components/Modal';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import { useAuth } from '../../context/AuthContext';

export const BuyerTransactions = () => {
  const { user } = useAuth();
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeChatTx, setActiveChatTx] = useState(null);
  const [chatMessages, setChatMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [chatLoading, setChatLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
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

  const handleCompleteTransaction = async (txId) => {
    if (!window.confirm('Confirm receipt of materials and mark transaction as completed?')) return;
    setActionLoading(true);
    try {
      await api.post(`/api/transactions/${txId}/complete`);
      setNotification({ type: 'success', text: 'Transaction marked as completed! Impact certificate registered.' });
      fetchTxs();
    } catch (err) {
      setNotification({ type: 'error', text: err.response?.data?.detail || 'Failed to complete transaction.' });
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Purchased Lots & Inbound Logistics</h1>
          <p className="text-xs text-slate-500 mt-1">
            Track confirmed recyclable purchases, gate dispatches, and coordinate with sellers in real-time.
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
        <LoadingSpinner text="Loading your circular purchases..." />
      ) : transactions.length === 0 ? (
        <EmptyState
          title="No purchase orders confirmed yet"
          description="Browse the marketplace or manage pending counter-offers in the Offers & Negotiations portal."
        />
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {transactions.map((tx) => (
            <div
              key={tx.id}
              className="bg-white rounded-3xl border border-slate-200/80 shadow-sm p-5 sm:p-6 space-y-4 hover:border-slate-300 transition-all"
            >
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-100">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-2xl bg-blue-50 flex items-center justify-center text-blue-600 font-bold">
                    <ReceiptText className="w-5 h-5" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-extrabold text-slate-900 text-sm">
                        {tx.material_type} Feedstock Batch
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
                      Seller: <strong className="text-slate-700">{tx.seller?.organization || tx.seller?.name || 'Industrial Generator'}</strong>
                    </p>
                  </div>
                </div>

                <div className="text-right">
                  <span className="text-[10px] uppercase font-bold text-slate-400 block">Order Date</span>
                  <span className="text-xs font-semibold text-slate-600">
                    {new Date(tx.created_at).toLocaleDateString()}
                  </span>
                </div>
              </div>

              {/* Deal Metrics */}
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50/70 p-3.5 rounded-2xl border border-slate-100 text-xs">
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Quantity</span>
                  <span className="font-bold text-slate-900 text-sm">{tx.quantity_kg.toLocaleString('en-IN')} kg</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Agreed Price</span>
                  <span className="font-bold text-slate-900 text-sm">₹{tx.agreed_price}/kg</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">Total Invoice Amount</span>
                  <span className="font-extrabold text-emerald-600 text-sm">₹{tx.total_amount.toLocaleString('en-IN')}</span>
                </div>
                <div>
                  <span className="text-slate-400 block text-[10px] uppercase font-semibold">CO₂ Avoided</span>
                  <div className="inline-flex items-center gap-1 text-emerald-700 font-bold text-xs bg-emerald-50 px-2 py-0.5 rounded-md mt-0.5">
                    <Leaf className="w-3 h-3 text-emerald-600" />
                    {tx.co2_avoided_kg || 0} kg
                  </div>
                </div>
              </div>

              {/* Pickup info */}
              {tx.pickup_location && (
                <div className="bg-slate-50 border border-slate-200/60 rounded-xl p-3 text-xs flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <div>
                    <span className="text-slate-400 font-bold text-[10px] uppercase block">Pickup Coordinates</span>
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

              {/* Actions */}
              <div className="flex flex-wrap items-center justify-between gap-3 pt-2">
                <button
                  onClick={() => handleOpenChat(tx)}
                  className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl border border-blue-200 bg-blue-50 hover:bg-blue-100 text-blue-700 text-xs font-bold transition-all"
                >
                  <MessageSquare className="w-3.5 h-3.5" />
                  Message Seller (Chat)
                </button>

                {tx.status !== 'COMPLETED' && tx.status !== 'completed' && tx.status !== 'CANCELLED' && (
                  <button
                    onClick={() => handleCompleteTransaction(tx.id)}
                    disabled={actionLoading}
                    className="px-4 py-2 rounded-xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-xs shadow-md shadow-eco-600/20 transition-all flex items-center gap-1.5"
                  >
                    <CheckCircle className="w-3.5 h-3.5" />
                    Confirm Delivery & Complete Order
                  </button>
                )}

                {(tx.status === 'COMPLETED' || tx.status === 'completed') && (
                  <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-xl border border-emerald-200">
                    ✓ Completed & Verified
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Transaction Chat Modal */}
      <Modal
        isOpen={!!activeChatTx}
        onClose={() => setActiveChatTx(null)}
        title={`Logistics Chat: ${activeChatTx?.material_type}`}
        subtitle={`Order #${activeChatTx?.id?.substring(0, 8)} with ${activeChatTx?.seller?.organization || activeChatTx?.seller?.name || 'Seller'}`}
        maxWidth="max-w-xl"
      >
        <div className="space-y-4">
          <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-4 h-72 overflow-y-auto space-y-3">
            {chatLoading ? (
              <LoadingSpinner text="Loading messages..." />
            ) : chatMessages.length === 0 ? (
              <div className="text-center py-12 text-slate-400 text-xs">
                No messages yet. Send a note to clarify pickup logistics, vehicle number, or arrival times.
              </div>
            ) : (
              chatMessages.map((m) => {
                const isMine = m.sender_id === user?.id;
                return (
                  <div key={m.id} className={`flex flex-col ${isMine ? 'items-end' : 'items-start'}`}>
                    <div className="flex items-center gap-1.5 text-[10px] text-slate-400 mb-0.5">
                      <span className="font-semibold">{m.sender_name || (isMine ? 'You' : 'Seller')}</span>
                      <span>•</span>
                      <span>{new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                    <div
                      className={`px-3.5 py-2 rounded-2xl text-xs max-w-xs ${
                        isMine ? 'bg-blue-600 text-white rounded-br-none shadow-sm' : 'bg-white border border-slate-200 text-slate-800 rounded-bl-none shadow-sm'
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
              placeholder="Type message regarding pickup time, vehicle info..."
              className="flex-1 px-3.5 py-2.5 rounded-xl border border-slate-200 text-xs focus:ring-2 focus:ring-blue-500 focus:outline-none"
            />
            <button
              type="submit"
              disabled={!newMessage.trim()}
              className="px-4 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-bold text-xs shadow-md flex items-center gap-1.5"
            >
              <Send className="w-3.5 h-3.5" />
              Send
            </button>
          </form>
        </div>
      </Modal>
    </div>
  );
};

export default BuyerTransactions;
