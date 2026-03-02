'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface PageHeaderProps {
    title: string;
    subtitle?: string;
    actions?: React.ReactNode;
}

export const PageHeader = ({ title, subtitle, actions }: PageHeaderProps) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, ease: [0.25, 0.46, 0.45, 0.94] }}
            className="relative pt-2 pb-2"
        >
            <div className="flex items-end justify-between gap-6">
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.15, duration: 0.5 }}
                >
                    <h1 className="text-4xl sm:text-5xl font-extrabold font-display tracking-tight mb-2 text-glow">
                        <span className="gradient-text">{title}</span>
                    </h1>
                    {subtitle && (
                        <p className="text-base text-white/35 max-w-xl leading-relaxed">
                            {subtitle}
                        </p>
                    )}
                </motion.div>
                {actions && (
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.3, duration: 0.4 }}
                        className="flex-shrink-0"
                    >
                        {actions}
                    </motion.div>
                )}
            </div>

            {/* Decorative glow behind title */}
            <div className="absolute -top-16 -left-10 w-[350px] h-[200px] bg-accent-purple/5 rounded-full blur-[100px] pointer-events-none" />
        </motion.div>
    );
};
