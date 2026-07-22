import React, { useEffect, useState, useCallback } from 'react';
import {
  Page, Card, IndexTable, Button, Modal, FormLayout, TextField, Select,
  Banner, Toast, Text, BlockStack, InlineStack, InlineGrid, Box, Divider,
} from '@shopify/polaris';
import { api, money, compactNumber } from '../api.js';

const emptyTier = { label: '', threshold: '', rewardDescription: '', cashAmount: '', productWholesaleCost: '', productRetailValue: '', commissionBumpPct: '' };
const emptyPrize = (rank) => ({ rank, board: 'both', cashAmount: '', productDescription: '', productWholesaleCost: '', productRetailValue: '' });
const BOARD_OPTIONS = [
  { label: 'Both boards', value: 'both' },
  { label: 'Views board', value: 'views' },
  { label: 'Sales board', value: 'sales' },
];

export default function Settings() {
  const [settings, setSettings] = useState(null);
  const [toast, setToast] = useState('');
  const [error, setError] = useState('');

  // Commission defaults + budget ceiling
  const [commission, setCommission] = useState({ Athlete: '', Influencer: '', Ambassador: '' });
  const [ceiling, setCeiling] = useState('');

  // Bonus tier modal
  const [tierModal, setTierModal] = useState(false);
  const [editingTier, setEditingTier] = useState(null);
  const [tierForm, setTierForm] = useState(emptyTier);

  // Leaderboard prizes (edited inline, saved together)
  const [prizes, setPrizes] = useState([emptyPrize(1), emptyPrize(2), emptyPrize(3)]);

  const load = useCallback(async () => {
    const s = await api.get('/settings');
    setSettings(s);
    setCommission({ Athlete: '', Influencer: '', Ambassador: '', ...s.commissionDefaults });
    setCeiling(String(s.monthlyBudgetCeiling || ''));
    const byRank = new Map((s.leaderboardPrizes || []).map((p) => [p.rank, p]));
    setPrizes([1, 2, 3].map((r) => ({
      ...emptyPrize(r),
      ...(byRank.get(r) || {}),
      cashAmount: String(byRank.get(r)?.cashAmount ?? ''),
      productWholesaleCost: String(byRank.get(r)?.productWholesaleCost ?? ''),
      productRetailValue: String(byRank.get(r)?.productRetailValue ?? ''),
      productDescription: byRank.get(r)?.productDescription ?? '',
      board: byRank.get(r)?.board ?? 'both',
    })));
  }, []);
  useEffect(() => { load(); }, [load]);

  const saveGeneral = async () => {
    setError('');
    try {
      await api.put('/settings', {
        commissionDefaults: {
          Athlete: Number(commission.Athlete) || 0,
          Influencer: Number(commission.Influencer) || 0,
          Ambassador: Number(commission.Ambassador) || 0,
        },
        monthlyBudgetCeiling: Number(ceiling) || 0,
        leaderboardPrizes: prizes.map((p) => ({
          rank: p.rank,
          board: p.board,
          cashAmount: Number(p.cashAmount) || 0,
          productDescription: p.productDescription || '',
          productWholesaleCost: Number(p.productWholesaleCost) || 0,
          productRetailValue: Number(p.productRetailValue) || 0,
        })),
      });
      setToast('Settings saved');
      await load();
    } catch (e) { setError(e.message); }
  };

  // ---- Bonus tiers ----
  const openNewTier = () => { setEditingTier(null); setTierForm(emptyTier); setTierModal(true); };
  const openEditTier = (t) => {
    setEditingTier(t);
    setTierForm({
      label: t.label, threshold: String(t.threshold), rewardDescription: t.rewardDescription || '',
      cashAmount: String(t.cashAmount), productWholesaleCost: String(t.productWholesaleCost),
      productRetailValue: String(t.productRetailValue), commissionBumpPct: String(t.commissionBumpPct),
    });
    setTierModal(true);
  };
  const setTf = (k) => (v) => setTierForm((f) => ({ ...f, [k]: v }));
  const saveTier = async () => {
    const payload = {
      label: tierForm.label, threshold: Number(tierForm.threshold) || 0, rewardDescription: tierForm.rewardDescription,
      cashAmount: Number(tierForm.cashAmount) || 0, productWholesaleCost: Number(tierForm.productWholesaleCost) || 0,
      productRetailValue: Number(tierForm.productRetailValue) || 0, commissionBumpPct: Number(tierForm.commissionBumpPct) || 0,
    };
    if (editingTier) await api.put(`/settings/tiers/${editingTier.id}`, payload);
    else await api.post('/settings/tiers', payload);
    setTierModal(false); setToast('Bonus tier saved'); await load();
  };
  const deleteTier = async (t) => { await api.del(`/settings/tiers/${t.id}`); setToast('Bonus tier deleted'); await load(); };

  if (!settings) return <Page title="Settings"><Card><Text as="p">Loading…</Text></Card></Page>;

  const tiers = settings.bonusTiers || [];

  return (
    <Page title="Settings" subtitle="You set these; the app uses them everywhere. Nothing here is hardcoded.">
      <BlockStack gap="500">
        {error ? <Banner tone="critical">{error}</Banner> : null}

        {/* Commission defaults + budget ceiling */}
        <Card>
          <BlockStack gap="400">
            <Text as="h2" variant="headingMd">Commission defaults & budget</Text>
            <Text as="p" tone="subdued" variant="bodySm">Default commission % per tier (suggested when adding an affiliate), plus your monthly payout ceiling.</Text>
            <InlineGrid columns={{ xs: 1, sm: 2, lg: 4 }} gap="400">
              <TextField label="Athlete %" type="number" suffix="%" value={commission.Athlete} onChange={(v) => setCommission((c) => ({ ...c, Athlete: v }))} autoComplete="off" />
              <TextField label="Influencer %" type="number" suffix="%" value={commission.Influencer} onChange={(v) => setCommission((c) => ({ ...c, Influencer: v }))} autoComplete="off" />
              <TextField label="Ambassador %" type="number" suffix="%" value={commission.Ambassador} onChange={(v) => setCommission((c) => ({ ...c, Ambassador: v }))} autoComplete="off" />
              <TextField label="Monthly budget ceiling" type="number" prefix="$" value={ceiling} onChange={setCeiling} autoComplete="off" helpText="Warns near this." />
            </InlineGrid>
          </BlockStack>
        </Card>

        {/* Bonus tiers */}
        <Card padding="0">
          <Box padding="400">
            <InlineStack align="space-between" blockAlign="center">
              <BlockStack gap="100">
                <Text as="h2" variant="headingMd">View bonus tiers</Text>
                <Text as="p" tone="subdued" variant="bodySm">A verified post auto-tags the highest tier it reaches. Thresholds and rewards are fully editable.</Text>
              </BlockStack>
              <Button onClick={openNewTier}>Add tier</Button>
            </InlineStack>
          </Box>
          <IndexTable
            resourceName={{ singular: 'tier', plural: 'tiers' }}
            itemCount={tiers.length}
            selectable={false}
            headings={[{ title: 'Tier' }, { title: 'Threshold' }, { title: 'Reward' }, { title: 'Cash' }, { title: 'Product (wholesale / retail)' }, { title: 'Commission bump' }, { title: '' }]}
          >
            {tiers.map((t, i) => (
              <IndexTable.Row id={String(t.id)} key={t.id} position={i}>
                <IndexTable.Cell><Text as="span" fontWeight="semibold">{t.label}</Text></IndexTable.Cell>
                <IndexTable.Cell>{compactNumber(t.threshold)} views</IndexTable.Cell>
                <IndexTable.Cell>{t.rewardDescription || '—'}</IndexTable.Cell>
                <IndexTable.Cell>{t.cashAmount ? money(t.cashAmount) : '—'}</IndexTable.Cell>
                <IndexTable.Cell>{t.productWholesaleCost || t.productRetailValue ? `${money(t.productWholesaleCost)} / ${money(t.productRetailValue)}` : '—'}</IndexTable.Cell>
                <IndexTable.Cell>{t.commissionBumpPct ? `+${t.commissionBumpPct}%` : '—'}</IndexTable.Cell>
                <IndexTable.Cell>
                  <InlineStack gap="200">
                    <Button size="slim" onClick={() => openEditTier(t)}>Edit</Button>
                    <Button size="slim" variant="tertiary" tone="critical" onClick={() => deleteTier(t)}>Delete</Button>
                  </InlineStack>
                </IndexTable.Cell>
              </IndexTable.Row>
            ))}
          </IndexTable>
        </Card>

        {/* Leaderboard prizes */}
        <Card>
          <BlockStack gap="400">
            <Text as="h2" variant="headingMd">Leaderboard prizes</Text>
            <Text as="p" tone="subdued" variant="bodySm">Prize for 1st / 2nd / 3rd each month. Choose whether it applies to the views board, the sales board, or both.</Text>
            {prizes.map((p, idx) => (
              <React.Fragment key={p.rank}>
                {idx > 0 ? <Divider /> : null}
                <BlockStack gap="200">
                  <Text as="h3" variant="headingSm">{['🥇 1st', '🥈 2nd', '🥉 3rd'][idx]} place</Text>
                  <InlineGrid columns={{ xs: 1, sm: 2, lg: 5 }} gap="300">
                    <Select label="Applies to" options={BOARD_OPTIONS} value={p.board} onChange={(v) => setPrizes((ps) => ps.map((x, i) => i === idx ? { ...x, board: v } : x))} />
                    <TextField label="Cash" type="number" prefix="$" value={p.cashAmount} onChange={(v) => setPrizes((ps) => ps.map((x, i) => i === idx ? { ...x, cashAmount: v } : x))} autoComplete="off" />
                    <TextField label="Product" value={p.productDescription} onChange={(v) => setPrizes((ps) => ps.map((x, i) => i === idx ? { ...x, productDescription: v } : x))} autoComplete="off" placeholder="e.g. Full kit" />
                    <TextField label="Product cost" type="number" prefix="$" value={p.productWholesaleCost} onChange={(v) => setPrizes((ps) => ps.map((x, i) => i === idx ? { ...x, productWholesaleCost: v } : x))} autoComplete="off" />
                    <TextField label="Product retail" type="number" prefix="$" value={p.productRetailValue} onChange={(v) => setPrizes((ps) => ps.map((x, i) => i === idx ? { ...x, productRetailValue: v } : x))} autoComplete="off" />
                  </InlineGrid>
                </BlockStack>
              </React.Fragment>
            ))}
          </BlockStack>
        </Card>

        <InlineStack align="end">
          <Button variant="primary" onClick={saveGeneral}>Save settings</Button>
        </InlineStack>
      </BlockStack>

      <Modal
        open={tierModal}
        onClose={() => setTierModal(false)}
        title={editingTier ? `Edit ${editingTier.label} tier` : 'Add bonus tier'}
        primaryAction={{ content: 'Save tier', onAction: saveTier }}
        secondaryActions={[{ content: 'Cancel', onAction: () => setTierModal(false) }]}
      >
        <Modal.Section>
          <FormLayout>
            <FormLayout.Group>
              <TextField label="Label" value={tierForm.label} onChange={setTf('label')} autoComplete="off" placeholder="25K" />
              <TextField label="Threshold (views)" type="number" value={tierForm.threshold} onChange={setTf('threshold')} autoComplete="off" />
            </FormLayout.Group>
            <TextField label="Reward description" value={tierForm.rewardDescription} onChange={setTf('rewardDescription')} autoComplete="off" />
            <FormLayout.Group>
              <TextField label="Cash amount" type="number" prefix="$" value={tierForm.cashAmount} onChange={setTf('cashAmount')} autoComplete="off" />
              <TextField label="Commission bump" type="number" suffix="%" value={tierForm.commissionBumpPct} onChange={setTf('commissionBumpPct')} autoComplete="off" />
            </FormLayout.Group>
            <FormLayout.Group>
              <TextField label="Product cost (wholesale)" type="number" prefix="$" value={tierForm.productWholesaleCost} onChange={setTf('productWholesaleCost')} autoComplete="off" helpText="Your real cost (budget math)." />
              <TextField label="Product retail value" type="number" prefix="$" value={tierForm.productRetailValue} onChange={setTf('productRetailValue')} autoComplete="off" helpText="Perceived value." />
            </FormLayout.Group>
          </FormLayout>
        </Modal.Section>
      </Modal>

      {toast ? <Toast content={toast} onDismiss={() => setToast('')} /> : null}
    </Page>
  );
}
