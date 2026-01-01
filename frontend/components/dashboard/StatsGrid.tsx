import React from 'react';
import { Link } from 'react-router-dom';
import { Server, Package, Bell } from 'lucide-react';

interface DashboardStats {
    totalDeployments: number;
    activeDeployments: number;
    failedDeployments: number;
    provisioningDeployments: number;
    totalPlugins: number;
    unreadNotifications: number;
}

interface StatsGridProps {
    stats: DashboardStats;
}

export const StatsGrid: React.FC<StatsGridProps> = ({ stats }) => {
    return (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {/* Total Deployments */}
            <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 transition-colors hover:border-gray-300 dark:hover:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                    <div className="p-3 rounded-xl bg-blue-500/10 text-blue-600 dark:text-blue-400">
                        <Server className="w-6 h-6" />
                    </div>
                    <Link to="/deployments" className="text-xs text-blue-600 dark:text-blue-400 hover:underline">
                        View all →
                    </Link>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalDeployments}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">Total Deployments</p>
                <div className="mt-2 flex gap-2 text-xs">
                    <span className="text-green-600 dark:text-green-400">{stats.activeDeployments} active</span>
                    {stats.failedDeployments > 0 && (
                        <span className="text-red-600 dark:text-red-400">{stats.failedDeployments} failed</span>
                    )}
                    {stats.provisioningDeployments > 0 && (
                        <span className="text-yellow-600 dark:text-yellow-400">{stats.provisioningDeployments} provisioning</span>
                    )}
                </div>
            </div>

            {/* Plugins */}
            <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 transition-colors hover:border-gray-300 dark:hover:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                    <div className="p-3 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400">
                        <Package className="w-6 h-6" />
                    </div>
                    <Link to="/services" className="text-xs text-purple-600 dark:text-purple-400 hover:underline">
                        View all →
                    </Link>
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{stats.totalPlugins}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">Available Plugins</p>
            </div>

            {/* Notifications */}
            <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 transition-colors hover:border-gray-300 dark:hover:border-gray-700">
                <div className="flex items-center justify-between mb-4">
                    <div className="p-3 rounded-xl bg-green-500/10 text-green-600 dark:text-green-400">
                        <Bell className="w-6 h-6" />
                    </div>
                    {stats.unreadNotifications > 0 && (
                        <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                            {stats.unreadNotifications}
                        </span>
                    )}
                </div>
                <h3 className="text-2xl font-bold text-gray-900 dark:text-white">{stats.unreadNotifications}</h3>
                <p className="text-sm text-gray-500 dark:text-gray-400 font-medium">Unread Notifications</p>
            </div>
        </div>
    );
};
