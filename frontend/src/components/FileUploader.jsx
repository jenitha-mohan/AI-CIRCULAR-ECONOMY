import React, { useState, useRef } from 'react';
import { UploadCloud, Image as ImageIcon, X, CheckCircle } from 'lucide-react';

export const FileUploader = ({ onFileSelected, previewUrl, onClear, isUploading = false }) => {
  const [dragOver, setDragOver] = useState(false);
  const inputRef = useRef(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      onFileSelected(e.dataTransfer.files[0]);
    }
  };

  const handleChange = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      onFileSelected(e.target.files[0]);
    }
  };

  return (
    <div>
      {previewUrl ? (
        <div className="relative rounded-2xl overflow-hidden border border-slate-200 bg-slate-900 group aspect-video max-h-64 flex items-center justify-center">
          <img
            src={previewUrl}
            alt="Material preview"
            className="w-full h-full object-cover group-hover:opacity-90 transition-opacity"
          />
          {onClear && (
            <button
              type="button"
              onClick={onClear}
              className="absolute top-3 right-3 p-1.5 rounded-full bg-slate-900/80 hover:bg-slate-900 text-white backdrop-blur-sm transition-colors shadow-lg"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <div className="absolute bottom-3 left-3 bg-slate-900/80 backdrop-blur-md px-3 py-1 rounded-full text-white text-[11px] font-medium flex items-center gap-1.5">
            <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
            Image Ready for AI Analysis
          </div>
        </div>
      ) : (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`border-2 border-dashed rounded-3xl p-8 text-center cursor-pointer transition-all ${
            dragOver
              ? 'border-eco-500 bg-eco-50/50'
              : 'border-slate-200 hover:border-eco-400 hover:bg-slate-50/80 bg-slate-50/40'
          }`}
        >
          <input
            ref={inputRef}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            className="hidden"
            onChange={handleChange}
          />
          <div className="w-14 h-14 rounded-2xl bg-white shadow-sm border border-slate-200/80 flex items-center justify-center text-eco-600 mx-auto mb-3">
            <UploadCloud className="w-7 h-7" />
          </div>
          <div className="text-sm font-bold text-slate-800">
            {isUploading ? 'Uploading & Analyzing...' : 'Upload Material Photo for AI Vision'}
          </div>
          <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
            Drag & drop or click to browse. Supports JPG, PNG, WEBP (up to 10MB).
          </p>
        </div>
      )}
    </div>
  );
};

export default FileUploader;
