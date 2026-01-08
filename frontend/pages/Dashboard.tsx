import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
    Zap,
    Shield
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { BusinessUnitWarningModal } from '../components/BusinessUnitWarningModal';
import api from '../services/api';
import { appLogger } from '../utils/logger';
import { StatsGrid } from '../components/dashboard/StatsGrid';
import { RecentDeployments } from '../components/dashboard/RecentDeployments';
import { QuickActions } from '../components/dashboard/QuickActions';
import { NotificationsList } from '../components/dashboard/NotificationsList';
import { EnvironmentBreakdown } from '../components/dashboard/EnvironmentBreakdown';

interface DashboardStats {
    totalDeployments: number;
    activeDeployments: number;
    failedDeployments: number;
    provisioningDeployments: number;
    totalPlugins: number;
    unreadNotifications: number;
    envStats: { environment: string; count: number }[];
}

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

interface RecentNotification {
    id: string;
    title: string;
    message: string;
    type: string;
    is_read: boolean;
    created_at: string;
    link?: string;
}

export const DashboardPage: React.FC = () => {
    const { user, isAdmin, activeBusinessUnit, hasBusinessUnitAccess, isLoadingBusinessUnits, isLoadingActiveBusinessUnit } = useAuth();
    const [showBusinessUnitWarning, setShowBusinessUnitWarning] = useState(false);
    const [stats, setStats] = useState<DashboardStats>({
        totalDeployments: 0,
        activeDeployments: 0,
        failedDeployments: 0,
        provisioningDeployments: 0,
        totalPlugins: 0,
        unreadNotifications: 0,
        envStats: []
    });
    const [recentDeployments, setRecentDeployments] = useState<RecentDeployment[]>([]);
    const [recentNotifications, setRecentNotifications] = useState<RecentNotification[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchDashboardData();
    }, [isLoadingBusinessUnits, isLoadingActiveBusinessUnit, activeBusinessUnit, hasBusinessUnitAccess]);

    const fetchDashboardData = async () => {
        // Wait for business units and active business unit to load before checking
        if (isLoadingBusinessUnits || isLoadingActiveBusinessUnit) {
            return;
        }

        // Check if business unit is selected (admins can bypass)
        const userIsAdmin = isAdmin;
        if (!userIsAdmin && (!activeBusinessUnit || !hasBusinessUnitAccess)) {
            setShowBusinessUnitWarning(true);
            setLoading(false);
            return;
        }

        try {
            setLoading(true);
            setError('');

            // Fetch all data in parallel (with error handling)
            const commonParams = {
                business_unit_id: activeBusinessUnit?.id || undefined
            };

            const [deploymentsData, pluginsData, notificationsData, envStatsData] = await Promise.all([
                api.listDeployments({ ...commonParams, limit: 100 }).catch(() => ({ items: [], total: 0 })),
                api.pluginsApi.listPlugins().catch(() => []),
                api.notificationsApi.getNotifications(false).catch(() => ({ items: [], total: 0 })),
                api.request(`/api/v1/deployments/stats/by-environment${activeBusinessUnit?.id ? `?business_unit_id=${activeBusinessUnit.id}` : ''}`).catch(() => [])
            ]);

            // Process deployments
            const deployments = Array.isArray(deploymentsData) ? deploymentsData : (deploymentsData?.items || []);
            const activeDeployments = deployments.filter((d: any) => d.status === 'active').length;
            const failedDeployments = deployments.filter((d: any) => d.status === 'failed').length;
            const provisioningDeployments = deployments.filter((d: any) => d.status === 'provisioning').length;

            // Get recent deployments (last 5)
            const recent = deployments
                .slice(0, 5)
                .map((d: any) => ({
                    id: d.id,
                    name: d.name,
                    status: d.status,
                    environment: d.environment,
                    plugin_id: d.plugin_id,
                    created_at: d.created_at,
                    update_status: d.update_status,
                    last_update_error: d.last_update_error
                }));

            // Process plugins
            const plugins = Array.isArray(pluginsData) ? pluginsData : (pluginsData?.items || []);

            // Process notifications
            const notifications = Array.isArray(notificationsData) ? notificationsData : (notificationsData?.items || []);
            const unreadNotifications = notifications.filter((n: any) => !n.is_read).length;
            const recentNotificationsList = notifications.slice(0, 5).map((n: any) => ({
                id: n.id,
                title: n.title,
                message: n.message,
                type: n.type,
                is_read: n.is_read,
                created_at: n.created_at,
                link: n.link
            }));

            // Process environment stats
            const envStats = Array.isArray(envStatsData) ? envStatsData : [];

            setStats({
                totalDeployments: deployments.length,
                activeDeployments,
                failedDeployments,
                provisioningDeployments,
                totalPlugins: plugins.length,
                unreadNotifications,
                envStats
            });

            setRecentDeployments(recent);
            setRecentNotifications(recentNotificationsList);

        } catch (err: any) {
            appLogger.error('Failed to fetch dashboard data:', err);
            setError(err.message || 'Failed to load dashboard');
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-in fade-in duration-500">
            {/* Header */}
            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Dashboard</h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">
                        Welcome back, {user?.full_name || user?.username}. Here's your platform overview.
                    </p>
                </div>
                <div className="flex gap-2">
                    <Link
                        to="/provision"
                        className="bg-orange-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-orange-500 transition-colors shadow-lg shadow-orange-500/20 flex items-center gap-2"
                    >
                        <Zap className="w-4 h-4" /> Quick Deploy
                    </Link>
                    {isAdmin && (
                        <Link
                            to="/admin-dashboard"
                            className="bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors flex items-center gap-2"
                        >
                            <Shield className="w-4 h-4" /> Admin
                        </Link>
                    )}
                </div>
            </div>

            {/* Stats Grid */}
            <StatsGrid stats={stats} />

            {/* Environment Breakdown - Moved above Recent Deployments for normal users */}
            <EnvironmentBreakdown
                envStats={stats.envStats}
                isAdmin={isAdmin}
                activeBusinessUnit={activeBusinessUnit}
                hasBusinessUnitAccess={hasBusinessUnitAccess}
                onBusinessUnitWarning={() => setShowBusinessUnitWarning(true)}
            />

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                {/* Recent Deployments */}
                <RecentDeployments
                    deployments={recentDeployments}
                    isAdmin={isAdmin}
                    activeBusinessUnit={activeBusinessUnit}
                    hasBusinessUnitAccess={hasBusinessUnitAccess}
                    onBusinessUnitWarning={() => setShowBusinessUnitWarning(true)}
                />

                {/* Quick Actions */}
                <QuickActions isAdmin={isAdmin} />
            </div>

            {/* Recent Notifications - Only for Admins */}
            {isAdmin && (
                <NotificationsList
                    notifications={recentNotifications}
                    unreadCount={stats.unreadNotifications}
                />
            )}

            {/* Business Unit Warning Modal */}
            <BusinessUnitWarningModal
                isOpen={showBusinessUnitWarning}
                onClose={() => setShowBusinessUnitWarning(false)}
                onSelectBusinessUnit={() => {
                    const selector = document.querySelector('[data-business-unit-selector]');
                    if (selector) {
                        (selector as HTMLElement).click();
                    }
                }}
                action="view deployments"
            />
        </div>
    );
};
