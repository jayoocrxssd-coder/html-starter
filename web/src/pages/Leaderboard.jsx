import React, { useEffect, useState, useCallback } from 'react';
import { Page, Card, Text, BlockStack, InlineStack, Badge, Box, InlineGrid, EmptyState } from '@shopify/polaris';
import { api, money, compactNumber } from '../api.js';
import MonthSelect from '../components/MonthSelect.jsx';
import { useMonth } from '../App.jsx';

const medal = ['🥇', '🥈', '🥉'];

function Board({ title, rows, format }) {
  return (
    <Card>
      <BlockStack gap="300">
        <Text as="h2" variant="headingMd">{title}</Text>
        {rows.length === 0 ? (
          <Text as="p" tone="subdued">No data yet this month.</Text>
        ) : (
          <BlockStack gap="200">
            {rows.slice(0, 10).map((r, i) => (
              <InlineStack key={r.affiliateId} align="space-between" blockAlign="center">
                <InlineStack gap="200" blockAlign="center">
                  <Box minWidth="28px"><Text as="span" variant="headingMd">{medal[i] || `${i + 1}.`}</Text></Box>
                  <BlockStack gap="0">
                    <Text as="span" fontWeight={i < 3 ? 'bold' : 'medium'}>{r.name}</Text>
                    <Text as="span" tone="subdued" variant="bodySm">{r.tier}</Text>
                  </BlockStack>
                </InlineStack>
                <Text as="span" fontWeight="semibold" numeric>{format(r.value)}</Text>
              </InlineStack>
            ))}
          </BlockStack>
        )}
      </BlockStack>
    </Card>
  );
}

export default function Leaderboard() {
  const { month } = useMonth();
  const [board, setBoard] = useState({ views: [], sales: [] });

  const load = useCallback(async () => {
    setBoard(await api.get(`/leaderboard?month=${month}`));
  }, [month]);
  useEffect(() => { load(); }, [load]);

  const hasData = board.views.length || board.sales.length;

  return (
    <Page title="Monthly leaderboard" subtitle="Two rankings, reset every month. Top 3 on each board can earn a prize (set in Settings)." titleMetadata={<MonthSelect />}>
      {!hasData ? (
        <Card><EmptyState heading="Nothing to rank yet this month" image=""><p>Log some posts and sync sales to build the leaderboard.</p></EmptyState></Card>
      ) : (
        <InlineGrid columns={{ xs: 1, md: 2 }} gap="400">
          <Board title="🔥 Top by views" rows={board.views} format={(v) => `${compactNumber(v)} views`} />
          <Board title="💰 Top by sales" rows={board.sales} format={money} />
        </InlineGrid>
      )}
    </Page>
  );
}
