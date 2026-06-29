'use client';

import React, { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { getToken, clearToken, getOrgId, setOrgId, api } from '@/lib/api';
import {
  LayoutDashboard, Users, MessageSquare, Settings, LogOut,
  Building2, ChevronDown, Check, Upload, Shield, Menu,
  Globe, ExternalLink,
} from 'lucide-react';
import AlertNotifications from '@/components/AlertNotifications';

const navItems = [
  { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/leads', label: 'Leads', icon: Users },
  { href: '/messages', label: 'Messages', icon: MessageSquare },
  { href: '/import', label: 'Import', icon: Upload },
  { href: '/organizations', label: 'Organizations', icon: Building2 },
  { href: '/audit', label: 'Audit Log', icon: Shield },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export default function ClientLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [authenticated, setAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const [orgs, setOrgs] = useState<any[]>([]);
  const [currentOrgId, setCurrentOrgId] = useState<string | null>(getOrgId());
  const [orgMenuOpen, setOrgMenuOpen] = useState(false);
  const [productMenuOpen, setProductMenuOpen] = useState(false);

  const products = [
    { id: 'leads', label: 'Parakram Leads', href: '/dashboard', icon: LayoutDashboard, description: 'AI Lead Intelligence', current: true },
    { id: 'website', label: 'Parakram Website', href: 'https://getparakram.in', icon: Globe, description: 'Brand Site', external: true },
    { id: 'edge', label: 'Parakram Edge', href: '#', icon: Settings, description: 'Mobile Edge Computing', locked: true },
    { id: 'research', label: 'Parakram Research', href: '#', icon: Settings, description: 'Research Automation', locked: true },
  ];

  useEffect(() => {
    const token = getToken();
    const publicPaths = ['/login', '/'];
    if (!token && !publicPaths.includes(pathname)) {
      router.push('/login');
    } else {
      setAuthenticated(!!token);
    }
    setLoading(false);
  }, [pathname, router]);

  useEffect(() => {
    if (!authenticated) return;
    api.organizations.list()
      .then((data) => {
        const list = Array.isArray(data) ? data : [];
        setOrgs(list);
        if (!currentOrgId && list.length > 0) {
          setOrgId(list[0].id);
          setCurrentOrgId(list[0].id);
        }
      })
      .catch(() => {});
  }, [authenticated]);

  const handleLogout = () => {
    clearToken();
    router.push('/login');
  };

  const handleSwitchOrg = async (orgId: string) => {
    try {
      await api.organizations.switch(orgId);
      setOrgId(orgId);
      setCurrentOrgId(orgId);
      setOrgMenuOpen(false);
      window.location.reload();
    } catch {
      // ignore
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-[#0a0a0b]">
        <div className="animate-spin rounded-full h-6 w-6 border-2 border-zinc-600 border-t-amber-400" />
      </div>
    );
  }

  const publicPaths = ['/login', '/'];
  if (publicPaths.includes(pathname)) {
    return <>{children}</>;
  }

  if (!authenticated) {
    return null;
  }

  const currentOrg = orgs.find((o) => o.id === currentOrgId);

  return (
    <div className="flex h-screen bg-[#0a0a0b] text-zinc-100 overflow-hidden">
      {/* Sidebar */}
      <aside className={`${sidebarOpen ? 'w-60' : 'w-16'} bg-zinc-950 border-r border-zinc-900 flex flex-col transition-all duration-200 relative z-30 shrink-0`}>
        <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
          {/* Logo & Product Switcher */}
          <div className={`px-5 mb-6 ${!sidebarOpen && 'px-3'}`}>
            <div className={`flex items-center gap-2.5 mb-1 ${sidebarOpen ? '' : 'justify-center'}`}>
              <img src="/parakram_logo.png" alt="Parakram" className="w-7 h-7 shrink-0" />
              {sidebarOpen && (
                <span className="text-sm font-semibold tracking-tight animate-fade-in">
                  <span className="text-zinc-200">Parakram</span>
                  <span className="text-gradient"> Leads</span>
                </span>
              )}
            </div>
            {sidebarOpen && <p className="text-[10px] text-zinc-600 font-medium ml-7">Sales Intelligence</p>}

            {/* Product Switcher */}
            {sidebarOpen && (
              <div className="relative mt-4">
                <button
                  onClick={() => setProductMenuOpen((v) => !v)}
                  className="flex items-center justify-between w-full px-3 py-2 rounded-lg bg-zinc-900/50 border border-zinc-800/50 hover:border-zinc-700/50 transition-all text-xs"
                >
                  <span className="text-zinc-400 font-medium">Switch Product</span>
                  <ChevronDown className={`w-3 h-3 text-zinc-600 transition-transform ${productMenuOpen ? 'rotate-180' : ''}`} />
                </button>
                {productMenuOpen && (
                  <>
                    <div className="fixed inset-0 z-10" onClick={() => setProductMenuOpen(false)} />
                    <div className="absolute left-0 mt-2 w-full bg-zinc-900 border border-zinc-800 rounded-xl shadow-2xl z-20 overflow-hidden">
                      <div className="p-1">
                        {products.map((p) => (
                          p.external ? (
                            <a key={p.id} href={p.href} target="_blank" rel="noopener noreferrer"
                              className="flex items-center justify-between w-full px-3 py-2 rounded-lg text-sm transition-colors text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200"
                              onClick={() => setProductMenuOpen(false)}
                            >
                              <div className="flex items-center gap-2">
                                <p.icon className="w-3.5 h-3.5 shrink-0" />
                                <div>
                                  <span className="text-xs">{p.label}</span>
                                  <p className="text-[9px] text-zinc-600">{p.description}</p>
                                </div>
                              </div>
                              <ExternalLink className="w-3 h-3 text-zinc-600 shrink-0" />
                            </a>
                          ) : p.current ? (
                            <div key={p.id}
                              className="flex items-center justify-between w-full px-3 py-2 rounded-lg text-sm bg-zinc-800/50 text-amber-400"
                            >
                              <div className="flex items-center gap-2">
                                <p.icon className="w-3.5 h-3.5 shrink-0" />
                                <div>
                                  <span className="text-xs">{p.label}</span>
                                  <p className="text-[9px] text-zinc-500">{p.description}</p>
                                </div>
                              </div>
                              <Check className="w-3 h-3 shrink-0" />
                            </div>
                          ) : (
                            <div key={p.id}
                              className="flex items-center justify-between w-full px-3 py-2 rounded-lg text-sm text-zinc-600 cursor-not-allowed"
                            >
                              <div className="flex items-center gap-2">
                                <p.icon className="w-3.5 h-3.5 shrink-0" />
                                <div>
                                  <span className="text-xs">{p.label}</span>
                                  <p className="text-[9px] text-zinc-700">{p.description}</p>
                                </div>
                              </div>
                              <span className="text-[8px] text-zinc-700 uppercase tracking-wider">Soon</span>
                            </div>
                          )
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {/* Nav */}
          <nav className="flex-1 px-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const active = pathname.startsWith(item.href);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 group relative overflow-hidden ${
                    active
                      ? 'bg-zinc-800/60 text-zinc-100'
                      : 'text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/30'
                  }`}
                >
                  {active && (
                    <span className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 rounded-full bg-gradient-to-b from-amber-400 to-amber-600 animate-fade-in" />
                  )}
                  <div className={`w-8 h-8 rounded-lg flex items-center justify-center transition-all duration-200 ${
                    active
                      ? 'bg-amber-500/10 text-amber-400'
                      : 'bg-transparent text-zinc-600 group-hover:text-zinc-400'
                  }`}>
                    <Icon className="w-4 h-4 shrink-0" />
                  </div>
                  {sidebarOpen && <span>{item.label}</span>}
                </Link>
              );
            })}
          </nav>
        </div>

        {/* Bottom section */}
        <div className="p-3 border-t border-zinc-900">
          {sidebarOpen && (
            <div className="px-3 py-2 mb-2 rounded-lg bg-zinc-900/50 border border-zinc-800/50">
              <div className="flex items-center justify-between mb-1">
                <span className="text-[10px] text-zinc-600 font-medium uppercase tracking-wider">Plan</span>
                <span className="text-[10px] font-semibold text-amber-400">Starter</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-[10px] text-zinc-600">Leads used</span>
                <span className="text-[10px] text-zinc-400">0 / 250</span>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium text-zinc-500 hover:text-zinc-300 hover:bg-zinc-800/30 transition-all w-full group"
          >
            <LogOut className="w-4 h-4 shrink-0 text-zinc-600 group-hover:text-zinc-400 transition-colors" />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </aside>

      {/* Main Panel */}
      <main className="flex-1 flex flex-col overflow-hidden min-w-0">
        <header className="bg-zinc-950/80 backdrop-blur-md border-b border-zinc-900 px-6 py-3 z-20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={() => setSidebarOpen((v) => !v)}
                className="p-1.5 rounded-lg hover:bg-zinc-800/50 text-zinc-500 hover:text-zinc-300 transition-colors"
              >
                <Menu className="w-4 h-4" />
              </button>
              <h2 className="text-sm font-semibold text-zinc-200">
                {navItems.find((i) => pathname.startsWith(i.href))?.label || 'Dashboard'}
              </h2>
            </div>

            <div className="flex items-center gap-3">
              {orgs.length > 0 && (
                <div className="relative">
                  <button
                    onClick={() => setOrgMenuOpen((v) => !v)}
                    className="flex items-center gap-2 px-3 py-1.5 bg-zinc-900 border border-zinc-800 rounded-lg text-sm text-zinc-400 hover:text-zinc-200 hover:border-zinc-700 transition-all"
                  >
                    <Building2 className="w-3.5 h-3.5 text-zinc-500" />
                    <span className="font-medium max-w-[120px] truncate text-xs">
                      {currentOrg?.name || 'Select Org'}
                    </span>
                    <ChevronDown className={`w-3 h-3 text-zinc-600 transition-transform ${orgMenuOpen ? 'rotate-180' : ''}`} />
                  </button>
                  {orgMenuOpen && (
                    <>
                      <div className="fixed inset-0 z-10" onClick={() => setOrgMenuOpen(false)} />
                      <div className="absolute right-0 mt-2 w-56 bg-zinc-900 border border-zinc-800 rounded-xl shadow-2xl z-20 overflow-hidden">
                        <div className="p-2 border-b border-zinc-800">
                          <p className="text-xs text-zinc-600 px-3 py-1">Switch Organization</p>
                        </div>
                        <div className="p-1 max-h-56 overflow-y-auto">
                          {orgs.map((org) => (
                            <button
                              key={org.id}
                              onClick={() => handleSwitchOrg(org.id)}
                              className={`flex items-center justify-between w-full px-3 py-2 rounded-lg text-sm transition-colors ${
                                org.id === currentOrgId
                                  ? 'bg-zinc-800 text-amber-400'
                                  : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
                              }`}
                            >
                              <div className="flex items-center gap-2">
                                <Building2 className="w-3.5 h-3.5 shrink-0" />
                                <span className="truncate text-xs">{org.name}</span>
                              </div>
                              {org.id === currentOrgId && (
                                <Check className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                              )}
                            </button>
                          ))}
                        </div>
                        <div className="p-1 border-t border-zinc-800">
                          <Link
                            href="/organizations"
                            onClick={() => setOrgMenuOpen(false)}
                            className="flex items-center gap-2 w-full px-3 py-2 rounded-lg text-xs text-amber-400 hover:bg-zinc-800 transition-colors"
                          >
                            <Building2 className="w-3.5 h-3.5" />
                            Manage Organizations
                          </Link>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}
              <AlertNotifications />
            </div>
          </div>
        </header>

        <div className="flex-1 overflow-auto px-6 py-6 bg-[#0a0a0b]">
          <div className="max-w-[1400px] mx-auto">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
