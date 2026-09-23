import React from 'react';
import { Recycle, Cpu, ShieldCheck, Calculator, ArrowRight, Sparkles, Layers, Award } from 'lucide-react';
import Badge from '../../components/Badge';

export const About = () => {
  return (
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-12 space-y-12">
      {/* Title */}
      <div className="text-center space-y-3">
        <Badge variant="eco" size="sm">Methodology & Transparency</Badge>
        <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tight">
          AI & Circular Science Architecture
        </h1>
        <p className="text-sm sm:text-base text-slate-600 max-w-2xl mx-auto">
          Scientific framework powering automated waste identification, non-linear pricing intelligence, and transparent matchmaking.
        </p>
      </div>

      {/* Matching Engine Math Box */}
      <div className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-purple-50 text-purple-600">
            <Calculator className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Transparent Matchmaking Formula</h2>
            <p className="text-xs text-slate-500">Every match score is explainable with zero black-box bias.</p>
          </div>
        </div>

        <div className="bg-slate-900 text-slate-100 p-6 rounded-2xl font-mono text-xs sm:text-sm leading-relaxed overflow-x-auto border border-slate-800">
          <div className="text-eco-400 font-bold mb-2"># Transparent Composite Match Formula:</div>
          MatchScore = (0.35 × MaterialSimilarity) +<br />
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(0.25 × QuantityCompatibility) +<br />
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(0.20 × QualityCompatibility) +<br />
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(0.10 × LocationProximity) +<br />
          &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;(0.10 × PurposeCompatibility)
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs text-slate-600">
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60">
            <span className="font-bold text-slate-900 block mb-1">Geospatial Haversine Formula</span>
            Exact great-circle spherical distance calculated between coordinates to estimate transport emissions and logistics feasibility.
          </div>
          <div className="p-4 rounded-2xl bg-slate-50 border border-slate-200/60">
            <span className="font-bold text-slate-900 block mb-1">Match Reason Generation</span>
            The system returns natural language explanations alongside every percentage match score for complete visibility.
          </div>
        </div>
      </div>

      {/* CO2 Conversion Factors Table */}
      <div className="bg-white rounded-3xl p-8 border border-slate-200/80 shadow-sm space-y-6">
        <div className="flex items-center gap-3">
          <div className="p-2.5 rounded-xl bg-emerald-50 text-emerald-600">
            <Award className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-900">Life Cycle Assessment (LCA) Carbon Offset Factors</h2>
            <p className="text-xs text-slate-500">Peer-reviewed displacement coefficients per kilogram of recycled feedstock.</p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs border-collapse">
            <thead>
              <tr className="border-b border-slate-200 bg-slate-50/80 text-slate-600 font-bold uppercase text-[10px] tracking-wider">
                <th className="py-3 px-4">Material Category</th>
                <th className="py-3 px-4">CO₂ Offset (kg CO₂/kg)</th>
                <th className="py-3 px-4">Landfill Diversion</th>
                <th className="py-3 px-4">Virgin Energy Reduction</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 font-medium text-slate-700">
              <tr>
                <td className="py-3 px-4 font-bold text-slate-900">Aluminum (Alloy & Cans)</td>
                <td className="py-3 px-4 text-emerald-600 font-bold">9.10 kg</td>
                <td className="py-3 px-4">98%</td>
                <td className="py-3 px-4">Up to 95%</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-slate-900">Copper (Millberry Scrap)</td>
                <td className="py-3 px-4 text-emerald-600 font-bold">4.50 kg</td>
                <td className="py-3 px-4">99%</td>
                <td className="py-3 px-4">Up to 85%</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-slate-900">E-waste (PCBs & Servers)</td>
                <td className="py-3 px-4 text-emerald-600 font-bold">5.80 kg</td>
                <td className="py-3 px-4">96%</td>
                <td className="py-3 px-4">Up to 80%</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-slate-900">Plastic (HDPE / PET / PP)</td>
                <td className="py-3 px-4 text-emerald-600 font-bold">1.50 kg</td>
                <td className="py-3 px-4">90%</td>
                <td className="py-3 px-4">Up to 70%</td>
              </tr>
              <tr>
                <td className="py-3 px-4 font-bold text-slate-900">Steel (Structural & HMS)</td>
                <td className="py-3 px-4 text-emerald-600 font-bold">1.80 kg</td>
                <td className="py-3 px-4">95%</td>
                <td className="py-3 px-4">Up to 75%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default About;
