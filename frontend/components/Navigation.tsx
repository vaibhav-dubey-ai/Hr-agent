'use client';

import Link from 'next/link';
import { useState } from 'react';

export default function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <nav className="fixed top-0 w-full bg-white dark:bg-gray-800 shadow-md z-40">
      <div className="container flex justify-between items-center h-20">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 font-bold text-xl">
          <span className="text-2xl">🤖</span>
          <span>HR Agent</span>
        </Link>

        {/* Desktop Menu */}
        <div className="hidden md:flex gap-6">
          <Link href="/" className="hover:text-primary transition">
            Dashboard
          </Link>
          <Link href="/ranking" className="hover:text-primary transition">
            Resume Ranking
          </Link>
          <Link href="/leave" className="hover:text-primary transition">
            Leave Management
          </Link>
          <Link href="/scheduling" className="hover:text-primary transition">
            Scheduling
          </Link>
          <Link href="/pipeline" className="hover:text-primary transition">
            Pipeline
          </Link>
        </div>

        {/* Mobile Menu Button */}
        <button
          className="md:hidden"
          onClick={() => setIsMenuOpen(!isMenuOpen)}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
          <Link href="/" className="block px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700">
            Dashboard
          </Link>
          <Link href="/ranking" className="block px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700">
            Resume Ranking
          </Link>
          <Link href="/leave" className="block px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700">
            Leave Management
          </Link>
          <Link href="/scheduling" className="block px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700">
            Scheduling
          </Link>
          <Link href="/pipeline" className="block px-4 py-3 hover:bg-gray-100 dark:hover:bg-gray-700">
            Pipeline
          </Link>
        </div>
      )}
    </nav>
  );
}
