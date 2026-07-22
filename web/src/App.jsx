import React, { useState, useCallback, createContext, useContext } from 'react';
import { Frame, Navigation, TopBar, Text } from '@shopify/polaris';
import {
  HomeIcon, PersonIcon, PlayIcon, ChartVerticalFilledIcon,
  CashDollarIcon, OrderIcon, SettingsIcon,
} from '@shopify/polaris-icons';

import Overview from './pages/Overview.jsx';
import Affiliates from './pages/Affiliates.jsx';
import ViewsPage from './pages/Views.jsx';
import Sales from './pages/Sales.jsx';
import Leaderboard from './pages/Leaderboard.jsx';
import Payouts from './pages/Payouts.jsx';
import Settings from './pages/Settings.jsx';
import { monthOptions } from './api.js';

// Shared selected-month context so month-scoped pages stay in sync.
export const MonthContext = createContext(null);
export const useMonth = () => useContext(MonthContext);

const PAGES = {
  overview: { label: 'Overview', icon: HomeIcon, Component: Overview },
  affiliates: { label: 'Affiliates', icon: PersonIcon, Component: Affiliates },
  views: { label: 'View logging', icon: PlayIcon, Component: ViewsPage },
  sales: { label: 'Sales', icon: OrderIcon, Component: Sales },
  leaderboard: { label: 'Leaderboard', icon: ChartVerticalFilledIcon, Component: Leaderboard },
  payouts: { label: 'Payouts', icon: CashDollarIcon, Component: Payouts },
  settings: { label: 'Settings', icon: SettingsIcon, Component: Settings },
};

export default function App() {
  const [page, setPage] = useState('overview');
  const [month, setMonth] = useState(monthOptions()[0].value);
  const [mobileNavActive, setMobileNavActive] = useState(false);

  const toggleMobileNav = useCallback(() => setMobileNavActive((a) => !a), []);
  const Current = PAGES[page].Component;

  const topBar = (
    <TopBar
      showNavigationToggle
      onNavigationToggle={toggleMobileNav}
      secondaryMenu={
        <div style={{ display: 'flex', alignItems: 'center', paddingRight: 16 }}>
          <Text variant="headingSm" as="span" tone="subdued">Owner dashboard</Text>
        </div>
      }
    />
  );

  const navigation = (
    <Navigation location="/">
      <Navigation.Section
        title="ATHLYST Affiliates"
        items={Object.entries(PAGES).map(([key, { label, icon }]) => ({
          label,
          icon,
          selected: page === key,
          onClick: () => {
            setPage(key);
            setMobileNavActive(false);
          },
        }))}
      />
    </Navigation>
  );

  return (
    <MonthContext.Provider value={{ month, setMonth }}>
      <Frame
        topBar={topBar}
        navigation={navigation}
        showMobileNavigation={mobileNavActive}
        onNavigationDismiss={toggleMobileNav}
      >
        <Current />
      </Frame>
    </MonthContext.Provider>
  );
}
