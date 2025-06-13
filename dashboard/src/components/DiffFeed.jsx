
import React, { useState, useEffect } from 'react';
import { Typography, Box } from '@mui/material';
/**
 * DiffFeed fetches the latest raw diff payload and displays
 * request, Open5GS, and Free5GC JSON side by side.
 *
 * Props:
 *  - refreshTrigger: value to re-fetch when changed.
 */
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

  function safeJSON(txt) {
    if (!txt) return {};          
    try {
      return JSON.parse(txt);
    } catch (err) {
      return { _error: true, raw: txt }; 
    }
  }
  
  const raw = diffs[0].diff || diffs[0];

  const parts = {
    Request:  safeJSON(raw.request),
    Open5GS:  safeJSON(raw.open5gs),
    Free5GC:  safeJSON(raw.free5gc),
  };
 
  return (
    <Box
      sx={{
        display: 'grid',
        gridTemplateColumns: 'repeat(3, 1fr)',
        gap: 2,        
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