'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface LoaderProps {
  size?: 'sm' | 'md' | 'lg';
  color?: 'primary' | 'secondary' | 'white';
  message?: string;
}

export const Loader = ({ size = 'md', color = 'primary', message }: LoaderProps) => {
  const sizeMap = {
    sm: { container: 'w-8 h-8', dot: 'w-2 h-2' },
    md: { container: 'w-12 h-12', dot: 'w-3 h-3' },
    lg: { container: 'w-16 h-16', dot: 'w-4 h-4' },
  };

  const colorMap = {
    primary: 'bg-primary-600',
    secondary: 'bg-secondary-600',
    white: 'bg-white',
  };

  const containerVariants = {
    animate: { rotate: 360 },
  };

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      <motion.div
        variants={containerVariants}
        animate="animate"
        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        className={`${sizeMap[size].container} relative`}
      >
        {[0, 1, 2].map((index) => (
          <motion.div
            key={index}
            className={`absolute ${sizeMap[size].dot} rounded-full ${colorMap[color]} opacity-70`}
            animate={{
              x: [0, Math.cos((index * 2 * Math.PI) / 3) * 20],
              y: [0, Math.sin((index * 2 * Math.PI) / 3) * 20],
              opacity: [0.3, 1, 0.3],
            }}
            transition={{
              duration: 1.5,
              repeat: Infinity,
              delay: index * 0.15,
            }}
            style={{
              left: '50%',
              top: '50%',
              x: '-50%',
              y: '-50%',
            }}
          />
        ))}
      </motion.div>
      {message && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          className="text-sm text-slate-600 dark:text-slate-400 font-medium"
        >
          {message}
        </motion.p>
      )}
    </div>
  );
};

export const SkeletonLoader = ({ count = 3 }: { count?: number }) => {
  return (
    <div className="space-y-4">
      {Array.from({ length: count }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0.6 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1.5, repeat: Infinity, repeatType: 'reverse' }}
          className="h-12 bg-slate-200 dark:bg-slate-700 rounded-lg"
        />
      ))}
    </div>
  );
};

export const PulseLoader = () => {
  return (
    <motion.div
      animate={{ scale: [1, 1.1, 1], opacity: [1, 0.7, 1] }}
      transition={{ duration: 2, repeat: Infinity }}
      className="w-3 h-3 bg-primary-600 rounded-full"
    />
  );
};
