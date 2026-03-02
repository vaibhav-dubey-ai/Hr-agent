'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import {
  BarChart3,
  Users,
  CheckCircle,
  Calendar,
  ArrowRight,
  Activity,
  Shield,
  Zap,
  TrendingUp,
  Sparkles,
} from 'lucide-react';
import {
  GlassCard,
  AnimatedCounter,
  GlowBadge,
  PageTransition,
  ShimmerLoader,
  PageHeader,
} from '@/components/ui';

export default function Dashboard() {
  const [stats, setStats] = useState({
    total_resumes: 0,
    ranked_today: 0,
    approved_leaves: 0,
    scheduled_interviews: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const timer = setTimeout(() => {
      setStats({
        total_resumes: 1200,
        ranked_today: 47,
        approved_leaves: 15,
        scheduled_interviews: 23,
      });
      setLoading(false);
    }, 800);
    return () => clearTimeout(timer);
  }, []);

  if (loading) {
    return (
      <div className="space-y-8 pt-4">
        <div className="skeleton h-12 w-96 mb-4" />
        <div className="skeleton h-5 w-64 mb-8" />
        <ShimmerLoader count={4} variant="card" />
      </div>
    );
  }

  const kpiCards = [
    {
      label: 'Total Resumes',
      value: stats.total_resumes,
      icon: Users,
      change: '+12%',
      glow: 'purple' as const,
      gradient: 'from-accent-purple/15 to-accent-blue/5',
      iconColor: 'text-accent-purple-light',
    },
    {
      label: 'Ranked Today',
      value: stats.ranked_today,
      icon: BarChart3,
      change: '+8%',
      glow: 'blue' as const,
      gradient: 'from-accent-blue/15 to-accent-cyan/5',
      iconColor: 'text-accent-blue-light',
    },
    {
      label: 'Approved Leaves',
      value: stats.approved_leaves,
      icon: CheckCircle,
      change: '+3%',
      glow: 'green' as const,
      gradient: 'from-green-500/15 to-emerald-500/5',
      iconColor: 'text-emerald-400',
    },
    {
      label: 'Interviews Scheduled',
      value: stats.scheduled_interviews,
      icon: Calendar,
      change: '+5%',
      glow: 'cyan' as const,
      gradient: 'from-accent-cyan/15 to-accent-blue/5',
      iconColor: 'text-accent-cyan-light',
    },
  ];

  const quickActions = [
    { title: 'Rank Resumes', desc: 'AI-powered resume matching & scoring', href: '/ranking', icon: Users, accent: 'group-hover:bg-accent-purple/10' },
    { title: 'Process Leave', desc: 'Automated leave decisions with policy', href: '/leave', icon: Calendar, accent: 'group-hover:bg-emerald-500/10' },
    { title: 'Schedule Interview', desc: 'Smart scheduling with conflict detection', href: '/scheduling', icon: Sparkles, accent: 'group-hover:bg-accent-blue/10' },
    { title: 'View Pipeline', desc: 'Track candidate journey through stages', href: '/pipeline', icon: TrendingUp, accent: 'group-hover:bg-accent-cyan/10' },
  ];

  const recentActivity = [
    { action: 'Ranked 47 resumes for Senior Dev role', time: '2h ago', type: 'ranking', color: 'bg-accent-purple' },
    { action: 'Approved 5 leave requests automatically', time: '4h ago', type: 'leave', color: 'bg-emerald-400' },
    { action: 'Scheduled 8 candidate interviews', time: '6h ago', type: 'schedule', color: 'bg-accent-blue' },
    { action: '3 candidates moved to offer stage', time: 'Yesterday', type: 'pipeline', color: 'bg-accent-cyan' },
    { action: 'Generated personalized interview questions', time: 'Yesterday', type: 'ai', color: 'bg-pink-400' },
  ];

  return (
    <PageTransition>
      <div className="space-y-10">
        {/* Hero Section */}
        <PageHeader
          title="Deterministic AI"
          subtitle="Automated resume ranking, intelligent leave management, and predictive scheduling — all powered by explainable AI."
        />
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          className="text-3xl sm:text-4xl font-extrabold font-display text-white/85 -mt-8 tracking-tight"
        >
          Governance for HR
        </motion.p>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {kpiCards.map((kpi, i) => {
            const Icon = kpi.icon;
            return (
              <GlassCard
                key={kpi.label}
                glowColor={kpi.glow}
                delay={i * 0.08}
                className="group"
              >
                <div className="flex items-start justify-between mb-5">
                  <div
                    className={`p-2.5 rounded-[14px] bg-gradient-to-br ${kpi.gradient} ring-1 ring-white/5`}
                  >
                    <Icon className={`w-5 h-5 ${kpi.iconColor}`} />
                  </div>
                  <GlowBadge variant="success" size="sm">
                    <TrendingUp className="w-2.5 h-2.5" />
                    {kpi.change}
                  </GlowBadge>
                </div>
                <div className="space-y-1.5">
                  <AnimatedCounter
                    value={kpi.value}
                    className="text-3xl font-bold text-white stat-value"
                    duration={1500 + i * 200}
                  />
                  <p className="text-[13px] text-white/30 font-medium">{kpi.label}</p>
                </div>
              </GlassCard>
            );
          })}
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Actions */}
          <GlassCard delay={0.3} className="lg:col-span-2" padding="p-0">
            <div className="card-header">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-accent-purple/8">
                  <Zap className="w-4 h-4 text-accent-purple" />
                </div>
                <h3 className="text-[13px] font-semibold text-white/85">Quick Actions</h3>
              </div>
            </div>
            <div className="p-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
              {quickActions.map((action, i) => {
                const Icon = action.icon;
                return (
                  <Link key={i} href={action.href} className="no-underline">
                    <motion.div
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.4 + i * 0.06 }}
                      whileHover={{ y: -2 }}
                      className="p-4 rounded-[14px] transition-all duration-200 cursor-pointer group border border-transparent hover:border-white/5"
                      style={{ background: 'rgba(255,255,255,0.01)' }}
                    >
                      <div className="flex items-center gap-3">
                        <div className={`p-2.5 rounded-xl bg-white/4 ${action.accent} transition-colors`}>
                          <Icon className="w-4 h-4 text-white/40 group-hover:text-white/70 transition-colors" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="font-semibold text-[13px] text-white/75 group-hover:text-white transition-colors">
                            {action.title}
                          </p>
                          <p className="text-[11px] text-white/25 mt-0.5">{action.desc}</p>
                        </div>
                        <ArrowRight className="w-4 h-4 text-white/8 group-hover:text-white/30 transition-all group-hover:translate-x-1" />
                      </div>
                    </motion.div>
                  </Link>
                );
              })}
            </div>
          </GlassCard>

          {/* System Status */}
          <GlassCard delay={0.4} padding="p-0">
            <div className="card-header">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-xl bg-green-500/8">
                  <Shield className="w-4 h-4 text-green-400" />
                </div>
                <h3 className="text-[13px] font-semibold text-white/85">System Status</h3>
              </div>
              <GlowBadge variant="success" size="sm" pulse>All OK</GlowBadge>
            </div>
            <div className="p-5 space-y-4">
              {[
                { name: 'API Server', status: 'Operational', color: 'bg-green-400' },
                { name: 'ML Pipeline', status: 'Active', color: 'bg-green-400' },
                { name: 'Database', status: 'Connected', color: 'bg-green-400' },
                { name: 'AI Agents', status: 'Running', color: 'bg-accent-purple' },
              ].map((service, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.5 + i * 0.06 }}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-2 h-2 rounded-full ${service.color} pulse-dot`} />
                    <span className="text-[13px] text-white/50 font-medium">{service.name}</span>
                  </div>
                  <span className="text-[11px] text-white/25 font-medium">{service.status}</span>
                </motion.div>
              ))}
            </div>
          </GlassCard>
        </div>

        {/* Recent Activity */}
        <GlassCard delay={0.5} padding="p-0">
          <div className="card-header">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-xl bg-accent-blue/8">
                <Activity className="w-4 h-4 text-accent-blue" />
              </div>
              <h3 className="text-[13px] font-semibold text-white/85">Recent Activity</h3>
            </div>
            <GlowBadge variant="purple" pulse size="sm">Live</GlowBadge>
          </div>
          <div className="p-4 space-y-0.5">
            {recentActivity.map((item, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.6 + i * 0.05 }}
                className="flex items-center justify-between p-3 rounded-xl hover:bg-white/[0.015] transition-colors group"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-1.5 h-1.5 rounded-full ${item.color}/40`} />
                  <span className="text-[13px] text-white/45 group-hover:text-white/65 transition-colors">
                    {item.action}
                  </span>
                </div>
                <span className="text-[11px] text-white/18 font-medium whitespace-nowrap ml-4">
                  {item.time}
                </span>
              </motion.div>
            ))}
          </div>
        </GlassCard>
      </div>
    </PageTransition>
  );
}
