import { createCrudApi } from './helpers';
import { apiClient } from './client';

/**
 * Deployments API
 * Handles deployment CRUD operations
 * 
 * NOTE: This service now uses gRPC-Web via deploymentGrpcClient for CRUD operations.
 * History, CI/CD, and other complex operations still use REST.
 */
let useGrpc = false;
try {
    const { deploymentGrpcClient } = require('../../src/services/grpc');
    useGrpc = !!deploymentGrpcClient;
} catch (e) {
    // gRPC not available, use REST fallback (silently - REST API works fine)
    // Uncomment below if you want to see the warning during development
    // console.warn('gRPC clients not available, using REST API. Run "npm run generate-proto" to enable gRPC.');
}

const baseApi = createCrudApi('/api/v1/deployments');

export const deploymentsApi = {
    ...baseApi,
    
    // Alias methods for backward compatibility
    getDeployment: async (id: string) => {
        if (useGrpc) {
            try {
                const { deploymentGrpcClient } = require('../../src/services/grpc');
                return await deploymentGrpcClient.getDeployment(id);
            } catch (error) {
                console.error('gRPC getDeployment failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return baseApi.get(id);
    },
    
    deleteDeployment: async (id: string) => {
        if (useGrpc) {
            try {
                const { deploymentGrpcClient } = require('../../src/services/grpc');
                await deploymentGrpcClient.deleteDeployment(id);
                return { success: true };
            } catch (error) {
                console.error('gRPC deleteDeployment failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return baseApi.delete(id);
    },
    
    listDeployments: async (params?: any) => {
        if (useGrpc) {
            try {
                const { deploymentGrpcClient } = require('../../src/services/grpc');
                const result = await deploymentGrpcClient.listDeployments(params);
                return result.deployments;
            } catch (error) {
                console.error('gRPC listDeployments failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return baseApi.list(params);
    },
    
    createDeployment: async (data: any) => {
        if (useGrpc) {
            try {
                const { deploymentGrpcClient } = require('../../src/services/grpc');
                return await deploymentGrpcClient.createDeployment(data);
            } catch (error) {
                console.error('gRPC createDeployment failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return baseApi.create(data);
    },
    
    // Update deployment with new inputs
    async updateDeployment(deploymentId: string, data: { inputs?: Record<string, any>; tags?: Record<string, string>; cost_center?: string; project_code?: string; environment?: string; status?: string }) {
        if (useGrpc) {
            try {
                const { deploymentGrpcClient } = require('../../src/services/grpc');
                return await deploymentGrpcClient.updateDeployment(deploymentId, {
                    inputs: data.inputs,
                    cost_center: data.cost_center,
                    project_code: data.project_code,
                    environment: data.environment,
                    status: data.status
                });
            } catch (error) {
                console.error('gRPC updateDeployment failed, falling back to REST:', error);
                // Fall through to REST
            }
        }
        return apiClient.request(`/api/v1/deployments/${deploymentId}`, {
            method: 'PUT',
            body: JSON.stringify(data)
        });
    },
    
    // Retry a failed deployment
    async retryDeployment(deploymentId: string) {
        return apiClient.request(`/api/v1/deployments/${deploymentId}/retry`, {
            method: 'POST'
        });
    },
    
    // CI/CD status for microservices
    async getCICDStatus(deploymentId: string) {
        return apiClient.request(`/api/v1/deployments/${deploymentId}/ci-cd-status`);
    },
    
    // Repository information for microservices
    async getRepositoryInfo(deploymentId: string) {
        return apiClient.request(`/api/v1/deployments/${deploymentId}/repository`);
    },
    
    // Sync CI/CD status manually
    async syncCICDStatus(deploymentId: string) {
        return apiClient.request(`/api/v1/deployments/${deploymentId}/sync-ci-cd`, {
            method: 'POST'
        });
    },
    
    // Get deployment history
    async getDeploymentHistory(deploymentId: string) {
        return apiClient.request(`/api/v1/deployments/${deploymentId}/history`);
    },
    
    // Rollback deployment to a previous version
    async rollbackDeployment(deploymentId: string, versionNumber: number) {
        return apiClient.request(`/api/v1/deployments/${deploymentId}/rollback/${versionNumber}`, {
            method: 'POST'
        });
    }
};
