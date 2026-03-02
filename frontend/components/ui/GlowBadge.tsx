'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface GlowBadgeProps {
    children: React.ReactNode;
    variant?: 'success' | 'danger' | 'warning' | 'info' | 'purple';
    size?: 'sm' | 'md';
    pulse?: boolean;
    className?: string;
    icon?: React.ReactNode;
}

export const GlowBadge = ({
    children,
    variant = 'info',
    size = 'md',
    pulse = false,
    className,
    icon,
}: GlowBadgeProps) => {
    const sizeStyles = {
        sm: 'text-[10px] px-2.5 py-1',
        md: 'text-[11px] px-3.5 py-1.5',
    };

    return (
        <motion.span
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            className={clsx(
                'glow-badge',
                `glow-badge-${variant}`,
                sizeStyles[size],
                className
            )}
        >
            {pulse && (
                <span
                    className={clsx(
                        'w-1.5 h-1.5 rounded-full animate-pulse',
                        variant === 'success' && 'bg-green-400',
                        variant === 'danger' && 'bg-red-400',
                        variant === 'warning' && 'bg-amber-400',
                        variant === 'info' && 'bg-blue-400',
                        variant === 'purple' && 'bg-purple-400',
                    )}
                />
            )}
            {icon && <span className="flex-shrink-0">{icon}</span>}
            {children}
        </motion.span>
    );
};
