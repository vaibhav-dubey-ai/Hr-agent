'use client';

import React, { useEffect, useState, useRef } from 'react';

interface AnimatedCounterProps {
    value: number;
    duration?: number;
    prefix?: string;
    suffix?: string;
    className?: string;
    decimals?: number;
}

export const AnimatedCounter = ({
    value,
    duration = 1500,
    prefix = '',
    suffix = '',
    className = '',
    decimals = 0,
}: AnimatedCounterProps) => {
    const [displayValue, setDisplayValue] = useState(0);
    const startTime = useRef<number | null>(null);
    const rafId = useRef<number>();

    useEffect(() => {
        startTime.current = null;

        const animate = (timestamp: number) => {
            if (!startTime.current) startTime.current = timestamp;
            const progress = Math.min((timestamp - startTime.current) / duration, 1);

            // Ease out cubic
            const eased = 1 - Math.pow(1 - progress, 3);
            setDisplayValue(Math.round(eased * value * Math.pow(10, decimals)) / Math.pow(10, decimals));

            if (progress < 1) {
                rafId.current = requestAnimationFrame(animate);
            }
        };

        rafId.current = requestAnimationFrame(animate);
        return () => {
            if (rafId.current) cancelAnimationFrame(rafId.current);
        };
    }, [value, duration, decimals]);

    const formatted = decimals > 0
        ? displayValue.toFixed(decimals)
        : displayValue.toLocaleString();

    return (
        <span className={className}>
            {prefix}{formatted}{suffix}
        </span>
    );
};
