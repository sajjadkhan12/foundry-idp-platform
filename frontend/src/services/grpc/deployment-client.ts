/**
 * gRPC-Web Client for Deployment Service
 */
import { DeploymentServiceClient } from '../../generated/deployment/DeploymentServiceClientPb';
import {
    CreateDeploymentRequest,
    GetDeploymentRequest,
    UpdateDeploymentRequest,
    DeleteDeploymentRequest,
    ListDeploymentsRequest,
} from '../../generated/deployment/deployment_pb';

import { getAccessToken } from '../../utils/tokenStorage';

const GRPC_WEB_URL = import.meta.env.VITE_GRPC_WEB_URL || 'http://localhost:8080';

/**
 * gRPC-Web Client for Deployment Service
 */
export class DeploymentGrpcClient {
    private client: DeploymentServiceClient;

    constructor() {
        this.client = new DeploymentServiceClient(GRPC_WEB_URL);
    }

    /**
     * Get metadata with authentication token
     */
    private getMetadata(): { [key: string]: string } {
        const token = getAccessToken();
        return token ? { authorization: `Bearer ${token}` } : {};
    }

    /**
     * Create deployment
     */
    async createDeployment(data: {
        name: string;
        deployment_type: string;
        plugin_id: string;
        version: string;
        environment: string;
        business_unit_id?: string;
        inputs?: any;
        cost_center?: string;
        project_code?: string;
    }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new CreateDeploymentRequest();
            request.setName(data.name);
            request.setDeploymentType(data.deployment_type);
            request.setPluginId(data.plugin_id);
            request.setVersion(data.version);
            request.setEnvironment(data.environment);
            if (data.business_unit_id) {
                request.setBusinessUnitId(data.business_unit_id);
            }
            if (data.inputs) {
                request.setInputs(JSON.stringify(data.inputs));
            }
            if (data.cost_center) {
                request.setCostCenter(data.cost_center);
            }
            if (data.project_code) {
                request.setProjectCode(data.project_code);
            }

            this.client.createDeployment(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve(this._deploymentResponseToObject(response));
                }
            });
        });
    }

    /**
     * Get deployment by ID
     */
    async getDeployment(deploymentId: string, includeTags: boolean = true): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new GetDeploymentRequest();
            request.setDeploymentId(deploymentId);
            request.setIncludeTags(includeTags);

            this.client.getDeployment(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve(this._deploymentResponseToObject(response));
                }
            });
        });
    }

    /**
     * Update deployment
     */
    async updateDeployment(
        deploymentId: string,
        data: {
            name?: string;
            environment?: string;
            inputs?: any;
            cost_center?: string;
            project_code?: string;
            status?: string;
        }
    ): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new UpdateDeploymentRequest();
            request.setDeploymentId(deploymentId);
            if (data.name) {
                request.setName(data.name);
            }
            if (data.environment) {
                request.setEnvironment(data.environment);
            }
            if (data.inputs) {
                request.setInputs(JSON.stringify(data.inputs));
            }
            if (data.cost_center) {
                request.setCostCenter(data.cost_center);
            }
            if (data.project_code) {
                request.setProjectCode(data.project_code);
            }
            if (data.status) {
                request.setStatus(data.status);
            }

            this.client.updateDeployment(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve(this._deploymentResponseToObject(response));
                }
            });
        });
    }

    /**
     * Delete deployment
     */
    async deleteDeployment(deploymentId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new DeleteDeploymentRequest();
            request.setDeploymentId(deploymentId);

            this.client.deleteDeployment(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * List deployments
     */
    async listDeployments(params?: {
        search?: string;
        status?: string;
        cloud_provider?: string;
        plugin_id?: string;
        environment?: string;
        tags?: string;
        user_id?: string;
        business_unit_id?: string;
        skip?: number;
        limit?: number;
    }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ListDeploymentsRequest();
            if (params?.search) {
                request.setSearch(params.search);
            }
            if (params?.status) {
                request.setStatus(params.status);
            }
            if (params?.cloud_provider) {
                request.setCloudProvider(params.cloud_provider);
            }
            if (params?.plugin_id) {
                request.setPluginId(params.plugin_id);
            }
            if (params?.environment) {
                request.setEnvironment(params.environment);
            }
            if (params?.tags) {
                request.setTags(params.tags);
            }
            if (params?.user_id) {
                request.setUserId(params.user_id);
            }
            if (params?.business_unit_id) {
                request.setBusinessUnitId(params.business_unit_id);
            }
            request.setSkip(params?.skip || 0);
            request.setLimit(params?.limit || 50);

            this.client.listDeployments(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        deployments: response.getDeploymentsList().map(d => this._deploymentResponseToObject(d)),
                        total: response.getTotal(),
                        skip: response.getSkip(),
                        limit: response.getLimit(),
                    });
                }
            });
        });
    }

    /**
     * Convert DeploymentResponse proto to object
     */
    private _deploymentResponseToObject(response: any): any {
        return {
            id: response.getId(),
            name: response.getName(),
            status: response.getStatus(),
            deployment_type: response.getDeploymentType(),
            environment: response.getEnvironment(),
            plugin_id: response.getPluginId(),
            version: response.getVersion(),
            stack_name: response.getStackName(),
            cloud_provider: response.getCloudProvider(),
            region: response.getRegion(),
            git_branch: response.getGitBranch(),
            github_repo_url: response.getGithubRepoUrl(),
            github_repo_name: response.getGithubRepoName(),
            ci_cd_status: response.getCiCdStatus(),
            ci_cd_run_id: response.getCiCdRunId(),
            ci_cd_run_url: response.getCiCdRunUrl(),
            ci_cd_updated_at: response.getCiCdUpdatedAt(),
            update_status: response.getUpdateStatus(),
            last_update_job_id: response.getLastUpdateJobId(),
            last_update_error: response.getLastUpdateError(),
            last_update_attempted_at: response.getLastUpdateAttemptedAt(),
            inputs: JSON.parse(response.getInputs() || '{}'),
            outputs: JSON.parse(response.getOutputs() || '{}'),
            user_id: response.getUserId(),
            business_unit_id: response.getBusinessUnitId(),
            cost_center: response.getCostCenter(),
            project_code: response.getProjectCode(),
            created_at: response.getCreatedAt(),
            updated_at: response.getUpdatedAt(),
            tags: response.getTagsList().map((t: any) => ({
                id: t.getId(),
                deployment_id: t.getDeploymentId(),
                key: t.getKey(),
                value: t.getValue(),
                created_at: t.getCreatedAt(),
            })),
        };
    }
}

// Export singleton instance
export const deploymentGrpcClient = new DeploymentGrpcClient();
