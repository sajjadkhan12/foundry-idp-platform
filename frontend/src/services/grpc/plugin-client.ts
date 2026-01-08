/**
 * gRPC-Web Client for Plugin Service
 */
import { PluginServiceClient } from '../../generated/plugin/PluginServiceClientPb';
import {
    ListPluginsRequest,
    GetPluginRequest,
    DeletePluginRequest,
    LockPluginRequest,
    UnlockPluginRequest,
    ListPluginVersionsRequest,
    GetPluginVersionRequest,
    RequestPluginAccessRequest,
    GrantPluginAccessRequest,
    RejectPluginAccessRequest,
    RevokePluginAccessRequest,
    RestorePluginAccessRequest,
    ListAccessRequestsRequest,
    ListAccessGrantsRequest,
} from '../../generated/plugin/plugin_pb';

import { getAccessToken } from '../../utils/tokenStorage';

const GRPC_WEB_URL = import.meta.env.VITE_GRPC_WEB_URL || 'http://localhost:8080';

/**
 * gRPC-Web Client for Plugin Service
 */
export class PluginGrpcClient {
    private client: PluginServiceClient;

    constructor() {
        this.client = new PluginServiceClient(GRPC_WEB_URL);
    }

    /**
     * Get metadata with authentication token
     */
    private getMetadata(): { [key: string]: string } {
        const token = getAccessToken();
        return token ? { authorization: `Bearer ${token}` } : {};
    }

    /**
     * List plugins
     */
    async listPlugins(params?: { skip?: number; limit?: number }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ListPluginsRequest();
            request.setSkip(params?.skip || 0);
            request.setLimit(params?.limit || 50);

            this.client.listPlugins(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        plugins: response.getPluginsList().map(p => ({
                            id: p.getId(),
                            name: p.getName(),
                            description: p.getDescription(),
                            author: p.getAuthor(),
                            is_locked: p.getIsLocked(),
                            deployment_type: p.getDeploymentType(),
                            created_at: p.getCreatedAt(),
                            updated_at: p.getUpdatedAt(),
                        })),
                        total: response.getTotal(),
                    });
                }
            });
        });
    }

    /**
     * Get plugin by ID
     */
    async getPlugin(pluginId: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new GetPluginRequest();
            request.setPluginId(pluginId);

            this.client.getPlugin(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    const plugin = response.getPlugin();
                    resolve({
                        id: plugin?.getId(),
                        name: plugin?.getName(),
                        description: plugin?.getDescription(),
                        author: plugin?.getAuthor(),
                        is_locked: plugin?.getIsLocked(),
                        deployment_type: plugin?.getDeploymentType(),
                        created_at: plugin?.getCreatedAt(),
                        updated_at: plugin?.getUpdatedAt(),
                    });
                }
            });
        });
    }

    /**
     * Delete plugin
     */
    async deletePlugin(pluginId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new DeletePluginRequest();
            request.setPluginId(pluginId);

            this.client.deletePlugin(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * Lock plugin
     */
    async lockPlugin(pluginId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new LockPluginRequest();
            request.setPluginId(pluginId);

            this.client.lockPlugin(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * Unlock plugin
     */
    async unlockPlugin(pluginId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new UnlockPluginRequest();
            request.setPluginId(pluginId);

            this.client.unlockPlugin(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * List plugin versions
     */
    async listPluginVersions(pluginId: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ListPluginVersionsRequest();
            request.setPluginId(pluginId);

            this.client.listPluginVersions(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        versions: response.getVersionsList().map(v => ({
                            id: v.getId(),
                            plugin_id: v.getPluginId(),
                            version: v.getVersion(),
                            manifest: JSON.parse(v.getManifest()),
                            storage_path: v.getStoragePath(),
                            git_repo_url: v.getGitRepoUrl(),
                            git_branch: v.getGitBranch(),
                            template_repo_url: v.getTemplateRepoUrl(),
                            template_path: v.getTemplatePath(),
                            created_at: v.getCreatedAt(),
                        })),
                    });
                }
            });
        });
    }

    /**
     * Get plugin version
     */
    async getPluginVersion(pluginId: string, version: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new GetPluginVersionRequest();
            request.setPluginId(pluginId);
            request.setVersion(version);

            this.client.getPluginVersion(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    const version = response.getVersion();
                    resolve({
                        id: version?.getId(),
                        plugin_id: version?.getPluginId(),
                        version: version?.getVersion(),
                        manifest: JSON.parse(version?.getManifest() || '{}'),
                        storage_path: version?.getStoragePath(),
                        git_repo_url: version?.getGitRepoUrl(),
                        git_branch: version?.getGitBranch(),
                        template_repo_url: version?.getTemplateRepoUrl(),
                        template_path: version?.getTemplatePath(),
                        created_at: version?.getCreatedAt(),
                    });
                }
            });
        });
    }

    /**
     * Request plugin access
     */
    async requestPluginAccess(pluginId: string, reason?: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new RequestPluginAccessRequest();
            request.setPluginId(pluginId);
            if (reason) {
                request.setReason(reason);
            }

            this.client.requestPluginAccess(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    const accessRequest = response.getAccessRequest();
                    resolve({
                        id: accessRequest?.getId(),
                        plugin_id: accessRequest?.getPluginId(),
                        user_id: accessRequest?.getUserId(),
                        reason: accessRequest?.getReason(),
                        status: accessRequest?.getStatus(),
                        created_at: accessRequest?.getCreatedAt(),
                        updated_at: accessRequest?.getUpdatedAt(),
                    });
                }
            });
        });
    }

    /**
     * Grant plugin access
     */
    async grantPluginAccess(requestId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new GrantPluginAccessRequest();
            request.setRequestId(requestId);

            this.client.grantPluginAccess(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * Reject plugin access request
     */
    async rejectPluginAccessRequest(requestId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new RejectPluginAccessRequest();
            request.setRequestId(requestId);

            this.client.rejectPluginAccessRequest(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * Revoke plugin access
     */
    async revokePluginAccess(pluginId: string, userId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new RevokePluginAccessRequest();
            request.setPluginId(pluginId);
            request.setUserId(userId);

            this.client.revokePluginAccess(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * Restore plugin access
     */
    async restorePluginAccess(pluginId: string, userId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new RestorePluginAccessRequest();
            request.setPluginId(pluginId);
            request.setUserId(userId);

            this.client.restorePluginAccess(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * List access requests
     */
    async listAccessRequests(params?: { plugin_id?: string; status?: string }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ListAccessRequestsRequest();
            if (params?.plugin_id) {
                request.setPluginId(params.plugin_id);
            }
            if (params?.status) {
                request.setStatus(params.status);
            }

            this.client.listAccessRequests(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        requests: response.getRequestsList().map(r => ({
                            id: r.getId(),
                            plugin_id: r.getPluginId(),
                            user_id: r.getUserId(),
                            user_email: r.getUserEmail(),
                            user_name: r.getUserName(),
                            reason: r.getReason(),
                            status: r.getStatus(),
                            created_at: r.getCreatedAt(),
                            updated_at: r.getUpdatedAt(),
                        })),
                    });
                }
            });
        });
    }

    /**
     * List access grants
     */
    async listAccessGrants(pluginId?: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ListAccessGrantsRequest();
            if (pluginId) {
                request.setPluginId(pluginId);
            }

            this.client.listAccessGrants(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        grants: response.getGrantsList().map(g => ({
                            id: g.getId(),
                            plugin_id: g.getPluginId(),
                            user_id: g.getUserId(),
                            user_email: g.getUserEmail(),
                            user_name: g.getUserName(),
                            granted_at: g.getGrantedAt(),
                            revoked_at: g.getRevokedAt(),
                            is_active: g.getIsActive(),
                        })),
                    });
                }
            });
        });
    }
}

// Export singleton instance
export const pluginGrpcClient = new PluginGrpcClient();
