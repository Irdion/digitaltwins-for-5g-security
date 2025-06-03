import React, { useState } from 'react';
import { Box, Grid, Typography, Container } from '@mui/material';
import TestForm from './components/ApiForm';
import DiffFeed from './components/DiffFeed';
import AnalysisFeed from './components/AnalysisFeed';

export default function App() {
  const [trigger, setTrigger] = useState(0);

  return (
    <Container maxWidth={false} sx={{ py: 4 }}>
      <Typography variant="h4" align="center" gutterBottom>
        5GC NRF Diff Dashboard
      </Typography>
      <Grid container spacing={4}>
        
        <Grid item xs={12} md={6}>
          <Box component="section" p={2} sx={{ bgcolor: 'background.paper', borderRadius: 1, boxShadow: 1 }}>
            <Typography variant="h6" gutterBottom>
              Invoke NRF API
            </Typography>
            <TestForm onSubmitDone={() => setTrigger(t => t + 1)} />
          </Box>
        </Grid>
       
        <Grid item xs={12} md={6}>
          <Box component="section" p={2} sx={{ bgcolor: 'background.paper', borderRadius: 1, boxShadow: 1 }}>
          <DiffFeed refreshTrigger={trigger} />
          </Box>
        </Grid>

        <Grid item xs={12} md={4} sx={{ overflow: 'auto' }}>
          <AnalysisFeed refreshTrigger={trigger} />
        </Grid>

      </Grid>
    </Container>
  );
}