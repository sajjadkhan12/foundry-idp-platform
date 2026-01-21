import React from 'react';
import { X } from 'lucide-react';

interface ModalProps {
    isOpen: boolean;
    onClose: () => void;
    title: string;
    children: React.ReactNode;
    footer?: React.ReactNode;
    size?: 'sm' | 'md' | 'lg' | 'xl';
}

const sizeClasses = {
    sm: 'max-w-sm',
    md: 'max-w-md',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl'
};

export const Modal: React.FC<ModalProps> = ({
    isOpen,
    onClose,
    title,
    children,
    footer,
    size = 'md'
}) => {
    if (!isOpen) return null;
    
    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/50 backdrop-blur-sm overflow-y-auto">
            <div className={`bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full ${sizeClasses[size]} border border-gray-200 dark:border-gray-800 animate-in fade-in zoom-in-95 duration-200 my-auto max-h-[95vh] flex flex-col`}>
                {/* Header */}
                <div className="flex items-center justify-between p-4 sm:p-6 border-b border-gray-200 dark:border-gray-800 flex-shrink-0">
                    <h3 className="text-base sm:text-lg font-semibold text-gray-900 dark:text-white pr-2">
                        {title}
                    </h3>
                    <button 
                        onClick={onClose} 
                        className="text-gray-400 hover:text-gray-500 transition-colors flex-shrink-0"
                        aria-label="Close modal"
                    >
                        <X className="w-5 h-5" />
                    </button>
                </div>
                
                {/* Content - scrollable */}
                <div className="p-4 sm:p-6 overflow-y-auto flex-1 min-h-0">
                    {children}
                </div>
                
                {/* Footer */}
                {footer && (
                    <div className="flex flex-col sm:flex-row justify-end gap-3 p-4 sm:p-6 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 rounded-b-xl flex-shrink-0">
                        {footer}
                    </div>
                )}
            </div>
        </div>
    );
};
