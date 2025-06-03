// src/components/DiffFeed.jsx
import React, { useState, useEffect } from 'react';
import { Typography, Box } from '@mui/material';

export default function DiffFeed({ refreshTrigger }) {
  const [diffs, setDiffs] = useState([]);

  useEffect(() => {
    (async () => {
      try {
        const res  = await fetch('http://localhost:9000/diffs/latest?count=1');
        const data = await res.json();
        setDiffs(data);
      } catch (e) {
        console.error('Failed to fetch diffs', e);
      }
    })();
  }, [refreshTrigger]);

  if (diffs.length === 0) {
    return <Typography>No diffs yet.</Typography>;
  }

  // We only care about the first (latest) diff
  const raw = diffs[0].diff || diffs[0];

  // Parse the three JSON-string fields
  const parts = {
    Request:    JSON.parse(raw.request),
    Open5GS:    JSON.parse(raw.open5gs),
    Free5GC:    JSON.parse(raw.free5gc),
  };

  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: 2,           // theme spacing * 2
        height: '100%',
      }}
    >
      {Object.entries(parts).map(([title, obj]) => (
        <Box
          key={title}
          sx={{
            bgcolor: 'grey.900',
            color: 'grey.100',
            borderRadius: 1,
            p: 2,
            overflow: 'auto',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Typography
            variant="subtitle1"
            sx={{ mb: 1, borderBottom: '1px solid rgba(255,255,255,0.2)' }}
          >
            {title}
          </Typography>
          <Box
            component="pre"
            sx={{
              m: 0,
              flex: 1,
              fontFamily: 'monospace',
              whiteSpace: 'pre-wrap',
              fontSize: '0.85rem',
            }}
          >
            {JSON.stringify(obj, null, 2)}
          </Box>
        </Box>
      ))}
    </Box>
  );
}