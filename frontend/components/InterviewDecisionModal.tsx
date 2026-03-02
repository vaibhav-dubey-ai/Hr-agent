'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface InterviewDecisionModalProps {
  candidateId: string;
  candidateName: string;
  onClose: () => void;
  onDecisionSubmitted: (result: any) => void;
}

export function InterviewDecisionModal({
  candidateId,
  candidateName,
  onClose,
  onDecisionSubmitted,
}: InterviewDecisionModalProps) {
  const [decision, setDecision] = useState<'selected' | 'rejected' | null>(null);
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!decision || !reason.trim()) {
      setError('Please select a decision and provide a reason');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/interview-result', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          candidate_id: candidateId,
          decision,
          reason: reason.trim(),
        }),
      });

      const data = await response.json();

      if (data.status !== 'success') {
        setError(data.message || 'Failed to submit interview result');
        setLoading(false);
        return;
      }

      onDecisionSubmitted(data);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Network error');
      setLoading(false);
    }
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ type: 'spring', damping: 25 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-slate-900 rounded-2xl shadow-2xl max-w-md w-full p-8 border border-slate-700"
        >
          <h2 className="text-2xl font-bold mb-2 text-white">Interview Decision</h2>
          <p className="text-sm text-slate-400 mb-6">{candidateName}</p>

          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="mb-4 p-3 bg-red-500/10 border border-red-500/30 text-red-200 rounded-lg flex gap-2 items-start"
            >
              <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
              <span className="text-sm">{error}</span>
            </motion.div>
          )}

          <div className="space-y-4 mb-6">
            {/* Decision Selection */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-3">
                Decision
              </label>
              <div className="flex gap-3">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setDecision('selected')}
                  className={`flex-1 py-3 px-4 rounded-xl font-medium transition flex items-center justify-center gap-2 ${
                    decision === 'selected'
                      ? 'bg-green-500/20 border border-green-500/50 text-green-200'
                      : 'bg-slate-800 border border-slate-700 text-slate-400 hover:border-slate-600'
                  }`}
                >
                  <CheckCircle className="w-4 h-4" />
                  Selected
                </motion.button>
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={() => setDecision('rejected')}
                  className={`flex-1 py-3 px-4 rounded-xl font-medium transition flex items-center justify-center gap-2 ${
                    decision === 'rejected'
                      ? 'bg-red-500/20 border border-red-500/50 text-red-200'
                      : 'bg-slate-800 border border-slate-700 text-slate-400 hover:border-slate-600'
                  }`}
                >
                  <XCircle className="w-4 h-4" />
                  Rejected
                </motion.button>
              </div>
            </div>

            {/* Reason */}
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Reason
              </label>
              <textarea
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                placeholder={
                  decision === 'selected'
                    ? 'e.g., Excellent technical skills, great culture fit'
                    : 'e.g., Does not meet technical requirements'
                }
                className="w-full p-3 rounded-lg bg-slate-800 border border-slate-700 text-white placeholder-slate-500 focus:outline-none focus:border-accent-purple focus:ring-1 focus:ring-accent-purple"
                rows={4}
              />
            </div>
          </div>

          <div className="flex gap-3">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onClose}
              disabled={loading}
              className="flex-1 py-3 px-4 rounded-lg bg-slate-800 hover:bg-slate-700 text-white font-medium disabled:opacity-50 transition"
            >
              Cancel
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleSubmit}
              disabled={loading}
              className="flex-1 py-3 px-4 rounded-lg bg-accent-purple hover:bg-accent-purple/80 text-white font-medium disabled:opacity-50 transition"
            >
              {loading ? 'Submitting...' : 'Submit'}
            </motion.button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
