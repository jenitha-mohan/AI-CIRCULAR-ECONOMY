import React, { useState, useEffect } from 'react';
import { ReceiptText, Leaf, ShieldCheck, Download } from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export const BuyerTransactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTxs = async () => {
      setLoading(true);
      try {
        const res = await api.get('/api/transactions');
        setTransactions(res.data);
      } catch (err) {
        console.error('Error fetching transactions:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTxs();
  }, []);

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Procurement Orders & Certificates</h1>
        <p className="text-xs text-slate-500 mt-1">
          Review secondary material settlements and verified environmental offset certificates
        </p>
      </div>

      {loading ? (
        <LoadingSpinner text="Loading procurement history..." />
      ) : transactions.length === 0 ? (
        <EmptyState title="No purchases recorded yet" />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/80 text-slate-500 font-bold uppercase text-[10px] tracking-wider">
                  <th className="py-3.5 px-6">Order ID</th>
                  <th className="py-3.5 px-6">Seller</th>
                  <th className="py-3.5 px-6">Material & Qty</th>
                  <th className="py-3.5 px-6">Price</th>
                  <th className="py-3.5 px-6">Total Amount</th>
                  <th className="py-3.5 px-6">CO₂ Diverted</th>
                  <th className="py-3.5 px-6">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-4 px-6 font-mono text-[11px] text-slate-500">
                      {tx.id.substring(0, 8)}...
                    </td>
                    <td className="py-4 px-6 font-bold text-slate-900">
                      {tx.seller?.organization || tx.seller?.name || 'Verified Seller'}
                    </td>
                    <td className="py-4 px-6">
                      <span className="font-bold text-slate-900">{tx.material_type}</span>
                      <span className="text-slate-400 block text-[11px]">{tx.quantity_kg.toLocaleString('en-IN')} kg</span>
                    </td>
                    <td className="py-4 px-6 font-bold text-slate-900">
                      ₹{tx.agreed_price}/kg
                    </td>
                    <td className="py-4 px-6 font-extrabold text-emerald-600 text-sm">
                      ₹{tx.total_amount.toLocaleString('en-IN')}
                    </td>
                    <td className="py-4 px-6">
                      <div className="inline-flex items-center gap-1 text-emerald-700 font-bold text-xs bg-emerald-50 px-2 py-0.5 rounded-md">
                        <Leaf className="w-3 h-3 text-emerald-600" />
                        {tx.co2_avoided_kg || 180} kg
                      </div>
                    </td>
                    <td className="py-4 px-6">
                      <Badge variant={tx.status === 'completed' ? 'success' : 'warning'} size="xs">
                        {tx.status}
                      </Badge>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default BuyerTransactions;
