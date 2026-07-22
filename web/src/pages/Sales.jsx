import React, { useEffect, useState, useCallback } from 'react';
import {
  Page, Card, IndexTable, Badge, Button, Banner, Toast, Text, BlockStack,
  InlineStack, EmptyState, Box,
} from '@shopify/polaris';
import { api, money } from '../api.js';
import MonthSelect from '../components/MonthSelect.jsx';
import { useMonth } from '../App.jsx';

export default function Sales() {
  const { month } = useMonth();
  const [status, setStatus] = useState(null);
  const [sales, setSales] = useState([]);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [toast, setToast] = useState('');
  const [error, setError] = useState('');
  const [syncResult, setSyncResult] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    const [st, sl] = await Promise.all([api.get('/sales/status'), api.get(`/sales?month=${month}`)]);
    setStatus(st);
    setSales(sl);
    setLoading(false);
  }, [month]);

  useEffect(() => { load(); }, [load]);

  const sync = async () => {
    setSyncing(true); setError(''); setSyncResult(null);
    try {
      const res = await api.post('/sales/sync', { month });
      setSyncResult(res);
      setToast(`Synced: ${res.matched} of ${res.scanned} orders matched`);
      await load();
    } catch (e) { setError(e.message); } finally { setSyncing(false); }
  };

  const totals = sales.reduce((acc, s) => {
    acc.amount += s.amount;
    const key = s.affiliate?.name || s.discountCode;
    acc.byAff[key] = (acc.byAff[key] || 0) + s.amount;
    return acc;
  }, { amount: 0, byAff: {} });

  const rowMarkup = sales.map((s, index) => (
    <IndexTable.Row id={String(s.id)} key={s.id} position={index}>
      <IndexTable.Cell><Text as="span" fontWeight="semibold">{s.affiliate?.name || '—'}</Text></IndexTable.Cell>
      <IndexTable.Cell><code>{s.discountCode}</code></IndexTable.Cell>
      <IndexTable.Cell>{s.orderName || '—'}</IndexTable.Cell>
      <IndexTable.Cell><Text as="span" numeric>{money(s.amount)}</Text></IndexTable.Cell>
      <IndexTable.Cell>{new Date(s.orderedAt).toLocaleDateString()}</IndexTable.Cell>
    </IndexTable.Row>
  ));

  return (
    <Page
      title="Sales"
      subtitle="Live orders pulled from Shopify, matched to each affiliate by their discount code."
      titleMetadata={<MonthSelect />}
      primaryAction={{
        content: syncing ? 'Syncing…' : 'Sync sales from Shopify',
        onAction: sync,
        loading: syncing,
        disabled: !status?.connected,
      }}
    >
      <BlockStack gap="400">
        {status && !status.connected ? (
          <Banner tone="warning" title="Shopify not connected">
            <p>
              Add <code>SHOPIFY_SHOP</code> and <code>SHOPIFY_ADMIN_TOKEN</code> to the server's <code>.env</code> to pull
              live sales. Until then you can still add sales manually via the API, and everything else works on logged data.
            </p>
          </Banner>
        ) : status?.connected ? (
          <Banner tone="success" title={`Connected to ${status.shop}`}>
            <p>Admin API {status.apiVersion}. Click “Sync sales from Shopify” to match this month's orders to your affiliates.</p>
          </Banner>
        ) : null}

        {error ? <Banner tone="critical">{error}</Banner> : null}
        {syncResult ? (
          <Banner tone="info" title="Last sync">
            <p>{syncResult.matched} of {syncResult.scanned} orders matched a discount code for {syncResult.month}.</p>
          </Banner>
        ) : null}

        <InlineStack gap="400" align="start" blockAlign="stretch">
          <Box minWidth="220px">
            <Card>
              <BlockStack gap="100">
                <Text as="p" tone="subdued" variant="bodySm">Matched sales this month</Text>
                <Text as="p" variant="heading2xl">{money(totals.amount)}</Text>
                <Text as="p" tone="subdued" variant="bodySm">{sales.length} order{sales.length === 1 ? '' : 's'}</Text>
              </BlockStack>
            </Card>
          </Box>
          <Box minWidth="260px">
            <Card>
              <BlockStack gap="200">
                <Text as="p" tone="subdued" variant="bodySm">By affiliate</Text>
                {Object.keys(totals.byAff).length === 0 ? (
                  <Text as="p" tone="subdued">No matched sales yet.</Text>
                ) : (
                  Object.entries(totals.byAff).sort((a, b) => b[1] - a[1]).map(([name, amt]) => (
                    <InlineStack key={name} align="space-between">
                      <Text as="span">{name}</Text>
                      <Text as="span" fontWeight="semibold" numeric>{money(amt)}</Text>
                    </InlineStack>
                  ))
                )}
              </BlockStack>
            </Card>
          </Box>
        </InlineStack>

        <Card padding="0">
          {sales.length === 0 && !loading ? (
            <EmptyState heading="No matched sales this month" image="">
              <p>{status?.connected ? 'Run a sync to pull orders from Shopify.' : 'Connect Shopify to pull live orders, or add sales manually via the API.'}</p>
            </EmptyState>
          ) : (
            <IndexTable
              resourceName={{ singular: 'sale', plural: 'sales' }}
              itemCount={sales.length}
              loading={loading}
              selectable={false}
              headings={[{ title: 'Affiliate' }, { title: 'Code' }, { title: 'Order' }, { title: 'Amount' }, { title: 'Date' }]}
            >
              {rowMarkup}
            </IndexTable>
          )}
        </Card>
      </BlockStack>

      {toast ? <Toast content={toast} onDismiss={() => setToast('')} /> : null}
    </Page>
  );
}
