import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import LiveMonitoring from './pages/LiveMonitoring';
import Analytics from './pages/Analytics';
import Alerts from './pages/Alerts';
import DeviceSimulator from './pages/DeviceSimulator';
import Settings from './pages/Settings';
import About from './pages/About';
import { api } from './api/client';

import './styles/global.css';
import './styles/dashboard.css';
import './styles/components.css';
import './styles/responsive.css';

export default function App() {
  const [currentPage, setCurrentPage] = useState('dashboard');
  const [unackAlerts, setUnackAlerts] = useState(0);
  const [simulationState, setSimulationState] = useState({
    is_running: false,
    is_paused: false,
    profile: 'normal',
    speed: 1.0,
  });

  const syncAppState = async () => {
    try {
      const [sumRes, simRes] = await Promise.all([
        api.getAlertSummary().catch(() => ({ summary: {} })),
        api.getSimulationStatus().catch(() => ({ simulation: {} })),
      ]);

      if (sumRes.summary) {
        setUnackAlerts(sumRes.summary.unacknowledged || 0);
      }
      if (simRes.simulation) {
        setSimulationState(simRes.simulation);
      }
    } catch (err) {
      // Quiet background polling error handling
    }
  };

  useEffect(() => {
    syncAppState();
    const interval = setInterval(syncAppState, 3000);
    return () => clearInterval(interval);
  }, []);

  const getPageTitle = () => {
    switch (currentPage) {
      case 'dashboard':
        return 'System Overview Dashboard';
      case 'live':
        return 'Live Telemetry & Waveform Monitoring';
      case 'analytics':
        return 'Historical Energy Analytics';
      case 'alerts':
        return 'Alerts, Alarms & ML Anomalies';
      case 'simulator':
        return 'Device Simulator & Scenario Generator';
      case 'settings':
        return 'System & Threshold Configuration';
      case 'about':
        return 'About PowerGuard Platform';
      default:
        return 'PowerGuard Platform';
    }
  };

  const renderPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard onNavigate={setCurrentPage} />;
      case 'live':
        return <LiveMonitoring />;
      case 'analytics':
        return <Analytics />;
      case 'alerts':
        return <Alerts />;
      case 'simulator':
        return <DeviceSimulator />;
      case 'settings':
        return <Settings />;
      case 'about':
        return <About />;
      default:
        return <Dashboard onNavigate={setCurrentPage} />;
    }
  };

  return (
    <div className="app-layout">
      <Sidebar
        currentPage={currentPage}
        setCurrentPage={setCurrentPage}
        alertCount={unackAlerts}
      />

      <div className="main-wrapper">
        <Header
          pageTitle={getPageTitle()}
          simulationState={simulationState}
          unacknowledgedAlerts={unackAlerts}
          onNavigate={setCurrentPage}
          onStatusChange={syncAppState}
        />

        <main className="main-content">
          {renderPage()}
        </main>
      </div>
    </div>
  );
}
