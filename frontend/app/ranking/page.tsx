'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Users, Trophy, Sparkles, X, Eye } from 'lucide-react';
import {
  GlassCard,
  GradientButton,
  GlowBadge,
  PageTransition,
  PageHeader,
  EmptyState,
} from '@/components/ui';
import { AILoader } from '@/components/ui/ShimmerLoader';

interface Candidate {
  rank: number;
  candidate_id: string;
  name: string;
  score: number;
  normalized_score: number;
  reasoning: Record<string, string>;
  target_job: string;
}

export default function RankingPage() {
  const [jdText, setJdText] = useState('');
  const [results, setResults] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSubmitted, setHasSubmitted] = useState(false);
  const [selectedCandidate, setSelectedCandidate] = useState<Candidate | null>(null);

  const handleRank = async () => {
    if (!jdText.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/rank', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ jd_text: jdText, top_k: 10 }),
      });
      if (response.ok) {
        const data = await response.json();
        setResults(data.candidates);
        setHasSubmitted(true);
      }
    } catch (error) {
      console.error('Ranking failed:', error);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-400';
    if (score >= 0.6) return 'text-accent-blue-light';
    if (score >= 0.4) return 'text-amber-400';
    return 'text-red-400';
  };

  const getScoreBadge = (score: number): 'success' | 'info' | 'warning' | 'danger' => {
    if (score >= 0.8) return 'success';
    if (score >= 0.6) return 'info';
    if (score >= 0.4) return 'warning';
    return 'danger';
  };

  const getScoreBarGradient = (score: number) => {
    if (score >= 0.8) return 'from-green-500 to-emerald-400';
    if (score >= 0.6) return 'from-accent-purple to-accent-blue';
    if (score >= 0.4) return 'from-amber-500 to-orange-400';
    return 'from-red-500 to-red-400';
  };

  return (
    <PageTransition>
      <div className="space-y-8">
        <PageHeader
          title="Resume Ranking"
          subtitle="AI-powered candidate matching with explainable scoring"
        />

        {/* Input */}
        <GlassCard delay={0.1} glowColor="purple">
          <div className="flex items-center gap-3 mb-5">
            <div className="p-2 rounded-xl bg-accent-purple/8">
              <Sparkles className="w-4 h-4 text-accent-purple" />
            </div>
            <div>
              <h3 className="text-[13px] font-semibold text-white/85">Job Description</h3>
              <p className="text-[11px] text-white/25">Paste the JD to match against your resume database</p>
            </div>
          </div>
          <div className="relative">
            <textarea
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              placeholder="Enter job requirements, skills, responsibilities..."
              rows={5}
              className="w-full mb-1 resize-none"
            />
            <p className="text-[10px] text-white/15 text-right mb-4">{jdText.length} characters</p>
          </div>
          <GradientButton
            onClick={handleRank}
            isLoading={loading}
            disabled={loading || !jdText.trim()}
            size="lg"
          >
            <Trophy className="w-5 h-5" />
            {loading ? 'Analyzing...' : 'Rank Resumes'}
          </GradientButton>
        </GlassCard>

        {/* Loading */}
        {loading && <AILoader message="Running AI analysis on resume database..." />}

        {/* Results */}
        <AnimatePresence>
          {hasSubmitted && !loading && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
            >
              <GlassCard delay={0} padding="p-0">
                <div className="card-header">
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-xl bg-accent-blue/8">
                      <Users className="w-4 h-4 text-accent-blue" />
                    </div>
                    <div>
                      <h3 className="text-[13px] font-semibold text-white/85">Ranking Results</h3>
                      <p className="text-[11px] text-white/25">{results.length} top candidates matched</p>
                    </div>
                  </div>
                  <GlowBadge variant="purple" pulse>AI Scored</GlowBadge>
                </div>

                {/* Results Table */}
                <div className="overflow-x-auto p-2">
                  <table>
                    <thead>
                      <tr>
                        <th>Rank</th>
                        <th>Candidate ID</th>
                        <th>Name</th>
                        <th>Target Role</th>
                        <th>Match Score</th>
                        <th>Confidence</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.map((candidate, index) => (
                        <motion.tr
                          key={candidate.candidate_id}
                          initial={{ opacity: 0, x: -20 }}
                          animate={{ opacity: 1, x: 0 }}
                          transition={{ delay: index * 0.05 }}
                          className="group hover:bg-white/[0.015]"
                        >
                          <td>
                            <div className="w-8 h-8 rounded-[10px] bg-gradient-to-br from-accent-purple/15 to-accent-blue/8 flex items-center justify-center text-[13px] font-bold text-white/75 ring-1 ring-white/5">
                              {candidate.rank}
                            </div>
                          </td>
                          <td>
                            <span className="font-mono text-[13px] text-accent-blue/80">{candidate.candidate_id}</span>
                          </td>
                          <td>
                            <span
                              className="font-semibold text-[13px] text-white/75 cursor-pointer hover:text-white transition-colors"
                              onClick={() => setSelectedCandidate(candidate)}
                            >
                              {candidate.name}
                            </span>
                          </td>
                          <td>
                            <span className="text-[13px] text-white/35">{candidate.target_job}</span>
                          </td>
                          <td>
                            <div className="flex items-center gap-2.5">
                              <div className="w-20 h-1.5 rounded-full bg-white/5 overflow-hidden">
                                <motion.div
                                  initial={{ width: 0 }}
                                  animate={{ width: `${candidate.normalized_score * 100}%` }}
                                  transition={{ duration: 0.8, delay: index * 0.05 }}
                                  className={`h-full rounded-full bg-gradient-to-r ${getScoreBarGradient(candidate.normalized_score)}`}
                                />
                              </div>
                              <span className={`text-[13px] font-bold ${getScoreColor(candidate.normalized_score)}`}>
                                {(candidate.normalized_score * 100).toFixed(0)}%
                              </span>
                            </div>
                          </td>
                          <td>
                            <GlowBadge variant={getScoreBadge(candidate.normalized_score)} size="sm">
                              {candidate.normalized_score >= 0.8 ? 'High' : candidate.normalized_score >= 0.6 ? 'Medium' : 'Low'}
                            </GlowBadge>
                          </td>
                          <td>
                            <button
                              onClick={() => setSelectedCandidate(candidate)}
                              className="p-1.5 hover:bg-white/5 rounded-lg transition-colors"
                              title="View details"
                            >
                              <Eye className="w-4 h-4 text-white/30 hover:text-accent-purple transition-colors" />
                            </button>
                          </td>
                        </motion.tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </GlassCard>
            </motion.div>
          )}
        </AnimatePresence>

        {/* SHAP Explanation Modal */}
        <AnimatePresence>
          {selectedCandidate && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
              onClick={() => setSelectedCandidate(null)}
            >
              <motion.div
                initial={{ opacity: 0, scale: 0.9, y: 30 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.9, y: 30 }}
                transition={{ type: 'spring', damping: 25 }}
                className="glass-card p-6 max-w-lg w-full max-h-[80vh] overflow-y-auto"
                onClick={(e) => e.stopPropagation()}
              >
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <h3 className="text-lg font-bold font-display text-white">{selectedCandidate.name}</h3>
                    <p className="text-[12px] text-white/25 mt-0.5">SHAP Explanation — AI Reasoning</p>
                  </div>
                  <button
                    onClick={() => setSelectedCandidate(null)}
                    className="p-1.5 rounded-lg hover:bg-white/5 transition-colors"
                  >
                    <X className="w-5 h-5 text-white/35" />
                  </button>
                </div>

                {/* Score */}
                <div className="mb-6 p-5 rounded-[14px] bg-gradient-to-r from-accent-purple/8 to-accent-blue/4 border border-accent-purple/10">
                  <div className="flex items-center justify-between">
                    <span className="text-[13px] text-white/45">Overall Match</span>
                    <span className="text-2xl font-bold font-display text-white">
                      {(selectedCandidate.normalized_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div className="mt-3 h-2 rounded-full bg-white/5 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${selectedCandidate.normalized_score * 100}%` }}
                      transition={{ duration: 1, ease: 'easeOut' }}
                      className={`h-full rounded-full bg-gradient-to-r ${getScoreBarGradient(selectedCandidate.normalized_score)}`}
                    />
                  </div>
                </div>

                {/* Reasoning */}
                <div className="space-y-2.5">
                  <h4 className="text-[10px] font-semibold text-white/30 uppercase tracking-[0.08em]">Feature Contributions</h4>
                  {Object.entries(selectedCandidate.reasoning).map(([key, value], i) => (
                    <motion.div
                      key={key}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.06 }}
                      className="p-3.5 rounded-[14px] bg-white/[0.02] border border-white/4"
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[13px] font-medium text-white/55 capitalize">
                          {key.replace(/_/g, ' ')}
                        </span>
                      </div>
                      <p className="text-[12px] text-white/25">{value}</p>
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Empty State */}
        {!loading && !hasSubmitted && (
          <EmptyState
            icon={<Trophy className="w-16 h-16" />}
            title="Start Ranking"
            description="Enter a job description to match against your resume database"
          />
        )}
      </div>
    </PageTransition>
  );
}
