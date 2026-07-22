import React, { useEffect, useState, useCallback } from 'react';
import {
  Page, Card, IndexTable, Badge, Button, Modal, FormLayout, TextField, Select,
  Banner, Toast, Text, InlineStack, EmptyState, Checkbox,
} from '@shopify/polaris';
import { api, money } from '../api.js';

const TIERS = [
  { label: 'Athlete', value: 'Athlete' },
  { label: 'Influencer', value: 'Influencer' },
  { label: 'Ambassador', value: 'Ambassador' },
];

const empty = {
  name: '', email: '', payoutEmail: '', country: '', platform: '', handle: '',
  tier: 'Athlete', discountCode: '', commissionPct: '', monthlyBase: '', status: 'active',
};

export default function Affiliates() {
  const [rows, setRows] = useState([]);
  const [loading, setLoading] = useState(true);
  const [includeArchived, setIncludeArchived] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(empty);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    const data = await api.get(`/affiliates${includeArchived ? '?includeArchived=1' : ''}`);
    setRows(data);
    setLoading(false);
  }, [includeArchived]);

  useEffect(() => { load(); }, [load]);

  const openNew = () => { setEditing(null); setForm(empty); setError(''); setModalOpen(true); };
  const openEdit = (a) => {
    setEditing(a);
    setForm({
      name: a.name, email: a.email || '', payoutEmail: a.payoutEmail || '', country: a.country || '',
      platform: a.platform || '', handle: a.handle || '', tier: a.tier, discountCode: a.discountCode,
      commissionPct: String(a.commissionPct ?? ''), monthlyBase: String(a.monthlyBase ?? ''), status: a.status,
    });
    setError('');
    setModalOpen(true);
  };

  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));

  const save = async () => {
    setSaving(true); setError('');
    try {
      const payload = { ...form, commissionPct: Number(form.commissionPct) || 0, monthlyBase: Number(form.monthlyBase) || 0 };
      if (editing) await api.put(`/affiliates/${editing.id}`, payload);
      else await api.post('/affiliates', payload);
      setModalOpen(false);
      setToast(editing ? 'Affiliate updated' : 'Affiliate added');
      await load();
    } catch (e) {
      setError(e.message);
    } finally {
      setSaving(false);
    }
  };

  const toggleArchive = async (a) => {
    await api.post(`/affiliates/${a.id}/archive`, { archived: !a.archived });
    setToast(a.archived ? 'Affiliate restored' : 'Affiliate archived');
    await load();
  };

  const rowMarkup = rows.map((a, index) => (
    <IndexTable.Row id={String(a.id)} key={a.id} position={index}>
      <IndexTable.Cell>
        <Text variant="bodyMd" fontWeight="semibold" as="span">{a.name}</Text>
        {a.handle ? <div><Text tone="subdued" as="span" variant="bodySm">{a.platform} {a.handle}</Text></div> : null}
      </IndexTable.Cell>
      <IndexTable.Cell><Badge tone={a.tier === 'Ambassador' ? 'success' : a.tier === 'Influencer' ? 'info' : undefined}>{a.tier}</Badge></IndexTable.Cell>
      <IndexTable.Cell><Text as="span" fontWeight="medium"><code>{a.discountCode}</code></Text></IndexTable.Cell>
      <IndexTable.Cell>{a.commissionPct}%</IndexTable.Cell>
      <IndexTable.Cell>{a.tier === 'Ambassador' ? money(a.monthlyBase) : '—'}</IndexTable.Cell>
      <IndexTable.Cell>
        {a.archived ? <Badge tone="warning">Archived</Badge> : <Badge tone={a.status === 'active' ? 'success' : undefined}>{a.status}</Badge>}
      </IndexTable.Cell>
      <IndexTable.Cell>
        <InlineStack gap="200">
          <Button size="slim" onClick={() => openEdit(a)}>Edit</Button>
          <Button size="slim" tone={a.archived ? undefined : 'critical'} variant="tertiary" onClick={() => toggleArchive(a)}>
            {a.archived ? 'Restore' : 'Archive'}
          </Button>
        </InlineStack>
      </IndexTable.Cell>
    </IndexTable.Row>
  ));

  return (
      <Page
        title="Affiliate roster"
        subtitle="Add, edit, and archive the people repping ATHLYST."
        primaryAction={{ content: 'Add affiliate', onAction: openNew }}
        secondaryActions={[{ content: includeArchived ? 'Hide archived' : 'Show archived', onAction: () => setIncludeArchived((v) => !v) }]}
      >
        <Card padding="0">
          {rows.length === 0 && !loading ? (
            <EmptyState heading="No affiliates yet" action={{ content: 'Add affiliate', onAction: openNew }} image="">
              <p>Add your first affiliate to start tracking sales, views, and payouts.</p>
            </EmptyState>
          ) : (
            <IndexTable
              resourceName={{ singular: 'affiliate', plural: 'affiliates' }}
              itemCount={rows.length}
              loading={loading}
              selectable={false}
              headings={[
                { title: 'Name' }, { title: 'Tier' }, { title: 'Code' },
                { title: 'Commission' }, { title: 'Monthly base' }, { title: 'Status' }, { title: 'Actions' },
              ]}
            >
              {rowMarkup}
            </IndexTable>
          )}
        </Card>

        <Modal
          open={modalOpen}
          onClose={() => setModalOpen(false)}
          title={editing ? `Edit ${editing.name}` : 'Add affiliate'}
          primaryAction={{ content: editing ? 'Save' : 'Add affiliate', onAction: save, loading: saving }}
          secondaryActions={[{ content: 'Cancel', onAction: () => setModalOpen(false) }]}
        >
          <Modal.Section>
            {error ? <div style={{ marginBottom: 16 }}><Banner tone="critical">{error}</Banner></div> : null}
            <FormLayout>
              <FormLayout.Group>
                <TextField label="Name" value={form.name} onChange={set('name')} autoComplete="off" requiredIndicator />
                <TextField label="Discount code" value={form.discountCode} onChange={set('discountCode')} autoComplete="off" requiredIndicator helpText="Unique — used to match Shopify orders." />
              </FormLayout.Group>
              <FormLayout.Group>
                <TextField label="Email" type="email" value={form.email} onChange={set('email')} autoComplete="off" />
                <TextField label="Payout email (PayPal)" type="email" value={form.payoutEmail} onChange={set('payoutEmail')} autoComplete="off" />
              </FormLayout.Group>
              <FormLayout.Group>
                <TextField label="Country" value={form.country} onChange={set('country')} autoComplete="off" />
                <TextField label="Primary platform" value={form.platform} onChange={set('platform')} autoComplete="off" placeholder="Instagram" />
                <TextField label="Handle" value={form.handle} onChange={set('handle')} autoComplete="off" placeholder="@name" />
              </FormLayout.Group>
              <FormLayout.Group>
                <Select label="Tier" options={TIERS} value={form.tier} onChange={set('tier')} />
                <TextField label="Commission %" type="number" suffix="%" value={form.commissionPct} onChange={set('commissionPct')} autoComplete="off" />
                {form.tier === 'Ambassador' ? (
                  <TextField label="Monthly base" type="number" prefix="$" value={form.monthlyBase} onChange={set('monthlyBase')} autoComplete="off" />
                ) : null}
              </FormLayout.Group>
              <Checkbox label="Active" checked={form.status === 'active'} onChange={(c) => set('status')(c ? 'active' : 'inactive')} />
            </FormLayout>
          </Modal.Section>
        </Modal>

        {toast ? <Toast content={toast} onDismiss={() => setToast('')} /> : null}
      </Page>
  );
}
