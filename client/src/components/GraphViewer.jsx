import React from 'react';

const GraphViewer = ({ graphUrl }) => {
  if (!graphUrl) return null;

  return (
    <div style={{ marginTop: '20px' }}>
      <iframe
        src={graphUrl}
        title="Dependency Graph"
        width="100%"
        height="800px"
        style={{ border: 'none' }}
      />
    </div>
  );
};

export default GraphViewer;
