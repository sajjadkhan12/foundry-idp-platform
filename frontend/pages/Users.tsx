import React, { useState, useEffect } from 'react';
import { Search, User as UserIcon, Lock, CheckCircle2, XCircle, Edit2, Save, Trash2, AlertCircle, Loader2 } from 'lucide-react';
import api from '../services/api';
import { API_URL } from '../constants/api';
import { appLogger } from '../utils/logger';
import { Pagination } from '../components/Pagination';
import { PasswordStrength } from '../components/PasswordStrength';
import { Modal } from '../components/common/Modal';
import { ConfirmDialog } from '../components/common/ConfirmDialog';
import { useDebounce, usePagination, useModal } from '../hooks';

interface User {
    id: string;
    email: string;
    username: string;
    full_name: string;
    roles: string[];
    is_active: boolean;
    avatar_url?: string;
    created_at: string;
}

interface Role {
    id: string;
    name: string;
    description?: string;
    is_platform_role?: boolean;
}

export const UsersPage: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [roles, setRoles] = useState<Role[]>([]);
    const [loading, setLoading] = useState(true);
    const [loadingRoles, setLoadingRoles] = useState(true);
    const [search, setSearch] = useState('');
    const [roleFilter, setRoleFilter] = useState('');
    const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);

    // Use custom hooks
    const debouncedSearch = useDebounce(search, 300);
    const pagination = usePagination(50);
    const createModal = useModal();
    const editModal = useModal<User>();
    const deleteModal = useModal<User>();

    const [editForm, setEditForm] = useState({
        email: '',
        full_name: '',
        password: '',
        is_active: true
    });
    const [createForm, setCreateForm] = useState({
        username: '',
        email: '',
        full_name: '',
        password: ''
    });
    const [createError, setCreateError] = useState<string | null>(null);
    const [isCreating, setIsCreating] = useState(false);
    const [isSaving, setIsSaving] = useState(false);
    const [isDeleting, setIsDeleting] = useState(false);

    const fetchUsers = async () => {
        setLoading(true);
        try {

            const response = await api.listUsers({
                search: debouncedSearch,
                role: roleFilter,
                skip: pagination.skip,
                limit: pagination.itemsPerPage
            });



            // Handle both old format (array) and new format (object with users/items/total)
            if (Array.isArray(response)) {

                setUsers(response);
                pagination.setTotalItems(response.length);
            } else {
                // Support both "users" and "items" keys for backward compatibility
                const usersList = response.users || response.items || [];

                setUsers(usersList);
                pagination.setTotalItems(response.total || 0);
            }
        } catch (error) {
            console.error('[Users Page] Failed to fetch users:', error);
            appLogger.error('Failed to fetch users:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchRoles = async () => {
        setLoadingRoles(true);
        try {
            const response = await api.listRoles({ skip: 0, limit: 100 });

            // Handle both old format (array) and new format (object with items/total)
            if (Array.isArray(response)) {
                setRoles(response);
            } else {
                setRoles(response?.items || []);
            }
        } catch (error) {
            appLogger.error('Failed to fetch roles:', error);
            setRoles([]);
        } finally {
            setLoadingRoles(false);
        }
    };

    useEffect(() => {
        fetchRoles();
    }, []);

    useEffect(() => {
        pagination.resetPage();
    }, [debouncedSearch, roleFilter]);

    useEffect(() => {
        fetchUsers();
    }, [pagination.currentPage, pagination.itemsPerPage, debouncedSearch, roleFilter]);

    const handleEditClick = (user: User) => {
        setEditForm({
            email: user.email,
            full_name: user.full_name || '',
            password: '',
            is_active: user.is_active
        });
        editModal.open(user);
        setMessage(null);
    };

    const handleSaveUser = async () => {
        if (!editModal.data) return;

        setIsSaving(true);
        try {
            const updateData: any = {
                email: editForm.email,
                full_name: editForm.full_name || null,
                is_active: editForm.is_active
            };

            if (editForm.password) {
                if (editForm.password.length < 8) {
                    setMessage({ type: 'error', text: 'Password must be at least 8 characters' });
                    setIsSaving(false);
                    return;
                }
                updateData.password = editForm.password;
            }

            await api.adminUpdateUser(editModal.data.id, updateData);

            setMessage({ type: 'success', text: 'User updated successfully' });
            fetchUsers();
            setTimeout(() => editModal.close(), 1500);
        } catch (error: any) {
            setMessage({ type: 'error', text: error.message || 'Failed to update user' });
        } finally {
            setIsSaving(false);
        }
    };

    const handleCreateUser = async () => {
        setCreateError(null);

        if (!createForm.username || !createForm.email || !createForm.password) {
            setCreateError('Username, email, and password are required');
            return;
        }

        setIsCreating(true);
        try {
            await api.createUser({
                ...createForm
            });
            setMessage({ type: 'success', text: 'User created successfully' });
            createModal.close();
            setCreateForm({ username: '', email: '', full_name: '', password: '' });
            setCreateError(null);

            // Clear filters and refresh the user list
            setSearch('');
            setRoleFilter('');
            pagination.resetPage();
            await fetchUsers();
        } catch (error: any) {
            // Parse error message from backend
            let errorMessage = 'Failed to create user';
            if (error.message) {
                errorMessage = error.message;
            } else if (error.response?.data?.detail) {
                errorMessage = error.response.data.detail;
            } else if (typeof error === 'string') {
                errorMessage = error;
            }
            setCreateError(errorMessage);
        } finally {
            setIsCreating(false);
        }
    };

    const confirmDeleteUser = async () => {
        if (!deleteModal.data) return;

        setIsDeleting(true);
        try {
            await api.deleteUser(deleteModal.data.id);
            setMessage({ type: 'success', text: 'User deleted successfully' });
            deleteModal.close();
            // Small delay to ensure backend processing is complete
            await new Promise(resolve => setTimeout(resolve, 200));
            await fetchUsers();
        } catch (error: any) {
            setMessage({ type: 'error', text: error.message || 'Failed to delete user' });
        } finally {
            setIsDeleting(false);
        }
    };

    return (
        <div className="max-w-7xl mx-auto space-y-6">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-gray-900 dark:text-white">User Management</h1>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">Manage system users, roles, and access</p>
                </div>
                <div className="flex items-center gap-3">
                    <button
                        onClick={() => createModal.open()}
                        className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 flex items-center gap-2 text-sm font-medium"
                    >
                        <UserIcon className="w-4 h-4" /> Create User
                    </button>
                    <div className="relative">
                        <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                        <input
                            type="text"
                            placeholder="Search users..."
                            value={search}
                            onChange={(e) => setSearch(e.target.value)}
                            className="pl-9 pr-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 w-full sm:w-64"
                        />
                    </div>
                    <select
                        value={roleFilter}
                        onChange={(e) => setRoleFilter(e.target.value)}
                        className="px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-sm focus:outline-none focus:ring-2 focus:ring-orange-500"
                        disabled={loadingRoles}
                    >
                        <option value="">All Roles</option>
                        {roles.map((role) => (
                            <option key={role.id} value={role.name}>
                                {role.name.charAt(0).toUpperCase() + role.name.slice(1).replace(/-/g, ' ')}
                            </option>
                        ))}
                    </select>
                </div>
            </div>

            {message && (
                <div className={`p-4 rounded-lg ${message.type === 'success' ? 'bg-green-50 text-green-700 dark:bg-green-900/20 dark:text-green-400' : 'bg-red-50 text-red-700 dark:bg-red-900/20 dark:text-red-400'}`}>
                    {message.text}
                </div>
            )}

            <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl overflow-hidden shadow-sm">
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead className="bg-gray-50 dark:bg-gray-800/50 border-b border-gray-200 dark:border-gray-800">
                            <tr>
                                <th className="px-6 py-4 font-medium text-gray-500 dark:text-gray-400">User</th>
                                <th className="px-6 py-4 font-medium text-gray-500 dark:text-gray-400">Role</th>
                                <th className="px-6 py-4 font-medium text-gray-500 dark:text-gray-400">Status</th>
                                <th className="px-6 py-4 font-medium text-gray-500 dark:text-gray-400">Joined</th>
                                <th className="px-6 py-4 font-medium text-gray-500 dark:text-gray-400 text-right">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200 dark:divide-gray-800">
                            {loading ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                                        <div className="flex justify-center items-center gap-2">
                                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-600"></div>
                                            Loading users...
                                        </div>
                                    </td>
                                </tr>
                            ) : users.length === 0 ? (
                                <tr>
                                    <td colSpan={5} className="px-6 py-8 text-center text-gray-500">
                                        No users found matching your criteria
                                    </td>
                                </tr>
                            ) : (
                                users.map((user) => (
                                    <tr key={user.id} className="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                {user.avatar_url && user.avatar_url.trim() !== '' && !user.avatar_url.includes('data:;base64,=') ? (
                                                    <img
                                                        src={user.avatar_url.startsWith('http') || user.avatar_url.startsWith('data:') ? user.avatar_url : `${API_URL}${user.avatar_url}`}
                                                        alt={user.username}
                                                        className="w-10 h-10 rounded-full object-cover ring-2 ring-gray-100 dark:ring-gray-800"
                                                        onError={(e) => {
                                                            (e.target as HTMLImageElement).style.display = 'none';
                                                        }}
                                                    />
                                                ) : (
                                                    <div className="w-10 h-10 rounded-full bg-orange-100 dark:bg-orange-900/30 flex items-center justify-center text-orange-600 dark:text-orange-400 font-bold">
                                                        {user.full_name?.charAt(0) || user.username.charAt(0)}
                                                    </div>
                                                )}
                                                <div>
                                                    <p className="font-medium text-gray-900 dark:text-white">{user.full_name || user.username}</p>
                                                    <p className="text-xs text-gray-500">{user.email}</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex flex-wrap gap-1">
                                                {user.roles && user.roles.length > 0 ? (
                                                    user.roles.map((roleName) => {
                                                        const roleInfo = roles.find(r => r.name === roleName);
                                                        const isPlatformRole = roleInfo?.is_platform_role === true;

                                                        return (
                                                            <span
                                                                key={roleName}
                                                                className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${isPlatformRole
                                                                    ? 'bg-orange-50 dark:bg-orange-900/20 text-orange-700 dark:text-orange-400 border-orange-200 dark:border-orange-800'
                                                                    : 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400 border-blue-200 dark:border-blue-800'
                                                                    }`}
                                                            >
                                                                <UserIcon className="w-3 h-3" />
                                                                {roleName.charAt(0).toUpperCase() + roleName.slice(1).replace(/-/g, ' ')}
                                                                {isPlatformRole ? (
                                                                    <span className="ml-1 text-[10px] opacity-75">(Platform)</span>
                                                                ) : (
                                                                    <span className="ml-1 text-[10px] opacity-75">(BU)</span>
                                                                )}
                                                            </span>
                                                        );
                                                    })
                                                ) : (
                                                    <span className="text-gray-500 text-xs">No roles</span>
                                                )}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium border ${user.is_active
                                                ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400 border-green-200 dark:border-green-800'
                                                : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 border-red-200 dark:border-red-800'
                                                }`}>
                                                {user.is_active ? <CheckCircle2 className="w-3 h-3" /> : <XCircle className="w-3 h-3" />}
                                                {user.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-gray-500 dark:text-gray-400">
                                            {new Date(user.created_at).toLocaleDateString()}
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <div className="flex justify-end gap-2">
                                                <button
                                                    onClick={() => handleEditClick(user)}
                                                    className="p-2 text-gray-400 hover:text-orange-600 dark:hover:text-orange-400 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-lg transition-colors"
                                                    title="Edit User"
                                                >
                                                    <Edit2 className="w-4 h-4" />
                                                </button>
                                                <button
                                                    onClick={() => deleteModal.open(user)}
                                                    className="p-2 text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                                                    title="Delete User"
                                                >
                                                    <Trash2 className="w-4 h-4" />
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>

                {/* Pagination */}
                {pagination.totalItems > 0 && (
                    <Pagination
                        currentPage={pagination.currentPage}
                        totalPages={pagination.totalPages}
                        totalItems={pagination.totalItems}
                        itemsPerPage={pagination.itemsPerPage}
                        onPageChange={(page) => {
                            pagination.setPage(page);
                            window.scrollTo({ top: 0, behavior: 'smooth' });
                        }}
                        onItemsPerPageChange={(newItemsPerPage) => {
                            pagination.setItemsPerPage(newItemsPerPage);
                        }}
                        showItemsPerPage={true}
                    />
                )}
            </div>

            {/* Create User Modal */}
            <Modal
                isOpen={createModal.isOpen}
                onClose={createModal.close}
                title="Create New User"
                footer={
                    <>
                        <button
                            onClick={createModal.close}
                            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleCreateUser}
                            disabled={isCreating}
                            className="px-4 py-2 text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-lg shadow-sm shadow-orange-500/20 flex items-center gap-2"
                        >
                            {isCreating ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" /> Creating...
                                </>
                            ) : (
                                <>
                                    <UserIcon className="w-4 h-4" /> Create User
                                </>
                            )}
                        </button>
                    </>
                }
            >
                {createError && (
                    <div className="p-3 rounded-lg bg-red-50 dark:bg-red-950/30 border border-red-200 dark:border-red-800 flex items-start gap-2 mb-4">
                        <AlertCircle className="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                        <div className="flex-1">
                            <p className="text-sm font-medium text-red-800 dark:text-red-300">Error</p>
                            <p className="text-sm text-red-700 dark:text-red-400 mt-1">{createError}</p>
                        </div>
                        <button
                            onClick={() => setCreateError(null)}
                            className="text-red-400 hover:text-red-600 flex-shrink-0"
                        >
                            <AlertCircle className="w-4 h-4" />
                        </button>
                    </div>
                )}

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Username <span className="text-red-500">*</span></label>
                        <input
                            type="text"
                            value={createForm.username}
                            onChange={(e) => {
                                setCreateForm({ ...createForm, username: e.target.value });
                                setCreateError(null);
                            }}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-500"
                            placeholder="username"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email Address <span className="text-red-500">*</span></label>
                        <input
                            type="email"
                            value={createForm.email}
                            onChange={(e) => {
                                setCreateForm({ ...createForm, email: e.target.value });
                                setCreateError(null);
                            }}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-500"
                            placeholder="user@example.com"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Full Name</label>
                        <input
                            type="text"
                            value={createForm.full_name}
                            onChange={(e) => setCreateForm({ ...createForm, full_name: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-500"
                            placeholder="John Doe"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Password</label>
                        <input
                            type="password"
                            value={createForm.password}
                            onChange={(e) => {
                                setCreateForm({ ...createForm, password: e.target.value });
                                setCreateError(null);
                            }}
                            className={`w-full px-3 py-2 border rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 ${createError ? 'border-red-300 dark:border-red-700 focus:ring-red-500' : 'border-gray-300 dark:border-gray-700 focus:ring-orange-500'
                                }`}
                            placeholder="••••••••"
                        />
                        <PasswordStrength password={createForm.password} />
                    </div>
                </div>
            </Modal>

            {/* Edit User Modal */}
            <Modal
                isOpen={editModal.isOpen}
                onClose={editModal.close}
                title="Edit User"
                footer={
                    <>
                        <button
                            onClick={editModal.close}
                            className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                        >
                            Cancel
                        </button>
                        <button
                            onClick={handleSaveUser}
                            disabled={isSaving}
                            className="px-4 py-2 text-sm font-medium text-white bg-orange-600 hover:bg-orange-700 disabled:bg-gray-400 disabled:cursor-not-allowed rounded-lg shadow-sm shadow-orange-500/20 flex items-center gap-2"
                        >
                            {isSaving ? (
                                <>
                                    <Loader2 className="w-4 h-4 animate-spin" /> Saving...
                                </>
                            ) : (
                                <>
                                    <Save className="w-4 h-4" /> Save Changes
                                </>
                            )}
                        </button>
                    </>
                }
            >
                {message && (
                    <div className={`p-3 rounded-lg text-sm mb-4 ${message.type === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                        {message.text}
                    </div>
                )}

                <div className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Full Name</label>
                        <input
                            type="text"
                            value={editForm.full_name}
                            onChange={(e) => setEditForm({ ...editForm, full_name: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-500"
                            placeholder="Enter full name"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
                        <input
                            type="email"
                            value={editForm.email}
                            onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-500"
                            placeholder="Enter email address"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Status</label>
                        <div className="flex items-center gap-3">
                            <button
                                onClick={() => setEditForm({ ...editForm, is_active: !editForm.is_active })}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 ${editForm.is_active ? 'bg-orange-600' : 'bg-gray-200 dark:bg-gray-700'
                                    }`}
                            >
                                <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${editForm.is_active ? 'translate-x-6' : 'translate-x-1'
                                        }`}
                                />
                            </button>
                            <span className="text-sm text-gray-600 dark:text-gray-400">
                                {editForm.is_active ? 'Active Account' : 'Inactive Account'}
                            </span>
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                            Reset Password <span className="text-gray-400 font-normal">(Optional)</span>
                        </label>
                        <div className="relative">
                            <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                            <input
                                type="password"
                                value={editForm.password}
                                onChange={(e) => setEditForm({ ...editForm, password: e.target.value })}
                                placeholder="Enter new password to reset"
                                className="w-full pl-9 pr-4 py-2 border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-500"
                            />
                        </div>
                        {editForm.password && <PasswordStrength password={editForm.password} />}
                    </div>
                </div>
            </Modal>

            {/* Delete Confirmation Modal */}
            <ConfirmDialog
                isOpen={deleteModal.isOpen}
                onClose={deleteModal.close}
                onConfirm={confirmDeleteUser}
                title="Delete User"
                message={
                    deleteModal.data ? (
                        <>
                            Are you sure you want to delete <strong>{deleteModal.data.full_name || deleteModal.data.email}</strong>? This action cannot be undone.
                        </>
                    ) : (
                        'Are you sure you want to delete this user? This action cannot be undone.'
                    )
                }
                confirmText="Delete User"
                variant="danger"
                isLoading={isDeleting}
            />
        </div>
    );
};
