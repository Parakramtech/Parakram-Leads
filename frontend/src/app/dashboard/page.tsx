'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { formatCurrency, formatCompactNumber } from '@/lib/format';
import { PRODUCT } from '@/lib/product';
import Link from 'next/link';
import ActivityFeed from '@/components/ActivityFeed';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
} from 'recharts';
import {
  Users, TrendingUp, DollarSign, Target, ArrowRight, Sparkles, ArrowUpRight,
} from 'lucide-react';

interface DashboardData {
  total_leads: number;
  hot_leads: number;
  warm_leads: number;
  cold_leads: number;
  messages_sent: number;
  responses: number;
  estimated_pipeline_value: number;
  conversion_rate: number;
  revenue_forecast: number;
  high_priority_leads: number;
  leads_ready_to_contact: number;
  avg_quality_score: number;
  avg_conversion_probability: number;
  pipeline_counts: Record<string, number>;
  top_lead: {
    id: string;
    business_name: string;
    industry: string;
    quality_score: number;
    conversion_probability: number;
    buying_urgency: number;
    optimal_channel: string;
    category_flag: string;
  } | null;
}

const defaultData: DashboardData = {
  total_leads: 0, hot_leads: 0, warm_leads: 0, cold_leads: 0,
  messages_sent: 0, responses: 0, estimated_pipeline_value: 0,
  conversion_rate: 0, revenue_forecast: 0,
  high_priority_leads: 0, leads_ready_to_contact: 0,
  avg_quality_score: 0, avg_conversion_probability: 0,
  pipeline_counts: {},
  top_lead: null,
};

const PIPELINE_STAGES = [
  { key: 'discovered', label: 'Discovered', color: '#52525b' },
  { key: 'analyzed', label: 'Analyzed', color: '#3b82f6' },
  { key: 'approved', label: 'Approved', color: '#f59e0b' },
  { key: 'contacted', label: 'Contacted', color: '#a855f7' },
  { key: 'responded', label: 'Responded', color: '#10b981' },
  { key: 'meeting_scheduled', label: 'Meeting', color: '#14b8a6' },
  { key: 'converted', label: 'Converted', color: '#34d399' },
  { key: 'disqualified', label: 'Lost', color: '#f87171' },
];

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-[#1a1a1d] border border-zinc-800 rounded-xl px-4 py-3 shadow-2xl">
        <p className="text-xs text-zinc-400 mb-1">{label}</p>
        <p className="text-lg font-bold text-zinc-100">{payload[0].value}</p>
      </div>
    );
  }
  return null;
};

export default function DashboardPage() {
  const [data, setData] = useState<DashboardData>(defaultData);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.dashboard.get()
      .then(setData)
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const pipelineData = PIPELINE_STAGES.map((s) => ({
    name: s.label,
    value: data.pipeline_counts[s.key] || 0,
    fill: s.color,
  }));

  const metrics = [
    {
      label: 'Pipeline Value',
      value: formatCurrency(data.estimated_pipeline_value),
      change: `${data.hot_leads + data.warm_leads} active deals`,
      icon: DollarSign,
    },
    {
      label: 'Conversion Rate',
      value: `${data.conversion_rate}%`,
      change: `${data.responses} responses from ${data.messages_sent} sent`,
      icon: TrendingUp,
    },
    {
      label: 'Avg Quality Score',
      value: `${Math.round(data.avg_quality_score)}`,
      change: `${data.high_priority_leads} high priority`,
      icon: Target,
    },
    {
      label: 'Revenue Forecast',
      value: formatCurrency(data.revenue_forecast),
      change: `${data.total_leads} leads in pipeline`,
      icon: Sparkles,
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-2 border-zinc-600 border-t-amber-400" />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between animate-fade-in">
        <div>
          <h1 className="text-2xl font-bold text-zinc-100">Dashboard</h1>
          <p className="text-sm text-zinc-500 mt-1.5">Your lead intelligence overview</p>
        </div>
        <div className="flex items-center gap-2.5 px-3 py-1.5 rounded-lg bg-emerald-500/5 border border-emerald-500/10 text-xs text-emerald-400">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse-glow" />
          System Online
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-5">
        {metrics.map((m, i) => {
          const Icon = m.icon;
          return (
            <div
              key={m.label}
              className={`rounded-xl bg-zinc-900/60 border border-zinc-800/60 p-5 card-hover glow-card opacity-0 animate-fade-in-up stagger-${i + 1}`}
            >
              <div className="flex items-center justify-between mb-3">
                <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">{m.label}</span>
                <div className="w-8 h-8 rounded-lg bg-zinc-800/50 flex items-center justify-center">
                  <Icon className="w-4 h-4 text-amber-400/70" />
                </div>
              </div>
              <p className="text-2xl md:text-3xl font-bold text-zinc-100 tracking-tight">{m.value}</p>
              <p className="text-xs text-zinc-600 mt-1.5">{m.change}</p>
            </div>
          );
        })}
      </div>

      {/* Main Grid — Chart + Stats */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Pipeline Funnel Chart */}
        <div className="lg:col-span-2 rounded-xl bg-zinc-900/60 border border-zinc-800/60 p-6 glow-card opacity-0 animate-fade-in-up stagger-5">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-sm font-semibold text-zinc-100">Pipeline Funnel</h3>
            <Link href="/leads" className="text-xs text-amber-400 hover:text-amber-300 transition-colors flex items-center gap-1 font-medium">
              View all <ArrowRight className="w-3 h-3" />
            </Link>
          </div>
          {pipelineData.some((d) => d.value > 0) ? (
            <div className="h-[280px]">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={pipelineData} barSize={32} barGap={4}>
                  <XAxis
                    dataKey="name"
                    axisLine={false}
                    tickLine={false}
                    tick={{ fill: '#71717a', fontSize: 11, fontWeight: 500 }}
                  />
                  <YAxis hide />
                  <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                  <Bar dataKey="value" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center justify-center h-[280px]">
              <p className="text-sm text-zinc-600">No leads in pipeline yet</p>
            </div>
          )}
        </div>

        {/* Right Column — Lead Summary */}
        <div className="space-y-4">
          {/* Category Breakdown */}
          <div className="rounded-xl bg-zinc-900/60 border border-zinc-800/60 p-5 glow-card opacity-0 animate-fade-in-up stagger-6">
            <h3 className="text-sm font-semibold text-zinc-100 mb-4">Lead Categories</h3>
            <div className="space-y-3">
              {[
                { label: 'Hot', value: data.hot_leads, color: 'bg-red-500', textColor: 'text-red-400' },
                { label: 'Warm', value: data.warm_leads, color: 'bg-amber-500', textColor: 'text-amber-400' },
                { label: 'Cold', value: data.cold_leads, color: 'bg-zinc-600', textColor: 'text-zinc-400' },
              ].map((cat) => {
                const total = data.hot_leads + data.warm_leads + data.cold_leads;
                const pct = total > 0 ? (cat.value / total) * 100 : 0;
                return (
                  <div key={cat.label}>
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="text-sm text-zinc-400 font-medium">{cat.label}</span>
                      <span className={`text-sm font-semibold ${cat.textColor}`}>{cat.value} ({Math.round(pct)}%)</span>
                    </div>
                    <div className="h-2 rounded-full bg-zinc-800 overflow-hidden">
                      <div className={`h-full rounded-full ${cat.color} transition-all duration-700 ease-out`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Top Lead / Quick Actions */}
          {data.top_lead ? (
            <Link href={`/leads/${data.top_lead.id}`}>
              <div className="rounded-xl bg-zinc-900/60 border border-zinc-800/60 p-5 card-hover group cursor-pointer glow-card opacity-0 animate-fade-in-up stagger-7">
                <div className="flex items-center gap-2 mb-3">
                  <Sparkles className="w-4 h-4 text-amber-400" />
                  <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider">Top Priority</span>
                </div>
                <p className="text-base font-semibold text-zinc-100 truncate group-hover:text-amber-300 transition-colors">{data.top_lead.business_name}</p>
                <p className="text-xs text-zinc-500 mt-0.5">{data.top_lead.industry}</p>
                <div className="flex items-center gap-4 mt-3 text-xs">
                  <span className="text-zinc-500">Quality <span className="text-emerald-400 font-semibold">{Math.round(data.top_lead.quality_score)}</span></span>
                  <span className="text-zinc-500">Conv. <span className="text-amber-400 font-semibold">{(data.top_lead.conversion_probability * 100).toFixed(0)}%</span></span>
                  <span className="flex items-center gap-1.5 text-amber-400 ml-auto group-hover:translate-x-0.5 transition-transform font-medium">
                    View <ArrowUpRight className="w-3.5 h-3.5" />
                  </span>
                </div>
              </div>
            </Link>
          ) : null}

          {/* Conversion Rate Ring */}
          <div className="rounded-xl bg-zinc-900/60 border border-zinc-800/60 p-5 glow-card opacity-0 animate-fade-in-up stagger-8">
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Conversion</span>
              <div className="w-8 h-8 rounded-lg bg-zinc-800/50 flex items-center justify-center">
                <Users className="w-4 h-4 text-emerald-400/70" />
              </div>
            </div>
            <div className="flex items-end gap-2">
              <p className="text-4xl font-bold text-zinc-100">{data.conversion_rate}%</p>
              <p className="text-xs text-zinc-600 mb-1.5">of leads convert</p>
            </div>
            <div className="mt-3 h-2 rounded-full bg-zinc-800 overflow-hidden">
              <div
                className="h-full rounded-full bg-gradient-to-r from-amber-500 to-emerald-400 transition-all duration-1000 ease-out"
                style={{ width: `${Math.min(data.conversion_rate, 100)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row — Recent Leads + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 rounded-xl bg-zinc-900/60 border border-zinc-800/60 p-6 glow-card opacity-0 animate-fade-in-up stagger-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-semibold text-zinc-100">Pipeline Summary</h3>
            <Link href="/leads" className="text-xs text-amber-400 hover:text-amber-300 transition-colors font-medium">View leads</Link>
          </div>
          <div className="space-y-2">
            {PIPELINE_STAGES.map((stage) => {
              const count = data.pipeline_counts[stage.key] || 0;
              const maxCount = Math.max(...Object.values(data.pipeline_counts), 1);
              return (
                <div key={stage.key} className="flex items-center gap-3">
                  <div className="w-20 shrink-0 text-right">
                    <span className="text-sm text-zinc-500">{stage.label}</span>
                  </div>
                  <div className="flex-1 h-8 rounded-lg bg-zinc-800/50 overflow-hidden relative">
                    <div
                      className="h-full rounded-lg transition-all duration-700 ease-out"
                      style={{ width: `${(count / maxCount) * 100}%`, backgroundColor: stage.color, opacity: 0.7 }}
                    />
                    <span className="absolute inset-0 flex items-center px-3 text-xs font-semibold text-zinc-200">{count}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        <ActivityFeed />
      </div>
    </div>
  );
}
