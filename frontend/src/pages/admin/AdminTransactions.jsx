import React, { useState, useEffect } from 'react';
import { ReceiptText, Leaf, ShieldCheck, CheckCircle } from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';

export const AdminTransactions = () => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTransactions = async () => {
      setLoading(true);
      try {
        const res = await api.get('/api/transactions');
        setTransactions(res.data);
      } catch (err) {
        console.error('Error loading transactions:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchTransactions();
  }, []);

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Platform Transaction Ledger</h1>
        <p className="text-xs text-slate-500 mt-1">Audit circular exchanges, trade volumes, and registered carbon offsets</p>
      </div>

      {loading ? (
        <LoadingSpinner text="Loading transaction records..." />
      ) : (
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-slate-100 bg-slate-50/80 text-slate-500 font-bold uppercase text-[10px] tracking-wider">
                  <th className="py-3.5 px-6">ID</th>
                  <th className="py-3.5 px-6">Buyer & Seller</th>
                  <th className="py-3.5 px-6">Material</th>
                  <th className="py-3.5 px-6">Quantity</th>
                  <th className="py-3.5 px-6">Settlement (₹)</th>
                  <th className="py-3.5 px-6">CO₂ Avoided</th>
                  <th className="py-3.5 px-6">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
                {transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-50/60 transition-colors">
                    <td className="py-4 px-6 font-mono text-[11px] text-slate-400">
                      {tx.id.substring(0, 8)}
                    </td>
                    <td className="py-4 px-6">
                      <div className="font-bold text-slate-900">Buyer: {tx.buyer?.name}</div>
                      <div className="text-[11px] text-slate-500">Seller: {tx.seller?.name}</div>
                    </td>
                    <td className="py-4 px-6 font-bold text-slate-900">
                      {tx.material_type}
                    </td>
                    <td className="py-4 px-6 font-semibold text-slate-900">
                      {tx.quantity_kg.toLocaleString('en-IN')} kg
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

export default AdminTransactions;
