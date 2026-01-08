/**
 * Centralized API configuration
 * gRPC-Web URL for Envoy proxy
 */
export const GRPC_WEB_URL = import.meta.env.VITE_GRPC_WEB_URL || 'http://localhost:8080';

/**
 * Legacy REST API URL (for backward compatibility during migration)
 */
/**
 * Legacy REST API URL (for backward compatibility during migration)
 */
// Use relative path '/api' which will be proxied by Nginx or Vite
// Fallback to localhost:8000 only if explicitly defined in env
export const API_URL = import.meta.env.VITE_API_URL || '';

// Debug: Log the API URL being used
if (typeof window !== 'undefined') {
    console.log('[API Config] VERSION: 2026-01-06-V4-PROXY');
    console.log('[API Config] API_URL configured to:', API_URL || '(relative /api)');
}

/**
 * Get the base gRPC-Web URL
 * Use this for gRPC-Web clients
 */
export function getGrpcWebUrl(): string {
    return GRPC_WEB_URL;
}

/**
 * Get the base API URL (legacy REST)
 * Use this instead of hardcoding URLs
 */
export function getApiUrl(): string {
    return API_URL;
}

/**
 * Build a full API URL from an endpoint
 */
export function buildApiUrl(endpoint: string): string {
    const baseUrl = API_URL.endsWith('/') ? API_URL.slice(0, -1) : API_URL;
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${baseUrl}${path}`;
}

