'use client';

import React, { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';
import {
  Users, MessageSquare, Sparkles, ArrowRight, Activity,
  Zap, Clock, CheckCircle, Target,
} from 'lucide-react';

export default function ActivityFeed() {
  const [leads, setLeads] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.leads.list({ page: 1, per_page: 5 }).catch(() => ({ leads: [] })),
      api.messages.filter({ page: '1', per_page: '5' }).catch(() => []),
    ]).then(([leadsRes, msgs]) => {
      setLeads(leadsRes.leads || []);
      setMessages(Array.isArray(msgs) ? msgs : []);
    }).finally(() => setLoading(false));
  }, []);

  const activities: { time: string; icon: any; color: string; text: string; link?: string }[] = [];

  leads.forEach((l) => {
    activities.push({
      time: l.created_at,
      icon: Users,
      color: 'text-blue-400 bg-blue-500/10',
      text: `Lead "${l.business_name}" was discovered`,
      link: `/leads/${l.id}`,
    });
    if (l.category_flag === 'hot') {
      activities.push({
        time: l.updated_at || l.created_at,
        icon: Zap,
        color: 'text-red-400 bg-red-500/10',
        text: `Lead "${l.business_name}" flagged as HOT`,
        link: `/leads/${l.id}`,
      });
    }
    if (l.last_intelligence_update) {
      activities.push({
        time: l.last_intelligence_update,
        icon: Sparkles,
        color: 'text-emerald-400 bg-emerald-500/10',
        text: `Lead "${l.business_name}" intelligence updated`,
        link: `/leads/${l.id}`,
      });
    }
  });

  messages.forEach((m) => {
    activities.push({
      time: m.sent_at || m.created_at,
      icon: MessageSquare,
      color: 'text-purple-400 bg-purple-500/10',
      text: `Message sent via ${m.channel}`,
      link: `/messages`,
    });
    if (m.reply_content) {
      activities.push({
        time: m.replied_at || m.updated_at,
        icon: CheckCircle,
        color: 'text-emerald-400 bg-emerald-500/10',
        text: `Reply received for ${m.channel} message`,
        link: `/messages`,
      });
    }
  });

  activities.sort((a, b) => new Date(b.time).getTime() - new Date(a.time).getTime());
  const recent = activities.slice(0, 10);

  if (loading) {
    return (
      <div className="rounded-2xl p-5 bg-zinc-900/80 border border-zinc-800 shadow-xl">
        <div className="animate-pulse space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-lg bg-zinc-800" />
              <div className="flex-1 space-y-2">
                <div className="h-3 bg-zinc-800 rounded w-3/4" />
                <div className="h-2 bg-zinc-800/50 rounded w-1/3" />
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-2xl p-5 bg-zinc-900/80 border border-zinc-800 shadow-xl glow-card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Activity className="w-4 h-4 text-amber-400" />
          <h3 className="text-xs uppercase tracking-wider text-zinc-500 font-semibold">Activity Feed</h3>
        </div>
        {recent.length > 0 && (
          <span className="px-2 py-0.5 rounded-full bg-zinc-800/50 text-[10px] font-medium text-zinc-500">{recent.length} events</span>
        )}
      </div>
      {recent.length === 0 ? (
        <div className="text-center py-8 animate-fade-in">
          <Activity className="w-10 h-10 text-zinc-700 mx-auto mb-2" />
          <p className="text-xs text-zinc-600">No recent activity</p>
          <p className="text-[10px] text-zinc-700 mt-1">Actions will appear here as you work</p>
        </div>
      ) : (
        <div className="space-y-1 max-h-[380px] overflow-y-auto -mx-1 px-1">
          {recent.map((a, i) => {
            const Icon = a.icon;
            return (
              <div key={i} className="opacity-0 animate-slide-up" style={{ animationDelay: `${i * 30}ms`, animationFillMode: 'forwards' }}>
                {a.link ? (
                  <Link href={a.link} className="flex items-start gap-3 p-2.5 rounded-xl hover:bg-zinc-800/40 transition-all duration-200 group">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${a.color} group-hover:scale-105 transition-transform duration-200`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-zinc-300 group-hover:text-zinc-100 transition-colors leading-relaxed">{a.text}</p>
                      <p className="text-[11px] text-zinc-600 mt-0.5 font-medium">
                        {new Date(a.time).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                    <ArrowRight className="w-3 h-3 text-zinc-700 opacity-0 group-hover:opacity-100 transition-all duration-200 shrink-0 group-hover:translate-x-0.5" />
                  </Link>
                ) : (
                  <div className="flex items-start gap-3 p-2.5">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center shrink-0 ${a.color}`}>
                      <Icon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs text-zinc-300 leading-relaxed">{a.text}</p>
                      <p className="text-[11px] text-zinc-600 mt-0.5 font-medium">
                        {new Date(a.time).toLocaleString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                      </p>
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
      <div className="mt-3 pt-3 border-t border-zinc-800/50">
        <Link href="/messages" className="flex items-center justify-center gap-1.5 py-2 text-xs text-zinc-500 hover:text-zinc-300 transition-colors rounded-lg hover:bg-zinc-800/30">
          View all activity <ArrowRight className="w-3 h-3" />
        </Link>
      </div>
    </div>
  );
}
