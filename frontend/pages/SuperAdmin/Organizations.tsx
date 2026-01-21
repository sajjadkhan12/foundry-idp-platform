import React, { useState, useEffect } from 'react';
import { Building2, Plus, Search, Loader2, AlertCircle, CheckCircle2, Eye, Crown, X } from 'lucide-react';
import { organizationsApi, type Organization, type CreateOrganizationWithAdminRequest } from '../../services/api/organizations';
import { Modal } from '../../components/common/Modal';
import { useAuth } from '../../contexts/AuthContext';

export const OrganizationsPage: React.FC = () => {
    const { isSuperAdmin } = useAuth();
    const [organizations, setOrganizations] = useState<Organization[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
    const [isCreating, setIsCreating] = useState(false);

    const [createForm, setCreateForm] = useState<CreateOrganizationWithAdminRequest>({
        name: '',
        slug: '',
        description: '',
        admin_email: '',
        admin_username: '',
        admin_password: '',
        admin_full_name: ''
    });
    const [createError, setCreateError] = useState<string | null>(null);

    useEffect(() => {
        if (!isSuperAdmin) {
            setMessage({ type: 'error', text: 'Access denied. Super admin privileges required.' });
            return;
        }
        fetchOrganizations();
    }, [isSuperAdmin]);

    const fetchOrganizations = async () => {
        setLoading(true);
        try {
            const data = await organizationsApi.listOrganizations();
            setOrganizations(data);
        } catch (error: any) {
            console.error('Failed to fetch organizations:', error);
            const errorMessage = error?.message || error?.toString() || 'Failed to fetch organizations';
            setMessage({ type: 'error', text: errorMessage });
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async () => {
        setCreateError(null);
        setIsCreating(true);

        try {
            // Validate form
            if (!createForm.name || !createForm.slug || !createForm.admin_email ||
                !createForm.admin_username || !createForm.admin_password) {
                setCreateError('Please fill in all required fields');
                setIsCreating(false);
                return;
            }

            // Validate password strength (basic check)
            if (createForm.admin_password.length < 12) {
                setCreateError('Password must be at least 12 characters long');
                setIsCreating(false);
                return;
            }

            await organizationsApi.createOrganizationWithAdmin(createForm);
            setMessage({ type: 'success', text: 'Organization created successfully!' });
            setIsCreateModalOpen(false);
            setCreateForm({
                name: '',
                slug: '',
                description: '',
                admin_email: '',
                admin_username: '',
                admin_password: '',
                admin_full_name: ''
            });
            fetchOrganizations();
        } catch (error: any) {
            console.error('Failed to create organization:', error);
            const errorMessage = error?.message || error?.toString() || 'Failed to create organization';
            setCreateError(errorMessage);
        } finally {
            setIsCreating(false);
        }
    };

    const filteredOrganizations = organizations.filter(org =>
        org.name.toLowerCase().includes(search.toLowerCase()) ||
        org.slug.toLowerCase().includes(search.toLowerCase()) ||
        org.description?.toLowerCase().includes(search.toLowerCase())
    );

    if (!isSuperAdmin) {
        return (
            <div className="max-w-4xl mx-auto p-6">
                <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                    <div className="flex items-center gap-2 text-red-800 dark:text-red-200">
                        <AlertCircle className="w-5 h-5" />
                        <p className="font-medium">Access Denied</p>
                    </div>
                    <p className="text-sm text-red-600 dark:text-red-300 mt-2">
                        You need super admin privileges to access this page.
                    </p>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto p-6 space-y-8">
            {/* SaaS Manager Branding */}
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6 bg-gradient-to-br from-orange-600 to-orange-400 p-8 rounded-3xl shadow-xl shadow-orange-500/20 text-white">
                <div>
                    <h1 className="text-3xl font-black tracking-tight flex items-center gap-3">
                        <Crown className="w-10 h-10" />
                        SaaS Management
                    </h1>
                    <p className="text-orange-50/80 font-medium mt-2 max-w-lg">
                        You are in the control center for all organizations. Create and monitor organizations across the entire platform.
                    </p>
                </div>
                <button
                    onClick={() => setIsCreateModalOpen(true)}
                    className="flex items-center justify-center gap-2 px-6 py-4 bg-white/10 backdrop-blur-md border border-white/20 text-white rounded-2xl font-bold hover:bg-white/20 transition-all duration-300 transform hover:scale-105 active:scale-95"
                >
                    <Plus className="w-5 h-5" />
                    Create New Organization
                </button>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
                    <p className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Total Organizations</p>
                    <h3 className="text-3xl font-black text-gray-900 dark:text-white">{organizations.length}</h3>
                </div>
                <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
                    <p className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Active</p>
                    <h3 className="text-3xl font-black text-green-600 dark:text-green-400">
                        {organizations.filter(o => o.is_active).length}
                    </h3>
                </div>
                <div className="bg-white dark:bg-gray-900 p-6 rounded-2xl border border-gray-200 dark:border-gray-800 shadow-sm">
                    <p className="text-sm font-bold text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-1">Growth</p>
                    <h3 className="text-3xl font-black text-blue-600 dark:text-blue-400">+100%</h3>
                </div>
            </div>

            {/* Message */}
            {message && (
                <div className={`p-4 rounded-xl flex items-center gap-2 animate-in slide-in-from-top-4 duration-300 ${message.type === 'success'
                        ? 'bg-green-50 dark:bg-green-900/20 text-green-800 dark:text-green-200 border border-green-200 dark:border-green-800'
                        : 'bg-red-50 dark:bg-red-900/20 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800'
                    }`}>
                    {message.type === 'success' ? (
                        <CheckCircle2 className="w-5 h-5 text-green-600" />
                    ) : (
                        <AlertCircle className="w-5 h-5 text-red-600" />
                    )}
                    <p className="font-medium">{message.text}</p>
                    <button
                        onClick={() => setMessage(null)}
                        className="ml-auto p-1 hover:bg-black/5 rounded-lg transition-colors"
                    >
                        <X className="w-4 h-4" />
                    </button>
                </div>
            )}

            {/* Search & Actions */}
            <div className="bg-white/50 dark:bg-gray-900/50 backdrop-blur-xl p-4 rounded-2xl border border-gray-200 dark:border-gray-800 flex flex-col sm:flex-row gap-4">
                <div className="relative flex-1">
                    <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                    <input
                        type="text"
                        placeholder="Filter organizations by name, slug or description..."
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 bg-white dark:bg-gray-800 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none transition-all duration-300 shadow-inner"
                    />
                </div>
            </div>

            {/* Organizations Grid */}
            {loading ? (
                <div className="flex flex-col items-center justify-center py-20 gap-4">
                    <Loader2 className="w-12 h-12 animate-spin text-orange-600" />
                    <p className="text-gray-500 font-bold animate-pulse">Loading Organizations...</p>
                </div>
            ) : filteredOrganizations.length === 0 ? (
                <div className="text-center py-24 bg-white dark:bg-gray-900 rounded-3xl border border-gray-200 dark:border-gray-800 shadow-sm animate-in fade-in duration-700">
                    <div className="bg-gray-100 dark:bg-gray-800 w-20 h-20 rounded-2xl flex items-center justify-center mx-auto mb-6">
                        <Building2 className="w-10 h-10 text-gray-400" />
                    </div>
                    <h3 className="text-2xl font-black text-gray-900 dark:text-white mb-2">No organizations found</h3>
                    <p className="text-gray-500 dark:text-gray-400 font-medium max-w-md mx-auto">
                        {search ? `We couldn't find any results for "${search}". Try adjusting your filters.` : 'Get started by creating your first platform organization.'}
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {filteredOrganizations.map((org) => (
                        <div
                            key={org.id}
                            className="group relative bg-white dark:bg-gray-900 rounded-3xl border-2 border-transparent hover:border-orange-500/20 hover:shadow-2xl hover:shadow-orange-500/10 p-8 transition-all duration-500"
                        >
                            <div className="flex items-start justify-between mb-6">
                                <div className="p-4 bg-orange-50 dark:bg-orange-950/30 rounded-2xl group-hover:scale-110 transition-transform duration-500">
                                    <Building2 className="w-8 h-8 text-orange-600 dark:text-orange-400" />
                                </div>
                                <div className={`px-4 py-1.5 rounded-full text-xs font-black uppercase tracking-widest ${org.is_active
                                        ? 'bg-green-100 dark:bg-green-950/30 text-green-700 dark:text-green-400'
                                        : 'bg-gray-100 dark:bg-gray-800 text-gray-600'
                                    }`}>
                                    {org.is_active ? 'Active' : 'Inactive'}
                                </div>
                            </div>

                            <div className="mb-6">
                                <h3 className="text-xl font-black text-gray-900 dark:text-white group-hover:text-orange-600 transition-colors">
                                    {org.name}
                                </h3>
                                <p className="text-sm font-bold text-gray-500 dark:text-gray-400 mt-1 font-mono">
                                    /{org.slug}
                                </p>
                            </div>

                            {org.description && (
                                <p className="text-sm text-gray-600 dark:text-gray-400 mb-8 line-clamp-3 leading-relaxed">
                                    {org.description}
                                </p>
                            )}

                            <div className="flex items-center justify-between pt-6 border-t border-gray-100 dark:border-gray-800">
                                <div className="flex flex-col">
                                    <span className="text-[10px] font-black uppercase text-gray-400 tracking-tighter">Onboarded</span>
                                    <span className="text-sm font-bold text-gray-600 dark:text-gray-400">
                                        {new Date(org.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                                    </span>
                                </div>
                                <div className="flex items-center gap-2 text-gray-300 dark:text-gray-700">
                                    <Eye className="w-5 h-5 cursor-help opacity-0 group-hover:opacity-100 transition-opacity" title="Configuration managed by Org Admin" />
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Create Organization Modal */}
            <Modal
                isOpen={isCreateModalOpen}
                onClose={() => {
                    setIsCreateModalOpen(false);
                    setCreateError(null);
                    setCreateForm({
                        name: '',
                        slug: '',
                        description: '',
                        admin_email: '',
                        admin_username: '',
                        admin_password: '',
                        admin_full_name: ''
                    });
                }}
                title="Onboard New Organization"
                size="lg"
            >
                <div className="space-y-6">
                    {createError && (
                        <div className="p-4 bg-red-50 dark:bg-red-950/30 border-2 border-red-500/20 rounded-2xl text-red-700 dark:text-red-400 text-sm font-bold flex items-center gap-3">
                            <AlertCircle className="w-5 h-5 flex-shrink-0" />
                            {createError}
                        </div>
                    )}

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="space-y-4">
                            <h4 className="text-xs font-black uppercase text-orange-600 tracking-widest">Organization Details</h4>
                            <div>
                                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
                                    Display Name <span className="text-orange-500">*</span>
                                </label>
                                <input
                                    type="text"
                                    value={createForm.name}
                                    onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-gray-900 dark:text-white transition-all outline-none"
                                    placeholder="Acme Corporation"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
                                    Slug (URL segment) <span className="text-orange-500">*</span>
                                </label>
                                <input
                                    type="text"
                                    value={createForm.slug}
                                    onChange={(e) => setCreateForm({ ...createForm, slug: e.target.value.toLowerCase().replace(/[^a-z0-9-]/g, '-') })}
                                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-gray-900 dark:text-white font-mono transition-all outline-none"
                                    placeholder="acme-corp"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
                                    Description
                                </label>
                                <textarea
                                    value={createForm.description}
                                    onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-gray-900 dark:text-white transition-all outline-none resize-none"
                                    rows={3}
                                    placeholder="Describe this organization..."
                                />
                            </div>
                        </div>

                        <div className="space-y-4">
                            <h4 className="text-xs font-black uppercase text-orange-600 tracking-widest">Administrator Credentials</h4>
                            <div>
                                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
                                    Admin Email <span className="text-orange-500">*</span>
                                </label>
                                <input
                                    type="email"
                                    value={createForm.admin_email}
                                    onChange={(e) => setCreateForm({ ...createForm, admin_email: e.target.value })}
                                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-gray-900 dark:text-white transition-all outline-none"
                                    placeholder="admin@acme.com"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
                                    Admin Username <span className="text-orange-500">*</span>
                                </label>
                                <input
                                    type="text"
                                    value={createForm.admin_username}
                                    onChange={(e) => setCreateForm({ ...createForm, admin_username: e.target.value })}
                                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-gray-900 dark:text-white transition-all outline-none"
                                    placeholder="admin_acme"
                                />
                            </div>

                            <div>
                                <label className="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">
                                    Initial Password <span className="text-orange-500">*</span>
                                </label>
                                <input
                                    type="password"
                                    value={createForm.admin_password}
                                    onChange={(e) => setCreateForm({ ...createForm, admin_password: e.target.value })}
                                    className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-950 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-gray-900 dark:text-white transition-all outline-none"
                                    placeholder="••••••••••••"
                                />
                                <p className="text-[10px] text-gray-500 font-bold mt-2 uppercase">12+ chars • Upper • Lower • Digit • Symbol</p>
                            </div>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 p-4 bg-orange-50 dark:bg-orange-950/20 rounded-2xl border border-orange-200 dark:border-orange-800/30">
                        <AlertCircle className="w-5 h-5 text-orange-600 flex-shrink-0" />
                        <p className="text-xs font-bold text-orange-800 dark:text-orange-300 leading-relaxed">
                            Creating this organization will automatically generate a default Business Unit and assign the administrator user. The organization admin will be responsible for further configuration.
                        </p>
                    </div>

                    <div className="flex flex-col sm:flex-row justify-end gap-3 pt-4">
                        <button
                            onClick={() => setIsCreateModalOpen(false)}
                            className="px-6 py-3 text-gray-500 font-bold hover:bg-gray-100 dark:hover:bg-gray-800 rounded-xl transition-all"
                            disabled={isCreating}
                        >
                            Discard
                        </button>
                        <button
                            onClick={handleCreate}
                            disabled={isCreating}
                            className="px-8 py-3 bg-orange-600 text-white rounded-xl font-black shadow-lg shadow-orange-500/20 hover:bg-orange-500 hover:shadow-orange-500/40 transition-all disabled:opacity-50 flex items-center justify-center gap-2"
                        >
                            {isCreating && <Loader2 className="w-5 h-5 animate-spin" />}
                            Complete Onboarding
                        </button>
                    </div>
                </div>
            </Modal>
        </div>
    );
};
