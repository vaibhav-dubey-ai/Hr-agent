'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Clock, Plus, X, Check, AlertTriangle, Calendar } from 'lucide-react';
import { registerInterviewerAvailability, scheduleInterview } from '../api/client';
import { GlassCard, GradientButton, GlowBadge, PageTransition, PageHeader, EmptyState } from '@/components/ui';

interface ScheduleResult {
  candidate_id: string; interviewer_id: string; status: string;
  reason: string; scheduled_date?: string; scheduled_time?: string;
}

export default function SchedulingPage() {
  const [tab, setTab] = useState('availability');
  const [availForm, setAvailForm] = useState({ interviewerId: '', dates: [] as string[], times: [] as string[] });
  const [schedForm, setSchedForm] = useState({ candidateId: '', interviewerId: '', date: '', time: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<ScheduleResult | null>(null);
  const [success, setSuccess] = useState('');

  function addDate() {
    const el = document.querySelector('#newDate') as HTMLInputElement;
    if (el?.value && !availForm.dates.includes(el.value)) {
      setAvailForm({ ...availForm, dates: [...availForm.dates, el.value] });
      el.value = '';
    }
  }
  function addTime() {
    const el = document.querySelector('#newTime') as HTMLInputElement;
    if (el?.value && !availForm.times.includes(el.value)) {
      setAvailForm({ ...availForm, times: [...availForm.times, el.value] });
      el.value = '';
    }
  }

  async function handleAvailability(e: React.FormEvent) {
    e.preventDefault();
    if (!availForm.interviewerId || !availForm.dates.length || !availForm.times.length) { setError('Fill all fields'); return; }
    setLoading(true); setError('');
    const r = await registerInterviewerAvailability(availForm.interviewerId, availForm.dates, availForm.times);
    if (r.error) { setError(r.error); }
    else { setSuccess('Availability registered!'); setAvailForm({ interviewerId: '', dates: [], times: [] }); setTimeout(() => setSuccess(''), 3000); }
    setLoading(false);
  }

  async function handleSchedule(e: React.FormEvent) {
    e.preventDefault();
    if (!schedForm.candidateId || !schedForm.interviewerId || !schedForm.date || !schedForm.time) { setError('All fields required'); return; }
    setLoading(true); setError('');
    const r = await scheduleInterview(schedForm.candidateId, schedForm.interviewerId, schedForm.date, schedForm.time);
    if (r.error) { setError(r.error); setResult(null); }
    else { setResult((r.data as any)?.schedule); setSchedForm({ candidateId: '', interviewerId: '', date: '', time: '' }); }
    setLoading(false);
  }

  return (
    <PageTransition>
      <div className="space-y-8">
        <PageHeader title="Interview Scheduler" subtitle="Smart scheduling with conflict detection" />

        {/* Tabs */}
        <div className="flex gap-1.5 p-1.5 rounded-[16px] glass-card-static w-fit">
          {[{ id: 'availability', label: 'Availability', icon: Clock }, { id: 'schedule', label: 'Schedule', icon: Calendar }].map((t) => {
            const Icon = t.icon;
            const isActive = tab === t.id;
            return (
              <motion.button key={t.id} whileTap={{ scale: 0.95 }}
                onClick={() => { setTab(t.id); setError(''); }}
                className={`relative px-5 py-2.5 rounded-[12px] text-[13px] font-medium flex items-center gap-2 transition-all ${isActive ? 'text-white' : 'text-white/35 hover:text-white/55'}`}>
                {isActive && (
                  <motion.div
                    layoutId="tabActive"
                    className="absolute inset-0 rounded-[12px] bg-gradient-to-r from-accent-purple to-accent-blue shadow-glow-sm"
                    transition={{ type: 'spring', damping: 25, stiffness: 300 }}
                  />
                )}
                <Icon className="w-4 h-4 relative z-10" />
                <span className="relative z-10">{t.label}</span>
              </motion.button>
            );
          })}
        </div>

        {/* Success Toast */}
        <AnimatePresence>
          {success && (
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -10 }}
              className="p-3 rounded-[14px] bg-green-500/8 border border-green-500/15 text-[13px] text-green-400 flex items-center gap-2">
              <Check className="w-4 h-4" />{success}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Availability Tab */}
        {tab === 'availability' && (
          <GlassCard delay={0.1} glowColor="purple" className="max-w-2xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-xl bg-accent-purple/8"><Clock className="w-4 h-4 text-accent-purple" /></div>
              <h3 className="text-[13px] font-semibold text-white/85">Register Availability</h3>
            </div>
            <form onSubmit={handleAvailability} className="space-y-5">
              <div>
                <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">Interviewer ID</label>
                <input type="text" value={availForm.interviewerId} onChange={(e) => setAvailForm({ ...availForm, interviewerId: e.target.value })} placeholder="e.g., interviewer_001" />
              </div>
              <div>
                <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">Available Dates</label>
                <div className="flex gap-2 mb-3">
                  <input id="newDate" type="date" className="flex-1" />
                  <GradientButton variant="ghost" onClick={addDate} type="button"><Plus className="w-4 h-4" />Add</GradientButton>
                </div>
                <div className="flex flex-wrap gap-2">
                  {availForm.dates.map((d, i) => (
                    <motion.span key={i} initial={{ scale: 0 }} animate={{ scale: 1 }} className="glow-badge glow-badge-purple flex items-center gap-1.5">
                      {d}
                      <button type="button" onClick={() => setAvailForm({ ...availForm, dates: availForm.dates.filter((_, j) => j !== i) })} className="hover:text-white"><X className="w-3 h-3" /></button>
                    </motion.span>
                  ))}
                </div>
              </div>
              <div>
                <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">Available Times</label>
                <div className="flex gap-2 mb-3">
                  <input id="newTime" type="time" className="flex-1" />
                  <GradientButton variant="ghost" onClick={addTime} type="button"><Plus className="w-4 h-4" />Add</GradientButton>
                </div>
                <div className="flex flex-wrap gap-2">
                  {availForm.times.map((t, i) => (
                    <motion.span key={i} initial={{ scale: 0 }} animate={{ scale: 1 }} className="glow-badge glow-badge-info flex items-center gap-1.5">
                      {t}
                      <button type="button" onClick={() => setAvailForm({ ...availForm, times: availForm.times.filter((_, j) => j !== i) })} className="hover:text-white"><X className="w-3 h-3" /></button>
                    </motion.span>
                  ))}
                </div>
              </div>
              <AnimatePresence>{error && <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="p-3 rounded-[14px] bg-red-500/8 border border-red-500/15 text-[13px] text-red-400">{error}</motion.div>}</AnimatePresence>
              <GradientButton type="submit" isLoading={loading} fullWidth size="lg"><Check className="w-4 h-4" />Register</GradientButton>
            </form>
          </GlassCard>
        )}

        {/* Schedule Tab */}
        {tab === 'schedule' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <GlassCard delay={0.1} glowColor="blue">
              <div className="flex items-center gap-3 mb-6">
                <div className="p-2 rounded-xl bg-accent-blue/8"><Sparkles className="w-4 h-4 text-accent-blue" /></div>
                <h3 className="text-[13px] font-semibold text-white/85">Schedule Interview</h3>
              </div>
              <form onSubmit={handleSchedule} className="space-y-5">
                <div>
                  <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">Candidate ID</label>
                  <input type="text" value={schedForm.candidateId} onChange={(e) => setSchedForm({ ...schedForm, candidateId: e.target.value })} placeholder="e.g., candidate_5" />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">Interviewer ID</label>
                  <input type="text" value={schedForm.interviewerId} onChange={(e) => setSchedForm({ ...schedForm, interviewerId: e.target.value })} placeholder="e.g., interviewer_001" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">Date</label>
                    <input type="date" value={schedForm.date} onChange={(e) => setSchedForm({ ...schedForm, date: e.target.value })} />
                  </div>
                  <div>
                    <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">Time</label>
                    <input type="time" value={schedForm.time} onChange={(e) => setSchedForm({ ...schedForm, time: e.target.value })} />
                  </div>
                </div>
                <AnimatePresence>{error && <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} className="p-3 rounded-[14px] bg-red-500/8 border border-red-500/15 text-[13px] text-red-400 flex items-center gap-2"><AlertTriangle className="w-4 h-4" />{error}</motion.div>}</AnimatePresence>
                <GradientButton type="submit" isLoading={loading} fullWidth size="lg"><Sparkles className="w-4 h-4" />Schedule</GradientButton>
              </form>
            </GlassCard>

            <AnimatePresence mode="wait">
              {result ? (
                <motion.div key="res" initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}>
                  <GlassCard delay={0} animated={false} className={result.status === 'success' ? 'border-green-500/15 shadow-glow-green' : 'border-red-500/15 shadow-glow-red'}>
                    <div className="flex items-center gap-3 mb-6">
                      <div className={`p-2 rounded-xl ${result.status === 'success' ? 'bg-green-500/8' : 'bg-red-500/8'}`}>
                        {result.status === 'success' ? <Check className="w-4 h-4 text-green-400" /> : <AlertTriangle className="w-4 h-4 text-red-400" />}
                      </div>
                      <h3 className="text-[13px] font-semibold text-white/85">Result</h3>
                    </div>
                    <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring' }} className="text-center py-4">
                      <GlowBadge variant={result.status === 'success' ? 'success' : 'danger'} pulse>
                        {result.status === 'success' ? '✓ SCHEDULED' : '✗ CONFLICT'}
                      </GlowBadge>
                    </motion.div>
                    <div className="mt-4 p-4 rounded-[14px] bg-white/[0.015] border border-white/4">
                      <p className="text-[10px] font-semibold text-white/25 mb-1 uppercase tracking-[0.08em]">Details</p>
                      <p className="text-[13px] text-white/55">{result.reason}</p>
                      {result.scheduled_date && (
                        <p className="text-[13px] font-semibold text-white/75 mt-2">{result.scheduled_date} at {result.scheduled_time}</p>
                      )}
                    </div>
                  </GlassCard>
                </motion.div>
              ) : (
                <motion.div key="empty" className="flex items-center justify-center">
                  <EmptyState
                    icon={<Sparkles className="w-16 h-16" />}
                    title="Schedule an Interview"
                    description="Results will appear here"
                  />
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        )}
      </div>
    </PageTransition>
  );
}
