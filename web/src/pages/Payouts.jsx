import React, { useEffect, useState, useCallback } from 'react';
import {
  Page, Card, IndexTable, Badge, Button, Toast, Text, BlockStack, InlineStack,
  Select, Box, InlineGrid, ProgressBar, Banner, Tooltip, Icon,
} from '@shopify/polaris';
import { CheckIcon, InfoIcon } from '@shopify/polaris-icons';
import { api, money } from '../api.js';
import MonthSelect from '../components/MonthSelect.jsx';
import { useMonth } from '../App.jsx';

const PAYOUT_TYPES = [
  { label: 'Cash', value: 'cash' },
  { label: 'Product / credit', value: 'product' },
  { label: 'Split', value: 'split' },
];

function Stat({ label, value, tone }) {
  return (
    <Card>
      <BlockStack gap="100">
        <Text as="p" tone="subdued" variant="bodySm">{label}</Text>
        <Text as="p" variant="headingXl" tone={tone}>{value}</Text>
      </BlockStack>
    </Card>
  );
}

export default function Payouts() {
  const { month } = useMonth();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [toast, setToast] = useState('');

  const load = useCallback(async () => {
    setLoading(true);
    setData(await api.get(`/payouts?month=${month}`));
    setLoading(false);
  }, [month]);
  useEffect(() => { load(); }, [load]);

  const markPaid = async (row, paid) => {
    await api.post(`/payouts/${row.affiliateId}/paid`, { month, paid });
    setToast(paid ? `Marked ${row.name} paid` : `Marked ${row.name} unpaid`);
    await load();
  };
  const setType = async (row, payoutType) => {
    await api.post(`/payouts/${row.affiliateId}/settings`, { month, payoutType });
    await load();
  };

  const exportCsv = () => { window.location.href = `/api/payouts/export?month=${month}`; };

  const rows = data?.rows || [];
  const budget = data?.budget;
  const paidCount = rows.filter((r) => r.paid).length;

  const rowMarkup = rows.map((r, index) => (
    <IndexTable.Row id={String(r.affiliateId)} key={r.affiliateId} position={index}>
      <IndexTable.Cell>
        <BlockStack gap="0">
          <Text as="span" fontWeight="semibold">{r.name}</Text>
          <Text as="span" tone="subdued" variant="bodySm">{r.tier} · <code>{r.discountCode}</code></Text>
        </BlockStack>
      </IndexTable.Cell>
      <IndexTable.Cell>
        <Text as="span" numeric>{money(r.sales)}</Text>
        <div><Text as="span" tone="subdued" variant="bodySm">{r.orderCount} order{r.orderCount === 1 ? '' : 's'}</Text></div>
      </IndexTable.Cell>
      <IndexTable.Cell>
        <Text as="span" numeric>{money(r.commission)}</Text>
        <div><Text as="span" tone="subdued" variant="bodySm">{r.commissionPct}%{r.commissionBump ? ` +${r.commissionBump}` : ''}</Text></div>
      </IndexTable.Cell>
      <IndexTable.Cell><Text as="span" numeric>{r.ambassadorBase ? money(r.ambassadorBase) : '—'}</Text></IndexTable.Cell>
      <IndexTable.Cell><Text as="span" numeric>{r.viewBonusCash ? money(r.viewBonusCash) : '—'}</Text></IndexTable.Cell>
      <IndexTable.Cell>
        {r.leaderboardCash || r.leaderboardWins?.length ? (
          <Tooltip content={r.leaderboardWins.map((w) => `${w.board} #${w.rank}${w.product ? ` + ${w.product}` : ''}`).join(', ')}>
            <Text as="span" numeric>{money(r.leaderboardCash)} <Icon source={InfoIcon} tone="subdued" /></Text>
          </Tooltip>
        ) : '—'}
      </IndexTable.Cell>
      <IndexTable.Cell>
        <Text as="span" fontWeight="bold" numeric>{money(r.cashOwed)}</Text>
        {r.productWholesale ? <div><Tooltip content={`Product/credit — retail value ${money(r.productRetail)}`}><Text as="span" tone="subdued" variant="bodySm">+ {money(r.productWholesale)} product</Text></Tooltip></div> : null}
      </IndexTable.Cell>
      <IndexTable.Cell>
        <Box minWidth="150px"><Select label="" labelHidden options={PAYOUT_TYPES} value={r.payoutType} onChange={(v) => setType(r, v)} /></Box>
      </IndexTable.Cell>
      <IndexTable.Cell>
        {r.paid ? (
          <InlineStack gap="200" blockAlign="center">
            <Badge tone="success" icon={CheckIcon}>Paid</Badge>
            <Button size="micro" variant="plain" onClick={() => markPaid(r, false)}>Undo</Button>
          </InlineStack>
        ) : (
          <Button size="slim" onClick={() => markPaid(r, true)}>Mark paid</Button>
        )}
      </IndexTable.Cell>
    </IndexTable.Row>
  ));

  return (
    <Page
      title="Payout calculator"
      subtitle="Everything each active affiliate is owed this month — commission, bonuses, base, and prizes."
      titleMetadata={<MonthSelect />}
      primaryAction={{ content: 'Export batch (CSV)', onAction: exportCsv, disabled: rows.length === 0 }}
    >
      <BlockStack gap="400">
        {budget?.overBudget ? (
          <Banner tone="critical" title="Over budget">
            <p>Projected spend {money(budget.projectedSpend)} exceeds your ceiling of {money(budget.ceiling)}.</p>
          </Banner>
        ) : budget?.warning ? (
          <Banner tone="warning" title="Approaching budget ceiling">
            <p>Projected spend {money(budget.projectedSpend)} is {budget.pctOfCeiling}% of your {money(budget.ceiling)} ceiling.</p>
          </Banner>
        ) : null}

        <InlineGrid columns={{ xs: 1, sm: 2, lg: 4 }} gap="400">
          <Stat label="Total cash owed" value={money(budget?.totalCash || 0)} />
          <Stat label="Product cost (wholesale)" value={money(budget?.totalProductWholesale || 0)} />
          <Stat label="Projected spend" value={money(budget?.projectedSpend || 0)} tone={budget?.overBudget ? 'critical' : undefined} />
          <Stat label="Paid" value={`${paidCount} / ${rows.length}`} />
        </InlineGrid>

        {budget?.ceiling > 0 ? (
          <Card>
            <BlockStack gap="200">
              <InlineStack align="space-between">
                <Text as="span" fontWeight="medium">Budget ceiling</Text>
                <Text as="span" tone="subdued">{money(budget.projectedSpend)} of {money(budget.ceiling)} · {budget.pctOfCeiling}%</Text>
              </InlineStack>
              <ProgressBar progress={Math.min(budget.pctOfCeiling, 100)} tone={budget.overBudget ? 'critical' : budget.warning ? 'warning' : 'success'} />
            </BlockStack>
          </Card>
        ) : null}

        <Card padding="0">
          <IndexTable
            resourceName={{ singular: 'payout', plural: 'payouts' }}
            itemCount={rows.length}
            loading={loading}
            selectable={false}
            headings={[
              { title: 'Affiliate' }, { title: 'Sales' }, { title: 'Commission' }, { title: 'Base' },
              { title: 'View bonus' }, { title: 'Leaderboard' }, { title: 'Cash owed' }, { title: 'Type' }, { title: 'Status' },
            ]}
          >
            {rowMarkup}
          </IndexTable>
        </Card>

        <Text as="p" tone="subdued" variant="bodySm">
          Payouts run once monthly as one batch. Export the CSV, pay everyone from it, then mark each as paid.
          Product/credit rewards are tracked at wholesale cost for your budget math, separate from retail value.
        </Text>
      </BlockStack>

      {toast ? <Toast content={toast} onDismiss={() => setToast('')} /> : null}
    </Page>
  );
}
