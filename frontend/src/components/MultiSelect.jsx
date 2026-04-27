import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, Check } from 'lucide-react';

export default function MultiSelect({ options, selected, onChange, placeholder, icon: Icon }) {
  const [isOpen, setIsOpen] = useState(false);
  const containerRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (containerRef.current && !containerRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const toggleOption = (option) => {
    if (selected.includes(option)) {
      onChange(selected.filter(item => item !== option));
    } else {
      onChange([...selected, option]);
    }
  };

  const displayText = selected.length === 0 
    ? placeholder 
    : selected.length === 1 
      ? selected[0] 
      : `${selected.length} mục đã chọn`;

  return (
    <div className="relative" ref={containerRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center pl-10 pr-10 py-2.5 w-full bg-gray-50 border-none rounded-xl text-sm font-medium hover:bg-gray-100 transition-colors text-left"
      >
        <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400">
          {Icon && <Icon size={16} />}
        </span>
        <span className="truncate flex-1 text-gray-700">{displayText}</span>
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
          <ChevronDown size={16} className={`transition-transform duration-200 ${isOpen ? 'rotate-180' : ''}`} />
        </span>
      </button>

      {isOpen && (
        <div className="absolute z-50 w-full mt-2 bg-white border border-gray-100 rounded-xl shadow-lg max-h-60 overflow-auto">
          {options.length === 0 ? (
            <div className="px-4 py-3 text-sm text-gray-500 text-center">Không có dữ liệu</div>
          ) : (
            options.map((option) => {
              const isSelected = selected.includes(option);
              return (
                <div
                  key={option}
                  onClick={() => toggleOption(option)}
                  className="flex items-center px-4 py-2.5 hover:bg-gray-50 cursor-pointer text-sm transition-colors"
                >
                  <div className={`w-4 h-4 mr-3 flex items-center justify-center rounded border ${isSelected ? 'bg-indigo-600 border-indigo-600' : 'border-gray-300'}`}>
                    {isSelected && <Check size={12} className="text-white" />}
                  </div>
                  <span className={isSelected ? 'font-medium text-indigo-900' : 'text-gray-700'}>{option}</span>
                </div>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}
