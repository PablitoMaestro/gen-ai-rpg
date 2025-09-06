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
  const baseStyles = 'inline-flex items-center justify-center rounded-lg font-semibold transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  
  const variants = {
    primary: 'bg-gradient-to-r from-amber-600 to-amber-500 text-dark-900 hover:from-amber-500 hover:to-amber-400 focus:ring-amber-500 shadow-golden hover:shadow-golden-lg font-semibold tracking-wide transform hover:scale-105 active:scale-95 transition-all duration-200',
    secondary: 'bg-gradient-to-r from-secondary-800 to-secondary-700 text-secondary-50 hover:from-secondary-700 hover:to-secondary-600 focus:ring-secondary-600 shadow-nature hover:shadow-nature-lg border border-secondary-600/30 transform hover:scale-105 active:scale-95 transition-all duration-200',
    ghost: 'bg-transparent text-amber-200 hover:bg-amber-900/20 focus:ring-amber-600 border border-amber-600/30 hover:border-amber-500/50 hover:shadow-golden-sm transform hover:scale-105 active:scale-95 transition-all duration-200',
    danger: 'bg-gradient-to-r from-red-700 to-red-600 text-white hover:from-red-600 hover:to-red-500 focus:ring-red-500 shadow-blood hover:shadow-blood animate-pulse-gentle transform hover:scale-105 active:scale-95 transition-all duration-200',
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
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          Loading...
        </>
      ) : children}
    </button>
  );
};