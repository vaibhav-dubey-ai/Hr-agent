'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle, Lightbulb, MessageSquare, X } from 'lucide-react';

interface InterviewQuestionsModalProps {
  candidateName: string;
  technicalQuestions: string[];
  behavioralQuestions: string[];
  onClose: () => void;
}

export function InterviewQuestionsModal({
  candidateName,
  technicalQuestions,
  behavioralQuestions,
  onClose,
}: InterviewQuestionsModalProps) {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, x: -20 },
    visible: { opacity: 1, x: 0 },
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50 p-4"
        onClick={onClose}
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          transition={{ type: 'spring', damping: 25 }}
          onClick={(e) => e.stopPropagation()}
          className="bg-slate-900 rounded-2xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-y-auto border border-slate-700"
        >
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="sticky top-0 bg-slate-900 px-8 py-6 border-b border-slate-700 flex justify-between items-start gap-4 z-10"
          >
            <div>
              <h2 className="text-2xl font-bold text-white flex items-center gap-3 mb-2">
                <CheckCircle className="w-6 h-6 text-green-400" />
                Interview Questions
              </h2>
              <p className="text-sm text-slate-400">Selected Candidate: {candidateName}</p>
            </div>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              onClick={onClose}
              className="p-2 hover:bg-slate-800 rounded-lg transition text-slate-400 hover:text-white"
            >
              <X className="w-5 h-5" />
            </motion.button>
          </motion.div>

          {/* Content */}
          <div className="px-8 py-6 space-y-8">
            {/* Technical Questions */}
            <motion.section variants={containerVariants} initial="hidden" animate="visible">
              <div className="flex items-center gap-3 mb-4">
                <Lightbulb className="w-5 h-5 text-blue-400" />
                <h3 className="text-lg font-bold text-white">
                  Technical Questions ({technicalQuestions.length})
                </h3>
              </div>
              <div className="space-y-3">
                {technicalQuestions.map((question, idx) => (
                  <motion.div
                    key={idx}
                    variants={itemVariants}
                    className="flex gap-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-blue-500/30 transition"
                  >
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500/20 border border-blue-500/50 flex items-center justify-center text-xs font-bold text-blue-200">
                      {idx + 1}
                    </span>
                    <p className="text-sm text-slate-300 leading-relaxed">{question}</p>
                  </motion.div>
                ))}
              </div>
            </motion.section>

            {/* Behavioral Questions */}
            <motion.section variants={containerVariants} initial="hidden" animate="visible">
              <div className="flex items-center gap-3 mb-4">
                <MessageSquare className="w-5 h-5 text-purple-400" />
                <h3 className="text-lg font-bold text-white">
                  Behavioral Questions ({behavioralQuestions.length})
                </h3>
              </div>
              <div className="space-y-3">
                {behavioralQuestions.map((question, idx) => (
                  <motion.div
                    key={idx}
                    variants={itemVariants}
                    className="flex gap-4 p-4 bg-slate-800/50 rounded-lg border border-slate-700 hover:border-purple-500/30 transition"
                  >
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-purple-500/20 border border-purple-500/50 flex items-center justify-center text-xs font-bold text-purple-200">
                      {idx + 1}
                    </span>
                    <p className="text-sm text-slate-300 leading-relaxed">{question}</p>
                  </motion.div>
                ))}
              </div>
            </motion.section>
          </div>

          {/* Footer */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="px-8 py-6 border-t border-slate-700 flex gap-3"
          >
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={onClose}
              className="flex-1 py-3 px-4 rounded-lg bg-accent-purple hover:bg-accent-purple/80 text-white font-medium transition"
            >
              Close
            </motion.button>
          </motion.div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
