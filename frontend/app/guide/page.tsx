'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  CheckCircle,
  Users,
  Clipboard,
  Calendar,
  Phone,
  Trophy,
  TrendingUp,
  Download,
  ChevronDown,
  ChevronUp,
  ArrowRight,
  Sparkles,
  Shield,
  AlertTriangle,
  BookOpen,
} from 'lucide-react';
import {
  GlassCard,
  GlowBadge,
  PageTransition,
  PageHeader,
} from '@/components/ui';

interface Step {
  id: number;
  icon: React.ReactNode;
  title: string;
  description: string;
  details: string[];
  color: string;
  iconColor: string;
}

const steps: Step[] = [
  {
    id: 1,
    icon: <Clipboard className="w-6 h-6" />,
    title: 'Upload Job Description',
    description: 'Start by uploading the job description to rank candidates automatically.',
    details: [
      'Paste or upload the job description (JD)',
      'System analyzes required skills and experience',
      'Automatic ranking against all resumes',
      'Get top 10 best-fit candidates'
    ],
    color: 'from-blue-500/15 to-blue-400/5',
    iconColor: 'text-blue-400',
  },
  {
    id: 2,
    icon: <Users className="w-6 h-6" />,
    title: 'Screen & Select Candidates',
    description: 'Review ranked candidates and move qualified ones to next stage.',
    details: [
      'Review candidate profiles and scores',
      'Click "Move to Screened" for qualified candidates',
      'System validates resume quality',
      'Transition: applied → screened'
    ],
    color: 'from-purple-500/15 to-purple-400/5',
    iconColor: 'text-purple-400',
  },
  {
    id: 3,
    icon: <Calendar className="w-6 h-6" />,
    title: 'Schedule Interviews',
    description: 'Schedule interviews with conflict detection and auto-confirmation.',
    details: [
      'Select candidate and interviewer',
      'Choose date and time from available slots',
      'System checks for scheduling conflicts',
      'Transition: screened → interview_scheduled'
    ],
    color: 'from-green-500/15 to-green-400/5',
    iconColor: 'text-green-400',
  },
  {
    id: 4,
    icon: <Phone className="w-6 h-6" />,
    title: 'Conduct Interview',
    description: 'Interview the candidate and record completion in system.',
    details: [
      'Conduct interview with candidate',
      'Mark as "Interview Completed"',
      'System records timestamp',
      'Transition: interview_scheduled → interviewed'
    ],
    color: 'from-amber-500/15 to-amber-400/5',
    iconColor: 'text-amber-400',
  },
  {
    id: 5,
    icon: <Trophy className="w-6 h-6" />,
    title: 'Submit Interview Result',
    description: 'Decide to select or reject — auto-generates questions for selected candidates.',
    details: [
      'Choose "Selected" or "Rejected"',
      'Provide decision reason',
      'If Selected: System generates technical & behavioral questions',
      'If Rejected: Shows red badge, no further transitions allowed'
    ],
    color: 'from-red-500/15 to-red-400/5',
    iconColor: 'text-red-400',
  },
  {
    id: 6,
    icon: <TrendingUp className="w-6 h-6" />,
    title: 'Extend & Accept Offer',
    description: 'Complete the final stages of the hiring process.',
    details: [
      'For selected candidates: Create and extend offer',
      'Candidate reviews and accepts offer',
      'System transitions: offer_extended → offer_accepted',
      'Ready for final hiring'
    ],
    color: 'from-indigo-500/15 to-indigo-400/5',
    iconColor: 'text-indigo-400',
  },
  {
    id: 7,
    icon: <CheckCircle className="w-6 h-6" />,
    title: 'Hire & Onboard',
    description: 'Complete the hiring process and transition to hired status.',
    details: [
      'Final onboarding steps',
      'Mark candidate as "Hired"',
      'Transition to terminal state: hired',
      'No further transitions allowed'
    ],
    color: 'from-emerald-500/15 to-emerald-400/5',
    iconColor: 'text-emerald-400',
  },
  {
    id: 8,
    icon: <Download className="w-6 h-6" />,
    title: 'Export Results',
    description: 'Download complete hiring pipeline data and decision history.',
    details: [
      'Access /export endpoint',
      'Get rankings, leave decisions, schedules',
      'Full pipeline history with timestamps',
      'JSON format for integration'
    ],
    color: 'from-orange-500/15 to-orange-400/5',
    iconColor: 'text-orange-400',
  }
];

const policyFeatures = [
  {
    title: 'Leave Policy Compliance',
    icon: <Clipboard className="w-5 h-5" />,
    color: 'text-accent-purple',
    items: [
      'Automatic leave balance validation',
      'Leave type eligibility checks',
      'Date overlap conflict detection',
      'Policy evidence documentation'
    ]
  },
  {
    title: 'State Machine Enforcement',
    icon: <TrendingUp className="w-5 h-5" />,
    color: 'text-accent-blue',
    items: [
      'Strict state transition validation',
      'No skipping pipeline stages',
      'Terminal states cannot revert',
      'Full transition history logging'
    ]
  },
  {
    title: 'Data Integrity',
    icon: <Shield className="w-5 h-5" />,
    color: 'text-accent-cyan',
    items: [
      'Deterministic processing',
      'JSON schema validation',
      'Error handling with codes',
      'Timestamp for all operations'
    ]
  }
];

interface ExpandedState {
  [key: number]: boolean;
}

const pipelineStages = ['applied', 'screened', 'interview_scheduled', 'interviewed', 'offer_extended', 'offer_accepted', 'hired'];

export default function GuidePage() {
  const [expanded, setExpanded] = useState<ExpandedState>({});

  const toggleExpand = (id: number) => {
    setExpanded(prev => ({
      ...prev,
      [id]: !prev[id]
    }));
  };

  return (
    <PageTransition>
      <div className="space-y-10">
        <PageHeader
          title="System Guide"
          subtitle="Complete step-by-step guide for using the AI HR Agent system"
        />

        {/* Pipeline Flow Diagram */}
        <GlassCard delay={0.1}>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-accent-purple/8">
              <Sparkles className="w-4 h-4 text-accent-purple" />
            </div>
            <h3 className="text-[13px] font-semibold text-white/85">Hiring Pipeline Flow</h3>
          </div>
          <div className="flex items-center justify-between overflow-x-auto pb-2 px-2">
            {pipelineStages.map((state, idx) => (
              <React.Fragment key={state}>
                <motion.div
                  initial={{ scale: 0.8, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ delay: idx * 0.06 }}
                  className="flex flex-col items-center flex-shrink-0"
                >
                  <div className="w-20 h-12 bg-gradient-to-r from-accent-purple/15 to-accent-blue/10 rounded-[12px] flex items-center justify-center font-semibold text-[10px] text-center text-white/65 border border-white/5 px-2">
                    {state.replace(/_/g, '\n')}
                  </div>
                </motion.div>
                {idx < pipelineStages.length - 1 && (
                  <ArrowRight className="w-4 h-4 text-white/15 flex-shrink-0 mx-1" />
                )}
              </React.Fragment>
            ))}
          </div>
          <div className="mt-4 flex justify-center">
            <GlowBadge variant="danger" size="sm">
              <AlertTriangle className="w-3 h-3" />
              Rejection allowed from any non-terminal state
            </GlowBadge>
          </div>
        </GlassCard>

        {/* Steps Grid */}
        <div>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-accent-blue/8">
              <BookOpen className="w-4 h-4 text-accent-blue" />
            </div>
            <h3 className="text-[13px] font-semibold text-white/85">Step-by-Step Process</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {steps.map((step, i) => (
              <motion.div
                key={step.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + i * 0.05 }}
              >
                <GlassCard delay={0} animated={false} hoverable={false} padding="p-0">
                  <div
                    onClick={() => toggleExpand(step.id)}
                    className="p-5 cursor-pointer hover:bg-white/[0.015] transition-colors rounded-t-3xl"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4 flex-1">
                        <div className={`p-2.5 rounded-[14px] bg-gradient-to-br ${step.color} flex-shrink-0`}>
                          <div className={step.iconColor}>{step.icon}</div>
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <GlowBadge variant="purple" size="sm">Step {step.id}</GlowBadge>
                          </div>
                          <h3 className="text-[14px] font-bold font-display text-white/80 mt-1.5">{step.title}</h3>
                          <p className="text-[12px] text-white/30 mt-1.5 leading-relaxed">{step.description}</p>
                        </div>
                      </div>
                      <motion.div
                        animate={{ rotate: expanded[step.id] ? 180 : 0 }}
                        className="ml-3 flex-shrink-0 mt-1"
                      >
                        <ChevronDown className="w-4 h-4 text-white/20" />
                      </motion.div>
                    </div>
                  </div>

                  <AnimatePresence>
                    {expanded[step.id] && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="overflow-hidden"
                      >
                        <div className="px-5 pb-5 pt-2" style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
                          <div className="space-y-2.5">
                            {step.details.map((detail, idx) => (
                              <motion.div
                                key={idx}
                                initial={{ opacity: 0, x: -10 }}
                                animate={{ opacity: 1, x: 0 }}
                                transition={{ delay: idx * 0.05 }}
                                className="flex items-start gap-3"
                              >
                                <CheckCircle className="w-4 h-4 text-green-400/60 flex-shrink-0 mt-0.5" />
                                <span className="text-[12px] text-white/45 leading-relaxed">{detail}</span>
                              </motion.div>
                            ))}
                          </div>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Key Features */}
        <div>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-accent-cyan/8">
              <Shield className="w-4 h-4 text-accent-cyan" />
            </div>
            <h3 className="text-[13px] font-semibold text-white/85">Key Features</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {policyFeatures.map((feature, idx) => (
              <motion.div
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + idx * 0.08 }}
              >
                <GlassCard delay={0} animated={false} glowColor="purple">
                  <div className={`mb-4 ${feature.color}`}>{feature.icon}</div>
                  <h3 className="text-[14px] font-bold font-display text-white/80 mb-4">{feature.title}</h3>
                  <div className="space-y-2.5">
                    {feature.items.map((item, itemIdx) => (
                      <div key={itemIdx} className="flex items-start gap-2.5">
                        <CheckCircle className="w-3.5 h-3.5 text-green-400/50 flex-shrink-0 mt-0.5" />
                        <span className="text-[12px] text-white/40 leading-relaxed">{item}</span>
                      </div>
                    ))}
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>

        {/* Important Rules */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <GlassCard delay={0.2} className="border-red-500/10">
            <h3 className="text-[14px] font-bold font-display text-red-400 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              What NOT to do
            </h3>
            <div className="space-y-2.5">
              {[
                'Skip pipeline stages (e.g., go directly from screened to hired)',
                'Try to modify hired or rejected candidates',
                'Submit interview result twice for same candidate',
                'Use invalid decision values (only "selected" or "rejected")'
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-2.5">
                  <span className="text-red-400/50 text-[12px] mt-0.5">✗</span>
                  <span className="text-[12px] text-white/40 leading-relaxed">{item}</span>
                </div>
              ))}
            </div>
          </GlassCard>

          <GlassCard delay={0.25} className="border-green-500/10">
            <h3 className="text-[14px] font-bold font-display text-green-400 mb-4 flex items-center gap-2">
              <CheckCircle className="w-4 h-4" />
              Best Practices
            </h3>
            <div className="space-y-2.5">
              {[
                'Always provide a reason for decisions',
                'Review candidate scores before screening',
                'Schedule interviews only for screened candidates',
                'Export results regularly for backup'
              ].map((item, i) => (
                <div key={i} className="flex items-start gap-2.5">
                  <CheckCircle className="w-3.5 h-3.5 text-green-400/50 flex-shrink-0 mt-0.5" />
                  <span className="text-[12px] text-white/40 leading-relaxed">{item}</span>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>

        {/* Interview Decision */}
        <GlassCard delay={0.3}>
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 rounded-xl bg-accent-purple/8">
              <Trophy className="w-4 h-4 text-accent-purple" />
            </div>
            <h3 className="text-[13px] font-semibold text-white/85">Interview Decision Flow</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-5 rounded-[14px] bg-green-500/4 border border-green-500/10">
              <h4 className="text-[13px] font-bold font-display text-green-400 mb-4">When SELECTED</h4>
              <div className="space-y-3">
                {[
                  'Candidate state moves to: offer_extended',
                  'System automatically generates interview questions',
                  'Frontend shows technical & behavioral questions',
                  'Green badge indicates successful decision'
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <span className="text-green-400/60 font-bold text-[13px]">{i + 1}.</span>
                    <span className="text-[12px] text-white/45 leading-relaxed">{item}</span>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-5 rounded-[14px] bg-red-500/4 border border-red-500/10">
              <h4 className="text-[13px] font-bold font-display text-red-400 mb-4">When REJECTED</h4>
              <div className="space-y-3">
                {[
                  'Candidate state moves to: rejected',
                  'No interview questions are generated',
                  'Rejection reason is displayed and stored',
                  'Red badge shown — no further transitions allowed'
                ].map((item, i) => (
                  <div key={i} className="flex items-start gap-3">
                    <span className="text-red-400/60 font-bold text-[13px]">{i + 1}.</span>
                    <span className="text-[12px] text-white/45 leading-relaxed">{item}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </GlassCard>

        {/* Help CTA */}
        <GlassCard delay={0.35} variant="gradient-border">
          <div className="text-center py-4">
            <h2 className="text-xl font-bold font-display text-white/85 mb-2">Need Help?</h2>
            <p className="text-[13px] text-white/35 mb-4 max-w-lg mx-auto">
              For detailed API documentation, visit the <code className="px-2 py-0.5 rounded-lg bg-white/5 text-accent-blue text-[11px]">/docs</code> endpoint
            </p>
            <div className="flex flex-wrap gap-4 justify-center text-[12px] text-white/30">
              <span>📧 Check API docs for questions</span>
              <span>🔍 Review pipeline diagram above</span>
              <span>📊 Use Export Results on dashboard</span>
            </div>
          </div>
        </GlassCard>
      </div>
    </PageTransition>
  );
}
