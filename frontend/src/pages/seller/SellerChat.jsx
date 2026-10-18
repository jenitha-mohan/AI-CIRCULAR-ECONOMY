import React, { useState, useEffect } from 'react';
import {
  MessageSquare,
  Send,
  Building2,
  Calendar,
  CheckCircle,
  Clock,
  ShieldCheck,
  AlertCircle,
  Truck
} from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import Badge from '../../components/Badge';

export const SellerChat = () => {
  const { user } = useAuth();
  const [conversations, setConversations] = useState([]);
  const [selectedTx, setSelectedTx] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [chatLoading, setChatLoading] = useState(false);
  const [error, setError] = useState('');

  const fetchConversations = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get('/api/chat/conversations');
      const convos = res.data || [];
      setConversations(convos);
      if (convos.length > 0 && !selectedTx) {
        setSelectedTx(convos[0]);
      }
    } catch (err) {
      console.error('Error fetching chat conversations:', err);
      setError('Failed to load chat conversations.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (!selectedTx) return;

    const fetchMessages = async () => {
      setChatLoading(true);
      try {
        const res = await api.get(`/api/transactions/${selectedTx.transaction_id}/messages`);
        setMessages(res.data || []);
      } catch (err) {
        console.error('Error fetching messages:', err);
      } finally {
        setChatLoading(false);
      }
    };

    fetchMessages();
  }, [selectedTx]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !selectedTx) return;

    const text = newMessage.trim();
    setNewMessage('');
    try {
      const res = await api.post(`/api/transactions/${selectedTx.transaction_id}/messages`, {
        message: text,
      });
      setMessages((prev) => [...prev, res.data]);
    } catch (err) {
      console.error('Error sending message:', err);
      alert('Failed to send message: ' + (err.response?.data?.detail || err.message));
    }
  };

  if (loading) {
    return <LoadingSpinner text="Loading your transaction conversations..." />;
  }

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Direct Transaction Chat</h1>
        <p className="text-xs text-slate-500 mt-1">
          Secure, verified buyer-seller messaging strictly tied to confirmed recyclable transactions
        </p>
      </div>

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-700 text-xs rounded-2xl flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {conversations.length === 0 ? (
        <EmptyState
          title="No active chat threads"
          description="Direct chat activates automatically when a buyer's offer is accepted into a confirmed circular transaction."
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-12 gap-6 bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden min-h-[500px]">
          {/* Conversation List */}
          <div className="md:col-span-5 border-r border-slate-200/80 p-4 space-y-2 overflow-y-auto max-h-[600px]">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider px-2 mb-2">
              Confirmed Deals ({conversations.length})
            </div>
            {conversations.map((c) => {
              const isSelected = selectedTx?.transaction_id === c.transaction_id;
              return (
                <button
                  key={c.transaction_id}
                  onClick={() => setSelectedTx(c)}
                  className={`w-full text-left p-3.5 rounded-2xl transition-all ${
                    isSelected
                      ? 'bg-eco-50 border border-eco-200 text-slate-900 shadow-sm'
                      : 'hover:bg-slate-50 border border-transparent text-slate-700'
                  }`}
                >
                  <div className="flex items-center justify-between mb-1">
                    <span className="font-bold text-sm text-slate-900">
                      {c.other_party?.name || 'Verified Buyer'}
                    </span>
                    <Badge variant="info" size="xs">
                      {c.material_type}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-500 line-clamp-1">
                    {c.last_message?.message || 'Chat opened for transaction'}
                  </p>
                  <div className="flex items-center gap-2 mt-2 text-[10px] text-slate-400">
                    <Truck className="w-3 h-3" />
                    <span>Deal #{c.transaction_id?.substring(0, 8)}</span>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Active Chat Window */}
          <div className="md:col-span-7 flex flex-col justify-between p-4 sm:p-6 min-h-[400px]">
            {selectedTx ? (
              <>
                {/* Chat Header */}
                <div className="pb-4 border-b border-slate-100 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-2xl bg-eco-50 text-eco-600 flex items-center justify-center font-bold">
                      <Building2 className="w-5 h-5" />
                    </div>
                    <div>
                      <h3 className="text-sm font-extrabold text-slate-900">
                        {selectedTx.other_party?.organization || selectedTx.other_party?.name || 'Buyer'}
                      </h3>
                      <p className="text-[11px] text-slate-500">
                        {selectedTx.material_type} • {selectedTx.quantity_kg} kg @ ₹{selectedTx.agreed_price}/kg
                      </p>
                    </div>
                  </div>
                  <Badge variant="success" size="xs">
                    {selectedTx.status || 'CONFIRMED'}
                  </Badge>
                </div>

                {/* Messages Body */}
                <div className="flex-1 overflow-y-auto py-4 space-y-3 max-h-[380px]">
                  {chatLoading ? (
                    <div className="flex justify-center py-8">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-eco-600"></div>
                    </div>
                  ) : messages.length === 0 ? (
                    <div className="text-center py-12 text-slate-400 text-xs">
                      No messages in this transaction yet. Send a note to coordinate dispatch or pickup.
                    </div>
                  ) : (
                    messages.map((m) => {
                      const isMe = m.sender_id === user?.id;
                      return (
                        <div
                          key={m.id}
                          className={`flex flex-col ${isMe ? 'items-end' : 'items-start'}`}
                        >
                          <div
                            className={`max-w-[75%] p-3.5 rounded-2xl text-xs sm:text-sm ${
                              isMe
                                ? 'bg-eco-600 text-white rounded-br-none'
                                : 'bg-slate-100 text-slate-800 rounded-bl-none'
                            }`}
                          >
                            {m.message}
                          </div>
                          <span className="text-[10px] text-slate-400 mt-1 px-1">
                            {new Date(m.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                      );
                    })
                  )}
                </div>

                {/* Input form */}
                <form onSubmit={handleSendMessage} className="pt-3 border-t border-slate-100 flex gap-2">
                  <input
                    type="text"
                    value={newMessage}
                    onChange={(e) => setNewMessage(e.target.value)}
                    placeholder="Type dispatch updates, pickup time, or note..."
                    className="flex-1 px-4 py-2.5 rounded-xl border border-slate-200 text-sm focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
                  />
                  <button
                    type="submit"
                    disabled={!newMessage.trim()}
                    className="px-4 py-2.5 rounded-xl bg-eco-600 hover:bg-eco-700 disabled:opacity-50 text-white font-bold text-xs flex items-center gap-1.5 transition-all shadow-sm"
                  >
                    <Send className="w-3.5 h-3.5" />
                    Send
                  </button>
                </form>
              </>
            ) : (
              <div className="flex items-center justify-center h-full text-slate-400 text-xs">
                Select a conversation from the left to start messaging.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default SellerChat;
