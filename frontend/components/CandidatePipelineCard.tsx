'use client';

import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { usePipelineState } from '@/hooks/usePipelineState';
import { InterviewDecisionModal } from './InterviewDecisionModal';
import { InterviewQuestionsModal } from './InterviewQuestionsModal';
import { CandidateRejectionBadge } from './CandidateRejectionBadge';
import { ChevronRight, AlertCircle, CheckCircle } from 'lucide-react';

interface CandidatePipelineCardProps {
  candidateId: string;
  name: string;
  score: number;
  email?: string;
  phone?: string;
}

const PIPELINE_STATES = [
  { key: 'applied', label: 'Applied', color: 'slate' },
  { key: 'screened', label: 'Screened', color: 'blue' },
  { key: 'interview_scheduled', label: 'Scheduled', color: 'cyan' },
  { key: 'interviewed', label: 'Interviewed', color: 'purple' },
  { key: 'offer_extended', label: 'Offer Extended', color: 'amber' },
  { key: 'offer_accepted', label: 'Offer Accepted', color: 'emerald' },
  { key: 'hired', label: 'Hired', color: 'green' },
];

export function CandidatePipelineCard({
  candidateId,
  name,
  score,
  email,
  phone,
}: CandidatePipelineCardProps) {
  const { state, history, loading, transitionTo } = usePipelineState(candidateId);
  const [showInterviewDecision, setShowInterviewDecision] = useState(false);
  const [showQuestions, setShowQuestions] = useState(false);
  const [questions, setQuestions] = useState<{
    technical: string[];
    behavioral: string[];
  } | null>(null);
  const [rejectionReason, setRejectionReason] = useState<string | null>(null);
  const [transitioning, setTransitioning] = useState(false);

  const stateIndex = PIPELINE_STATES.findIndex((s) => s.key === state);
  const isTerminal = state === 'hired' || state === 'rejected';

  const handleInterviewDecision = async (result: any) => {
    if (result.new_state === 'offer_extended' && result.questions_generated) {
      setQuestions({
        technical: result.technical_questions || [],
        behavioral: result.behavioral_questions || [],
      });
      setShowQuestions(true);
    } else if (result.new_state === 'rejected') {
      setRejectionReason(result.rejection_reason);
    }
  };

  const handleNextState = async () => {
    if (stateIndex >= PIPELINE_STATES.length - 1) return;

    const nextState = PIPELINE_STATES[stateIndex + 1].key;
    setTransitioning(true);

    const result = await transitionTo(nextState, `Moved to ${nextState}`);

    setTransitioning(false);

    if (!result.success && result.error) {
      alert(`Transition failed: ${result.error}`);
    }
  };

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-slate-900 rounded-2xl p-6 border border-slate-700 shadow-lg hover:shadow-xl transition"
      >
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div className="flex-1">
            <h3 className="text-xl font-bold text-white mb-1">{name}</h3>
            <p className="text-sm text-slate-400">ID: {candidateId}</p>
            {email && <p className="text-sm text-slate-500">{email}</p>}
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold text-accent-purple">
              {(score * 100).toFixed(0)}%
            </div>
            <p className="text-xs text-slate-500">Match Score</p>
          </div>
        </div>

        {/* Status Badge */}
        {rejectionReason ? (
          <div className="mb-6">
            <CandidateRejectionBadge rejectionReason={rejectionReason} />
          </div>
        ) : (
          <div className="mb-6 p-3 bg-slate-800/50 rounded-lg border border-slate-700">
            <p className="text-sm font-medium text-slate-300">
              Current Status:{' '}
              <span className="text-accent-purple font-bold capitalize">
                {state.replace(/_/g, ' ')}
              </span>
            </p>
          </div>
        )}

        {/* Pipeline Progress */}
        <div className="mb-6">
          <div className="flex justify-between text-xs text-slate-500 mb-2 px-1">
            {PIPELINE_STATES.map((s) => (
              <span key={s.key} title={s.label} className="font-medium">
                {s.label.substring(0, 3)}
              </span>
            ))}
          </div>
          <div className="w-full bg-slate-800 rounded-full h-2 overflow-hidden">
            <motion.div
              initial={{ width: 0 }}
              animate={{
                width: `${((stateIndex + 1) / PIPELINE_STATES.length) * 100}%`,
              }}
              transition={{ type: 'spring', damping: 20 }}
              className="h-full bg-gradient-to-r from-accent-purple to-accent-blue rounded-full"
            />
          </div>
        </div>

        {/* History Timeline */}
        {history.length > 1 && (
          <div className="mb-6 p-3 bg-slate-800/30 rounded-lg border border-slate-700/50">
            <p className="text-xs font-semibold text-slate-400 mb-2 uppercase">History</p>
            <div className="space-y-1 max-h-24 overflow-y-auto text-xs text-slate-500">
              {history.map((entry, idx) => (
                <div key={idx} className="flex justify-between">
                  <span className="capitalize">{entry.state.replace(/_/g, ' ')}</span>
                  <span className="text-slate-600">
                    {new Date(entry.timestamp).toLocaleDateString()}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-3">
          {state === 'interviewed' && !isTerminal && !rejectionReason && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowInterviewDecision(true)}
              className="flex-1 py-3 px-4 bg-green-500/20 hover:bg-green-500/30 border border-green-500/50 text-green-200 rounded-lg font-medium transition flex items-center justify-center gap-2"
            >
              <CheckCircle className="w-4 h-4" />
              Submit Decision
            </motion.button>
          )}

          {!isTerminal && !rejectionReason && stateIndex < PIPELINE_STATES.length - 1 && (
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={handleNextState}
              disabled={transitioning || loading}
              className="flex-1 py-3 px-4 bg-accent-purple hover:bg-accent-purple/80 text-white rounded-lg font-medium disabled:opacity-50 transition flex items-center justify-center gap-2"
            >
              {transitioning ? 'Moving...' : 'Next'}
              {!transitioning && <ChevronRight className="w-4 h-4" />}
            </motion.button>
          )}

          {isTerminal && (
            <div className="flex-1 py-3 px-4 rounded-lg bg-slate-800 border border-slate-700 text-slate-400 font-medium text-center">
              Terminal State
            </div>
          )}
        </div>
      </motion.div>

      {/* Modals */}
      {showInterviewDecision && (
        <InterviewDecisionModal
          candidateId={candidateId}
          candidateName={name}
          onClose={() => setShowInterviewDecision(false)}
          onDecisionSubmitted={handleInterviewDecision}
        />
      )}

      {showQuestions && questions && (
        <InterviewQuestionsModal
          candidateName={name}
          technicalQuestions={questions.technical}
          behavioralQuestions={questions.behavioral}
          onClose={() => setShowQuestions(false)}
        />
      )}
    </>
  );
}
