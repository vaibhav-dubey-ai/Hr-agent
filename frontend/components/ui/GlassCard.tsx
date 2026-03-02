'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface GlassCardProps {
    children: React.ReactNode;
    className?: string;
    hoverable?: boolean;
    animated?: boolean;
    glowColor?: 'purple' | 'blue' | 'cyan' | 'green' | 'none';
    delay?: number;
    padding?: string;
    variant?: 'default' | 'elevated' | 'gradient-border';
}

export const GlassCard = ({
    children,
    className,
    hoverable = true,
    animated = true,
    glowColor = 'none',
    delay = 0,
    padding = 'p-6',
    variant = 'default',
}: GlassCardProps) => {
    const glowStyles = {
        purple: 'hover:shadow-glow-sm hover:border-accent-purple/20',
        blue: 'hover:shadow-glow-blue hover:border-accent-blue/20',
        cyan: 'hover:shadow-glow-cyan hover:border-accent-cyan/20',
        green: 'hover:shadow-glow-green hover:border-green-500/20',
        none: '',
    };

    const variantStyles = {
        default: 'glass-card',
        elevated: 'glass-card-elevated',
        'gradient-border': 'glass-card gradient-border',
    };

    return (
        <motion.div
            initial={animated ? { opacity: 0, y: 24 } : {}}
            animate={animated ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay, ease: [0.25, 0.46, 0.45, 0.94] }}
            whileHover={hoverable ? { y: -3, transition: { duration: 0.25 } } : {}}
            className={clsx(
                variantStyles[variant],
                padding,
                glowStyles[glowColor],
                className
            )}
        >
            {children}
        </motion.div>
    );
};
