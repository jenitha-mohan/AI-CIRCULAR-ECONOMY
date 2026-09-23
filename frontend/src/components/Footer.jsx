import React from 'react';
import { Recycle, Heart, Shield, Cpu, ExternalLink } from 'lucide-react';
import { Link } from 'react-router-dom';

export const Footer = () => {
  return (
    <footer className="bg-slate-900 text-slate-400 text-sm border-t border-slate-800 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-eco-600 flex items-center justify-center text-white">
                <Recycle className="w-5 h-5" />
              </div>
              <span className="font-extrabold text-white text-lg tracking-tight">
                Circul<span className="text-eco-400">AI</span>
              </span>
            </div>
            <p className="text-xs text-slate-400 leading-relaxed">
              Industrial AI-driven circular economy exchange accelerating landfill diversion, precision recyclables pricing, and intelligent buyer matchmaking.
            </p>
          </div>

          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">Platform</h4>
            <ul className="space-y-2 text-xs">
              <li><Link to="/marketplace" className="hover:text-white transition-colors">Material Catalogue</Link></li>
              <li><Link to="/about" className="hover:text-white transition-colors">AI & Circular Methodology</Link></li>
              <li><a href="/docs" target="_blank" rel="noreferrer" className="hover:text-white transition-colors flex items-center gap-1">FastAPI Swagger <ExternalLink className="w-3 h-3" /></a></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">AI Subsystems</h4>
            <ul className="space-y-2 text-xs">
              <li><span className="text-slate-300">MobileNetV2 Vision Classifier</span></li>
              <li><span className="text-slate-300">Gradient Boosting Price Regressor</span></li>
              <li><span className="text-slate-300">Haversine Geospatial Matchmaker</span></li>
              <li><span className="text-slate-300">Time-Series Demand Forecaster</span></li>
            </ul>
          </div>

          <div>
            <h4 className="text-xs font-bold text-white uppercase tracking-wider mb-4">Circularity Standards</h4>
            <p className="text-xs text-slate-400 leading-relaxed">
              CO₂ offset metrics and lifecycle diversion factors calibrated according to peer-reviewed industrial recycling benchmarks.
            </p>
          </div>
        </div>

        <div className="pt-8 border-t border-slate-800 flex flex-col sm:flex-row items-center justify-between text-xs gap-4">
          <div>
            © {new Date().getFullYear()} CirculAI Marketplace — AI for Sustainable Future
          </div>
          <div className="flex items-center gap-4 text-slate-400">
            <span>Powered by Scikit-Learn, PyTorch & FastAPI</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
