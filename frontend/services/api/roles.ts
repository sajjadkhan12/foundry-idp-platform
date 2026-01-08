import { apiClient } from './client';
import { createCrudApi } from './helpers';
import { usersApi } from './users';
import { groupsApi } from './groups';

/**
 * Roles API
 * Handles role and permission management
 */
const baseCrud = createCrudApi('/api/v1/roles');

export const rolesApi = {
    ...baseCrud,

    // Aliases for backward compatibility
    async listRoles(params?: { skip?: number; limit?: number }) {
        return baseCrud.list(params);
    },

    async getRole(id: string) {
        return baseCrud.get(id);
    },

    async createRole(data: any) {
        return baseCrud.create(data);
    },

    async updateRole(id: string, data: any) {
        return baseCrud.update(id, data);
    },

    async deleteRole(id: string) {
        return baseCrud.delete(id);
    },

    async getAdminStats() {
        // Calculate stats from existing APIs
        try {
            // Fetch all data in parallel
            const [usersResponse, rolesResponse, groupsResponse] = await Promise.all([
                usersApi.listUsers({ limit: 1000 }).catch(() => ({ users: [], total: 0 })),
                rolesApi.listRoles().catch(() => []),
                groupsApi.listGroups({ limit: 1000 }).catch(() => ({ items: [], total: 0 }))
            ]);

            // Handle different response formats
            const users = Array.isArray(usersResponse) 
                ? usersResponse 
                : (usersResponse?.users || usersResponse?.items || []);
            
            const roles = Array.isArray(rolesResponse) 
                ? rolesResponse 
                : (rolesResponse?.items || rolesResponse?.roles || []);
            
            const groups = Array.isArray(groupsResponse)
                ? groupsResponse
                : (groupsResponse?.items || groupsResponse?.groups || []);

            // Calculate user stats
            const total_users = users.length;
            const active_users = users.filter((u: any) => u.is_active !== false).length;
            const inactive_users = total_users - active_users;

            // Calculate role distribution
            const roleCounts: Record<string, number> = {};
            users.forEach((user: any) => {
                const userRoles = user.roles || [];
                userRoles.forEach((role: string) => {
                    roleCounts[role] = (roleCounts[role] || 0) + 1;
                });
            });

            const role_distribution = Object.entries(roleCounts).map(([role, count]) => ({
                role,
                count: count as number
            }));

            return {
                total_users,
                active_users,
                inactive_users,
                total_roles: roles.length,
                total_groups: groups.length,
                role_distribution
            };
        } catch (error) {
            console.error('Failed to fetch admin stats:', error);
            // Return default structure with empty role_distribution array
            return {
                total_users: 0,
                active_users: 0,
                inactive_users: 0,
                total_roles: 0,
                total_groups: 0,
                role_distribution: []
            };
        }
    }
};
