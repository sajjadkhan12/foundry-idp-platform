import React from 'react';
import { Link } from 'react-router-dom';
import { Server, CheckCircle, XCircle, Clock, AlertCircle, Loader2 } from 'lucide-react';
import { EnvironmentBadge } from '../EnvironmentBadge';

interface RecentDeployment {
    id: string;
    name: string;
    status: string;
    environment: string;
    plugin_id: string;
    created_at: string;
    update_status?: string;
    last_update_error?: string;
}

interface RecentDeploymentsProps {
    deployments: RecentDeployment[];
    isAdmin: boolean;
    activeBusinessUnit: any;
    hasBusinessUnitAccess: boolean;
    onBusinessUnitWarning: () => void;
}

export const RecentDeployments: React.FC<RecentDeploymentsProps> = ({
    deployments,
    isAdmin,
    activeBusinessUnit,
    hasBusinessUnitAccess,
    onBusinessUnitWarning
}) => {
    const getStatusIcon = (status: string) => {
        switch (status.toLowerCase()) {
            case 'active':
                return <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />;
            case 'failed':
            case 'dead_letter':
                return <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />;
            case 'provisioning':
            case 'pending':
            case 'running':
                return <Clock className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />;
            default:
                return <Server className="w-4 h-4 text-gray-600 dark:text-gray-400" />;
        }
    };

    const getStatusColor = (status: string) => {
        switch (status.toLowerCase()) {
            case 'active':
            case 'success':
                return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20';
            case 'failed':
            case 'dead_letter':
                return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20';
            case 'provisioning':
            case 'pending':
            case 'running':
                return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20';
            default:
                return 'text-gray-600 dark:text-gray-400 bg-gray-50 dark:bg-gray-800';
        }
    };

    const handleClick = (e: React.MouseEvent) => {
        const userIsAdmin = isAdmin;
        if (!userIsAdmin && (!activeBusinessUnit || !hasBusinessUnitAccess)) {
            e.preventDefault();
            onBusinessUnitWarning();
        }
    };

    return (
        <div className="lg:col-span-2 bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <Server className="w-5 h-5" />
                    Recent Deployments
                </h2>
                <Link 
                    to="/deployments" 
                    onClick={handleClick}
                    className="text-sm text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                >
                    View all <span>→</span>
                </Link>
            </div>
            <div className="space-y-3">
                {deployments.length > 0 ? (
                    deployments.map((deployment) => (
                        <Link
                            key={deployment.id}
                            to={`/deployment/${deployment.id}`}
                            onClick={handleClick}
                            className="block p-4 rounded-lg bg-gray-50 dark:bg-gray-800 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                        >
                            <div className="flex items-center justify-between">
                                <div className="flex items-center gap-3 flex-1 min-w-0">
                                    {getStatusIcon(deployment.status)}
                                    <div className="flex-1 min-w-0">
                                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                            {deployment.name}
                                        </p>
                                        <div className="flex items-center gap-2 mt-1">
                                            <EnvironmentBadge environment={deployment.environment} size="sm" />
                                            <span className="text-xs text-gray-500 dark:text-gray-400">
                                                {new Date(deployment.created_at).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-1.5">
                                    <span className={`text-xs font-medium px-2 py-1 rounded-full ${getStatusColor(deployment.status)}`}>
                                        {deployment.status}
                                    </span>
                                    {deployment.update_status === 'update_failed' && (
                                        <AlertCircle className="w-4 h-4 text-yellow-500" title={deployment.last_update_error || 'Update failed'} />
                                    )}
                                    {deployment.update_status === 'updating' && (
                                        <Loader2 className="w-4 h-4 text-blue-500 animate-spin" />
                                    )}
                                </div>
                            </div>
                        </Link>
                    ))
                ) : (
                    <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                        <Server className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No deployments yet</p>
                        <Link 
                            to="/provision" 
                            className="text-blue-600 dark:text-blue-400 hover:underline mt-2 inline-block"
                        >
                            Create your first deployment
                        </Link>
                    </div>
                )}
            </div>
        </div>
    );
};
