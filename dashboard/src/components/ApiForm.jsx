import React, { useState } from 'react';
import {
  TextField,
  Button,
  Grid,
  MenuItem,
  Paper,
  Box
} from '@mui/material';

/**
 * TestForm allows crafting and submitting an NRF registration payload.
 *
 * Props:
 * - onSubmitDone: callback invoked after successful submission.
 */

export default function TestForm({ onSubmitDone }) {
  const [nfInstanceId, setNfInstanceId]     = useState('');
  const [nfType, setNfType]                 = useState('UPF');
  const [nfStatus, setNfStatus]             = useState('REGISTERED');
  const [heartBeatTimer, setHeartBeat]      = useState(120);
  const [ipv4Addresses, setIpv4]            = useState('198.51.100.10');
  const [serviceName, setServiceName]       = useState('nupf-data');
  const [apiVersionInUri, setApiVersion]    = useState('v1');
  const [apiFullVersion, setApiFull]        = useState('1.0.0');
  const [scheme, setScheme]                 = useState('http');
  const [nfServiceStatus, setServiceStatus] = useState('REGISTERED');
  const [response, setResponse]             = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!nfInstanceId) return;

    const payloadBody = {
      nfInstanceId,
      nfType,
      nfStatus,
      heartBeatTimer: Number(heartBeatTimer),
      ipv4Addresses: ipv4Addresses.split(',').map(ip => ip.trim()),
      nfServiceList: {
        [`svc-${nfInstanceId}`]: {
          serviceInstanceId: `svc-${nfInstanceId}`,
          serviceName,
          versions: [{ apiVersionInUri, apiFullVersion }],
          scheme,
          nfServiceStatus
        }
      }
    };

    const testPayload = {
      method: 'PUT',
      path: `/nnrf-nfm/v1/nf-instances/${nfInstanceId}`,
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payloadBody)
    };

    const res = await fetch('http://localhost:7100/api/test', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(testPayload)
    });
    const json = await res.json();
    setResponse(json);
    onSubmitDone && onSubmitDone();
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <TextField
            fullWidth label="NF Instance ID"
            value={nfInstanceId}
            onChange={e => setNfInstanceId(e.target.value)}
            required
          />
        </Grid>
        {[
          { label: 'NF Type', value: nfType, setter: setNfType },
          { label: 'NF Status', value: nfStatus, setter: setNfStatus },
          { label: 'Heartbeat Timer', value: heartBeatTimer, setter: setHeartBeat, type: 'number' },
          { label: 'IPv4 Addresses', value: ipv4Addresses, setter: setIpv4 },
          { label: 'Service Name', value: serviceName, setter: setServiceName },
          { label: 'Service Status', value: nfServiceStatus, setter: setServiceStatus },
          { label: 'API Version In URI', value: apiVersionInUri, setter: setApiVersion },
          { label: 'API Full Version', value: apiFullVersion, setter: setApiFull },
          { label: 'Scheme', value: scheme, setter: setScheme },
        ].map((fld) => (
          <Grid item xs={12} sm={6} key={fld.label}>
            <TextField
              fullWidth
              type={fld.type || 'text'}
              label={fld.label}
              value={fld.value}
              onChange={e => fld.setter(e.target.value)}
            />
          </Grid>
        ))}
        <Grid item xs={12}>
          <Button
            type="submit" fullWidth variant="contained"
            sx={{ py: 1.5 }}
          >
            Send PUT
          </Button>
        </Grid>
        {response && (
          <Grid item xs={12}>
            <Paper variant="outlined" sx={{ p: 2, bgcolor: '#fafafa' }}>
              <pre style={{ whiteSpace: 'pre-wrap' }}>
                {JSON.stringify(response, null, 2)}
              </pre>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}