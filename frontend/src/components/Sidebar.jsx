import React from 'react';
import {
  LayoutDashboard,
  Activity,
  BarChart3,
  AlertTriangle,
  Cpu,
  Settings,
  Info,
  Zap,
} from 'lucide-react';

export default function Sidebar({ currentPage, setCurrentPage, alertCount = 0 }) {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'live', label: 'Live Monitoring', icon: Activity },
    { id: 'analytics', label: 'Energy Analytics', icon: BarChart3 },
    { id: 'alerts', label: 'Alerts & Events', icon: AlertTriangle, badge: alertCount },
    { id: 'simulator', label: 'Device Simulator', icon: Cpu },
    { id: 'settings', label: 'Settings', icon: Settings },
    { id: 'about', label: 'About PowerGuard', icon: Info },
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-header">
        <div className="brand-icon">
          <Zap size={20} />
        </div>
        <div>
          <div className="brand-text">PowerGuard</div>
          <div className="brand-sub">Load Intelligence</div>
        </div>
      </div>

      <nav className="sidebar-nav">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          return (
            <button
              key={item.id}
              className={`nav-link ${isActive ? 'active' : ''}`}
              onClick={() => setCurrentPage(item.id)}
              style={{ width: '100%', border: 'none', background: 'none', textAlign: 'left' }}
            >
              <Icon size={18} />
              <span style={{ flex: 1 }}>{item.label}</span>
              {item.badge > 0 && (
                <span className="badge badge-critical" style={{ fontSize: '0.65rem', padding: '1px 6px' }}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      <div className="sidebar-footer">
        <div className="sim-mode-tag">
          <Zap size={14} color="#38bdf8" />
          <span>SIMULATION MODE ONLY</span>
        </div>
        <p style={{ marginTop: '8px', lineHeight: 1.3, fontSize: '0.6875rem' }}>
          Academic prototype. No physical electrical sensors connected.
        </p>
      </div>
    </aside>
  );
}
