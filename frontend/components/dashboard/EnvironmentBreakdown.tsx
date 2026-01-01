import React from 'react';
import { Link } from 'react-router-dom';
import { TrendingUp } from 'lucide-react';
import { EnvironmentBadge } from '../EnvironmentBadge';

interface EnvStat {
    environment: string;
    count: number;
}

interface EnvironmentBreakdownProps {
    envStats: EnvStat[];
    isAdmin: boolean;
    activeBusinessUnit: any;
    hasBusinessUnitAccess: boolean;
    onBusinessUnitWarning: () => void;
}

export const EnvironmentBreakdown: React.FC<EnvironmentBreakdownProps> = ({
    envStats,
    isAdmin,
    activeBusinessUnit,
    hasBusinessUnitAccess,
    onBusinessUnitWarning
}) => {
    const handleClick = (e: React.MouseEvent) => {
        const userIsAdmin = isAdmin;
        if (!userIsAdmin && (!activeBusinessUnit || !hasBusinessUnitAccess)) {
            e.preventDefault();
            onBusinessUnitWarning();
        }
    };

    if (envStats.length === 0) return null;

    return (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-4">
                <TrendingUp className="w-5 h-5" />
                Environment Breakdown
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                {['development', 'staging', 'production'].map((env) => {
                    const envStat = envStats.find(s => s.environment === env);
                    const count = envStat?.count || 0;
                    return (
                        <Link
                            key={env}
                            to={`/deployments?environment=${env}`}
                            onClick={handleClick}
                            className="p-4 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        >
                            <div className="flex items-center justify-between mb-2">
                                <EnvironmentBadge environment={env} size="md" showIcon={true} />
                            </div>
                            <p className="text-2xl font-bold text-gray-900 dark:text-white">{count}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">Deployments</p>
                        </Link>
                    );
                })}
            </div>
        </div>
    );
};
