import React, { useEffect, useState, useCallback } from 'react';
import {
  Page, Card, IndexTable, Badge, Button, Modal, FormLayout, TextField, Select,
  Banner, Toast, Text, InlineStack, EmptyState, Checkbox, Link, Tooltip,
} from '@shopify/polaris';
import { api, compactNumber } from '../api.js';
import MonthSelect from '../components/MonthSelect.jsx';
import { useMonth } from '../App.jsx';

const emptyForm = { affiliateId: '', postLink: '', platform: '', viewCount: '', postedAt: '', verified: false };

export default function ViewsPage() {
  const { month } = useMonth();
  const [rows, setRows] = useState([]);
  const [affiliates, setAffiliates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);
  const [error, setError] = useState('');
  const [toast, setToast] = useState('');
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    const [views, affs] = await Promise.all([api.get(`/views?month=${month}`), api.get('/affiliates')]);
    setRows(views);
    setAffiliates(affs);
    setLoading(false);
  }, [month]);

  useEffect(() => { load(); }, [load]);

  const affOptions = [{ label: 'Select affiliate…', value: '' }, ...affiliates.map((a) => ({ label: `${a.name} (${a.discountCode})`, value: String(a.id) }))];
  const set = (k) => (v) => setForm((f) => ({ ...f, [k]: v }));

  const openNew = () => {
    setEditing(null);
    setForm({ ...emptyForm, postedAt: new Date().toISOString().slice(0, 10) });
    setError(''); setModalOpen(true);
  };
  const openEdit = (v) => {
    setEditing(v);
    setForm({ affiliateId: String(v.affiliateId), postLink: v.postLink, platform: v.platform || '', viewCount: String(v.viewCount), postedAt: v.postedAt.slice(0, 10), verified: v.verified });
    setError(''); setModalOpen(true);
  };

  const save = async () => {
    setSaving(true); setError('');
    try {
      const payload = { ...form, affiliateId: Number(form.affiliateId), viewCount: Number(form.viewCount) || 0 };
      if (!payload.affiliateId) throw new Error('Select an affiliate.');
      if (editing) await api.put(`/views/${editing.id}`, payload);
      else await api.post('/views', payload);
      setModalOpen(false);
      setToast(editing ? 'Post updated' : 'Post logged');
      await load();
    } catch (e) { setError(e.message); } finally { setSaving(false); }
  };

  const toggleVerify = async (v) => {
    await api.post(`/views/${v.id}/verify`, { verified: !v.verified });
    await load();
  };
  const remove = async (v) => { await api.del(`/views/${v.id}`); setToast('Post removed'); await load(); };

  const rowMarkup = rows.map((v, index) => (
    <IndexTable.Row id={String(v.id)} key={v.id} position={index}>
      <IndexTable.Cell>
        <Text as="span" fontWeight="semibold">{v.affiliate?.name}</Text>
      </IndexTable.Cell>
      <IndexTable.Cell>{v.platform || '—'}</IndexTable.Cell>
      <IndexTable.Cell>
        <Link url={v.postLink} target="_blank" removeUnderline>View post</Link>
      </IndexTable.Cell>
      <IndexTable.Cell><Text as="span" numeric>{compactNumber(v.viewCount)}</Text></IndexTable.Cell>
      <IndexTable.Cell>
        {v.bonusTier ? <Badge tone="info">{v.bonusTier.label} tier</Badge> : <Text as="span" tone="subdued">No tier</Text>}
      </IndexTable.Cell>
      <IndexTable.Cell>{new Date(v.postedAt).toLocaleDateString()}</IndexTable.Cell>
      <IndexTable.Cell>
        <Tooltip content={v.verified ? 'Verified — counts toward bonuses' : 'Unverified — no bonus until you confirm the post features the product AND code'}>
          <Checkbox label="" labelHidden checked={v.verified} onChange={() => toggleVerify(v)} />
        </Tooltip>
      </IndexTable.Cell>
      <IndexTable.Cell>
        <InlineStack gap="200">
          <Button size="slim" onClick={() => openEdit(v)}>Edit</Button>
          <Button size="slim" variant="tertiary" tone="critical" onClick={() => remove(v)}>Delete</Button>
        </InlineStack>
      </IndexTable.Cell>
    </IndexTable.Row>
  ));

  return (
    <Page
      title="View logging"
      subtitle="Log posts from platform-native analytics. Verify each one so it counts toward bonuses."
      primaryAction={{ content: 'Log a post', onAction: openNew }}
      titleMetadata={<MonthSelect />}
    >
      <div style={{ marginBottom: 12 }}>
        <Banner tone="info">
          A view only counts toward a bonus if the post features the product <b>and</b> the affiliate's code.
          Tick <b>Verified</b> once you've confirmed it — unverified posts still show on the leaderboard but earn no bonus.
        </Banner>
      </div>
      <Card padding="0">
        {rows.length === 0 && !loading ? (
          <EmptyState heading="No posts logged this month" action={{ content: 'Log a post', onAction: openNew }} image="">
            <p>Manually log posts and their view counts to build the leaderboard and bonus totals.</p>
          </EmptyState>
        ) : (
          <IndexTable
            resourceName={{ singular: 'post', plural: 'posts' }}
            itemCount={rows.length}
            loading={loading}
            selectable={false}
            headings={[
              { title: 'Affiliate' }, { title: 'Platform' }, { title: 'Post' }, { title: 'Views' },
              { title: 'Bonus tier' }, { title: 'Date' }, { title: 'Verified' }, { title: 'Actions' },
            ]}
          >
            {rowMarkup}
          </IndexTable>
        )}
      </Card>

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? 'Edit logged post' : 'Log a post'}
        primaryAction={{ content: editing ? 'Save' : 'Log post', onAction: save, loading: saving }}
        secondaryActions={[{ content: 'Cancel', onAction: () => setModalOpen(false) }]}
      >
        <Modal.Section>
          {error ? <div style={{ marginBottom: 16 }}><Banner tone="critical">{error}</Banner></div> : null}
          <FormLayout>
            <Select label="Affiliate" options={affOptions} value={form.affiliateId} onChange={set('affiliateId')} requiredIndicator />
            <TextField label="Post link" value={form.postLink} onChange={set('postLink')} autoComplete="off" requiredIndicator placeholder="https://…" />
            <FormLayout.Group>
              <TextField label="Platform" value={form.platform} onChange={set('platform')} autoComplete="off" placeholder="Instagram" />
              <TextField label="View count" type="number" value={form.viewCount} onChange={set('viewCount')} autoComplete="off" helpText="From platform-native analytics only." />
              <TextField label="Date" type="date" value={form.postedAt} onChange={set('postedAt')} autoComplete="off" />
            </FormLayout.Group>
            <Checkbox
              label="Verified — this post features the product and the affiliate's code"
              checked={form.verified}
              onChange={set('verified')}
              helpText="Only verified posts count toward bonus tiers."
            />
          </FormLayout>
        </Modal.Section>
      </Modal>

      {toast ? <Toast content={toast} onDismiss={() => setToast('')} /> : null}
    </Page>
  );
}
