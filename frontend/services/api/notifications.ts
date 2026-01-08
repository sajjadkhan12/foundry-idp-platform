import { apiClient } from './client';
import { buildQueryString } from './helpers';

/**
 * Notifications API
 * Handles notification retrieval and management
 * 
 * NOTE: This service now uses gRPC-Web via notificationGrpcClient.
 * The REST endpoints are kept as fallback during migration.
 */
let useGrpc = false;
try {
    const { notificationGrpcClient } = require('../../src/services/grpc');
    useGrpc = !!notificationGrpcClient;
} catch (e) {
    // gRPC not available, use REST fallback (silently - REST API works fine)
    // Uncomment below if you want to see the warning during development
    // console.warn('gRPC clients not available, using REST API. Run "npm run generate-proto" to enable gRPC.');
}

export const notificationsApi = {
    async getNotifications(unreadOnly = false) {
        if (useGrpc) {
            try {
                const { notificationGrpcClient } = require('../../src/services/grpc');
                const result = await notificationGrpcClient.listNotifications({
                    unread_only: unreadOnly
                });
                return result.notifications;
            } catch (error) {
                console.error('gRPC getNotifications failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        
        // REST fallback
        const query = buildQueryString({ unread_only: unreadOnly });
        return apiClient.request(`/api/v1/notifications${query}`);
    },

    async markNotificationRead(id: string) {
        if (useGrpc) {
            try {
                const { notificationGrpcClient } = require('../../src/services/grpc');
                await notificationGrpcClient.markAsRead(id);
                // Return the updated notification
                const notification = await notificationGrpcClient.getNotification(id);
                return notification;
            } catch (error) {
                console.error('gRPC markNotificationRead failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        
        // REST fallback
        return apiClient.request(`/api/v1/notifications/${id}/read`, {
            method: 'PUT'
        });
    },

    async markAllNotificationsRead(userId?: string) {
        if (useGrpc) {
            try {
                const { notificationGrpcClient } = require('../../src/services/grpc');
                await notificationGrpcClient.markAllAsRead(userId);
                return { message: 'All notifications marked as read' };
            } catch (error) {
                console.error('gRPC markAllNotificationsRead failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        
        // REST fallback - user_id will be extracted from token if not provided
        const query = userId ? `?user_id=${userId}` : '';
        return apiClient.request(`/api/v1/notifications/read-all${query}`, {
            method: 'PUT'
        });
    }
};
