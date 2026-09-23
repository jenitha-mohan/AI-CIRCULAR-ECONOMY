import React, { useState, useEffect } from 'react';
import { Sparkles, Building2, MapPin, CheckCircle2, ArrowRight } from 'lucide-react';
import api from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';

export const SellerRecommendations = () => {
  const { user } = useAuth();
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchRecs = async () => {
      setLoading(true);
      setError('');
      try {
        // Get this seller's materials first
        const matRes = await api.get(user?.id ? `/api/materials?seller_id=${user.id}` : '/api/materials');
        const myMaterials = matRes.data;

        // For each material, fetch buyer recommendations from the matching engine
        const allRecs = [];
        for (const mat of myMaterials.slice(0, 5)) {
          try {
            const recRes = await api.get(`/api/recommendations/buyers/${mat.id}?limit=3`);
            const buyers = recRes.data || [];
            buyers.forEach((b) => {
              allRecs.push({ ...b, source_material: mat.material_type, source_material_id: mat.id });
            });
          } catch (_) { /* skip individual material failures */ }
        }

        // Deduplicate by buyer_id, keeping highest match
        const seen = {};
        const deduped = [];
        for (const r of allRecs.sort((a, b) => b.match_score - a.match_score)) {
          if (!seen[r.buyer_id]) {
            seen[r.buyer_id] = true;
            deduped.push(r);
          }
        }
        setRecommendations(deduped);
      } catch (err) {
        console.error('Error fetching buyer leads:', err);
        setError('Could not load recommendations. Please try again.');
      } finally {
        setLoading(false);
      }
    };
    if (user?.id) fetchRecs();
  }, [user]);

  return (
    <div className="space-y-6 pb-12">
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="ai" size="xs">AI Matchmaking Leads</Badge>
        </div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">
          Active Buyer Sourcing Demands
        </h1>
        <p className="text-xs text-slate-500 mt-1">
          Verified recyclers and mills matched to your listed inventory by the 5-factor circular matching engine
        </p>
      </div>

      {error && (
        <div className="p-4 rounded-2xl bg-rose-50 border border-rose-200 text-rose-700 text-xs">{error}</div>
      )}

      {loading ? (
        <LoadingSpinner text="Computing compatibility match scores..." />
      ) : recommendations.length === 0 ? (
        <EmptyState title="No matched buyers yet" description="Add materials to your inventory to see AI-matched buyer leads." />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {recommendations.map((rec, idx) => (
            <div
              key={`${rec.buyer_id}-${idx}`}
              className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <Badge variant="eco" size="xs">{rec.material || rec.source_material}</Badge>
                    <h3 className="text-base font-bold text-slate-900 mt-1">
                      {rec.organization || rec.buyer_name || 'Verified Circular Buyer'}
                    </h3>
                    <p className="text-[11px] text-slate-500 mt-0.5">
                      {rec.distance_km ? `${rec.distance_km} km away` : 'Distance unknown'}
                    </p>
                  </div>
                  <div className="text-right flex-shrink-0">
                    <span className="text-base font-black text-emerald-600">
                      {(rec.match_score * 100).toFixed(0)}%
                    </span>
                    <span className="text-[10px] text-slate-400 block font-semibold uppercase">Match Score</span>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-2 bg-slate-50 p-3 rounded-2xl border border-slate-200/60 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Required Qty</span>
                    <span className="font-bold text-slate-900">{rec.required_quantity || '—'} kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Quality Req.</span>
                    <span className="font-bold text-slate-900">{rec.required_quality || '—'} Grade</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">For Material</span>
                    <span className="font-bold text-slate-900">{rec.source_material || rec.material}</span>
                  </div>
                </div>

                {rec.reasons && rec.reasons.length > 0 && (
                  <div className="mt-4 space-y-1.5">
                    {rec.reasons.slice(0, 2).map((reason, i) => (
                      <div key={i} className="text-[11px] text-slate-600 flex items-center gap-1.5">
                        <CheckCircle2 className="w-3.5 h-3.5 text-emerald-500 flex-shrink-0" />
                        <span>{reason}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              <button
                onClick={() => alert(`Direct negotiation initiated with ${rec.organization || rec.buyer_name}!`)}
                className="mt-6 w-full py-2.5 rounded-xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-xs shadow-sm shadow-eco-600/20 transition-all flex items-center justify-center gap-1.5"
              >
                Send Material Proposal <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SellerRecommendations;

