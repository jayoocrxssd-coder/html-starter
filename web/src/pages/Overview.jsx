import React, { useEffect, useState, useCallback } from 'react';
import {
  Page, Card, Text, BlockStack, InlineStack, InlineGrid, Box, Badge,
  ProgressBar, Banner, Divider, SkeletonBodyText,
} from '@shopify/polaris';
import { api, money, compactNumber } from '../api.js';
import MonthSelect from '../components/MonthSelect.jsx';
import { useMonth } from '../App.jsx';

function Stat({ label, value, sub, tone }) {
  return (
    <Card>
      <BlockStack gap="100">
        <Text as="p" tone="subdued" variant="bodySm">{label}</Text>
        <Text as="p" variant="heading2xl" tone={tone}>{value}</Text>
        {sub ? <Text as="p" tone="subdued" variant="bodySm">{sub}</Text> : null}
      </BlockStack>
    </Card>
  );
}

export default function Overview() {
  const { month } = useMonth();
  const [payouts, setPayouts] = useState(null);
  const [board, setBoard] = useState(null);
  const [status, setStatus] = useState(null);

  const load = useCallback(async () => {
    const [p, b, s] = await Promise.all([
      api.get(`/payouts?month=${month}`),
      api.get(`/leaderboard?month=${month}`),
      api.get('/sales/status'),
    ]);
    setPayouts(p); setBoard(b); setStatus(s);
  }, [month]);
  useEffect(() => { load(); }, [load]);

  if (!payouts || !board) {
    return <Page title="Overview" titleMetadata={<MonthSelect />}><Card><SkeletonBodyText lines={4} /></Card></Page>;
  }

  const budget = payouts.budget;
  const rows = payouts.rows;
  const totalSales = rows.reduce((s, r) => s + r.sales, 0);
  const totalOrders = rows.reduce((s, r) => s + r.orderCount, 0);
  const paidCount = rows.filter((r) => r.paid).length;

  return (
    <Page title="Overview" subtitle="Your affiliate program this month at a glance." titleMetadata={<MonthSelect />}>
      <BlockStack gap="400">
        {status && !status.connected ? (
          <Banner tone="info" title="Connect Shopify to pull live sales">
            <p>Add your Admin API credentials to the server's <code>.env</code> to auto-match orders. Everything else already works.</p>
          </Banner>
        ) : null}
        {budget?.overBudget ? (
          <Banner tone="critical" title="Over budget this month"><p>Projected {money(budget.projectedSpend)} vs ceiling {money(budget.ceiling)}.</p></Banner>
        ) : budget?.warning ? (
          <Banner tone="warning" title="Approaching budget ceiling"><p>Projected {money(budget.projectedSpend)} — {budget.pctOfCeiling}% of {money(budget.ceiling)}.</p></Banner>
        ) : null}

        <InlineGrid columns={{ xs: 1, sm: 2, lg: 4 }} gap="400">
          <Stat label="Matched sales" value={money(totalSales)} sub={`${totalOrders} order${totalOrders === 1 ? '' : 's'}`} />
          <Stat label="Cash owed" value={money(budget?.totalCash || 0)} sub="commission + bonuses + base + prizes" />
          <Stat label="Product cost" value={money(budget?.totalProductWholesale || 0)} sub={`${money(budget?.totalProductRetail || 0)} retail value`} />
          <Stat label="Paid" value={`${paidCount}/${rows.length}`} sub="marked paid this month" tone={paidCount === rows.length && rows.length > 0 ? 'success' : undefined} />
        </InlineGrid>

        {budget?.ceiling > 0 ? (
          <Card>
            <BlockStack gap="200">
              <InlineStack align="space-between">
                <Text as="span" fontWeight="medium">Monthly budget</Text>
                <Text as="span" tone="subdued">{money(budget.projectedSpend)} of {money(budget.ceiling)} · {budget.pctOfCeiling}%</Text>
              </InlineStack>
              <ProgressBar progress={Math.min(budget.pctOfCeiling, 100)} tone={budget.overBudget ? 'critical' : budget.warning ? 'warning' : 'success'} />
            </BlockStack>
          </Card>
        ) : null}

        <InlineGrid columns={{ xs: 1, md: 2 }} gap="400">
          <Card>
            <BlockStack gap="300">
              <Text as="h2" variant="headingMd">🔥 Top by views</Text>
              {board.views.length === 0 ? <Text as="p" tone="subdued">No posts logged yet.</Text> : board.views.slice(0, 5).map((r, i) => (
                <React.Fragment key={r.affiliateId}>
                  {i > 0 ? <Divider /> : null}
                  <InlineStack align="space-between">
                    <Text as="span">{['🥇', '🥈', '🥉'][i] || `${i + 1}.`} {r.name}</Text>
                    <Text as="span" fontWeight="semibold" numeric>{compactNumber(r.value)} views</Text>
                  </InlineStack>
                </React.Fragment>
              ))}
            </BlockStack>
          </Card>
          <Card>
            <BlockStack gap="300">
              <Text as="h2" variant="headingMd">💰 Top by sales</Text>
              {board.sales.length === 0 ? <Text as="p" tone="subdued">No matched sales yet.</Text> : board.sales.slice(0, 5).map((r, i) => (
                <React.Fragment key={r.affiliateId}>
                  {i > 0 ? <Divider /> : null}
                  <InlineStack align="space-between">
                    <Text as="span">{['🥇', '🥈', '🥉'][i] || `${i + 1}.`} {r.name}</Text>
                    <Text as="span" fontWeight="semibold" numeric>{money(r.value)}</Text>
                  </InlineStack>
                </React.Fragment>
              ))}
            </BlockStack>
          </Card>
        </InlineGrid>
      </BlockStack>
    </Page>
  );
}
