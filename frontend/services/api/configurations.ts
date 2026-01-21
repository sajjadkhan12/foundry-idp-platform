import { apiClient } from './client';

export interface Configuration {
  config_key: string;
  config_value: string;
  organization_id?: string;
  business_unit_id?: string;
}

export const configurationsApi = {
  /**
   * List all configurations for current organization/BU
   */
  listConfigurations: async (businessUnitId?: string): Promise<Record<string, string>> => {
    const params = businessUnitId ? { business_unit_id: businessUnitId } : {};
    const response = await apiClient.get('/api/v1/configurations', { params });
    return response.data;
  },

  /**
   * Get configuration value by key
   */
  getConfiguration: async (
    configKey: string,
    businessUnitId?: string
  ): Promise<Configuration> => {
    const params = businessUnitId ? { business_unit_id: businessUnitId } : {};
    const response = await apiClient.get(`/api/v1/configurations/${configKey}`, { params });
    return response.data;
  },

  /**
   * Set configuration value
   */
  setConfiguration: async (
    configKey: string,
    configValue: string,
    businessUnitId?: string
  ): Promise<Configuration> => {
    const response = await apiClient.post('/api/v1/configurations', {
      config_key: configKey,
      config_value: configValue,
      business_unit_id: businessUnitId
    });
    return response.data;
  },

  /**
   * Delete configuration
   */
  deleteConfiguration: async (
    configKey: string,
    businessUnitId?: string
  ): Promise<void> => {
    const params = businessUnitId ? { business_unit_id: businessUnitId } : {};
    await apiClient.delete(`/api/v1/configurations/${configKey}`, { params });
  }
};
