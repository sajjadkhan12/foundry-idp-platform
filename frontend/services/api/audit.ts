/**
 * Audit Logs API Service
 */
import { apiClient } from './client';

export interface AuditLog {
    id: string;
    user_id?: string;
    user_email?: string;
    user_name?: string;
    action: string;
    resource_type?: string;
    resource_id?: string;
    resource_name?: string;
    details?: Record<string, any>;
    ip_address?: string;
    user_agent?: string;
    status: string;
    error_message?: string;
    business_unit_id?: string;
    organization_id?: string;
    service_name?: string;
    correlation_id?: string;
    duration_ms?: number;
    created_at: string;
    user?: {
        id: string;
        email: string;
        username: string;
        full_name?: string;
        avatar_url?: string;
    };
}

export interface AuditLogListResponse {
    items: AuditLog[];
    total: number;
}

export interface AuditLogFilters {
    skip?: number;
    limit?: number;
    user_id?: string;
    action?: string;
    resource_type?: string;
    resource_id?: string;
    service_name?: string;
    business_unit_id?: string;
    start_date?: string;
    end_date?: string;
    search?: string;
    status?: 'success' | 'failure';
}

export interface AuditStats {
    period_days: number;
    total: number;
    success: number;
    failure: number;
    top_actions: Array<{ action: string; count: number }>;
}

/**
 * List audit logs with filtering and pagination
 */
export async function listAuditLogs(filters: AuditLogFilters = {}): Promise<AuditLogListResponse> {
    const params = new URLSearchParams();
    
    if (filters.skip !== undefined) params.append('skip', filters.skip.toString());
    if (filters.limit !== undefined) params.append('limit', filters.limit.toString());
    if (filters.user_id) params.append('user_id', filters.user_id);
    if (filters.action) params.append('action', filters.action);
    if (filters.resource_type) params.append('resource_type', filters.resource_type);
    if (filters.resource_id) params.append('resource_id', filters.resource_id);
    if (filters.service_name) params.append('service_name', filters.service_name);
    if (filters.business_unit_id) params.append('business_unit_id', filters.business_unit_id);
    if (filters.start_date) params.append('start_date', filters.start_date);
    if (filters.end_date) params.append('end_date', filters.end_date);
    if (filters.search) params.append('search', filters.search);
    if (filters.status) params.append('status', filters.status);
    
    const queryString = params.toString();
    const endpoint = `/api/v1/audit-logs${queryString ? `?${queryString}` : ''}`;
    
    return apiClient.request<AuditLogListResponse>(endpoint);
}

/**
 * Get a single audit log by ID
 */
export async function getAuditLog(logId: string): Promise<AuditLog> {
    return apiClient.request<AuditLog>(`/api/v1/audit-logs/${logId}`);
}

/**
 * Get audit log statistics
 */
export async function getAuditStats(days: number = 7, businessUnitId?: string): Promise<AuditStats> {
    const params = new URLSearchParams();
    params.append('days', days.toString());
    if (businessUnitId) params.append('business_unit_id', businessUnitId);
    
    return apiClient.request<AuditStats>(`/api/v1/audit-logs/stats/summary?${params.toString()}`);
}

export const auditApi = {
    listAuditLogs,
    getAuditLog,
    getAuditStats,
};
