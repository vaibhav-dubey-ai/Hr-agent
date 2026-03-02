'use client';

import React from 'react';
import { motion } from 'framer-motion';

interface ShimmerLoaderProps {
    count?: number;
    variant?: 'card' | 'line' | 'avatar';
    className?: string;
}

export const ShimmerLoader = ({
    count = 3,
    variant = 'card',
    className = '',
}: ShimmerLoaderProps) => {
    if (variant === 'card') {
        return (
            <div className={`grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 ${className}`}>
                {[...Array(count)].map((_, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: i * 0.1 }}
                        className="glass-card-static p-6"
                    >
                        <div className="skeleton h-4 w-24 mb-4" />
                        <div className="skeleton h-8 w-16 mb-3" />
                        <div className="skeleton h-3 w-32" />
                    </motion.div>
                ))}
            </div>
        );
    }

    if (variant === 'line') {
        return (
            <div className={`space-y-3 ${className}`}>
                {[...Array(count)].map((_, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0 }}
                        animate={{ opacity: 1 }}
                        transition={{ delay: i * 0.05 }}
                        className="skeleton h-12 w-full"
                    />
                ))}
            </div>
        );
    }

    return (
        <div className={`flex items-center gap-4 ${className}`}>
            <div className="skeleton h-10 w-10 rounded-full" />
            <div className="flex-1">
                <div className="skeleton h-4 w-32 mb-2" />
                <div className="skeleton h-3 w-48" />
            </div>
        </div>
    );
};

export const AILoader = ({ message = 'AI is thinking...' }: { message?: string }) => {
    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex flex-col items-center gap-4 py-12"
        >
            <div className="relative">
                <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
                    className="w-16 h-16 rounded-full border-2 border-transparent"
                    style={{
                        borderImage: 'linear-gradient(135deg, #a855f7, #3b82f6, #06b6d4) 1',
                        borderImageSlice: 1,
                    }}
                />
                <motion.div
                    animate={{ rotate: -360 }}
                    transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                    className="absolute inset-2 rounded-full border border-accent-purple/30"
                />
                <div className="absolute inset-0 flex items-center justify-center">
                    <div className="ai-pulse">
                        <span />
                        <span />
                        <span />
                    </div>
                </div>
            </div>
            <p className="text-sm text-white/50 font-medium">{message}</p>
        </motion.div>
    );
};
