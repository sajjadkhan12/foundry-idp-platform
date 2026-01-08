/**
 * gRPC-Web Client for Notification Service
 */
import { NotificationServiceClient } from '../../generated/notification/NotificationServiceClientPb';
import {
    CreateNotificationRequest,
    GetNotificationRequest,
    ListNotificationsRequest,
    MarkAsReadRequest,
    MarkAllAsReadRequest,
    DeleteNotificationRequest,
} from '../../generated/notification/notification_pb';

import { getAccessToken } from '../../utils/tokenStorage';

const GRPC_WEB_URL = import.meta.env.VITE_GRPC_WEB_URL || 'http://localhost:8080';

/**
 * gRPC-Web Client for Notification Service
 */
export class NotificationGrpcClient {
    private client: NotificationServiceClient;

    constructor() {
        this.client = new NotificationServiceClient(GRPC_WEB_URL);
    }

    /**
     * Get metadata with authentication token
     */
    private getMetadata(): { [key: string]: string } {
        const token = getAccessToken();
        return token ? { authorization: `Bearer ${token}` } : {};
    }

    /**
     * Create notification
     */
    async createNotification(data: {
        user_id: string;
        title: string;
        message: string;
        type?: string;
        link?: string;
    }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new CreateNotificationRequest();
            request.setUserId(data.user_id);
            request.setTitle(data.title);
            request.setMessage(data.message);
            if (data.type) {
                request.setType(data.type);
            }
            if (data.link) {
                request.setLink(data.link);
            }

            this.client.createNotification(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    const notification = response.getNotification();
                    resolve({
                        id: notification?.getId(),
                        user_id: notification?.getUserId(),
                        title: notification?.getTitle(),
                        message: notification?.getMessage(),
                        type: notification?.getType(),
                        link: notification?.getLink(),
                        is_read: notification?.getIsRead(),
                        created_at: notification?.getCreatedAt(),
                    });
                }
            });
        });
    }

    /**
     * Get notification by ID
     */
    async getNotification(notificationId: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new GetNotificationRequest();
            request.setNotificationId(notificationId);

            this.client.getNotification(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    const notification = response.getNotification();
                    resolve({
                        id: notification?.getId(),
                        user_id: notification?.getUserId(),
                        title: notification?.getTitle(),
                        message: notification?.getMessage(),
                        type: notification?.getType(),
                        link: notification?.getLink(),
                        is_read: notification?.getIsRead(),
                        created_at: notification?.getCreatedAt(),
                    });
                }
            });
        });
    }

    /**
     * List notifications
     */
    async listNotifications(params?: { skip?: number; limit?: number; unread_only?: boolean }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ListNotificationsRequest();
            request.setSkip(params?.skip || 0);
            request.setLimit(params?.limit || 50);
            request.setUnreadOnly(params?.unread_only || false);

            this.client.listNotifications(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        notifications: response.getNotificationsList().map(n => ({
                            id: n.getId(),
                            user_id: n.getUserId(),
                            title: n.getTitle(),
                            message: n.getMessage(),
                            type: n.getType(),
                            link: n.getLink(),
                            is_read: n.getIsRead(),
                            created_at: n.getCreatedAt(),
                        })),
                        total: response.getTotal(),
                        unread_count: response.getUnreadCount(),
                    });
                }
            });
        });
    }

    /**
     * Mark notification as read
     */
    async markAsRead(notificationId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new MarkAsReadRequest();
            request.setNotificationId(notificationId);

            this.client.markAsRead(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * Mark all notifications as read
     */
    async markAllAsRead(userId?: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new MarkAllAsReadRequest();
            
            // Set user_id if provided, otherwise backend should extract from token
            if (userId) {
                request.setUserId(userId);
            }

            this.client.markAllAsRead(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * Delete notification
     */
    async deleteNotification(notificationId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new DeleteNotificationRequest();
            request.setNotificationId(notificationId);

            this.client.deleteNotification(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }
}

// Export singleton instance
export const notificationGrpcClient = new NotificationGrpcClient();
