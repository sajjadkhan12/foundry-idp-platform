import React from 'react';
import { Link } from 'react-router-dom';
import { Zap, PlayCircle, LayoutGrid, Server, Users, Shield, ArrowRight } from 'lucide-react';

interface QuickActionsProps {
    isAdmin: boolean;
}

export const QuickActions: React.FC<QuickActionsProps> = ({ isAdmin }) => {
    return (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-4">
                <Zap className="w-5 h-5" />
                Quick Actions
            </h2>
            <div className="space-y-2">
                <Link
                    to="/provision"
                    className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-orange-50 dark:hover:bg-orange-900/20 transition-colors group"
                >
                    <div className="flex items-center gap-3">
                        <PlayCircle className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">Provision Infrastructure</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-orange-600 dark:group-hover:text-orange-400" />
                </Link>
                <Link
                    to="/services"
                    className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors group"
                >
                    <div className="flex items-center gap-3">
                        <LayoutGrid className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">Browse Catalog</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400" />
                </Link>
                <Link
                    to="/deployments"
                    className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-purple-50 dark:hover:bg-purple-900/20 transition-colors group"
                >
                    <div className="flex items-center gap-3">
                        <Server className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                        <span className="text-sm font-medium text-gray-900 dark:text-white">Deployments</span>
                    </div>
                    <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400" />
                </Link>
                {isAdmin && (
                    <>
                        <Link
                            to="/users"
                            className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors group"
                        >
                            <div className="flex items-center gap-3">
                                <Users className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                                <span className="text-sm font-medium text-gray-900 dark:text-white">Manage Users</span>
                            </div>
                            <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400" />
                        </Link>
                        <Link
                            to="/roles"
                            className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-pink-50 dark:hover:bg-pink-900/20 transition-colors group"
                        >
                            <div className="flex items-center gap-3">
                                <Shield className="w-5 h-5 text-pink-600 dark:text-pink-400" />
                                <span className="text-sm font-medium text-gray-900 dark:text-white">Manage Roles</span>
                            </div>
                            <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-pink-600 dark:group-hover:text-pink-400" />
                        </Link>
                    </>
                )}
            </div>
        </div>
    );
};
