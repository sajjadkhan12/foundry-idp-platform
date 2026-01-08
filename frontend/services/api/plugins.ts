import { apiClient } from './client';
import { uploadFile } from './helpers';

/**
 * Plugins API
 * Handles plugin upload, listing, and management
 * 
 * NOTE: This service now uses gRPC-Web via pluginGrpcClient for CRUD operations.
 * File upload operations still use REST (upload requires multipart/form-data).
 */
let useGrpc = false;
try {
    const { pluginGrpcClient } = require('../../src/services/grpc');
    useGrpc = !!pluginGrpcClient;
} catch (e) {
    // gRPC not available, use REST fallback (silently - REST API works fine)
    // Uncomment below if you want to see the warning during development
    // console.warn('gRPC clients not available, using REST API. Run "npm run generate-proto" to enable gRPC.');
}

export const pluginsApi = {
    async uploadPlugin(
        file: File,
        options?: {
            gitBranch?: string;
            gitRepoUrl?: string;
        }
    ) {
        const extraFields: Record<string, string> = {};
        if (options?.gitBranch) {
            extraFields['git_branch'] = options.gitBranch;
        }
        if (options?.gitRepoUrl) {
            extraFields['git_repo_url'] = options.gitRepoUrl;
        }

        return uploadFile('/api/v1/plugins/upload', file, 'file', extraFields);
    },

    async listPlugins() {
        if (useGrpc) {
            try {
                const { pluginGrpcClient } = require('../../src/services/grpc');
                const result = await pluginGrpcClient.listPlugins();
                return result.plugins;
            } catch (error) {
                console.error('gRPC listPlugins failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return apiClient.request('/api/v1/plugins');
    },

    async getPlugin(pluginId: string) {
        if (useGrpc) {
            try {
                const { pluginGrpcClient } = require('../../src/services/grpc');
                return await pluginGrpcClient.getPlugin(pluginId);
            } catch (error) {
                console.error('gRPC getPlugin failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return apiClient.request(`/api/v1/plugins/${pluginId}`);
    },

    async getPluginVersions(pluginId: string) {
        if (useGrpc) {
            try {
                const { pluginGrpcClient } = require('../../src/services/grpc');
                const result = await pluginGrpcClient.listPluginVersions(pluginId);
                return result.versions;
            } catch (error) {
                console.error('gRPC getPluginVersions failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return apiClient.request(`/api/v1/plugins/${pluginId}/versions`);
    },

    async deletePlugin(pluginId: string) {
        if (useGrpc) {
            try {
                const { pluginGrpcClient } = require('../../src/services/grpc');
                await pluginGrpcClient.deletePlugin(pluginId);
                return { success: true };
            } catch (error) {
                console.error('gRPC deletePlugin failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return apiClient.request(`/api/v1/plugins/${pluginId}`, {
            method: 'DELETE'
        });
    },

    async lockPlugin(pluginId: string) {
        if (useGrpc) {
            try {
                const { pluginGrpcClient } = require('../../src/services/grpc');
                await pluginGrpcClient.lockPlugin(pluginId);
                return { success: true };
            } catch (error) {
                console.error('gRPC lockPlugin failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return apiClient.request(`/api/v1/plugins/${pluginId}/lock`, {
            method: 'PUT'
        });
    },

    async unlockPlugin(pluginId: string) {
        if (useGrpc) {
            try {
                const { pluginGrpcClient } = require('../../src/services/grpc');
                await pluginGrpcClient.unlockPlugin(pluginId);
                return { success: true };
            } catch (error) {
                console.error('gRPC unlockPlugin failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return apiClient.request(`/api/v1/plugins/${pluginId}/unlock`, {
            method: 'PUT'
        });
    },

    async requestAccess(pluginId: string, note?: string, businessUnitId?: string) {
        if (useGrpc) {
            try {
                const { pluginGrpcClient } = require('../../src/services/grpc');
                return await pluginGrpcClient.requestPluginAccess(pluginId, note);
            } catch (error) {
                console.error('gRPC requestAccess failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        // Include business_unit_id as query param if provided
        const params = businessUnitId ? `?business_unit_id=${businessUnitId}` : '';
        return apiClient.request(`/api/v1/plugins/${pluginId}/access/request${params}`, {
            method: 'POST',
            body: JSON.stringify({ note: note || '' })
        });
    },

    async grantAccess(pluginId: string, userId: string) {
        return apiClient.request(`/api/v1/plugins/${pluginId}/access/grant`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        });
    },

    async rejectAccess(pluginId: string, userId: string) {
        return apiClient.request(`/api/v1/plugins/${pluginId}/access/reject`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ user_id: userId })
        });
    },

    async revokeAccess(pluginId: string, userId: string) {
        return apiClient.request(`/api/v1/plugins/${pluginId}/access/${userId}`, {
            method: 'DELETE'
        });
    },

    async restoreAccess(pluginId: string, userId: string) {
        return apiClient.request(`/api/v1/plugins/${pluginId}/access/${userId}/restore`, {
            method: 'POST'
        });
    },

    async getAccessRequests(pluginId: string) {
        return apiClient.request(`/api/v1/plugins/${pluginId}/access/requests`);
    },

    async getAllAccessRequests(search?: string, status?: string) {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (status) params.append('status', status);
        const queryString = params.toString();
        return apiClient.request(`/api/v1/plugins/access/requests${queryString ? `?${queryString}` : ''}`);
    },

    async getPluginAccess(pluginId: string) {
        return apiClient.request(`/api/v1/plugins/${pluginId}/access`);
    },

    async getAllAccessGrants(userEmail?: string) {
        const params = userEmail ? `?user_email=${encodeURIComponent(userEmail)}` : '';
        return apiClient.request(`/api/v1/plugins/access/grants${params}`);
    },

    async uploadMicroserviceTemplate(data: {
        plugin_id: string;
        name: string;
        version: string;
        description: string;
        template_repo_url: string;
        template_path: string;
        inputs?: Record<string, any>;
        author?: string;
    }) {
        const formData = new FormData();
        formData.append('plugin_id', data.plugin_id);
        formData.append('name', data.name);
        formData.append('version', data.version);
        formData.append('description', data.description);
        formData.append('template_repo_url', data.template_repo_url);
        formData.append('template_path', data.template_path);
        if (data.inputs) {
            formData.append('inputs', JSON.stringify(data.inputs));
        }
        if (data.author) {
            formData.append('author', data.author);
        }

        // Use raw fetch to avoid Content-Type header being set by apiClient
        const token = localStorage.getItem('access_token');
        const { API_URL } = await import('../../constants/api');
        const response = await fetch(`${API_URL}/api/v1/plugins/upload-template`, {
            method: 'POST',
            credentials: 'include',
            headers: {
                ...(token ? { Authorization: `Bearer ${token}` } : {})
                // Don't set Content-Type - browser will set it automatically with boundary
            },
            body: formData
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: response.statusText }));
            throw new Error(error.detail || 'Request failed');
        }

        return await response.json();
    }
};
