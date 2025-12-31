import React from 'react';
import { Bell, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface RecentNotification {
    id: string;
    title: string;
    message: string;
    type: string;
    is_read: boolean;
    created_at: string;
    link?: string;
}

interface NotificationsListProps {
    notifications: RecentNotification[];
    unreadCount: number;
}

export const NotificationsList: React.FC<NotificationsListProps> = ({ notifications, unreadCount }) => {
    const getNotificationIcon = (type: string) => {
        switch (type) {
            case 'success':
                return <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />;
            case 'error':
                return <XCircle className="w-4 h-4 text-red-600 dark:text-red-400" />;
            case 'warning':
                return <AlertCircle className="w-4 h-4 text-yellow-600 dark:text-yellow-400" />;
            default:
                return <Bell className="w-4 h-4 text-blue-600 dark:text-blue-400" />;
        }
    };

    return (
        <div className="bg-white dark:bg-gray-900 rounded-2xl border border-gray-200 dark:border-gray-800 p-6">
            <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                    <Bell className="w-5 h-5" />
                    Recent Notifications
                </h2>
                {unreadCount > 0 && (
                    <span className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full">
                        {unreadCount} unread
                    </span>
                )}
            </div>
            <div className="space-y-3">
                {notifications.length > 0 ? (
                    notifications.map((notification) => (
                        <div
                            key={notification.id}
                            className={`p-4 rounded-lg ${notification.is_read 
                                ? 'bg-gray-50 dark:bg-gray-800' 
                                : 'bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800'
                            }`}
                        >
                            <div className="flex items-start gap-3">
                                {getNotificationIcon(notification.type)}
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                                        {notification.title}
                                    </p>
                                    <p className="text-xs text-gray-600 dark:text-gray-400 mt-1 line-clamp-2">
                                        {notification.message}
                                    </p>
                                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                                        {new Date(notification.created_at).toLocaleDateString()}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="text-center py-8 text-gray-500 dark:text-gray-400">
                        <Bell className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p>No notifications</p>
                    </div>
                )}
            </div>
        </div>
    );
};
