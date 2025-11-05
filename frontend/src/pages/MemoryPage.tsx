import React, { useState } from 'react';
import MemoryInput from '../components/MemoryInput';
import MemoryList from '../components/MemoryList';

const MemoryPage: React.FC = () => {
  const [refreshKey, setRefreshKey] = useState(0);

  const handleMemoryAdded = () => {
    // Trigger refresh of memory list
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="h-full overflow-y-auto p-6 space-y-6">
      <MemoryInput onMemoryAdded={handleMemoryAdded} />
      <MemoryList key={refreshKey} />
    </div>
  );
};

export default MemoryPage;
