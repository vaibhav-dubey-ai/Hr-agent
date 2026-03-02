'use client';

import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Activity, Zap, Power, Clock, Shield, Sparkles } from 'lucide-react';
import { GlassCard, GlowBadge, PageTransition, PageHeader, AnimatedCounter } from '@/components/ui';

interface ActivityEntry {
    id: number; action: string; time: string; type: 'ranking' | 'leave' | 'schedule' | 'pipeline' | 'system';
}

const mockActivities: ActivityEntry[] = [
    { id: 1, action: 'Auto-ranked 23 resumes for Frontend Engineer role', time: '2 min ago', type: 'ranking' },
    { id: 2, action: 'Approved sick leave for Sarah Chen (3 days)', time: '5 min ago', type: 'leave' },
    { id: 3, action: 'Scheduled interview: candidate_12 with interviewer_003', time: '8 min ago', type: 'schedule' },
    { id: 4, action: 'Pipeline: Moved candidate_7 to offer_extended', time: '12 min ago', type: 'pipeline' },
    { id: 5, action: 'Rejected leave request for John Doe — exceeded quota', time: '15 min ago', type: 'leave' },
    { id: 6, action: 'Auto-ranked 15 resumes for Data Scientist role', time: '20 min ago', type: 'ranking' },
    { id: 7, action: 'Resolved scheduling conflict for interviewer_001', time: '25 min ago', type: 'schedule' },
    { id: 8, action: 'System health check passed — all services operational', time: '30 min ago', type: 'system' },
];

const typeConfig: Record<string, { icon: string; color: string }> = {
    ranking: { icon: '📊', color: 'border-l-accent-purple' },
    leave: { icon: '📅', color: 'border-l-emerald-400' },
    schedule: { icon: '⏰', color: 'border-l-accent-blue' },
    pipeline: { icon: '🔄', color: 'border-l-accent-cyan' },
    system: { icon: '🛡️', color: 'border-l-amber-400' },
};

export default function AutonomousPage() {
    const [isActive, setIsActive] = useState(false);
    const [activities, setActivities] = useState<ActivityEntry[]>([]);
    const [counter, setCounter] = useState(0);
    const logRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!isActive) return;
        let i = 0;
        const interval = setInterval(() => {
            if (i < mockActivities.length) {
                setActivities(prev => [mockActivities[i], ...prev]);
                setCounter(c => c + 1);
                i++;
            }
        }, 2000);
        return () => clearInterval(interval);
    }, [isActive]);

    return (
        <PageTransition>
            <div className="space-y-8">
                <PageHeader title="Autonomous Mode" subtitle="Let AI handle HR operations automatically" />

                {/* Toggle Card */}
                <GlassCard delay={0.1} glowColor={isActive ? 'purple' : 'none'}
                    className={isActive ? 'border-accent-purple/15 shadow-glow-md' : ''}>
                    <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                            <div className="relative">
                                <motion.div animate={isActive ? { rotate: [0, 360] } : {}}
                                    transition={isActive ? { duration: 4, repeat: Infinity, ease: 'linear' } : {}}>
                                    <div className={`p-3 rounded-[14px] transition-all ${isActive ? 'bg-gradient-to-br from-accent-purple to-accent-blue shadow-glow-sm' : 'bg-white/4'}`}>
                                        <Brain className={`w-6 h-6 ${isActive ? 'text-white' : 'text-white/25'}`} />
                                    </div>
                                </motion.div>
                                {isActive && (
                                    <motion.div
                                        animate={{ scale: [1, 1.6, 1], opacity: [0.3, 0, 0.3] }}
                                        transition={{ duration: 2, repeat: Infinity }}
                                        className="absolute inset-0 rounded-[14px] bg-accent-purple/20"
                                    />
                                )}
                            </div>
                            <div>
                                <h3 className="text-lg font-bold font-display text-white/85">AI Autonomous Agent</h3>
                                <p className="text-[13px] text-white/25">Automated resume ranking, leave processing, and scheduling</p>
                            </div>
                        </div>

                        {/* Toggle */}
                        <motion.button whileTap={{ scale: 0.95 }}
                            onClick={() => { setIsActive(!isActive); if (isActive) { setActivities([]); setCounter(0); } }}
                            className={`relative w-20 h-10 rounded-full transition-all duration-500 ${isActive ? 'bg-gradient-to-r from-accent-purple to-accent-blue shadow-glow-sm' : 'bg-white/8'}`}>
                            <motion.div animate={{ x: isActive ? 40 : 4 }}
                                transition={{ type: 'spring', damping: 20, stiffness: 300 }}
                                className={`absolute top-1 w-8 h-8 rounded-full flex items-center justify-center ${isActive ? 'bg-white shadow-lg' : 'bg-white/15'}`}>
                                <Power className={`w-4 h-4 ${isActive ? 'text-accent-purple' : 'text-white/35'}`} />
                            </motion.div>
                        </motion.button>
                    </div>

                    <div className="mt-5 flex items-center gap-3">
                        <GlowBadge variant={isActive ? 'success' : 'warning'} pulse={isActive}>
                            {isActive ? 'Active' : 'Standby'}
                        </GlowBadge>
                        {isActive && <span className="text-[11px] text-white/25">{counter} actions performed</span>}
                    </div>
                </GlassCard>

                {/* Stats Row */}
                {isActive && (
                    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                        className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                        {[
                            { label: 'Resumes Ranked', value: Math.floor(counter * 5.2), icon: Sparkles, color: 'text-accent-purple' },
                            { label: 'Leaves Processed', value: Math.floor(counter * 1.8), icon: Shield, color: 'text-green-400' },
                            { label: 'Interviews Set', value: Math.floor(counter * 2.1), icon: Clock, color: 'text-accent-blue' },
                            { label: 'Actions/min', value: 3.2, icon: Activity, color: 'text-accent-cyan' },
                        ].map((s, i) => {
                            const Icon = s.icon;
                            return (
                                <GlassCard key={i} delay={0} animated={false} padding="p-4">
                                    <Icon className={`w-4 h-4 ${s.color} mb-3`} />
                                    <p className="text-xl font-bold font-display text-white stat-value">
                                        {typeof s.value === 'number' && Number.isInteger(s.value) ? s.value : s.value}
                                    </p>
                                    <p className="text-[10px] text-white/25 font-medium mt-1">{s.label}</p>
                                </GlassCard>
                            );
                        })}
                    </motion.div>
                )}

                {/* Activity Timeline */}
                <GlassCard delay={0.2} padding="p-0">
                    <div className="card-header">
                        <div className="flex items-center gap-3">
                            <div className="p-2 rounded-xl bg-accent-blue/8"><Activity className="w-4 h-4 text-accent-blue" /></div>
                            <h3 className="text-[13px] font-semibold text-white/85">AI Activity Log</h3>
                        </div>
                        {isActive && <GlowBadge variant="purple" pulse size="sm">Recording</GlowBadge>}
                    </div>

                    <div ref={logRef} className="p-4 space-y-0.5 max-h-[400px] overflow-y-auto">
                        <AnimatePresence>
                            {activities.length === 0 ? (
                                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-12">
                                    <motion.div animate={{ y: [-6, 6, -6] }} transition={{ duration: 3, repeat: Infinity }}>
                                        <Zap className="w-12 h-12 text-white/8 mx-auto mb-3" />
                                    </motion.div>
                                    <p className="text-[13px] text-white/18">{isActive ? 'Waiting for first action...' : 'Enable autonomous mode to begin'}</p>
                                </motion.div>
                            ) : (
                                activities.map((a) => {
                                    if (!a) return null;
                                    const config = a.type && typeConfig[a.type] ? typeConfig[a.type] : { icon: '⚙️', color: 'border-l-white/10' };
                                    return (
                                        <motion.div key={a.id} initial={{ opacity: 0, x: -30, height: 0 }}
                                            animate={{ opacity: 1, x: 0, height: 'auto' }} exit={{ opacity: 0 }}
                                            transition={{ type: 'spring', damping: 22 }}
                                            className={`flex items-start gap-3 py-3 px-4 rounded-[14px] hover:bg-white/[0.015] transition-colors border-l-2 ${config.color}`}>
                                            <span className="text-lg mt-0.5">{config.icon}</span>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-[13px] text-white/55">{a.action}</p>
                                                <p className="text-[10px] text-white/18 mt-0.5">{a.time}</p>
                                            </div>
                                            <GlowBadge variant="success" size="sm">Done</GlowBadge>
                                        </motion.div>
                                    );
                                })
                            )}
                        </AnimatePresence>
                    </div>
                </GlassCard>
            </div>
        </PageTransition>
    );
}
