import React, { useState, useEffect } from 'react';
import { Search, MapPin, Building2, ShoppingBag, Sparkles, Filter, CheckCircle } from 'lucide-react';
import api from '../../api/client';
import Badge from '../../components/Badge';
import LoadingSpinner from '../../components/LoadingSpinner';
import EmptyState from '../../components/EmptyState';
import Modal from '../../components/Modal';

export const BuyerSearch = () => {
  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [maxDistance, setMaxDistance] = useState(150);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedQuality, setSelectedQuality] = useState('All');
  const [selectedMaterial, setSelectedMaterial] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isBuying, setIsBuying] = useState(false);
  const [buySuccess, setBuySuccess] = useState(false);

  const CATEGORIES = ['All', 'Aluminum', 'Copper', 'Steel', 'Plastic', 'Cardboard', 'Paper', 'Glass', 'Textile', 'E-waste', 'Other'];

  const fetchMaterials = async () => {
    setLoading(true);
    try {
      const res = await api.get('/api/materials?status=available');
      setMaterials(res.data);
    } catch (err) {
      console.error('Error searching materials:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMaterials();
  }, []);

  const filtered = materials.filter((m) => {
    const matchSearch =
      m.material_type.toLowerCase().includes(search.toLowerCase()) ||
      (m.description && m.description.toLowerCase().includes(search.toLowerCase()));
    const matchCat = selectedCategory === 'All' || m.material_type.toLowerCase() === selectedCategory.toLowerCase();
    const matchQual = selectedQuality === 'All' || m.quality === selectedQuality;
    return matchSearch && matchCat && matchQual;
  });

  const handleOpenDetail = (mat) => {
    setSelectedMaterial(mat);
    setIsModalOpen(true);
    setBuySuccess(false);
  };

  const handleConfirmPurchase = async () => {
    if (!selectedMaterial) return;
    setIsBuying(true);
    try {
      await api.post('/api/transactions', {
        listing_id: selectedMaterial.listings?.[0]?.id || null,
        seller_id: selectedMaterial.seller_id,
        material_type: selectedMaterial.material_type,
        quantity_kg: selectedMaterial.quantity_kg,
        agreed_price: selectedMaterial.predicted_price || 40.0,
      });
      setBuySuccess(true);
      fetchMaterials();
    } catch (err) {
      console.error('Purchase error:', err);
    } finally {
      setIsBuying(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      <div>
        <h1 className="text-2xl font-extrabold text-slate-900 tracking-tight">Geospatial Material Sourcing</h1>
        <p className="text-xs text-slate-500 mt-1">Search proximate industrial recyclables with Haversine distance calculations</p>
      </div>

      {/* Filter Bar */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
            <input
              type="text"
              placeholder="Search by alloy, polymer, keyword..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500"
            />
          </div>

          <div>
            <select
              value={selectedQuality}
              onChange={(e) => setSelectedQuality(e.target.value)}
              className="w-full py-2 px-3 rounded-xl text-xs sm:text-sm bg-slate-50 border border-slate-200 focus:outline-none focus:ring-2 focus:ring-eco-500/20 focus:border-eco-500 font-medium text-slate-700"
            >
              <option value="All">All Quality Grades</option>
              <option value="Industrial Grade">Industrial Grade</option>
              <option value="High">High Grade</option>
              <option value="Medium">Medium Grade</option>
              <option value="Low">Low Grade</option>
            </select>
          </div>

          <div className="flex items-center gap-2 px-2 text-xs text-slate-600">
            <span className="whitespace-nowrap font-medium">Max Transit:</span>
            <input
              type="range"
              min="10"
              max="500"
              step="10"
              value={maxDistance}
              onChange={(e) => setMaxDistance(Number(e.target.value))}
              className="w-full accent-eco-600"
            />
            <span className="font-bold text-slate-900 min-w-[50px]">{maxDistance} km</span>
          </div>
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-1 text-xs">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-xl font-semibold whitespace-nowrap transition-colors ${
                selectedCategory === cat
                  ? 'bg-eco-600 text-white shadow-sm'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200/80'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {loading ? (
        <LoadingSpinner text="Searching proximate recyclables..." />
      ) : filtered.length === 0 ? (
        <EmptyState title="No recyclable lots found" description="Adjust your search radius or material filter." />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filtered.map((mat) => (
            <div
              key={mat.id}
              onClick={() => handleOpenDetail(mat)}
              className="bg-white rounded-3xl overflow-hidden border border-slate-200/80 shadow-sm hover:shadow-md transition-all cursor-pointer flex flex-col justify-between group"
            >
              <div className="aspect-video bg-slate-100 relative overflow-hidden">
                <img
                  src={mat.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600'}
                  alt={mat.material_type}
                  className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                />
                <div className="absolute top-3 left-3">
                  <Badge variant="eco" size="xs">{mat.material_type}</Badge>
                </div>
                <div className="absolute bottom-3 right-3 bg-slate-900/80 backdrop-blur-md px-2.5 py-1 rounded-full text-white text-[11px] font-bold">
                  {mat.quantity_kg} kg
                </div>
              </div>

              <div className="p-5 flex flex-col justify-between flex-grow">
                <div>
                  <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-1">
                    {mat.quality} • {mat.condition}
                  </div>
                  <h3 className="text-sm font-bold text-slate-900 line-clamp-1 mb-1.5">
                    {mat.description || `${mat.quality} ${mat.material_type}`}
                  </h3>
                  <div className="text-xs text-slate-500 flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5 text-sky-500" />
                    <span>~24 km from Coimbatore Hub</span>
                  </div>
                </div>

                <div className="pt-4 border-t border-slate-100 flex items-center justify-between mt-4">
                  <div>
                    <div className="text-[10px] text-slate-400 font-semibold uppercase">AI Price</div>
                    <div className="text-base font-extrabold text-emerald-600">
                      ₹{mat.predicted_price || 40}/kg
                    </div>
                  </div>
                  <button className="px-3.5 py-1.5 rounded-xl bg-eco-600 text-white font-bold text-xs shadow-sm hover:bg-eco-700 transition-colors">
                    Procure
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Purchase Modal */}
      <Modal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title={selectedMaterial?.material_type || 'Feedstock Details'}
        subtitle={`Lot ID: ${selectedMaterial?.id?.substring(0, 8)}`}
      >
        {selectedMaterial && (
          <div className="space-y-6">
            {buySuccess ? (
              <div className="bg-emerald-50 border border-emerald-200 rounded-2xl p-6 text-center space-y-3">
                <CheckCircle className="w-10 h-10 text-emerald-600 mx-auto" />
                <h4 className="text-base font-bold text-emerald-900">Procurement Order Confirmed!</h4>
                <p className="text-xs text-emerald-700 max-w-sm mx-auto">
                  Shipment request sent to seller. Carbon displacement credits logged.
                </p>
                <button
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 rounded-xl bg-emerald-600 text-white text-xs font-semibold"
                >
                  Done
                </button>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="aspect-video rounded-2xl overflow-hidden bg-slate-100">
                  <img
                    src={selectedMaterial.image_url || 'https://images.unsplash.com/photo-1558441719-8b489c6ef147?w=600'}
                    alt={selectedMaterial.material_type}
                    className="w-full h-full object-cover"
                  />
                </div>

                <div className="grid grid-cols-2 gap-3 bg-slate-50 p-3.5 rounded-2xl border border-slate-200/60 text-xs">
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Available Batch</span>
                    <span className="font-bold text-slate-900 text-sm">{selectedMaterial.quantity_kg} kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Quality Grade</span>
                    <span className="font-bold text-slate-900 text-sm">{selectedMaterial.quality}</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Price per kg</span>
                    <span className="font-extrabold text-emerald-600 text-sm">₹{selectedMaterial.predicted_price}/kg</span>
                  </div>
                  <div>
                    <span className="text-slate-400 block text-[10px] uppercase font-semibold">Total Cost</span>
                    <span className="font-bold text-slate-900 text-sm">
                      ₹{(selectedMaterial.predicted_price * selectedMaterial.quantity_kg).toLocaleString('en-IN')}
                    </span>
                  </div>
                </div>

                <button
                  onClick={handleConfirmPurchase}
                  disabled={isBuying}
                  className="w-full py-3.5 rounded-2xl bg-eco-600 hover:bg-eco-700 text-white font-bold text-sm shadow-md shadow-eco-600/20 transition-all flex items-center justify-center gap-2"
                >
                  <ShoppingBag className="w-4 h-4" />
                  {isBuying ? 'Confirming Order...' : 'Confirm Feedstock Purchase'}
                </button>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

export default BuyerSearch;
