'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface EmptyStateProps {
    icon: React.ReactNode;
    title: string;
    description?: string;
    action?: React.ReactNode;
}

export const EmptyState = ({ icon, title, description, action }: EmptyStateProps) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.5 }}
            className="text-center py-20"
        >
            <motion.div
                animate={{ y: [-8, 8, -8] }}
                transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}
                className="inline-block mb-5"
            >
                <div className="text-white/8">
                    {icon}
                </div>
            </motion.div>
            <h3 className="text-lg font-semibold text-white/35 mb-2">{title}</h3>
            {description && (
                <p className="text-sm text-white/18 max-w-sm mx-auto">{description}</p>
            )}
            {action && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 0.3 }}
                    className="mt-6"
                >
                    {action}
                </motion.div>
            )}
        </motion.div>
    );
};
