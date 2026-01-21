import { apiClient } from './client';

export interface Organization {
  id: string;
  name: string;
  slug: string;
  description?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateOrganizationWithAdminRequest {
  name: string;
  slug: string;
  description?: string;
  admin_email: string;
  admin_username: string;
  admin_password: string;
  admin_full_name?: string;
}

export interface CreateOrganizationWithAdminResponse {
  organization: Organization;
  admin_user: {
    id: string;
    email: string;
    username: string;
    full_name: string;
  };
  default_business_unit: {
    id: string;
    name: string;
    slug: string;
    description: string;
    organization_id: string;
    is_active: boolean;
  };
}

export const organizationsApi = {
  /**
   * List all organizations (super admin only)
   */
  listOrganizations: async (skip: number = 0, limit: number = 100): Promise<Organization[]> => {
    const response = await apiClient.get('/api/v1/organizations', {
      params: { skip, limit }
    });
    return response.data;
  },

  /**
   * Get organization by ID
   */
  getOrganization: async (id: string): Promise<Organization> => {
    const response = await apiClient.get(`/api/v1/organizations/${id}`);
    return response.data;
  },

  /**
   * Create organization with admin user (super admin only)
   */
  createOrganizationWithAdmin: async (
    data: CreateOrganizationWithAdminRequest
  ): Promise<CreateOrganizationWithAdminResponse> => {
    const response = await apiClient.post('/api/v1/organizations/create-with-admin', data);
    return response.data;
  },

  /**
   * Delete organization (super admin only)
   */
  deleteOrganization: async (id: string): Promise<void> => {
    await apiClient.delete(`/api/v1/organizations/${id}`);
  },

  /**
   * Update organization
   */
  updateOrganization: async (
    id: string,
    data: Partial<Organization>
  ): Promise<Organization> => {
    const response = await apiClient.put(`/api/v1/organizations/${id}`, data);
    return response.data;
  }
};
