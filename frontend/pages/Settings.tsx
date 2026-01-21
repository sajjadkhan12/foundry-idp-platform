import React, { useState, useEffect } from 'react';
import { Save, Bell, Lock, Globe, Database, Settings as SettingsIcon, Key, Cloud, Github, Loader2, CheckCircle2, AlertCircle, Eye, EyeOff, Building2, ShieldCheck, Terminal, ExternalLink, Info } from 'lucide-react';
import { configurationsApi } from '../services/api/configurations';
import { useAuth } from '../contexts/AuthContext';
import { API_URL } from '../constants/api';

type Tab = 'general' | 'notifications' | 'api' | 'infrastructure';

export const SettingsPage: React.FC = () => {
  const { user, isAdmin, isSuperAdmin } = useAuth();
  const [activeTab, setActiveTab] = useState<Tab>('general');
  const [emailNotifs, setEmailNotifs] = useState(true);
  const [slackNotifs, setSlackNotifs] = useState(false);

  // Organization configuration state
  const [configs, setConfigs] = useState<Record<string, string>>({});
  const [loadingConfigs, setLoadingConfigs] = useState(false);
  const [savingConfig, setSavingConfig] = useState(false);
  const [showPasswords, setShowPasswords] = useState<Record<string, boolean>>({});
  const [configMessage, setConfigMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

  const [orgConfigForm, setOrgConfigForm] = useState({
    PULUMI_ACCESS_TOKEN: '',
    PULUMI_ORG: '',
    PULUMI_ESC_ENVIRONMENT_AWS: '',
    PULUMI_ESC_ENVIRONMENT_GCP: '',
    PULUMI_ESC_ENVIRONMENT_AZURE: '',
    GITHUB_TOKEN: '',
    GITHUB_REPOSITORY: '',
    MICROSERVICE_REPO_ORG: ''
  });

  useEffect(() => {
    if (activeTab === 'infrastructure' && isAdmin) {
      fetchConfigurations();
    }
  }, [activeTab, isAdmin]);

  const fetchConfigurations = async () => {
    setLoadingConfigs(true);
    try {
      const data = await configurationsApi.listConfigurations();
      setConfigs(data);
      // Populate form with existing configs
      setOrgConfigForm({
        PULUMI_ACCESS_TOKEN: data.PULUMI_ACCESS_TOKEN || '',
        PULUMI_ORG: data.PULUMI_ORG || '',
        PULUMI_ESC_ENVIRONMENT_AWS: data.PULUMI_ESC_ENVIRONMENT_AWS || '',
        PULUMI_ESC_ENVIRONMENT_GCP: data.PULUMI_ESC_ENVIRONMENT_GCP || '',
        PULUMI_ESC_ENVIRONMENT_AZURE: data.PULUMI_ESC_ENVIRONMENT_AZURE || '',
        GITHUB_TOKEN: data.GITHUB_TOKEN || '',
        GITHUB_REPOSITORY: data.GITHUB_REPOSITORY || data.GITHUB_REPO || '',
        MICROSERVICE_REPO_ORG: data.MICROSERVICE_REPO_ORG || ''
      });
    } catch (error: any) {
      console.error('Failed to fetch configurations:', error);
      setConfigMessage({ type: 'error', text: 'Failed to load configurations' });
    } finally {
      setLoadingConfigs(false);
    }
  };

  const handleSaveConfig = async (key: string, value: string) => {
    setSavingConfig(true);
    setConfigMessage(null);
    try {
      await configurationsApi.setConfiguration(key, value);
      setConfigs({ ...configs, [key]: value });
      setConfigMessage({ type: 'success', text: `${key.replace(/_/g, ' ')} saved successfully!` });
      setTimeout(() => setConfigMessage(null), 3000);
    } catch (error: any) {
      console.error(`Failed to save ${key}:`, error);
      setConfigMessage({ type: 'error', text: error?.response?.data?.detail || `Failed to save ${key}` });
    } finally {
      setSavingConfig(false);
    }
  };

  const togglePasswordVisibility = (key: string) => {
    setShowPasswords({ ...showPasswords, [key]: !showPasswords[key] });
  };

  const maskValue = (value: string): string => {
    if (!value) return '';
    if (value.length <= 8) return '•'.repeat(value.length);
    return value.substring(0, 4) + '•'.repeat(value.length - 8) + value.substring(value.length - 4);
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b border-gray-200 dark:border-gray-800 pb-8">
        <div>
          <h1 className="text-4xl font-black text-gray-900 dark:text-white tracking-tight">Settings</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-2 font-medium">Control center for {user?.organization_name || 'your organization'}.</p>
        </div>
        {isAdmin && (
          <div className="flex items-center gap-2 px-4 py-2 bg-orange-50 dark:bg-orange-950/30 rounded-full border border-orange-200 dark:border-orange-800/50">
            <ShieldCheck className="w-4 h-4 text-orange-600 dark:text-orange-400" />
            <span className="text-xs font-black text-orange-700 dark:text-orange-300 uppercase tracking-widest">Admin Privileges Active</span>
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="bg-gray-100/50 dark:bg-gray-900/50 p-1.5 rounded-2xl flex flex-wrap gap-1">
        <button
          onClick={() => setActiveTab('general')}
          className={`flex-1 min-w-[120px] py-3 px-4 rounded-xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 ${activeTab === 'general'
            ? 'bg-white dark:bg-gray-800 text-orange-600 dark:text-orange-400 shadow-md ring-1 ring-black/5'
            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-white/50 dark:hover:bg-gray-800/50'
            }`}
        >
          <Globe className="w-4 h-4" />
          General
        </button>
        <button
          onClick={() => setActiveTab('notifications')}
          className={`flex-1 min-w-[120px] py-3 px-4 rounded-xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 ${activeTab === 'notifications'
            ? 'bg-white dark:bg-gray-800 text-orange-600 dark:text-orange-400 shadow-md ring-1 ring-black/5'
            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-white/50 dark:hover:bg-gray-800/50'
            }`}
        >
          <Bell className="w-4 h-4" />
          Notifications
        </button>
        <button
          onClick={() => setActiveTab('api')}
          className={`flex-1 min-w-[120px] py-3 px-4 rounded-xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 ${activeTab === 'api'
            ? 'bg-white dark:bg-gray-800 text-orange-600 dark:text-orange-400 shadow-md ring-1 ring-black/5'
            : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-white/50 dark:hover:bg-gray-800/50'
            }`}
        >
          <Lock className="w-4 h-4" />
          API Access
        </button>
        {isAdmin && (
          <button
            onClick={() => setActiveTab('infrastructure')}
            className={`flex-1 min-w-[120px] py-3 px-4 rounded-xl font-bold text-sm transition-all duration-300 flex items-center justify-center gap-2 ${activeTab === 'infrastructure'
              ? 'bg-white dark:bg-gray-800 text-orange-600 dark:text-orange-400 shadow-md ring-1 ring-black/5'
              : 'text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-white/50 dark:hover:bg-gray-800/50'
              }`}
          >
            <Database className="w-4 h-4" />
            Infrastructure
          </button>
        )}
      </div>

      <div className="space-y-6">
        {configMessage && (
          <div className={`p-4 rounded-2xl flex items-center gap-3 animate-in fade-in slide-in-from-top-4 duration-300 ${configMessage.type === 'success'
            ? 'bg-green-50 dark:bg-green-950/30 text-green-800 dark:text-green-300 border border-green-200 dark:border-green-800'
            : 'bg-red-50 dark:bg-red-950/30 text-red-800 dark:text-red-300 border border-red-200 dark:border-red-800'
            }`}>
            {configMessage.type === 'success' ? (
              <CheckCircle2 className="w-5 h-5 text-green-600" />
            ) : (
              <AlertCircle className="w-5 h-5 text-red-600" />
            )}
            <p className="font-bold">{configMessage.text}</p>
          </div>
        )}

        {/* General Section */}
        {activeTab === 'general' && (
          <div className="bg-white dark:bg-gray-900 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
            <div className="p-8 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/30">
              <div className="flex items-center gap-3">
                <Building2 className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                <h2 className="text-xl font-black text-gray-900 dark:text-white">Organization Profile</h2>
              </div>
            </div>
            <div className="p-8 space-y-8">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div>
                  <label className="block text-sm font-black text-gray-700 dark:text-gray-300 uppercase tracking-widest mb-2">Display Name</label>
                  <input
                    type="text"
                    value={user?.organization_name || ''}
                    readOnly={!isSuperAdmin}
                    className="w-full bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-orange-500/20 rounded-xl px-4 py-3 text-gray-900 dark:text-white font-bold transition-all outline-none"
                  />
                  {!isSuperAdmin && (
                    <p className="text-[10px] font-bold text-gray-400 mt-2 uppercase">Contact platform administrator to change name</p>
                  )}
                </div>
                <div>
                  <label className="block text-sm font-black text-gray-700 dark:text-gray-300 uppercase tracking-widest mb-2">Organization ID</label>
                  <div className="flex items-center gap-2 p-3 bg-gray-100 dark:bg-gray-800 rounded-xl font-mono text-xs text-gray-500 select-all border border-gray-200 dark:border-gray-700">
                    {user?.organization_id || 'N/A'}
                  </div>
                </div>
              </div>

              <div className="pt-8 border-t border-gray-100 dark:border-gray-800">
                <h3 className="text-sm font-black text-gray-900 dark:text-white uppercase tracking-widest mb-4">Branding</h3>
                <div className="flex items-center gap-6">
                  <div className="w-20 h-20 rounded-3xl bg-orange-600 flex items-center justify-center text-white text-3xl font-black shadow-lg shadow-orange-500/30 hover:scale-105 transition-transform duration-300">
                    {(user?.organization_name || 'F').charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900 dark:text-white">Profile Picture</p>
                    <p className="text-xs text-gray-500 font-medium mt-1">Displayed in common sidebar and headers.</p>
                    <button className="mt-4 px-4 py-2 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-xl text-xs font-black hover:bg-gray-200 dark:hover:bg-gray-700 transition-colors uppercase tracking-widest">
                      Upload Logo
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Infrastructure Section - Centralized Hub for Org Admins */}
        {activeTab === 'infrastructure' && isAdmin && (
          <div className="space-y-8 animate-in fade-in duration-500">
            <div className="bg-gradient-to-br from-indigo-600 to-indigo-400 p-8 rounded-3xl shadow-xl shadow-indigo-500/20 text-white">
              <div className="flex items-center gap-4 mb-4">
                <Terminal className="w-8 h-8 opacity-80" />
                <h2 className="text-2xl font-black tracking-tight">Configuration Command Center</h2>
              </div>
              <p className="text-indigo-50/80 font-medium">Manage your organization's secrets, environment variables, and cloud provider integrations.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* Pulumi */}
              <div className="bg-white dark:bg-gray-900 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden flex flex-col">
                <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between bg-gray-50/50 dark:bg-gray-800/30">
                  <div className="flex items-center gap-3">
                    <Cloud className="w-5 h-5 text-indigo-600 dark:text-indigo-400" />
                    <h3 className="font-black text-gray-900 dark:text-white uppercase tracking-wider text-sm">Pulumi Cloud</h3>
                  </div>
                  <div className="p-1 bg-green-500/10 rounded-lg">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                  </div>
                </div>

                <div className="p-6 space-y-6 flex-1">
                  {loadingConfigs ? (
                    <div className="flex flex-col items-center justify-center py-12 gap-4">
                      <Loader2 className="w-8 h-8 animate-spin text-indigo-600" />
                      <p className="text-xs font-bold text-gray-400 uppercase">Loading Access tokens...</p>
                    </div>
                  ) : (
                    <>
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest">Access Token</label>
                          <a href="https://app.pulumi.com/account/tokens" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-[10px] font-bold text-indigo-500 hover:text-indigo-400">
                            Create Token <ExternalLink className="w-2 h-2" />
                          </a>
                        </div>
                        <div className="relative group">
                          <input
                            type={showPasswords.PULUMI_ACCESS_TOKEN ? 'text' : 'password'}
                            value={orgConfigForm.PULUMI_ACCESS_TOKEN}
                            onChange={(e) => setOrgConfigForm({ ...orgConfigForm, PULUMI_ACCESS_TOKEN: e.target.value })}
                            placeholder={configs.PULUMI_ACCESS_TOKEN ? maskValue(configs.PULUMI_ACCESS_TOKEN) : 'Enter Pulumi access token'}
                            className="w-full pr-12 px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-indigo-500/20 rounded-xl text-gray-900 dark:text-white font-mono text-sm transition-all outline-none"
                          />
                          <button
                            type="button"
                            onClick={() => togglePasswordVisibility('PULUMI_ACCESS_TOKEN')}
                            className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-indigo-600"
                          >
                            {showPasswords.PULUMI_ACCESS_TOKEN ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                        <p className="text-[10px] text-gray-400 mt-2 font-bold uppercase leading-tight">Authenticates your IDP with Pulumi Cloud to manage infrastructure state.</p>
                        <button
                          onClick={() => handleSaveConfig('PULUMI_ACCESS_TOKEN', orgConfigForm.PULUMI_ACCESS_TOKEN)}
                          disabled={savingConfig || !orgConfigForm.PULUMI_ACCESS_TOKEN}
                          className="mt-3 w-full py-2 bg-indigo-600 text-white rounded-xl text-xs font-black uppercase hover:bg-indigo-500 transition-all disabled:opacity-50"
                        >
                          {savingConfig ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Update Token'}
                        </button>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Organization</label>
                          <input
                            type="text"
                            value={orgConfigForm.PULUMI_ORG}
                            onChange={(e) => setOrgConfigForm({ ...orgConfigForm, PULUMI_ORG: e.target.value })}
                            placeholder={configs.PULUMI_ORG || 'org-name'}
                            className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-indigo-500/20 rounded-xl text-gray-900 dark:text-white font-bold text-sm outline-none"
                          />
                          <p className="text-[10px] text-gray-400 mt-2 font-bold uppercase">Your Pulumi Cloud org name</p>
                        </div>
                        <div className="flex items-end">
                          <button
                            onClick={() => handleSaveConfig('PULUMI_ORG', orgConfigForm.PULUMI_ORG)}
                            disabled={savingConfig}
                            className="w-full py-3 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-white rounded-xl text-[10px] font-black uppercase hover:bg-gray-200 dark:hover:bg-gray-700 transition-all"
                          >
                            Save
                          </button>
                        </div>
                      </div>

                      <div className="space-y-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                        <div className="flex items-center justify-between">
                          <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest">ESC Environments</label>
                          <a href="https://www.pulumi.com/docs/esc/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-[10px] font-bold text-indigo-500 hover:text-indigo-400">
                            Learn about ESC <ExternalLink className="w-2 h-2" />
                          </a>
                        </div>
                        <p className="text-[10px] text-gray-500 font-medium leading-relaxed italic">
                          ESC (Environments, Secrets, and Configuration) provides OIDC-based cloud credentials, removing the need for long-lived static keys.
                        </p>
                        {['AWS', 'GCP', 'AZURE'].map(provider => {
                          const configKey = `PULUMI_ESC_ENVIRONMENT_${provider}` as keyof typeof orgConfigForm;
                          return (
                            <div key={provider} className="flex gap-2">
                              <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                  <span className="w-1.5 h-1.5 rounded-full bg-indigo-500"></span>
                                  <span className="text-[10px] font-black text-gray-500 uppercase">{provider} Environment Path</span>
                                </div>
                                <input
                                  type="text"
                                  value={orgConfigForm[configKey]}
                                  onChange={(e) => setOrgConfigForm({ ...orgConfigForm, [configKey]: e.target.value })}
                                  placeholder={configs[configKey] || `org/${provider.toLowerCase()}-env`}
                                  className="w-full px-3 py-2 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-indigo-500/20 rounded-lg text-gray-900 dark:text-white text-xs outline-none"
                                />
                              </div>
                              <button
                                onClick={() => handleSaveConfig(configKey as string, orgConfigForm[configKey])}
                                disabled={savingConfig}
                                className="self-end p-2.5 bg-gray-100 dark:bg-gray-800 text-gray-400 hover:text-indigo-600 rounded-lg"
                                title={`Save ${provider} environment`}
                              >
                                <Save className="w-4 h-4" />
                              </button>
                            </div>
                          );
                        })}
                        <div className="mt-2 p-3 bg-indigo-50 dark:bg-indigo-950/20 rounded-xl border border-indigo-100 dark:border-indigo-800/30">
                          <div className="flex items-center gap-2 mb-1">
                            <Info className="w-3 h-3 text-indigo-500" />
                            <span className="text-[10px] font-black text-indigo-700 dark:text-indigo-400 uppercase">Format</span>
                          </div>
                          <p className="text-[9px] font-medium text-indigo-600 dark:text-indigo-300/70 capitalize">
                            Example: <code className="font-mono text-indigo-800 dark:text-indigo-200">my-org/production-gcp</code>.
                            Create them at <a href="https://app.pulumi.com/environments" target="_blank" rel="noopener noreferrer" className="underline hover:text-indigo-500">Pulumi Console</a>.
                          </p>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* GitHub */}
              <div className="bg-white dark:bg-gray-900 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden flex flex-col">
                <div className="p-6 border-b border-gray-100 dark:border-gray-800 flex items-center justify-between bg-gray-50/50 dark:bg-gray-800/30">
                  <div className="flex items-center gap-3">
                    <Github className="w-5 h-5 text-gray-900 dark:text-white" />
                    <h3 className="font-black text-gray-900 dark:text-white uppercase tracking-wider text-sm">GitHub Connector</h3>
                  </div>
                  <div className="p-1 bg-green-500/10 rounded-lg">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                  </div>
                </div>

                <div className="p-6 space-y-6 flex-1">
                  {loadingConfigs ? (
                    <div className="flex flex-col items-center justify-center py-12 gap-4">
                      <Loader2 className="w-8 h-8 animate-spin text-gray-900 dark:text-white" />
                      <p className="text-xs font-bold text-gray-400 uppercase">Verifying tokens...</p>
                    </div>
                  ) : (
                    <>
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest">Personal Access Token</label>
                          <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-[10px] font-bold text-gray-500 hover:text-gray-900 dark:hover:text-white">
                            Create PAT <ExternalLink className="w-2 h-2" />
                          </a>
                        </div>
                        <div className="relative group">
                          <input
                            type={showPasswords.GITHUB_TOKEN ? 'text' : 'password'}
                            value={orgConfigForm.GITHUB_TOKEN}
                            onChange={(e) => setOrgConfigForm({ ...orgConfigForm, GITHUB_TOKEN: e.target.value })}
                            placeholder={configs.GITHUB_TOKEN ? maskValue(configs.GITHUB_TOKEN) : 'Enter GitHub PAT'}
                            className="w-full pr-12 px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-gray-500/20 rounded-xl text-gray-900 dark:text-white font-mono text-sm transition-all outline-none"
                          />
                          <button
                            type="button"
                            onClick={() => togglePasswordVisibility('GITHUB_TOKEN')}
                            className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-900 dark:hover:text-white"
                          >
                            {showPasswords.GITHUB_TOKEN ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                          </button>
                        </div>
                        <p className="text-[10px] text-gray-400 mt-2 font-bold uppercase leading-tight">Requires 'repo' and 'workflow' scopes for GitOps operations.</p>
                        <button
                          onClick={() => handleSaveConfig('GITHUB_TOKEN', orgConfigForm.GITHUB_TOKEN)}
                          disabled={savingConfig || !orgConfigForm.GITHUB_TOKEN}
                          className="mt-3 w-full py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-xl text-xs font-black uppercase hover:bg-black dark:hover:bg-gray-100 transition-all disabled:opacity-50"
                        >
                          {savingConfig ? <Loader2 className="w-4 h-4 animate-spin mx-auto" /> : 'Authorize Connector'}
                        </button>
                      </div>

                      <div>
                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Target Infrastructure Repository</label>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={orgConfigForm.GITHUB_REPOSITORY}
                            onChange={(e) => setOrgConfigForm({ ...orgConfigForm, GITHUB_REPOSITORY: e.target.value })}
                            placeholder={configs.GITHUB_REPOSITORY || 'github-org/infrastructure'}
                            className="flex-1 px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-gray-500/20 rounded-xl text-gray-900 dark:text-white font-bold text-sm outline-none"
                          />
                          <button
                            onClick={() => handleSaveConfig('GITHUB_REPOSITORY', orgConfigForm.GITHUB_REPOSITORY)}
                            disabled={savingConfig}
                            className="p-3 bg-gray-100 dark:bg-gray-800 text-gray-500 hover:text-gray-900 dark:hover:text-white rounded-xl transition-all"
                          >
                            <Save className="w-5 h-5" />
                          </button>
                        </div>
                        <p className="text-[10px] text-gray-400 font-bold mt-2 uppercase">The central repository where Pulumi infrastructure code is managed.</p>
                      </div>

                      <div>
                        <label className="block text-[10px] font-black text-gray-400 uppercase tracking-widest mb-2">Microservice Target Organization</label>
                        <div className="flex gap-2">
                          <input
                            type="text"
                            value={orgConfigForm.MICROSERVICE_REPO_ORG}
                            onChange={(e) => setOrgConfigForm({ ...orgConfigForm, MICROSERVICE_REPO_ORG: e.target.value })}
                            placeholder={configs.MICROSERVICE_REPO_ORG || 'github-org'}
                            className="flex-1 px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-gray-500/20 rounded-xl text-gray-900 dark:text-white font-bold text-sm outline-none"
                          />
                          <button
                            onClick={() => handleSaveConfig('MICROSERVICE_REPO_ORG', orgConfigForm.MICROSERVICE_REPO_ORG)}
                            disabled={savingConfig}
                            className="p-3 bg-gray-100 dark:bg-gray-800 text-gray-500 hover:text-gray-900 dark:hover:text-white rounded-xl transition-all"
                          >
                            <Save className="w-5 h-5" />
                          </button>
                        </div>
                        <p className="text-[10px] text-gray-400 font-bold mt-2 uppercase">Target GitHub organization where new microservices will be created.</p>
                      </div>

                      <div className="mt-auto p-4 bg-orange-50 dark:bg-orange-950/20 rounded-2xl border border-orange-200 dark:border-orange-800/30">
                        <div className="flex items-center gap-2 mb-2">
                          <AlertCircle className="w-4 h-4 text-orange-600" />
                          <span className="text-[10px] font-black text-orange-800 dark:text-orange-400 uppercase">Security Note</span>
                        </div>
                        <p className="text-[10px] font-medium text-orange-700 dark:text-orange-300/80 leading-relaxed">
                          Tokens are encrypted at rest and never shared between organizations. Ensure your GitHub token has enough scopes for 'repo' and 'workflow'.
                        </p>
                      </div>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Notifications Section */}
        {activeTab === 'notifications' && (
          <div className="bg-white dark:bg-gray-900 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
            <div className="p-8 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/30">
              <div className="flex items-center gap-3">
                <Bell className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                <h2 className="text-xl font-black text-gray-900 dark:text-white">Notification Preferences</h2>
              </div>
            </div>
            <div className="p-8 space-y-6">
              <div className="group flex items-center justify-between py-4 border-b border-gray-100 dark:border-gray-800 last:border-0 hover:bg-gray-50/50 dark:hover:bg-gray-800/30 px-4 -mx-4 rounded-xl transition-colors">
                <div>
                  <p className="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wider">Email Dispatch</p>
                  <p className="text-xs text-gray-500 font-medium mt-1">Status updates for your team's provisioned services.</p>
                </div>
                <button
                  onClick={() => setEmailNotifs(!emailNotifs)}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition-all duration-300 ${emailNotifs ? 'bg-orange-600 shadow-lg shadow-orange-500/30' : 'bg-gray-200 dark:bg-gray-700'}`}
                >
                  <span className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform duration-300 ${emailNotifs ? 'translate-x-7' : 'translate-x-1'}`} />
                </button>
              </div>
              <div className="group flex items-center justify-between py-4 border-b border-gray-100 dark:border-gray-800 last:border-0 hover:bg-gray-50/50 dark:hover:bg-gray-800/30 px-4 -mx-4 rounded-xl transition-colors">
                <div>
                  <p className="text-sm font-black text-gray-900 dark:text-white uppercase tracking-wider">Slack Integration</p>
                  <p className="text-xs text-gray-500 font-medium mt-1">Forward deployment incidents to the #foundry-alerts channel.</p>
                </div>
                <button
                  onClick={() => setSlackNotifs(!slackNotifs)}
                  className={`relative inline-flex h-8 w-14 items-center rounded-full transition-all duration-300 ${slackNotifs ? 'bg-orange-600 shadow-lg shadow-orange-500/30' : 'bg-gray-200 dark:bg-gray-700'}`}
                >
                  <span className={`inline-block h-6 w-6 transform rounded-full bg-white transition-transform duration-300 ${slackNotifs ? 'translate-x-7' : 'translate-x-1'}`} />
                </button>
              </div>
            </div>
          </div>
        )}

        {/* API Access */}
        {activeTab === 'api' && (
          <div className="bg-white dark:bg-gray-900 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-sm overflow-hidden">
            <div className="p-8 border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/30">
              <div className="flex items-center gap-3">
                <Lock className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                <h2 className="text-xl font-black text-gray-900 dark:text-white">API Management</h2>
              </div>
            </div>
            <div className="p-8">
              <div className="bg-gray-50 dark:bg-gray-950 p-6 rounded-2xl border-2 border-dashed border-gray-200 dark:border-gray-800 flex flex-col md:flex-row items-center justify-between gap-6">
                <div>
                  <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Primary Access Identity</p>
                  <div className="flex items-center gap-3">
                    <Key className="w-5 h-5 text-orange-600" />
                    <code className="text-sm font-mono font-bold text-gray-800 dark:text-orange-400 bg-orange-50 dark:bg-orange-950/50 px-3 py-1 rounded-lg">foundry_live_••••••••••••••••••••</code>
                  </div>
                </div>
                <div className="flex gap-3">
                  <button className="px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-700 dark:text-white rounded-xl text-xs font-black uppercase hover:shadow-md transition-all">Copy</button>
                  <button className="px-4 py-2 bg-red-600 text-white rounded-xl text-xs font-black uppercase hover:bg-red-500 shadow-lg shadow-red-500/30 transition-all">Rotate</button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};