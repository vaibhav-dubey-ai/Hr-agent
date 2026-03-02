'use client';

import React from 'react';

export const AnimatedBackground = () => {
    // Use deterministic positions to avoid hydration mismatch
    const particles = [
        { w: 2, t: 8, l: 15, delay: 0.5, dur: 5 },
        { w: 3, t: 22, l: 72, delay: 1.2, dur: 6 },
        { w: 1, t: 45, l: 38, delay: 2.0, dur: 4.5 },
        { w: 2, t: 67, l: 85, delay: 0.8, dur: 5.5 },
        { w: 1, t: 12, l: 53, delay: 3.0, dur: 7 },
        { w: 3, t: 78, l: 20, delay: 1.5, dur: 6.5 },
        { w: 2, t: 35, l: 91, delay: 0.3, dur: 4 },
        { w: 1, t: 55, l: 7, delay: 2.5, dur: 5.2 },
        { w: 2, t: 90, l: 45, delay: 1.8, dur: 6.2 },
        { w: 1, t: 3, l: 68, delay: 0.7, dur: 4.8 },
        { w: 3, t: 42, l: 25, delay: 3.5, dur: 7.5 },
        { w: 1, t: 18, l: 80, delay: 2.2, dur: 5.8 },
        { w: 2, t: 62, l: 55, delay: 1.0, dur: 6.8 },
        { w: 1, t: 85, l: 32, delay: 0.2, dur: 4.3 },
        { w: 2, t: 28, l: 12, delay: 2.8, dur: 5.5 },
        { w: 1, t: 50, l: 96, delay: 1.6, dur: 6.1 },
        { w: 3, t: 73, l: 48, delay: 3.2, dur: 7.2 },
        { w: 1, t: 6, l: 35, delay: 0.9, dur: 4.6 },
        { w: 2, t: 38, l: 78, delay: 2.4, dur: 5.3 },
        { w: 1, t: 95, l: 62, delay: 1.3, dur: 6.4 },
    ];

    return (
        <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
            {/* Animated Grid */}
            <div className="absolute inset-0 animated-grid opacity-30" />

            {/* Floating Blobs */}
            <div
                className="blob animate-blob-1"
                style={{
                    width: '600px',
                    height: '600px',
                    background: 'radial-gradient(circle, rgba(168, 85, 247, 0.12) 0%, transparent 70%)',
                    top: '-10%',
                    right: '-5%',
                }}
            />
            <div
                className="blob animate-blob-2"
                style={{
                    width: '700px',
                    height: '700px',
                    background: 'radial-gradient(circle, rgba(59, 130, 246, 0.1) 0%, transparent 70%)',
                    bottom: '-15%',
                    left: '-10%',
                }}
            />
            <div
                className="blob animate-blob-3"
                style={{
                    width: '500px',
                    height: '500px',
                    background: 'radial-gradient(circle, rgba(6, 182, 212, 0.08) 0%, transparent 70%)',
                    top: '40%',
                    left: '50%',
                }}
            />

            {/* Deterministic Particle Dots */}
            <div className="absolute inset-0">
                {particles.map((p, i) => (
                    <div
                        key={i}
                        className="absolute rounded-full animate-float"
                        style={{
                            width: `${p.w}px`,
                            height: `${p.w}px`,
                            background: i % 3 === 0
                                ? 'rgba(168, 85, 247, 0.25)'
                                : i % 3 === 1
                                    ? 'rgba(59, 130, 246, 0.2)'
                                    : 'rgba(6, 182, 212, 0.2)',
                            top: `${p.t}%`,
                            left: `${p.l}%`,
                            animationDelay: `${p.delay}s`,
                            animationDuration: `${p.dur}s`,
                        }}
                    />
                ))}
            </div>
        </div>
    );
};
