
import React, { useEffect, useState } from 'react';
import { Box, Typography, Chip } from '@mui/material';


/**
 * Displays a real-time feed of diff-worker verdicts via Server-Sent Events.
 * Props:
 *  - refreshTrigger: value to recreate the SSE connection when changed.
 */


export default function AnalysisFeed({ refreshTrigger }) {
  const [results, setResults] = useState([]);

  useEffect(() => {
    const es = new EventSource('http://localhost:9100/analysis/latest');

    es.onmessage = (e) => {
      try {
        const payload = JSON.parse(e.data);          
        setResults((prev) => [payload, ...prev].slice(0, 100)); 
      } catch (err) {
        console.error('Malformed SSE payload', err);
      }
    };

    es.onerror = (err) => {
      console.error('SSE connection error', err);
      es.close();                                    
    };

    return () => es.close();
  }, [refreshTrigger]);  

  if (!results.length) {
    return <Typography>No analysis results yet.</Typography>;
  }

  return (
    <Box sx={{ display: 'grid', gap: 2, overflow: 'auto' }}>
      {results.map(({ nfInstanceId, verdict, report }, i) => (
        <Box
          key={i}
          sx={{
            p: 2,
            bgcolor: 'grey.200',
            color: 'text.primary',
            borderRadius: 1,
            boxShadow: 1,
            fontFamily: 'monospace',
            whiteSpace: 'pre-wrap',
            fontSize: '0.85rem',
          }}
        >
          <Box sx={{ mb: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Typography variant="subtitle2">{nfInstanceId}</Typography>
            <Chip size="small" label={verdict} color={
              verdict === 'CRITICAL' ? 'error'
              : verdict === 'WARNING' ? 'warning'
              : verdict === 'SUSPICIOUS' ? 'secondary'
              : 'success'
            }/>
          </Box>

          <pre style={{ margin: 0 }}>
            {JSON.stringify(report, null, 2)}
          </pre>
        </Box>
      ))}
    </Box>
  );
}
