'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { clsx } from 'clsx';

interface GradientButtonProps {
    children: React.ReactNode;
    onClick?: () => void;
    disabled?: boolean;
    isLoading?: boolean;
    variant?: 'primary' | 'ghost' | 'danger' | 'success';
    size?: 'sm' | 'md' | 'lg';
    className?: string;
    type?: 'button' | 'submit' | 'reset';
    fullWidth?: boolean;
}

export const GradientButton = ({
    children,
    onClick,
    disabled = false,
    isLoading = false,
    variant = 'primary',
    size = 'md',
    className,
    type = 'button',
    fullWidth = false,
}: GradientButtonProps) => {
    const sizeStyles = {
        sm: 'px-4 py-2 text-sm',
        md: 'px-6 py-2.5 text-sm',
        lg: 'px-8 py-3.5 text-base',
    };

    const variantStyles = {
        primary: 'btn-gradient',
        ghost: 'btn-ghost',
        danger: 'bg-gradient-to-r from-red-600 to-red-500 text-white hover:shadow-glow-red rounded-[14px] border-none cursor-pointer transition-all duration-400 relative overflow-hidden',
        success: 'btn-success',
    };

    return (
        <motion.button
            type={type}
            whileHover={!disabled ? { scale: 1.02 } : {}}
            whileTap={!disabled ? { scale: 0.98 } : {}}
            onClick={onClick}
            disabled={disabled || isLoading}
            className={clsx(
                variantStyles[variant],
                sizeStyles[size],
                fullWidth && 'w-full',
                'inline-flex items-center justify-center gap-2 font-semibold rounded-[14px] transition-all duration-300',
                disabled && 'opacity-50 cursor-not-allowed',
                className
            )}
        >
            {isLoading ? (
                <div className="ai-pulse">
                    <span />
                    <span />
                    <span />
                </div>
            ) : (
                children
            )}
        </motion.button>
    );
};
