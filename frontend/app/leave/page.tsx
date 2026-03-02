'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Calendar, Send, CheckCircle2, XCircle, ChevronDown, FileText, Shield } from 'lucide-react';
import { submitLeaveRequest } from '../api/client';
import {
  GlassCard,
  GradientButton,
  GlowBadge,
  PageTransition,
  PageHeader,
  EmptyState,
} from '@/components/ui';

interface LeaveDecision {
  employee_name: string;
  status: string;
  reason: string;
  applied_policy_rules: string[];
}

export default function LeavePage() {
  const [formData, setFormData] = useState({
    employeeName: '',
    leaveType: 'Casual',
    startDate: '',
    endDate: '',
    daysRequested: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState<LeaveDecision | null>(null);
  const [showRules, setShowRules] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!formData.employeeName || !formData.startDate || !formData.endDate || !formData.daysRequested) {
      setError('All fields are required');
      return;
    }

    setLoading(true);
    setError('');

    const response = await submitLeaveRequest(
      formData.employeeName,
      formData.leaveType,
      formData.startDate,
      formData.endDate,
      parseInt(formData.daysRequested)
    );

    if (response.error) {
      setError(response.error);
      setResult(null);
    } else {
      setResult((response.data as any)?.decision);
      setFormData({
        employeeName: '',
        leaveType: 'Casual',
        startDate: '',
        endDate: '',
        daysRequested: '',
      });
    }
    setLoading(false);
  }

  return (
    <PageTransition>
      <div className="space-y-8">
        <PageHeader
          title="Leave Management"
          subtitle="AI-powered leave decisions with policy-aware reasoning"
        />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Form */}
          <GlassCard delay={0.1} glowColor="purple">
            <div className="flex items-center gap-3 mb-6">
              <div className="p-2 rounded-xl bg-accent-purple/8">
                <Calendar className="w-4 h-4 text-accent-purple" />
              </div>
              <h3 className="text-[13px] font-semibold text-white/85">Submit Leave Request</h3>
            </div>

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">
                  Employee Name
                </label>
                <input
                  type="text"
                  value={formData.employeeName}
                  onChange={(e) => setFormData({ ...formData, employeeName: e.target.value })}
                  placeholder="Enter employee name"
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">
                  Leave Type
                </label>
                <select
                  value={formData.leaveType}
                  onChange={(e) => setFormData({ ...formData, leaveType: e.target.value })}
                >
                  <option>Casual</option>
                  <option>Sick</option>
                  <option>Annual</option>
                  <option>Maternity</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">
                    Start Date
                  </label>
                  <input
                    type="date"
                    value={formData.startDate}
                    onChange={(e) => setFormData({ ...formData, startDate: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">
                    End Date
                  </label>
                  <input
                    type="date"
                    value={formData.endDate}
                    onChange={(e) => setFormData({ ...formData, endDate: e.target.value })}
                  />
                </div>
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-white/30 mb-2 uppercase tracking-[0.08em]">
                  Days Requested
                </label>
                <input
                  type="number"
                  value={formData.daysRequested}
                  onChange={(e) => setFormData({ ...formData, daysRequested: e.target.value })}
                  min="1"
                  placeholder="Number of days"
                />
              </div>

              <AnimatePresence>
                {error && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="p-3 rounded-[14px] bg-red-500/8 border border-red-500/15 text-[13px] text-red-400"
                  >
                    {error}
                  </motion.div>
                )}
              </AnimatePresence>

              <GradientButton
                type="submit"
                isLoading={loading}
                disabled={loading}
                fullWidth
                size="lg"
              >
                <Send className="w-4 h-4" />
                {loading ? 'Processing...' : 'Submit Request'}
              </GradientButton>
            </form>
          </GlassCard>

          {/* Result */}
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div
                key="result"
                initial={{ opacity: 0, scale: 0.9, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: -20 }}
                transition={{ type: 'spring', damping: 22 }}
              >
                <GlassCard delay={0} animated={false} className={
                  result.status === 'approved'
                    ? 'border-green-500/15 shadow-glow-green'
                    : 'border-red-500/15 shadow-glow-red'
                }>
                  <div className="flex items-center gap-3 mb-6">
                    <div className={`p-2 rounded-xl ${result.status === 'approved' ? 'bg-green-500/8' : 'bg-red-500/8'
                      }`}>
                      {result.status === 'approved'
                        ? <CheckCircle2 className="w-4 h-4 text-green-400" />
                        : <XCircle className="w-4 h-4 text-red-400" />
                      }
                    </div>
                    <h3 className="text-[13px] font-semibold text-white/85">AI Decision</h3>
                  </div>

                  {/* Status Badge */}
                  <motion.div
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ delay: 0.2, type: 'spring' }}
                    className="text-center py-6"
                  >
                    <div className={`inline-flex items-center gap-3 px-6 py-3 rounded-2xl text-lg font-bold font-display ${result.status === 'approved'
                      ? 'bg-green-500/8 text-green-400 border border-green-500/15'
                      : 'bg-red-500/8 text-red-400 border border-red-500/15'
                      }`}>
                      {result.status === 'approved' ? (
                        <><CheckCircle2 className="w-6 h-6" /> APPROVED</>
                      ) : (
                        <><XCircle className="w-6 h-6" /> REJECTED</>
                      )}
                    </div>
                  </motion.div>

                  {/* Reason */}
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                    className="mt-4 p-4 rounded-[14px] bg-white/[0.02] border border-white/4"
                  >
                    <p className="text-[10px] font-semibold text-white/25 mb-2 uppercase tracking-[0.08em]">Reasoning</p>
                    <p className="text-[13px] text-white/65 leading-relaxed">{result.reason}</p>
                  </motion.div>

                  {/* Policy Rules */}
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.4 }}
                    className="mt-4"
                  >
                    <button
                      onClick={() => setShowRules(!showRules)}
                      className="flex items-center gap-2 text-[11px] font-medium text-white/25 hover:text-white/45 transition-colors w-full p-3 rounded-[14px] hover:bg-white/[0.015]"
                    >
                      <Shield className="w-3.5 h-3.5" />
                      <span>Policy Rules Applied ({(result.applied_policy_rules || []).length})</span>
                      <motion.div
                        animate={{ rotate: showRules ? 180 : 0 }}
                        className="ml-auto"
                      >
                        <ChevronDown className="w-3.5 h-3.5" />
                      </motion.div>
                    </button>

                    <AnimatePresence>
                      {showRules && (
                        <motion.div
                          initial={{ height: 0, opacity: 0 }}
                          animate={{ height: 'auto', opacity: 1 }}
                          exit={{ height: 0, opacity: 0 }}
                          className="overflow-hidden"
                        >
                          <div className="space-y-2 pt-2 px-1">
                            {(result.applied_policy_rules || []).map((rule, idx) => (
                              <motion.div
                                key={idx}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.04 }}
                                className="flex items-center gap-2 p-3 rounded-[14px] bg-white/[0.015] border border-white/4"
                              >
                                <div className="w-5 h-5 rounded-lg bg-accent-purple/8 flex items-center justify-center flex-shrink-0">
                                  <span className="text-[9px] font-bold text-accent-purple/60">{idx + 1}</span>
                                </div>
                                <span className="text-[11px] text-white/45 font-mono">{rule}</span>
                              </motion.div>
                            ))}
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </motion.div>
                </GlassCard>
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex items-center justify-center"
              >
                <EmptyState
                  icon={<Calendar className="w-16 h-16" />}
                  title="Submit a Request"
                  description="AI will instantly process your leave request"
                />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </PageTransition>
  );
}
