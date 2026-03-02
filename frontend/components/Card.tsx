'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hoverable?: boolean;
  animated?: boolean;
  gradient?: boolean;
}

export const Card = ({
  children,
  className,
  hoverable = false,
  animated = true,
  gradient = false,
}: CardProps) => {
  return (
    <motion.div
      initial={animated ? { opacity: 0, y: 10 } : {}}
      animate={animated ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.3 }}
      whileHover={hoverable ? { y: -4 } : {}}
      className={clsx(
        'bg-white dark:bg-slate-800 rounded-xl shadow-card hover:shadow-card-lg transition-all duration-300 p-6 border border-slate-200 dark:border-slate-700',
        gradient && 'bg-gradient-to-br from-white to-slate-50 dark:from-slate-800 dark:to-slate-900',
        hoverable && 'hover:border-primary-300 dark:hover:border-primary-600 cursor-pointer',
        className
      )}
    >
      {children}
    </motion.div>
  );
};

interface CardHeaderProps {
  title?: string;
  subtitle?: string;
  icon?: React.ReactNode;
  action?: React.ReactNode;
  className?: string;
  children?: React.ReactNode;
}

export const CardHeader = ({
  title,
  subtitle,
  icon,
  action,
  className,
  children,
}: CardHeaderProps) => {
  return (
    <div className={clsx('mb-6 pb-4 border-b border-slate-200 dark:border-slate-700', className)}>
      <div className="flex items-start justify-between gap-4">
        <div className="flex items-start gap-3">
          {icon && <div className="text-primary-600 dark:text-primary-400 mt-1">{icon}</div>}
          <div>
            {title && <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>}
            {subtitle && <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">{subtitle}</p>}
          </div>
        </div>
        {action && <div>{action}</div>}
      </div>
      {children}
    </div>
  );
};

interface CardBodyProps {
  children: React.ReactNode;
  className?: string;
}

export const CardBody = ({ children, className }: CardBodyProps) => {
  return <div className={clsx('space-y-4', className)}>{children}</div>;
};

interface CardFooterProps {
  children: React.ReactNode;
  className?: string;
}

export const CardFooter = ({ children, className }: CardFooterProps) => {
  return (
    <div className={clsx('mt-6 pt-4 border-t border-slate-200 dark:border-slate-700 flex items-center justify-between gap-3', className)}>
      {children}
    </div>
  );
};
