import { apiClient } from './client';
import { setAccessToken, removeAccessToken } from '../../utils/tokenStorage';

/**
 * Authentication API
 * Handles login, logout, and registration
 * 
 * NOTE: This service now uses gRPC-Web via authGrpcClient.
 * The REST endpoints are kept as fallback during migration.
 */
let useGrpc = false;
try {
    // Try to import gRPC client - will fail if proto files aren't generated
    const { authGrpcClient } = require('../../src/services/grpc');
    useGrpc = !!authGrpcClient;
} catch (e) {
    // gRPC not available, use REST fallback (silently - REST API works fine)
    // Uncomment below if you want to see the warning during development
    // console.warn('gRPC clients not available, using REST API. Run "npm run generate-proto" to enable gRPC.');
}

export const authApi = {
    async login(identifier: string, password: string) {
        try {
            if (useGrpc) {
                try {
                    const { authGrpcClient } = require('../../src/services/grpc');
                    const response = await authGrpcClient.login(identifier, password);
                    return response;
                } catch (error: any) {
                    console.error('gRPC login failed, falling back to REST:', error);
                    // Fall through to REST
                }
            }
            
            // REST fallback
            const response = await apiClient.request<any>('/api/v1/auth/login', {
                method: 'POST',
                body: JSON.stringify({ identifier, password })
            });
            setAccessToken(response.access_token);
            return response;
        } catch (error: any) {
            // Normalize all login errors to "Invalid credentials" for security best practices
            // This prevents user enumeration attacks (revealing which users exist)
            const status = error?.response?.status || error?.status;
            const isAuthError = status === 401 || status === 403 || 
                               error?.message?.toLowerCase().includes('invalid') ||
                               error?.message?.toLowerCase().includes('incorrect') ||
                               error?.message?.toLowerCase().includes('wrong') ||
                               error?.message?.toLowerCase().includes('unauthorized') ||
                               error?.message?.toLowerCase().includes('forbidden');
            
            // For authentication errors, show generic message
            if (isAuthError) {
                const genericError = new Error('Invalid credentials');
                (genericError as any).isAuthError = true;
                throw genericError;
            }
            
            // For network/connection errors, preserve the original message
            if (error?.message?.includes('Failed to fetch') || 
                error?.message?.includes('NetworkError') ||
                error?.message?.includes('Connection')) {
                throw new Error('Unable to connect to server. Please check your connection and try again.');
            }
            
            // For other errors, show generic message
            throw new Error('Invalid credentials');
        }
    },

    async logout() {
        if (useGrpc) {
            try {
                const { authGrpcClient } = require('../../src/services/grpc');
                await authGrpcClient.logout();
                removeAccessToken();
                return;
            } catch (error) {
                console.error('gRPC logout failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        
        // REST fallback
        try {
            await apiClient.request('/api/v1/auth/logout', {
                method: 'POST'
            });
        } finally {
            removeAccessToken();
        }
    }
};
