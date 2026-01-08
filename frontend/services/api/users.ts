import { apiClient } from './client';
import { uploadFile, buildQueryString } from './helpers';

/**
 * Users API
 * Handles user management, profile updates, and avatar uploads
 * 
 * NOTE: This service now uses gRPC-Web via authGrpcClient for user operations.
 * Avatar uploads still use REST (file upload).
 */
let useGrpc = false;
try {
    // Try to import gRPC client - will fail if proto files aren't generated or compiled
    const grpcModule = require('../../src/services/grpc');
    useGrpc = !!grpcModule?.authGrpcClient;
} catch (e) {
    // Silently fall back to REST - this is expected if gRPC isn't set up
    // Uncomment the line below if you want to see the warning during development
    // console.warn('gRPC clients not available, using REST API. Run "npm run generate-proto" to enable gRPC.');
}

export const usersApi = {
    async getCurrentUser() {
        if (useGrpc) {
            try {
                const { authGrpcClient } = require('../../src/services/grpc');
                return await authGrpcClient.getCurrentUser();
            } catch (error) {
                console.error('gRPC getCurrentUser failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return apiClient.request('/api/v1/users/me');
    },

    async updateCurrentUser(data: any) {
        return apiClient.request('/api/v1/users/me', {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async listUsers(params?: { search?: string; role?: string; skip?: number; limit?: number }) {
        if (useGrpc) {
            try {
                const { authGrpcClient } = require('../../src/services/grpc');
                const result = await authGrpcClient.listUsers({
                    skip: params?.skip,
                    limit: params?.limit,
                    search: params?.search,
                    role_filter: params?.role
                });
                return result.users;
            } catch (error) {
                console.error('gRPC listUsers failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        const query = buildQueryString(params);
        return apiClient.request(`/api/v1/users${query}`);
    },

    async createUser(data: any) {
        return apiClient.request('/api/v1/users', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async adminUpdateUser(userId: string, data: any) {
        return apiClient.request(`/api/v1/users/${userId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },

    async deleteUser(userId: string) {
        return apiClient.request(`/api/v1/users/${userId}`, {
            method: 'DELETE'
        });
    },

    async updateUserRole(userId: string, role: string) {
        return apiClient.request(`/api/v1/users/${userId}/role`, {
            method: 'PUT',
            body: JSON.stringify({ role })
        });
    },

    async changePassword(data: any) {
        return apiClient.request('/api/v1/users/me/change-password', {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },

    async uploadAvatar(file: File) {
        return uploadFile('/api/v1/users/me/avatar', file);
    }
};
