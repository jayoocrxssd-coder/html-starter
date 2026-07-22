import React from 'react';
import { Select } from '@shopify/polaris';
import { useMonth } from '../App.jsx';
import { monthOptions } from '../api.js';

// Reusable month switcher wired to the shared MonthContext.
export default function MonthSelect() {
  const { month, setMonth } = useMonth();
  return (
    <Select
      label="Month"
      labelInline
      options={monthOptions()}
      value={month}
      onChange={setMonth}
    />
  );
}
