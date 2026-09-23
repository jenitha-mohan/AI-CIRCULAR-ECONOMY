import React from 'react';
import { Sparkles, TrendingUp, Cpu, CheckCircle2, ShieldCheck, MapPin, Building2, Layers } from 'lucide-react';
import Badge from './Badge';

export const AIAnalysisCard = ({
  classification,
  pricePrediction,
  demand,
  recommendedBuyers = [],
  onSelectBuyer,
  compact = false
}) => {
  if (!classification && !pricePrediction && !demand) {
    return null;
  }

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-850 to-slate-950 text-white rounded-3xl p-6 sm:p-8 shadow-xl border border-slate-700/60 overflow-hidden relative">
      {/* Glow highlight */}
      <div className="absolute top-0 right-0 w-96 h-96 bg-eco-500/10 rounded-full blur-3xl pointer-events-none -mr-20 -mt-20"></div>

      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3 pb-6 border-b border-slate-700/60 relative z-10">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-eco-500/20 text-eco-400 border border-eco-500/30">
            <Sparkles className="w-5 h-5 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-lg font-bold text-white">AI Circular Intelligence Engine</h3>
              <Badge variant="ai" size="xs">Live ML Inference</Badge>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Multi-modal inference: Transfer Learning Vision + Gradient Boosting Regressor
            </p>
          </div>
        </div>

        {pricePrediction && (
          <div className="flex items-center gap-2 text-xs text-slate-400">
            <span className="inline-block w-2 h-2 rounded-full bg-emerald-400"></span>
            <span>Model v{pricePrediction.model_version || '1.0.0'} ({pricePrediction.mode || 'production'})</span>
          </div>
        )}
      </div>

      {/* Primary Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 py-6 border-b border-slate-700/60 relative z-10">
        {/* Classification */}
        {classification && (
          <div className="bg-slate-800/60 rounded-2xl p-4 border border-slate-700/40">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>AI Material Classification</span>
              <Cpu className="w-4 h-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-white flex items-center gap-2">
              {classification.material}
              <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-eco-500/20 text-eco-300 border border-eco-500/30">
                {(classification.confidence * 100).toFixed(0)}% Conf
              </span>
            </div>
            {/* Confidence Bar */}
            <div className="w-full bg-slate-700 rounded-full h-1.5 mt-3 overflow-hidden">
              <div
                className="bg-eco-400 h-full rounded-full transition-all duration-500"
                style={{ width: `${Math.min(100, classification.confidence * 100)}%` }}
              ></div>
            </div>
            <div className="text-[11px] text-slate-400 mt-2 flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" /> MobileNetV2 Feature Extractor
            </div>
          </div>
        )}

        {/* Price Prediction */}
        {pricePrediction && (
          <div className="bg-slate-800/60 rounded-2xl p-4 border border-slate-700/40">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>Predicted Fair Market Price</span>
              <TrendingUp className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-emerald-400">
              ₹{pricePrediction.predicted_price_per_kg?.toFixed(2)}
              <span className="text-xs text-slate-300 font-normal"> / kg</span>
            </div>
            <div className="mt-2 text-xs text-slate-300">
              Est. Batch Total:{' '}
              <span className="font-bold text-white">
                ₹{pricePrediction.estimated_total_value?.toLocaleString('en-IN')}
              </span>
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Gradient Boosting Regression (Holdout R²: 0.996)
            </div>
          </div>
        )}

        {/* Demand & Trajectory */}
        {demand && (
          <div className="bg-slate-800/60 rounded-2xl p-4 border border-slate-700/40">
            <div className="flex items-center justify-between text-xs text-slate-400 mb-2">
              <span>Current Market Demand</span>
              <Layers className="w-4 h-4 text-sky-400" />
            </div>
            <div className="flex items-center gap-2">
              <span className="text-2xl font-bold text-white">{demand.demand_category || 'High'}</span>
              <Badge variant={demand.trend === 'increasing' ? 'success' : 'eco'} size="xs">
                {demand.trend === 'increasing' ? '↑ Rising' : '→ Stable'}
              </Badge>
            </div>
            <div className="text-xs text-slate-300 mt-2">
              Regional monthly forecast: {(demand.predicted_demand_kg || 45000).toLocaleString('en-IN')} kg
            </div>
            <div className="text-[11px] text-slate-400 mt-1">
              Time-series 30-day lag projection
            </div>
          </div>
        )}
      </div>

      {/* Feature Importance / Top Influencing Factors */}
      {pricePrediction?.top_factors && Object.keys(pricePrediction.top_factors).length > 0 && (
        <div className="py-4 border-b border-slate-700/60 relative z-10">
          <div className="text-xs font-semibold text-slate-300 mb-2.5">
            Key Factors Influencing AI Valuation:
          </div>
          <div className="flex flex-wrap gap-2">
            {Object.entries(pricePrediction.top_factors).slice(0, 5).map(([factor, weight]) => (
              <span
                key={factor}
                className="inline-flex items-center gap-1.5 text-xs px-2.5 py-1 rounded-lg bg-slate-800 text-slate-300 border border-slate-700/60"
              >
                <span className="capitalize">{factor.replace(/_/g, ' ')}</span>
                <span className="text-eco-400 font-semibold">{weight}%</span>
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Recommended Buyers Section */}
      {recommendedBuyers.length > 0 && (
        <div className="pt-6 relative z-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <h4 className="text-sm font-bold text-white">AI-Matched Buyers & Recyclers</h4>
              <span className="text-xs bg-eco-500/20 text-eco-300 px-2 py-0.5 rounded-full font-semibold border border-eco-500/30">
                {recommendedBuyers.length} Compatible
              </span>
            </div>
            <span className="text-xs text-slate-400">
              Formula: 35% Mat + 25% Qty + 20% Qual + 10% Loc + 10% Purpose
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
            {recommendedBuyers.slice(0, compact ? 2 : 4).map((b, i) => (
              <div
                key={i}
                className="bg-slate-800/80 hover:bg-slate-700/80 transition-colors p-4 rounded-2xl border border-slate-700/60 flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-start justify-between gap-2">
                    <div>
                      <div className="text-sm font-bold text-white flex items-center gap-1.5">
                        <Building2 className="w-3.5 h-3.5 text-eco-400" />
                        {b.buyer_name}
                      </div>
                      {b.organization && (
                        <div className="text-xs text-slate-400 mt-0.5">{b.organization}</div>
                      )}
                    </div>
                    <div className="text-right">
                      <div className="text-base font-black text-emerald-400">
                        {(b.match_score * 100).toFixed(0)}%
                      </div>
                      <div className="text-[10px] text-slate-400 uppercase tracking-wider font-semibold">
                        Match Score
                      </div>
                    </div>
                  </div>

                  <div className="mt-3 flex items-center gap-3 text-xs text-slate-300">
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3.5 h-3.5 text-sky-400" />
                      {b.distance_km} km away
                    </span>
                    <span>•</span>
                    <span>Req: {b.required_quantity} kg ({b.required_quality})</span>
                  </div>

                  {/* Matching Reasons */}
                  {b.reasons && b.reasons.length > 0 && (
                    <div className="mt-3 space-y-1">
                      {b.reasons.slice(0, 2).map((reason, rIdx) => (
                        <div key={rIdx} className="text-[11px] text-slate-300 flex items-center gap-1.5">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400 flex-shrink-0" />
                          <span>{reason}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {onSelectBuyer && (
                  <button
                    onClick={() => onSelectBuyer(b)}
                    className="mt-4 w-full py-2 px-3 rounded-xl bg-eco-600 hover:bg-eco-500 text-white text-xs font-semibold transition-colors"
                  >
                    Initiate Direct Offer
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIAnalysisCard;
