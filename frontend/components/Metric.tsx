'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface MetricProps {
  label: string;
  value: string | number;
  icon?: React.ReactNode;
  change?: number;
  trend?: 'up' | 'down' | 'neutral';
  variant?: 'default' | 'primary' | 'success' | 'warning' | 'danger';
  animated?: boolean;
}

export const Metric = ({
  label,
  value,
  icon,
  change,
  trend = 'neutral',
  variant = 'default',
  animated = true,
}: MetricProps) => {
  const variantStyles = {
    default: 'bg-slate-50 dark:bg-slate-900 border-slate-200 dark:border-slate-700',
    primary: 'bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800',
    success: 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800',
    warning: 'bg-amber-50 dark:bg-amber-900/20 border-amber-200 dark:border-amber-800',
    danger: 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800',
  };

  const trendColor = {
    up: 'text-green-600 dark:text-green-400',
    down: 'text-red-600 dark:text-red-400',
    neutral: 'text-slate-600 dark:text-slate-400',
  };

  const containerVariants = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
  };

  const valueVariants = {
    initial: { scale: 0.8, opacity: 0 },
    animate: { scale: 1, opacity: 1 },
  };

  return (
    <motion.div
      variants={containerVariants}
      initial={animated ? 'initial' : 'animate'}
      animate="animate"
      transition={{ duration: 0.4 }}
      className={clsx(
        'p-6 rounded-xl border transition-all duration-300 hover:shadow-lg',
        variantStyles[variant]
      )}
    >
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <p className="text-sm font-medium text-slate-600 dark:text-slate-400 mb-2">{label}</p>
          <motion.div
            variants={valueVariants}
            initial={animated ? 'initial' : 'animate'}
            animate="animate"
            transition={{ duration: 0.5, delay: 0.1 }}
            className="flex items-baseline gap-2"
          >
            <span className="text-3xl font-bold text-slate-900 dark:text-white">{value}</span>
            {change !== undefined && (
              <span className={clsx('text-xs font-semibold', trendColor[trend])}>
                {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {Math.abs(change)}%
              </span>
            )}
          </motion.div>
        </div>
        {icon && (
          <motion.div
            initial={animated ? { scale: 0, rotate: -20 } : {}}
            animate={animated ? { scale: 1, rotate: 0 } : {}}
            transition={{ duration: 0.4, type: 'spring' }}
            className={clsx(
              'p-3 rounded-lg',
              variant === 'default'
                ? 'bg-slate-200 dark:bg-slate-700 text-slate-600 dark:text-slate-300'
                : `bg-${variant}-200 dark:bg-${variant}-900 text-${variant}-600 dark:text-${variant}-400`
            )}
          >
            {icon}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
};

export const MetricGrid = ({ children }: { children: React.ReactNode }) => {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {children}
    </div>
  );
};
