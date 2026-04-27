import React from 'react';
import { MoreHorizontal } from 'lucide-react';

const ChartCard = ({ title, children, className = "" }) => (
  <div className={`bg-white p-6 rounded-2xl shadow-sm border border-gray-100 ${className}`}>
    <div className="flex justify-between items-center mb-6">
      <h3 className="text-lg font-semibold text-gray-800">{title}</h3>
      <button className="text-gray-400 hover:text-gray-600">
        <MoreHorizontal size={20} />
      </button>
    </div>
    <div className="w-full h-[300px]">
      {children}
    </div>
  </div>
);

export default ChartCard;
