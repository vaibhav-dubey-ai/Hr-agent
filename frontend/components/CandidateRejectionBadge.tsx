'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { XCircle, ChevronDown } from 'lucide-react';

interface CandidateRejectionBadgeProps {
  rejectionReason: string;
}

export function CandidateRejectionBadge({ rejectionReason }: CandidateRejectionBadgeProps) {
  const [expanded, setExpanded] = useState(false);

  return (
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-red-500/10 border border-red-500/30 rounded-lg p-4"
    >
      <motion.button
        onClick={() => setExpanded(!expanded)}
        className="flex items-center gap-3 w-full text-left text-red-200 font-semibold hover:text-red-100 transition group"
      >
        <XCircle className="w-5 h-5 flex-shrink-0 text-red-400" />
        <span className="flex-1">Rejected</span>
        <motion.div
          animate={{ rotate: expanded ? 180 : 0 }}
          transition={{ duration: 0.2 }}
        >
          <ChevronDown className="w-4 h-4 text-red-400" />
        </motion.div>
      </motion.button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.2 }}
            className="mt-3 pt-3 border-t border-red-500/20"
          >
            <p className="text-sm text-slate-300 leading-relaxed">{rejectionReason}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
