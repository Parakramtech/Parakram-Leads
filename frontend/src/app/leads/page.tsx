'use client';

import React, { useState, useEffect, useCallback } from 'react';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/format';
import IntelligenceBadge from '@/components/IntelligenceBadge';
import Link from 'next/link';
import {
  Search, Filter, ChevronDown, Plus, ExternalLink, Zap,
  ChevronUp, Check, X, Loader2, Trash2, Sparkles,
  ArrowUpDown, Download, Columns,
} from 'lucide-react';

type SortField = 'business_name' | 'created_at' | 'opportunity_score' | 'quality_score' | 'conversion_probability' | 'buying_urgency' | 'category_flag' | 'industry' | 'location' | 'source';
type SortOrder = 'asc' | 'desc';

const STATUS_OPTIONS = ['discovered', 'analyzed', 'approved', 'contacted', 'responded', 'meeting_scheduled', 'converted', 'disqualified'];
const CATEGORY_OPTIONS = ['hot', 'warm', 'cold'];

const categoryBadge = (cat: string) => {
  const map: Record<string, string> = {
    hot: 'bg-red-500/15 text-red-400 border-red-500/25',
    warm: 'bg-amber-500/15 text-amber-400 border-amber-500/25',
    cold: 'bg-zinc-700 text-zinc-400 border-zinc-600',
  };
  return `px-2.5 py-0.5 rounded-full text-[10px] font-semibold uppercase border ${map[cat] || map.cold}`;
};

const statusBadge = (st: string) => {
  const map: Record<string, string> = {
    discovered: 'bg-zinc-700/50 text-zinc-400',
    analyzed: 'bg-blue-500/10 text-blue-400',
    approved: 'bg-amber-500/10 text-amber-400',
    contacted: 'bg-purple-500/10 text-purple-400',
    responded: 'bg-emerald-500/10 text-emerald-400',
    meeting_scheduled: 'bg-teal-500/10 text-teal-400',
    converted: 'bg-emerald-400/10 text-emerald-300',
    disqualified: 'bg-red-500/10 text-red-400',
  };
  return `px-2 py-0.5 rounded-full text-[10px] capitalize ${map[st] || 'bg-zinc-700/50 text-zinc-400'}`;
};

export default function LeadsPage() {
  const [leads, setLeads] = useState<any[]>([]);
  const [total, setTotal] = useState(0);
  const [hot, setHot] = useState(0);
  const [warm, setWarm] = useState(0);
  const [cold, setCold] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [status, setStatus] = useState('');
  const [page, setPage] = useState(1);
  const [sortBy, setSortBy] = useState<SortField>('opportunity_score');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [bulkAction, setBulkAction] = useState('');
  const [bulkProcessing, setBulkProcessing] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedLead, setSelectedLead] = useState<any>(null);

  const fetchLeads = useCallback(async () => {
    setLoading(true);
    try {
      const params: Record<string, string | number> = { page, per_page: 20, sort_by: sortBy, sort_order: sortOrder };
      if (category) params.category = category;
      if (status) params.status = status;
      if (search) params.search = search;
      const res = await api.leads.list(params);
      setLeads(res.leads);
      setTotal(res.total);
      setHot(res.hot);
      setWarm(res.warm);
      setCold(res.cold);
    } catch {}
    setLoading(false);
  }, [page, category, status, search, sortBy, sortOrder]);

  useEffect(() => { fetchLeads(); }, [fetchLeads]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setPage(1);
    fetchLeads();
  };

  const toggleSort = (field: SortField) => {
    if (sortBy === field) setSortOrder((o) => (o === 'desc' ? 'asc' : 'desc'));
    else { setSortBy(field); setSortOrder('desc'); }
    setPage(1);
  };

  const toggleSelect = (id: string) => {
    setSelectedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  };

  const toggleSelectAll = () => {
    if (selectedIds.size === leads.length) setSelectedIds(new Set());
    else setSelectedIds(new Set(leads.map((l) => l.id)));
  };

  const handleBulk = async () => {
    if (!bulkAction || selectedIds.size === 0) return;
    setBulkProcessing(true);
    try {
      await api.leads.bulk({ lead_ids: Array.from(selectedIds), action: bulkAction });
      setSelectedIds(new Set());
      setBulkAction('');
      fetchLeads();
    } catch {}
    setBulkProcessing(false);
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortBy !== field) return <ArrowUpDown className="w-3 h-3 text-zinc-600" />;
    return sortOrder === 'desc' ? <ChevronDown className="w-3 h-3 text-amber-400" /> : <ChevronUp className="w-3 h-3 text-amber-400" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">Leads</h1>
          <p className="text-sm text-zinc-500 mt-1">{total} total &middot; <span className="text-red-400">{hot} hot</span> &middot; <span className="text-amber-400">{warm} warm</span> &middot; <span className="text-zinc-500">{cold} cold</span></p>
        </div>
        <div className="flex items-center gap-3">
          <Link href="/import" className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-zinc-900 border border-zinc-800 text-sm text-zinc-300 hover:bg-zinc-800 transition-colors">
            <Download className="w-4 h-4" /> Import
          </Link>
          <button className="flex items-center gap-1.5 px-4 py-2 rounded-xl bg-gradient-to-r from-amber-400 to-orange-600 text-black text-sm font-semibold hover:opacity-90 transition-opacity">
            <Plus className="w-4 h-4" /> Add Lead
          </button>
        </div>
      </div>

      {/* Search + Filters */}
      <div className="space-y-3">
        <div className="flex items-center gap-3">
          <form onSubmit={handleSearch} className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-zinc-500" />
            <input
              type="text" value={search}
              onChange={(e) => { setSearch(e.target.value); setPage(1); }}
              placeholder="Search by name, phone, industry, location..."
              className="w-full pl-10 pr-4 py-2 rounded-xl bg-zinc-900/80 border border-zinc-800 text-sm text-zinc-300 placeholder-zinc-600 focus:ring-2 focus:ring-amber-500/50 outline-none transition-all"
            />
          </form>
          <select value={category} onChange={(e) => { setCategory(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-zinc-900/80 border border-zinc-800 text-sm text-zinc-300 focus:ring-2 focus:ring-amber-500/50 outline-none">
            <option value="">All Categories</option>
            {CATEGORY_OPTIONS.map((c) => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={status} onChange={(e) => { setStatus(e.target.value); setPage(1); }}
            className="px-3 py-2 rounded-xl bg-zinc-900/80 border border-zinc-800 text-sm text-zinc-300 focus:ring-2 focus:ring-amber-500/50 outline-none">
            <option value="">All Statuses</option>
            {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s.replace(/_/g, ' ')}</option>)}
          </select>
          <button onClick={() => setShowFilters((v) => !v)}
            className={`p-2 rounded-xl border transition-colors ${showFilters ? 'bg-amber-500/10 border-amber-500/30 text-amber-400' : 'bg-zinc-900/80 border-zinc-800 text-zinc-400 hover:text-zinc-200'}`}>
            <Filter className="w-4 h-4" />
          </button>
        </div>

        {showFilters && (
          <div className="rounded-xl p-4 bg-zinc-900/60 border border-zinc-800 flex flex-wrap items-center gap-4 text-xs">
            <span className="text-zinc-500 font-medium">Sort by:</span>
            {[
              { field: 'opportunity_score' as SortField, label: 'Opportunity' },
              { field: 'quality_score' as SortField, label: 'Quality' },
              { field: 'conversion_probability' as SortField, label: 'Conversion' },
              { field: 'buying_urgency' as SortField, label: 'Urgency' },
              { field: 'business_name' as SortField, label: 'Name' },
              { field: 'created_at' as SortField, label: 'Created' },
              { field: 'industry' as SortField, label: 'Industry' },
              { field: 'location' as SortField, label: 'Location' },
            ].map((opt) => (
              <button key={opt.field} onClick={() => toggleSort(opt.field)}
                className={`flex items-center gap-1 px-2.5 py-1.5 rounded-lg transition-colors ${
                  sortBy === opt.field ? 'bg-amber-500/10 text-amber-400' : 'text-zinc-400 hover:text-zinc-200'
                }`}>
                {opt.label} <SortIcon field={opt.field} />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Bulk Actions Bar */}
      {selectedIds.size > 0 && (
        <div className="flex items-center gap-3 px-5 py-3 rounded-xl bg-amber-500/10 border border-amber-500/20">
          <span className="text-sm text-zinc-300 font-medium">{selectedIds.size} selected</span>
          <select value={bulkAction} onChange={(e) => setBulkAction(e.target.value)}
            className="px-3 py-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-xs text-zinc-300 outline-none">
            <option value="">Bulk action...</option>
            <option value="approve">Approve Outreach</option>
            <option value="disqualify">Disqualify</option>
            <option value="reanalyze">Re-analyze</option>
          </select>
          <button onClick={handleBulk} disabled={!bulkAction || bulkProcessing}
            className="px-4 py-1.5 rounded-lg bg-amber-500 text-black text-xs font-semibold hover:bg-amber-400 disabled:opacity-50 transition-colors">
            {bulkProcessing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : 'Apply'}
          </button>
          <button onClick={() => setSelectedIds(new Set())} className="ml-auto text-xs text-zinc-500 hover:text-zinc-300 transition-colors">
            Clear selection
          </button>
        </div>
      )}

      {/* Table */}
      <div className="rounded-2xl bg-zinc-900/80 border border-zinc-800 shadow-xl overflow-hidden glow-card">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-zinc-800 bg-zinc-900/50">
                <th className="w-10 px-4 py-4">
                  <input type="checkbox" checked={leads.length > 0 && selectedIds.size === leads.length}
                    onChange={toggleSelectAll} className="rounded border-zinc-600 bg-zinc-800 accent-amber-500 cursor-pointer" />
                </th>
                <th className="text-left px-4 py-4 font-semibold text-zinc-500 text-xs uppercase tracking-wider cursor-pointer hover:text-zinc-300 transition-colors" onClick={() => toggleSort('business_name')}>
                  <div className="flex items-center gap-1.5">Business <SortIcon field="business_name" /></div>
                </th>
                <th className="text-left px-4 py-4 font-semibold text-zinc-500 text-xs uppercase tracking-wider">Contact</th>
                <th className="text-center px-4 py-4 font-semibold text-zinc-500 text-xs uppercase tracking-wider cursor-pointer hover:text-zinc-300 transition-colors" onClick={() => toggleSort('category_flag')}>
                  <div className="flex items-center justify-center gap-1.5">Category <SortIcon field="category_flag" /></div>
                </th>
                <th className="text-center px-4 py-4 font-semibold text-zinc-500 text-xs uppercase tracking-wider cursor-pointer hover:text-zinc-300 transition-colors" onClick={() => toggleSort('quality_score')}>
                  <div className="flex items-center justify-center gap-1.5">Quality <SortIcon field="quality_score" /></div>
                </th>
                <th className="text-center px-4 py-4 font-semibold text-zinc-500 text-xs uppercase tracking-wider cursor-pointer hover:text-zinc-300 transition-colors" onClick={() => toggleSort('opportunity_score')}>
                  <div className="flex items-center justify-center gap-1.5">Opportunity <SortIcon field="opportunity_score" /></div>
                </th>
                <th className="text-center px-4 py-4 font-semibold text-zinc-500 text-xs uppercase tracking-wider cursor-pointer hover:text-zinc-300 transition-colors" onClick={() => toggleSort('buying_urgency')}>
                  <div className="flex items-center justify-center gap-1.5">Urgency <SortIcon field="buying_urgency" /></div>
                </th>
                <th className="text-center px-4 py-4 font-semibold text-zinc-500 text-xs uppercase tracking-wider">Status</th>
                <th className="text-center px-4 py-4 font-semibold text-zinc-500 text-xs uppercase tracking-wider cursor-pointer hover:text-zinc-300 transition-colors" onClick={() => toggleSort('created_at')}>
                  <div className="flex items-center justify-center gap-1.5">Created <SortIcon field="created_at" /></div>
                </th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={9} className="text-center py-16">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-amber-400 mx-auto" />
                </td></tr>
              ) : leads.length === 0 ? (
                <tr><td colSpan={9} className="text-center py-16">
                  <p className="text-sm text-zinc-500">No leads found. {search ? 'Try a different search.' : 'Import leads to get started.'}</p>
                </td></tr>
              ) : (
                leads.map((lead, idx) => (
                  <tr
                    key={lead.id}
                    className={`border-b border-zinc-800/50 transition-all duration-200 opacity-0 animate-slide-up ${
                      selectedIds.has(lead.id) ? 'bg-amber-500/5' : ''
                    }`}
                    style={{ animationDelay: `${idx * 20}ms`, animationFillMode: 'forwards' }}
                    onMouseEnter={(e) => {
                      if (!selectedIds.has(lead.id)) e.currentTarget.classList.remove('hover:bg-zinc-800/30');
                    }}
                  >
                    <td className="px-4 py-3.5">
                      <input type="checkbox" checked={selectedIds.has(lead.id)} onChange={() => toggleSelect(lead.id)}
                        className="rounded border-zinc-600 bg-zinc-800 accent-amber-500 cursor-pointer" />
                    </td>
                    <td className="px-4 py-3.5">
                      <Link href={`/leads/${lead.id}`} className="font-semibold text-zinc-200 hover:text-amber-400 transition-colors">
                        {lead.business_name}
                      </Link>
                      {lead.industry && <p className="text-[11px] text-zinc-600 mt-0.5">{lead.industry}</p>}
                    </td>
                    <td className="px-4 py-3.5 text-xs text-zinc-400">
                      {lead.phone && <p>{lead.phone}</p>}
                      {lead.location && <p className="text-zinc-600">{lead.location}</p>}
                    </td>
                    <td className="px-4 py-3.5 text-center">
                      <span className={categoryBadge(lead.category_flag)}>{lead.category_flag}</span>
                    </td>
                    <td className="px-4 py-3.5 text-center">
                      <IntelligenceBadge
                        qualityScore={lead.predictive_quality_score}
                        conversionProb={lead.conversion_probability}
                        buyingUrgency={lead.buying_urgency}
                        optimalChannel={lead.optimal_channel}
                      />
                    </td>
                    <td className="px-4 py-3.5 text-center">
                      <span className="text-sm font-bold text-zinc-200">{Math.round(lead.opportunity_score)}</span>
                    </td>
                    <td className="px-4 py-3.5 text-center">
                      <span className={`text-xs font-semibold ${lead.buying_urgency >= 70 ? 'text-red-400' : lead.buying_urgency >= 40 ? 'text-amber-400' : 'text-zinc-500'}`}>
                        {lead.buying_urgency ? `${Math.round(lead.buying_urgency)}` : '-'}
                      </span>
                    </td>
                    <td className="px-4 py-3.5 text-center">
                      <span className={statusBadge(lead.status)}>{lead.status.replace(/_/g, ' ')}</span>
                    </td>
                    <td className="px-4 py-3.5 text-center text-xs text-zinc-600">
                      {new Date(lead.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {total > 20 && (
          <div className="flex items-center justify-between px-6 py-4 border-t border-zinc-800">
            <p className="text-sm text-zinc-500">Page {page} of {Math.max(1, Math.ceil(total / 20))}</p>
            <div className="flex gap-2">
              <button onClick={() => setPage(Math.max(1, page - 1))} disabled={page === 1}
                className="px-4 py-2 text-sm rounded-xl border border-zinc-800 text-zinc-400 disabled:opacity-40 hover:bg-zinc-800 transition-colors">Previous</button>
              <button onClick={() => setPage(page + 1)} disabled={page >= Math.ceil(total / 20)}
                className="px-4 py-2 text-sm rounded-xl border border-zinc-800 text-zinc-400 disabled:opacity-40 hover:bg-zinc-800 transition-colors">Next</button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
