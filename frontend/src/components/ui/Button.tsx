import React from 'react';

import { cn } from '@/utils/cn';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: React.ReactNode;
}

export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  className,
  children,
  disabled,
  ...props
}) => {
  const baseStyles = 'inline-flex items-center justify-center rounded-lg font-fantasy font-semibold transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-transparent disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden';
  
  const variants = {
    primary: 'bg-medieval-gradient text-dark-900 hover:bg-gradient-to-r hover:from-gold-500 hover:to-gold-400 focus:ring-gold-500 shadow-golden hover:shadow-golden-lg font-semibold tracking-wide transform hover:scale-105 active:scale-95 transition-all duration-300 border border-gold-600/40 hover:border-gold-400/60',
    secondary: 'bg-royal-gradient text-royal-50 hover:from-royal-700 hover:to-royal-600 focus:ring-royal-600 shadow-lg hover:shadow-2xl border border-royal-600/40 hover:border-royal-400/60 transform hover:scale-105 active:scale-95 transition-all duration-300',
    ghost: 'bg-transparent text-gold-200 hover:bg-gradient-to-r hover:from-gold-900/30 hover:to-royal-900/30 focus:ring-gold-600 border-2 border-gold-600/40 hover:border-gold-400/70 hover:shadow-golden-sm transform hover:scale-105 active:scale-95 transition-all duration-300',
    danger: 'bg-gradient-to-r from-red-800 to-red-700 text-white hover:from-red-700 hover:to-red-600 focus:ring-red-500 shadow-blood hover:shadow-blood border border-red-600/40 animate-pulse-gentle transform hover:scale-105 active:scale-95 transition-all duration-300',
  };
  
  const sizes = {
    sm: 'px-3 py-1.5 text-sm',
    md: 'px-4 py-2 text-base',
    lg: 'px-6 py-3 text-lg',
  };
  
  return (
    <button
      className={cn(
        baseStyles,
        variants[variant],
        sizes[size],
        className
      )}
      disabled={disabled || isLoading}
      {...props}
    >
      {isLoading ? (
        <>
          <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 0 1 8-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </>
      ) : children}
    </button>
  );
};