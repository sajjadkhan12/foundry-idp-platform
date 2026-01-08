/**
 * gRPC-Web Client for Auth Service
 * This replaces the REST API client for authentication operations
 */
import { AuthenticationServiceClient } from '../../generated/auth/AuthenticationServiceClientPb';
import { AuthorizationServiceClient } from '../../generated/auth/AuthorizationServiceClientPb';
import { UserServiceClient } from '../../generated/auth/UserServiceClientPb';
import { RoleServiceClient } from '../../generated/auth/RoleServiceClientPb';
import { GroupServiceClient } from '../../generated/auth/GroupServiceClientPb';
import { BusinessUnitServiceClient } from '../../generated/auth/BusinessUnitServiceClientPb';
import { OrganizationServiceClient } from '../../generated/auth/OrganizationServiceClientPb';
import { BusinessUnitGroupServiceClient } from '../../generated/auth/BusinessUnitGroupServiceClientPb';
import { CredentialServiceClient } from '../../generated/auth/CredentialServiceClientPb';

// Import message types
import {
    LoginRequest,
    RefreshTokenRequest,
    LogoutRequest,
    ValidateTokenRequest,
    TokenResponse,
    UserInfo,
    CreateUserRequest,
    UpdateUserRequest,
    GetUserRequest,
    ListUsersRequest,
    GetCurrentUserRequest,
    UpdateCurrentUserRequest,
    ChangePasswordRequest,
    CreateRoleRequest,
    UpdateRoleRequest,
    GetRoleRequest,
    ListRolesRequest,
    AssignRoleRequest,
    CreateGroupRequest,
    UpdateGroupRequest,
    GetGroupRequest,
    ListGroupsRequest,
    AddGroupMemberRequest,
    CreateBusinessUnitRequest,
    UpdateBusinessUnitRequest,
    GetBusinessUnitRequest,
    ListBusinessUnitsRequest,
    AddBusinessUnitMemberRequest,
    PermissionCheckRequest,
    CreateOrganizationRequest,
    UpdateOrganizationRequest,
    GetOrganizationRequest,
    ListOrganizationsRequest,
    GetCurrentOrganizationRequest,
    CreateBusinessUnitGroupRequest,
    UpdateBusinessUnitGroupRequest,
    GetBusinessUnitGroupRequest,
    ListBusinessUnitGroupsRequest,
    AddBusinessUnitGroupMemberRequest,
    RemoveBusinessUnitGroupMemberRequest,
    ListBusinessUnitGroupMembersRequest,
    CreateCredentialRequest,
    UpdateCredentialRequest,
    GetCredentialRequest,
    ListCredentialsRequest,
    DeleteCredentialRequest,
} from '../../generated/auth/auth_pb';

import { getAccessToken, setAccessToken, removeAccessToken } from '../../utils/tokenStorage';

const GRPC_WEB_URL = import.meta.env.VITE_GRPC_WEB_URL || 'http://localhost:8080';

/**
 * gRPC-Web Client for Auth Service
 */
export class AuthGrpcClient {
    private authClient: AuthenticationServiceClient;
    private authzClient: AuthorizationServiceClient;
    private userClient: UserServiceClient;
    private roleClient: RoleServiceClient;
    private groupClient: GroupServiceClient;
    private buClient: BusinessUnitServiceClient;

    constructor() {
        this.authClient = new AuthenticationServiceClient(GRPC_WEB_URL);
        this.authzClient = new AuthorizationServiceClient(GRPC_WEB_URL);
        this.userClient = new UserServiceClient(GRPC_WEB_URL);
        this.roleClient = new RoleServiceClient(GRPC_WEB_URL);
        this.groupClient = new GroupServiceClient(GRPC_WEB_URL);
        this.buClient = new BusinessUnitServiceClient(GRPC_WEB_URL);
        this.orgClient = new OrganizationServiceClient(GRPC_WEB_URL);
        this.buGroupClient = new BusinessUnitGroupServiceClient(GRPC_WEB_URL);
        this.credentialClient = new CredentialServiceClient(GRPC_WEB_URL);
    }

    /**
     * Get metadata with authentication token
     */
    private getMetadata(): { [key: string]: string } {
        const token = getAccessToken();
        return token ? { authorization: `Bearer ${token}` } : {};
    }

    /**
     * Login
     */
    async login(identifier: string, password: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new LoginRequest();
            request.setIdentifier(identifier);
            request.setPassword(password);

            this.authClient.login(request, {}, (err, response) => {
                if (err) {
                    // Normalize authentication errors to generic message for security
                    const isAuthError = err.code === 16 || // UNAUTHENTICATED
                                      err.code === 7 ||   // PERMISSION_DENIED
                                      err.message?.toLowerCase().includes('invalid') ||
                                      err.message?.toLowerCase().includes('incorrect') ||
                                      err.message?.toLowerCase().includes('wrong') ||
                                      err.message?.toLowerCase().includes('unauthorized');
                    
                    if (isAuthError) {
                        reject(new Error('Invalid credentials'));
                    } else {
                        reject(new Error(err.message || 'Login failed'));
                    }
                } else {
                    const result = {
                        access_token: response.getAccessToken(),
                        token_type: response.getTokenType(),
                        refresh_token: response.getRefreshToken(),
                        user: {
                            id: response.getUser()?.getId(),
                            email: response.getUser()?.getEmail(),
                            username: response.getUser()?.getUsername(),
                            full_name: response.getUser()?.getFullName(),
                            roles: response.getUser()?.getRolesList() || [],
                            avatar_url: response.getUser()?.getAvatarUrl(),
                            is_active: response.getUser()?.getIsActive(),
                            is_admin: response.getUser()?.getIsAdmin(),
                            created_at: response.getUser()?.getCreatedAt(),
                            organization_id: response.getUser()?.getOrganizationId(),
                        }
                    };
                    setAccessToken(result.access_token);
                    resolve(result);
                }
            });
        });
    }

    /**
     * Refresh token
     */
    async refreshToken(refreshToken?: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new RefreshTokenRequest();
            // Get refresh token from cookie or parameter
            const token = refreshToken || this.getRefreshTokenFromCookie();
            if (!token) {
                reject(new Error('Refresh token required'));
                return;
            }
            request.setRefreshToken(token);

            this.authClient.refreshToken(request, {}, (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    const result = {
                        access_token: response.getAccessToken(),
                        token_type: response.getTokenType(),
                        user: {
                            id: response.getUser()?.getId(),
                            email: response.getUser()?.getEmail(),
                            username: response.getUser()?.getUsername(),
                            full_name: response.getUser()?.getFullName(),
                            roles: response.getUser()?.getRolesList() || [],
                            avatar_url: response.getUser()?.getAvatarUrl(),
                            is_active: response.getUser()?.getIsActive(),
                            is_admin: response.getUser()?.getIsAdmin(),
                            created_at: response.getUser()?.getCreatedAt(),
                            organization_id: response.getUser()?.getOrganizationId(),
                        }
                    };
                    setAccessToken(result.access_token);
                    resolve(result);
                }
            });
        });
    }

    /**
     * Logout
     */
    async logout(refreshToken?: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new LogoutRequest();
            const token = refreshToken || this.getRefreshTokenFromCookie();
            if (token) {
                request.setRefreshToken(token);
            }

            this.authClient.logout(request, {}, (err) => {
                if (err) {
                    // Logout failures are not critical
                    console.warn('Logout error:', err.message);
                }
                removeAccessToken();
                resolve();
            });
        });
    }

    /**
     * Validate token
     */
    async validateToken(token: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ValidateTokenRequest();
            request.setToken(token);

            this.authClient.validateToken(request, {}, (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        user_id: response.getUserId(),
                        email: response.getEmail(),
                        username: response.getUsername(),
                        organization_id: response.getOrganizationId(),
                        is_active: response.getIsActive(),
                        roles: response.getRolesList() || []
                    });
                }
            });
        });
    }

    /**
     * Get current user
     */
    async getCurrentUser(): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new GetCurrentUserRequest();
            const token = getAccessToken();
            if (!token) {
                reject(new Error('Token required'));
                return;
            }
            request.setToken(token);

            this.userClient.getCurrentUser(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        id: response.getId(),
                        email: response.getEmail(),
                        username: response.getUsername(),
                        full_name: response.getFullName(),
                        roles: response.getRolesList() || [],
                        avatar_url: response.getAvatarUrl(),
                        is_active: response.getIsActive(),
                        is_admin: response.getIsAdmin(),
                        created_at: response.getCreatedAt(),
                        organization_id: response.getOrganizationId(),
                    });
                }
            });
        });
    }

    /**
     * List users
     */
    async listUsers(params?: { skip?: number; limit?: number; search?: string; role_filter?: string }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ListUsersRequest();
            request.setSkip(params?.skip || 0);
            request.setLimit(params?.limit || 50);
            request.setSearch(params?.search || '');
            request.setRoleFilter(params?.role_filter || '');

            this.userClient.listUsers(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        users: response.getUsersList().map(u => ({
                            id: u.getId(),
                            email: u.getEmail(),
                            username: u.getUsername(),
                            full_name: u.getFullName(),
                            roles: u.getRolesList() || [],
                            avatar_url: u.getAvatarUrl(),
                            is_active: u.getIsActive(),
                            is_admin: u.getIsAdmin(),
                            created_at: u.getCreatedAt(),
                            organization_id: u.getOrganizationId(),
                        })),
                        total: response.getTotal(),
                        skip: response.getSkip(),
                        limit: response.getLimit(),
                    });
                }
            });
        });
    }

    /**
     * Helper to get refresh token from cookie
     */
    private getRefreshTokenFromCookie(): string | null {
        // Cookies are handled by the browser, but we need to get it
        // This is a simplified version - in production, you might need a different approach
        const cookies = document.cookie.split(';');
        for (const cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'refresh_token') {
                return decodeURIComponent(value);
            }
        }
        return null;
    }

    /**
     * Organization methods
     */
    async createOrganization(data: { name: string; slug: string; description?: string }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new CreateOrganizationRequest();
            request.setName(data.name);
            request.setSlug(data.slug);
            if (data.description) {
                request.setDescription(data.description);
            }

            this.orgClient.createOrganization(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        id: response.getId(),
                        name: response.getName(),
                        slug: response.getSlug(),
                        description: response.getDescription(),
                        is_active: response.getIsActive(),
                        created_at: response.getCreatedAt(),
                        updated_at: response.getUpdatedAt(),
                    });
                }
            });
        });
    }

    async getOrganization(organizationId: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new GetOrganizationRequest();
            request.setOrganizationId(organizationId);

            this.orgClient.getOrganization(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        id: response.getId(),
                        name: response.getName(),
                        slug: response.getSlug(),
                        description: response.getDescription(),
                        is_active: response.getIsActive(),
                        created_at: response.getCreatedAt(),
                        updated_at: response.getUpdatedAt(),
                    });
                }
            });
        });
    }

    async getCurrentOrganization(): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new GetCurrentOrganizationRequest();
            // Get user ID from token or current user context
            // For now, we'll need to pass it - this should be handled by the backend
            const token = getAccessToken();
            if (!token) {
                reject(new Error('Token required'));
                return;
            }

            this.orgClient.getCurrentOrganization(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        id: response.getId(),
                        name: response.getName(),
                        slug: response.getSlug(),
                        description: response.getDescription(),
                        is_active: response.getIsActive(),
                        created_at: response.getCreatedAt(),
                        updated_at: response.getUpdatedAt(),
                    });
                }
            });
        });
    }

    async listOrganizations(params?: { skip?: number; limit?: number }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ListOrganizationsRequest();
            request.setSkip(params?.skip || 0);
            request.setLimit(params?.limit || 100);

            this.orgClient.listOrganizations(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        organizations: response.getOrganizationsList().map(org => ({
                            id: org.getId(),
                            name: org.getName(),
                            slug: org.getSlug(),
                            description: org.getDescription(),
                            is_active: org.getIsActive(),
                            created_at: org.getCreatedAt(),
                            updated_at: org.getUpdatedAt(),
                        })),
                    });
                }
            });
        });
    }

    /**
     * Business Unit Group methods
     */
    async createBusinessUnitGroup(data: {
        business_unit_id: string;
        name: string;
        description?: string;
        role_id: string;
    }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new CreateBusinessUnitGroupRequest();
            request.setBusinessUnitId(data.business_unit_id);
            request.setName(data.name);
            if (data.description) {
                request.setDescription(data.description);
            }
            request.setRoleId(data.role_id);

            this.buGroupClient.createBusinessUnitGroup(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        id: response.getId(),
                        business_unit_id: response.getBusinessUnitId(),
                        name: response.getName(),
                        description: response.getDescription(),
                        created_at: response.getCreatedAt(),
                        updated_at: response.getUpdatedAt(),
                    });
                }
            });
        });
    }

    async listBusinessUnitGroups(businessUnitId: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ListBusinessUnitGroupsRequest();
            request.setBusinessUnitId(businessUnitId);

            this.buGroupClient.listBusinessUnitGroups(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        groups: response.getGroupsList().map(g => ({
                            id: g.getId(),
                            business_unit_id: g.getBusinessUnitId(),
                            name: g.getName(),
                            description: g.getDescription(),
                            created_at: g.getCreatedAt(),
                            updated_at: g.getUpdatedAt(),
                        })),
                    });
                }
            });
        });
    }

    async addBusinessUnitGroupMember(data: {
        business_unit_id: string;
        group_id: string;
        user_id: string;
    }): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new AddBusinessUnitGroupMemberRequest();
            request.setBusinessUnitId(data.business_unit_id);
            request.setGroupId(data.group_id);
            request.setUserId(data.user_id);

            this.buGroupClient.addBusinessUnitGroupMember(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    /**
     * Credential methods
     */
    async createCredential(data: {
        name: string;
        provider: string;
        credentials: any; // JSON object
    }): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new CreateCredentialRequest();
            request.setName(data.name);
            request.setProvider(data.provider);
            request.setCredentials(JSON.stringify(data.credentials));

            this.credentialClient.createCredential(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        id: response.getId(),
                        name: response.getName(),
                        provider: response.getProvider(),
                        created_at: response.getCreatedAt(),
                        updated_at: response.getUpdatedAt(),
                    });
                }
            });
        });
    }

    async listCredentials(): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new ListCredentialsRequest();

            this.credentialClient.listCredentials(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        credentials: response.getCredentialsList().map(c => ({
                            id: c.getId(),
                            name: c.getName(),
                            provider: c.getProvider(),
                            created_at: c.getCreatedAt(),
                            updated_at: c.getUpdatedAt(),
                        })),
                    });
                }
            });
        });
    }

    async getCredential(credentialId: string): Promise<any> {
        return new Promise((resolve, reject) => {
            const request = new GetCredentialRequest();
            request.setCredentialId(credentialId);

            this.credentialClient.getCredential(request, this.getMetadata(), (err, response) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve({
                        id: response.getId(),
                        name: response.getName(),
                        provider: response.getProvider(),
                        created_at: response.getCreatedAt(),
                        updated_at: response.getUpdatedAt(),
                    });
                }
            });
        });
    }

    async deleteCredential(credentialId: string): Promise<void> {
        return new Promise((resolve, reject) => {
            const request = new DeleteCredentialRequest();
            request.setCredentialId(credentialId);

            this.credentialClient.deleteCredential(request, this.getMetadata(), (err) => {
                if (err) {
                    reject(new Error(err.message));
                } else {
                    resolve();
                }
            });
        });
    }

    // Add more methods for users, roles, groups, business units as needed...
}

// Export singleton instance
export const authGrpcClient = new AuthGrpcClient();
