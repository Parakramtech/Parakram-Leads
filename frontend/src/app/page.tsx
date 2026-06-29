'use client';

import React, { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { api, setToken } from '@/lib/api';
import { Sparkles, ArrowRight, TrendingUp, Globe, Zap, Shield, User } from 'lucide-react';

function FloatingParticles() {
  const particles = useMemo(() =>
    Array.from({ length: 20 }, (_, i) => ({
      left: `${Math.random() * 100}%`,
      top: `${Math.random() * 100}%`,
      size: Math.random() * 3 + 1,
      delay: Math.random() * 5,
      duration: Math.random() * 6 + 4,
      opacity: Math.random() * 0.3 + 0.1,
    })), []
  );
  return (
    <div className="absolute inset-0 pointer-events-none overflow-hidden">
      {particles.map((p, i) => (
        <div
          key={i}
          className="absolute rounded-full bg-amber-400/30 animate-float"
          style={{
            left: p.left,
            top: p.top,
            width: p.size,
            height: p.size,
            opacity: p.opacity,
            animationDelay: `${p.delay}s`,
            animationDuration: `${p.duration}s`,
          }}
        />
      ))}
    </div>
  );
}

export default function LandingPage() {
  const router = useRouter();
  const [mode, setMode] = useState<'login' | 'register'>('register');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      const fn = mode === 'register' ? api.auth.register : api.auth.login;
      const data = mode === 'register'
        ? { email, password, full_name: fullName }
        : { email, password };
      const res = await fn(data as any);
      setToken(res.access_token);
      router.push('/dashboard');
    } catch (err: any) {
      setError(err.message || (mode === 'register' ? 'Registration failed' : 'Login failed'));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-[#070708]">
      {/* Left Panel */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 p-16 relative overflow-hidden bg-gradient-to-br from-[#0a0a0b] via-[#0d0d0e] to-black">
        <FloatingParticles />
        <div className="absolute inset-0 bg-premium-glow pointer-events-none" />
        <div className="absolute top-[-30%] left-[-20%] w-[70%] h-[70%] bg-[#d4af37]/[0.03] blur-[150px] rounded-full pointer-events-none" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-zinc-500/[0.04] blur-[120px] rounded-full pointer-events-none" />

        <div className="relative z-10">
          <div className="flex items-center gap-3 mb-12">
            <img src="/parakram_logo.png" alt="Parakram" className="w-8 h-8 shrink-0" />
            <span className="text-xs tracking-[0.15em] text-zinc-500 font-semibold uppercase">Parakram Suite</span>
          </div>

          <h1 className="text-5xl font-bold leading-tight tracking-tight">
            <span className="text-zinc-100">Intelligence that</span>
            <br />
            <span className="text-gradient">finds your customers.</span>
          </h1>

          <p className="mt-6 text-base text-zinc-500 leading-relaxed max-w-md">
            Autonomous lead discovery, AI-powered scoring, and multi-channel outreach — unified in one premium platform.
          </p>

          <div className="mt-12 space-y-5">
            {[
              { icon: TrendingUp, text: 'AI-powered lead scoring & intent prediction' },
              { icon: Zap, text: 'Multi-channel outreach (Email, WhatsApp, LinkedIn)' },
              { icon: Globe, text: 'Global prospect discovery across 20+ data sources' },
            ].map((item, i) => {
              const Icon = item.icon;
              return (
                <div key={i} className="flex items-center gap-4 group">
                  <div className="w-10 h-10 rounded-xl bg-zinc-900 border border-zinc-800 flex items-center justify-center group-hover:border-amber-500/30 transition-all duration-300">
                    <Icon className="w-5 h-5 text-zinc-400 group-hover:text-amber-400 transition-colors" />
                  </div>
                  <span className="text-sm text-zinc-400 group-hover:text-zinc-300 transition-colors">{item.text}</span>
                </div>
              );
            })}
          </div>
        </div>

        <div className="relative z-10 flex items-center gap-6 text-xs text-zinc-600">
          <span className="flex items-center gap-1.5"><Shield className="w-3.5 h-3.5" /> SOC 2 Compliant</span>
          <span className="flex items-center gap-1.5"><Globe className="w-3.5 h-3.5" /> 99.9% Uptime</span>
          <span className="flex items-center gap-1.5"><Sparkles className="w-3.5 h-3.5" /> AI-Powered</span>
        </div>
      </div>

      {/* Right Panel — Auth Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-sm">
          <div className="text-center mb-10 lg:hidden">
            <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-500 text-[10px] uppercase tracking-widest font-semibold mb-4">
              <Sparkles className="w-3 h-3 text-amber-400" />
              Parakram Suite
            </div>
            <h1 className="text-3xl font-bold tracking-tight">
              <span className="text-zinc-200">Parakram </span>
              <span className="text-gradient">Leads</span>
            </h1>
            <p className="text-zinc-500 text-sm mt-2 font-medium">Autonomous Lead Discovery & Outreach</p>
          </div>

          <div className="mb-8 hidden lg:block">
            <h2 className="text-2xl font-bold text-zinc-100">
              {mode === 'login' ? 'Welcome back' : 'Create your account'}
            </h2>
            <p className="text-sm text-zinc-500 mt-1.5">
              {mode === 'login' ? 'Sign in to your account to continue' : 'Start your 14-day free trial. No credit card needed.'}
            </p>
          </div>

          {/* Mode Toggle */}
          <div className="flex rounded-xl bg-zinc-900 border border-zinc-800 p-1 mb-6">
            <button
              onClick={() => { setMode('login'); setError(''); }}
              className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
                mode === 'login' ? 'bg-zinc-800 text-zinc-200 shadow-sm' : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              Sign in
            </button>
            <button
              onClick={() => { setMode('register'); setError(''); }}
              className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${
                mode === 'register' ? 'bg-zinc-800 text-zinc-200 shadow-sm' : 'text-zinc-500 hover:text-zinc-300'
              }`}
            >
              Register
            </button>
          </div>

          {error && (
            <div className="mb-6 p-3.5 bg-red-950/30 border border-red-900/50 text-red-400 text-xs rounded-xl flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {mode === 'register' && (
              <div className="space-y-1.5">
                <label className="text-xs font-medium text-zinc-400">Full name</label>
                <input
                  type="text"
                  value={fullName}
                  onChange={(e) => setFullName(e.target.value)}
                  className="w-full bg-[#0d0d0e] border border-zinc-800 focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/10 text-zinc-100 rounded-xl px-4 py-3 text-sm outline-none transition-all duration-300 placeholder-zinc-600"
                  placeholder="Varshini CB"
                  required
                />
              </div>
            )}

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-400">Email</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full bg-[#0d0d0e] border border-zinc-800 focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/10 text-zinc-100 rounded-xl px-4 py-3 text-sm outline-none transition-all duration-300 placeholder-zinc-600"
                placeholder="cbvarshini1@gmail.com"
                required
              />
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-medium text-zinc-400">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full bg-[#0d0d0e] border border-zinc-800 focus:border-amber-500/50 focus:ring-2 focus:ring-amber-500/10 text-zinc-100 rounded-xl px-4 py-3 text-sm outline-none transition-all duration-300 placeholder-zinc-600"
                placeholder={mode === 'register' ? 'Create a strong password' : 'Enter your password'}
                required
                minLength={6}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 px-4 bg-gradient-to-r from-amber-400 to-amber-500 text-black font-semibold rounded-xl hover:from-amber-300 hover:to-amber-400 active:scale-[0.98] transition-all duration-200 disabled:opacity-50 text-sm flex items-center justify-center gap-2 group shadow-lg shadow-amber-500/10"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-black" />
              ) : (
                <>
                  {mode === 'login' ? 'Sign in' : 'Create account'}
                  <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform duration-200" />
                </>
              )}
            </button>
          </form>

          <p className="mt-8 text-center text-xs text-zinc-600">
            {mode === 'login' ? (
              <>Don&apos;t have an account? <button onClick={() => { setMode('register'); setError(''); }} className="text-amber-400 hover:text-amber-300 underline underline-offset-2 transition-colors font-medium">Register here</button></>
            ) : (
              <>Already have an account? <button onClick={() => { setMode('login'); setError(''); }} className="text-amber-400 hover:text-amber-300 underline underline-offset-2 transition-colors font-medium">Sign in</button></>
            )}
          </p>
        </div>
      </div>
    </div>
  );
}
