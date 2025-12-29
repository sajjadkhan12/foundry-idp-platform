import React, { useState, useEffect, useRef } from 'react';
import { Search, Plus, Edit2, Trash2, Users, Building2, X, Save, Mail, UserPlus, UserMinus, AlertCircle, Loader, Shield } from 'lucide-react';
import { businessUnitsApi, BusinessUnit, BusinessUnitMember, BusinessUnitCreate, BusinessUnitUpdate, BusinessUnitMemberAdd } from '../services/api/businessUnits';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import api from '../services/api';

export const BusinessUnitsPage: React.FC = () => {
    const { user, isAdmin } = useAuth();
    const { addNotification } = useNotification();
    const [businessUnits, setBusinessUnits] = useState<BusinessUnit[]>([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [showEditModal, setShowEditModal] = useState(false);
    const [showMembersModal, setShowMembersModal] = useState(false);
    const [showRolesModal, setShowRolesModal] = useState(false);
    const [selectedBusinessUnit, setSelectedBusinessUnit] = useState<BusinessUnit | null>(null);
    const [members, setMembers] = useState<BusinessUnitMember[]>([]);
    const [loadingMembers, setLoadingMembers] = useState(false);
    const [allUsers, setAllUsers] = useState<any[]>([]);
    
    const [createForm, setCreateForm] = useState<BusinessUnitCreate>({
        name: '',
        slug: '',
        description: ''
    });

    const [editForm, setEditForm] = useState<BusinessUnitUpdate>({
        name: '',
        description: '',
        is_active: true
    });

    const [addMemberForm, setAddMemberForm] = useState<BusinessUnitMemberAdd>({
        user_email: '',
        role_ids: []
    });
    const [availableRoles, setAvailableRoles] = useState<any[]>([]);
    const [loadingRoles, setLoadingRoles] = useState(false);
    const [userSearchQuery, setUserSearchQuery] = useState('');
    const [showUserDropdown, setShowUserDropdown] = useState(false);
    const [selectedUser, setSelectedUser] = useState<any | null>(null);
    const [selectedMemberForRoles, setSelectedMemberForRoles] = useState<{email: string, userId: string, currentRoles: BusinessUnitMember[]} | null>(null);
    const [pendingRoleChanges, setPendingRoleChanges] = useState<{toAdd: Set<string>, toRemove: Set<string>}>({toAdd: new Set(), toRemove: new Set()});
    const [memberRoleChanges, setMemberRoleChanges] = useState<Map<string, {toAdd: Set<string>, toRemove: Set<string>}>>(new Map());
    const [pendingMemberChanges, setPendingMemberChanges] = useState<{toAdd: Set<string>, toRemove: Set<string>}>({toAdd: new Set(), toRemove: new Set()});
    const [roleSearchQuery, setRoleSearchQuery] = useState('');
    const userSearchRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        fetchBusinessUnits();
        fetchAllUsers();
        fetchAvailableRoles();
    }, []);

    const fetchAvailableRoles = async () => {
        setLoadingRoles(true);
        try {
            // Use the business units endpoint which doesn't require platform permissions
            // This endpoint only returns BU roles (is_platform_role = False)
            const buRoles = await businessUnitsApi.getAvailableRoles();
            // Double-check: filter out any platform roles as a safety measure
            const filteredBuRoles = buRoles.filter(role => role.is_platform_role === false);
            setAvailableRoles(filteredBuRoles);
            if (filteredBuRoles.length === 0) {
                // No business unit roles found
            }
        } catch (error) {
            console.error('Failed to fetch roles:', error);
            // Don't set fallback roles - only show roles that actually exist in the database
            setAvailableRoles([]);
            addNotification('error', 'Failed to load roles. Please refresh the page.');
        } finally {
            setLoadingRoles(false);
        }
    };

    // Close dropdown when clicking outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (userSearchRef.current && !userSearchRef.current.contains(event.target as Node)) {
                setShowUserDropdown(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
        };
    }, []);

    const fetchBusinessUnits = async () => {
        setLoading(true);
        try {
            const data = await businessUnitsApi.listBusinessUnits();
            setBusinessUnits(data);
        } catch (error: any) {
            addNotification('error', error.message || 'Failed to fetch business units');
        } finally {
            setLoading(false);
        }
    };

    const fetchAllUsers = async () => {
        try {
            // Use the business units endpoint which doesn't require platform permissions
            const users = await businessUnitsApi.getAvailableUsers();
            setAllUsers(users);
        } catch (error) {
            console.error('Failed to fetch users:', error);
        }
    };

    const fetchMembers = async (businessUnitId: string) => {
        setLoadingMembers(true);
        try {
            const data = await businessUnitsApi.listMembers(businessUnitId);
            setMembers(data);
        } catch (error: any) {
            addNotification('error', error.message || 'Failed to fetch members');
        } finally {
            setLoadingMembers(false);
        }
    };

    const handleCreate = async () => {
        if (!createForm.name || !createForm.slug) {
            addNotification('error', 'Name and slug are required');
            return;
        }

        try {
            const created = await businessUnitsApi.createBusinessUnit(createForm);
            addNotification('success', `Business unit "${created.name}" created successfully`);
            setShowCreateModal(false);
            setCreateForm({ name: '', slug: '', description: '' });
            // Refresh the list to show the new business unit
            await fetchBusinessUnits();
        } catch (error: any) {
            addNotification('error', error.message || 'Failed to create business unit');
        }
    };

    const handleEdit = (bu: BusinessUnit) => {
        setSelectedBusinessUnit(bu);
        setEditForm({
            name: bu.name,
            description: bu.description || '',
            is_active: true
        });
        setShowEditModal(true);
    };

    const handleUpdate = async () => {
        if (!selectedBusinessUnit) return;

        try {
            await businessUnitsApi.updateBusinessUnit(selectedBusinessUnit.id, editForm);
            addNotification('success', 'Business unit updated successfully');
            setShowEditModal(false);
            setSelectedBusinessUnit(null);
            fetchBusinessUnits();
        } catch (error: any) {
            addNotification('error', error.message || 'Failed to update business unit');
        }
    };

    const handleDelete = async (bu: BusinessUnit) => {
        if (!confirm(`Are you sure you want to delete "${bu.name}"? This action cannot be undone.`)) {
            return;
        }

        try {
            await businessUnitsApi.deleteBusinessUnit(bu.id);
            addNotification('success', 'Business unit deleted successfully');
            fetchBusinessUnits();
        } catch (error: any) {
            addNotification('error', error.message || 'Failed to delete business unit');
        }
    };

    const handleViewMembers = async (bu: BusinessUnit) => {
        // Check if user has permission to view/manage members (permission-based, not role-name-based)
        const canManage = bu.can_manage_members === true || isAdmin;
        if (!canManage) {
            addNotification('error', 'You do not have permission to manage members of this business unit');
            return;
        }
        setSelectedBusinessUnit(bu);
        setShowMembersModal(true);
        setUserSearchQuery('');
        setSelectedUser(null);
        setShowUserDropdown(false);
        // Don't set a default role - user must select one
        setAddMemberForm({ user_email: '', role_ids: [] });
        setPendingMemberChanges({ toAdd: new Set(), toRemove: new Set() });
        await fetchMembers(bu.id);
    };

    const handleViewRoles = async (bu: BusinessUnit) => {
        // Check if user has permission to view/manage members (permission-based, not role-name-based)
        const canManage = bu.can_manage_members === true || isAdmin;
        if (!canManage) {
            addNotification('error', 'You do not have permission to manage roles in this business unit');
            return;
        }
        setSelectedBusinessUnit(bu);
        setShowRolesModal(true);
        setMemberRoleChanges(new Map());
        await fetchMembers(bu.id);
    };

    const handleStageAddRoleForMember = (userEmail: string, roleId: string) => {
        setMemberRoleChanges(prev => {
            const newMap = new Map(prev);
            const memberChanges = newMap.get(userEmail) || { toAdd: new Set<string>(), toRemove: new Set<string>() };
            
            if (memberChanges.toRemove.has(roleId)) {
                memberChanges.toRemove.delete(roleId);
            } else {
                // Check if member already has this role
                const member = members.find(m => m.user_email === userEmail && m.role_id === roleId);
                if (!member) {
                    memberChanges.toAdd.add(roleId);
                }
            }
            
            newMap.set(userEmail, memberChanges);
            return newMap;
        });
    };

    const handleStageRemoveRoleForMember = (userEmail: string, roleId: string) => {
        setMemberRoleChanges(prev => {
            const newMap = new Map(prev);
            const memberChanges = newMap.get(userEmail) || { toAdd: new Set<string>(), toRemove: new Set<string>() };
            
            if (memberChanges.toAdd.has(roleId)) {
                memberChanges.toAdd.delete(roleId);
            } else {
                memberChanges.toRemove.add(roleId);
            }
            
            newMap.set(userEmail, memberChanges);
            return newMap;
        });
    };

    const handleSaveAllRoleChanges = async () => {
        if (!selectedBusinessUnit) return;

        try {
            // Group members by email to check role counts
            const membersByUser = new Map<string, BusinessUnitMember[]>();
            members.forEach(member => {
                if (!membersByUser.has(member.user_email)) {
                    membersByUser.set(member.user_email, []);
                }
                membersByUser.get(member.user_email)!.push(member);
            });

            // Validate that no user will end up with zero roles
            for (const [userEmail, changes] of memberRoleChanges.entries()) {
                const userMembers = membersByUser.get(userEmail) || [];
                const currentRoleCount = userMembers.length;
                const willHaveRoles = currentRoleCount - changes.toRemove.size + changes.toAdd.size;
                
                if (willHaveRoles === 0) {
                    addNotification('error', `Cannot remove all roles from ${userEmail}. A member must have at least one role.`);
                    return;
                }
            }

            // Process all member role changes - additions first, then removals
            for (const [userEmail, changes] of memberRoleChanges.entries()) {
                const user = allUsers.find(u => u.email === userEmail);
                if (!user) continue;

                // Process additions FIRST (so user always has at least one role)
                for (const roleId of changes.toAdd) {
                    await businessUnitsApi.addMember(selectedBusinessUnit.id, {
                        user_email: userEmail,
                        role_ids: [roleId]
                    });
                }

                // Then process removals
                for (const roleId of changes.toRemove) {
                    const memberToRemove = members.find(m => m.user_email === userEmail && m.role_id === roleId);
                    if (memberToRemove) {
                        await businessUnitsApi.removeMember(selectedBusinessUnit.id, memberToRemove.user_id, roleId);
                    }
                }
            }

            addNotification('success', 'All role changes saved successfully');
            setMemberRoleChanges(new Map());
            await fetchMembers(selectedBusinessUnit.id);
            await fetchAllUsers();
            await fetchBusinessUnits();
        } catch (error: any) {
            addNotification('error', error.message || 'Failed to save role changes');
        }
    };

    const handleStageAddMember = (userEmail: string) => {
        setPendingMemberChanges(prev => {
            const newToAdd = new Set(prev.toAdd);
            const newToRemove = new Set(prev.toRemove);

            // Check if user is already a member
            const memberEmails = new Set(members.map(m => m.user_email));
            if (memberEmails.has(userEmail)) {
                // If they're marked for removal, unmark them
                if (newToRemove.has(userEmail)) {
                    newToRemove.delete(userEmail);
                }
            } else {
                // Toggle: if already in toAdd, remove it; otherwise add it
                if (newToAdd.has(userEmail)) {
                    newToAdd.delete(userEmail);
                } else {
                    // Only add if not marked for removal
                    if (!newToRemove.has(userEmail)) {
                        newToAdd.add(userEmail);
                    }
                }
            }

            return { toAdd: newToAdd, toRemove: newToRemove };
        });
    };

    const handleStageRemoveMember = (userEmail: string) => {
        setPendingMemberChanges(prev => {
            const newToAdd = new Set(prev.toAdd);
            const newToRemove = new Set(prev.toRemove);

            // If they're marked for addition, unmark them
            if (newToAdd.has(userEmail)) {
                newToAdd.delete(userEmail);
            } else {
                // Mark for removal
                newToRemove.add(userEmail);
            }

            return { toAdd: newToAdd, toRemove: newToRemove };
        });
    };

    const handleSaveMembers = async () => {
        if (!selectedBusinessUnit) return;

        try {
            // Process additions - add members without roles (roles can be assigned later in Manage Roles)
            for (const userEmail of pendingMemberChanges.toAdd) {
                // Add member without roles - they can be assigned roles later
                await businessUnitsApi.addMember(selectedBusinessUnit.id, {
                    user_email: userEmail,
                    role_ids: [] // Empty array - member added without roles
                });
            }

            // Process removals - remove all roles for each user
            for (const userEmail of pendingMemberChanges.toRemove) {
                const userMembers = members.filter(m => m.user_email === userEmail);
                for (const member of userMembers) {
                    await businessUnitsApi.removeMember(selectedBusinessUnit.id, member.user_id, member.role_id);
                }
            }

            addNotification('success', 'Members updated successfully');
            setPendingMemberChanges({ toAdd: new Set(), toRemove: new Set() });
            await fetchMembers(selectedBusinessUnit.id);
            await fetchAllUsers();
            await fetchBusinessUnits();
        } catch (error: any) {
            addNotification('error', error.message || 'Failed to save member changes');
        }
    };

    const handleManageRoles = (email: string, userId: string, currentRoles: BusinessUnitMember[]) => {
        // Filter out memberships without roles (role_id is null/undefined)
        const rolesWithActualRoles = currentRoles.filter(m => m.role_id != null);
        setSelectedMemberForRoles({ email, userId, currentRoles: rolesWithActualRoles });
        // Initialize pending changes
        setPendingRoleChanges({ toAdd: new Set(), toRemove: new Set() });
    };

    const handleStageAddRole = (roleId: string) => {
        setPendingRoleChanges(prev => {
            const newToAdd = new Set(prev.toAdd);
            const newToRemove = new Set(prev.toRemove);
            
            // If it was marked for removal, unmark it
            if (newToRemove.has(roleId)) {
                newToRemove.delete(roleId);
            } else {
                // Check if user already has this role
                if (selectedMemberForRoles && selectedMemberForRoles.currentRoles.some(m => m.role_id === roleId)) {
                    return prev; // Already has this role
                }
                newToAdd.add(roleId);
            }
            
            return { toAdd: newToAdd, toRemove: newToRemove };
        });
    };

    const handleStageRemoveRole = (roleId: string) => {
        setPendingRoleChanges(prev => {
            const newToAdd = new Set(prev.toAdd);
            const newToRemove = new Set(prev.toRemove);
            
            // If it was marked for addition, unmark it
            if (newToAdd.has(roleId)) {
                newToAdd.delete(roleId);
            } else {
                newToRemove.add(roleId);
            }
            
            return { toAdd: newToAdd, toRemove: newToRemove };
        });
    };

    const handleSaveRoleChanges = async () => {
        if (!selectedBusinessUnit || !selectedMemberForRoles) return;

        try {
            // Check if removing last role without adding a new one
            // Only count memberships with actual roles (filter out NULL role_id)
            const currentRoleCount = selectedMemberForRoles.currentRoles.filter(m => m.role_id != null).length;
            const willHaveRoles = currentRoleCount - pendingRoleChanges.toRemove.size + pendingRoleChanges.toAdd.size;
            
            if (willHaveRoles === 0) {
                addNotification('error', 'Cannot remove all roles. A member must have at least one role. Please add a role first or remove the member entirely from the Business Unit.');
                return;
            }

            // Process additions FIRST (so user always has at least one role)
            for (const roleId of pendingRoleChanges.toAdd) {
                await businessUnitsApi.addMember(selectedBusinessUnit.id, {
                    user_email: selectedMemberForRoles.email,
                    role_ids: [roleId]
                });
            }

            // Then process removals
            for (const roleId of pendingRoleChanges.toRemove) {
                const memberToRemove = selectedMemberForRoles.currentRoles.find(m => m.role_id === roleId);
                if (memberToRemove) {
                    await businessUnitsApi.removeMember(selectedBusinessUnit.id, selectedMemberForRoles.userId, roleId);
                }
            }

            addNotification('success', 'Roles updated successfully');
            setSelectedMemberForRoles(null);
            setPendingRoleChanges({ toAdd: new Set(), toRemove: new Set() });
            await fetchMembers(selectedBusinessUnit.id);
            await fetchAllUsers();
        } catch (error: any) {
            addNotification('error', error.message || 'Failed to save role changes');
        }
    };

    // Filter users based on search query
    const filteredUsers = allUsers.filter((user) => {
        if (!userSearchQuery.trim()) return false;
        const query = userSearchQuery.toLowerCase();
        const email = (user.email || '').toLowerCase();
        const name = (user.full_name || user.username || '').toLowerCase();
        return email.includes(query) || name.includes(query);
    });

    const handleUserSelect = (user: any) => {
        setSelectedUser(user);
        setAddMemberForm({ ...addMemberForm, user_email: user.email });
        setUserSearchQuery(user.email);
        setShowUserDropdown(false);
    };

    const handleRemoveMember = async (member: BusinessUnitMember) => {
        if (!selectedBusinessUnit) return;
        const roleName = member.role ? member.role.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'role';
        if (!confirm(`Remove ${roleName} role from ${member.user_email}?`)) {
            return;
        }

        try {
            await businessUnitsApi.removeMember(selectedBusinessUnit.id, member.user_id, member.role_id);
            addNotification('success', `Role removed successfully from ${member.user_email}`);
            await fetchMembers(selectedBusinessUnit.id);
            await fetchAllUsers(); // Refresh available users list
        } catch (error: any) {
            addNotification('error', error.message || 'Failed to remove role');
        }
    };

    const filteredBusinessUnits = businessUnits.filter(bu =>
        bu.name.toLowerCase().includes(search.toLowerCase()) ||
        bu.slug.toLowerCase().includes(search.toLowerCase())
    );

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-[400px]">
                <Loader className="w-8 h-8 animate-spin text-orange-600" />
            </div>
        );
    }

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Business Units</h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-1">Manage business units and their members</p>
                </div>
                {isAdmin && (
                    <button
                        onClick={() => setShowCreateModal(true)}
                        className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors font-medium"
                    >
                        <Plus className="w-5 h-5" />
                        Create Business Unit
                    </button>
                )}
            </div>

            {/* Search */}
            <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                    type="text"
                    placeholder="Search business units..."
                    value={search}
                    onChange={(e) => setSearch(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-900 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                />
            </div>

            {/* Business Units List */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredBusinessUnits.map((bu) => (
                    <div
                        key={bu.id}
                        className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-800 rounded-xl p-6 hover:border-orange-500 dark:hover:border-orange-500 transition-colors"
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex items-center gap-3">
                                <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
                                    <Building2 className="w-6 h-6 text-orange-600 dark:text-orange-400" />
                                </div>
                                <div>
                                    <h3 className="font-semibold text-gray-900 dark:text-white">{bu.name}</h3>
                                    <p className="text-sm text-gray-500 dark:text-gray-400">/{bu.slug}</p>
                                </div>
                            </div>
                            {(bu.can_manage_members === true || isAdmin) && (
                                <div className="flex items-center gap-2">
                                    <button
                                        onClick={() => handleEdit(bu)}
                                        className="p-1.5 text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded transition-colors"
                                        title="Edit Business Unit"
                                    >
                                        <Edit2 className="w-4 h-4" />
                                    </button>
                                    {isAdmin && (
                                        <button
                                            onClick={() => handleDelete(bu)}
                                            className="p-1.5 text-gray-400 hover:text-red-600 dark:hover:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded transition-colors"
                                            title="Delete Business Unit"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    )}
                                </div>
                            )}
                        </div>
                        {bu.description && (
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">{bu.description}</p>
                        )}
                        <div className="space-y-2 pt-4 border-t border-gray-100 dark:border-gray-800">
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-500 dark:text-gray-400">{bu.member_count || 0} {bu.member_count === 1 ? 'member' : 'members'}</span>
                                {(bu.can_manage_members === true || isAdmin) && (
                                    <button
                                        onClick={() => handleViewMembers(bu)}
                                        className="text-sm font-medium text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300"
                                    >
                                        Manage Members
                                    </button>
                                )}
                            </div>
                            <div className="flex items-center justify-between">
                                <span className="text-sm text-gray-500 dark:text-gray-400">Roles</span>
                                {(bu.can_manage_members === true || isAdmin) && (
                                    <button
                                        onClick={() => handleViewRoles(bu)}
                                        className="text-sm font-medium text-orange-600 dark:text-orange-400 hover:text-orange-700 dark:hover:text-orange-300"
                                    >
                                        Manage Roles
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {filteredBusinessUnits.length === 0 && (
                <div className="text-center py-12">
                    <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-500 dark:text-gray-400">No business units found</p>
                </div>
            )}

            {/* Create Modal */}
            {showCreateModal && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto">
                    <div className="bg-white dark:bg-gray-900 rounded-2xl p-4 sm:p-6 max-w-md w-full border border-gray-200 dark:border-gray-800 my-4">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Create Business Unit</h2>
                            <button
                                onClick={() => setShowCreateModal(false)}
                                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Name *
                                </label>
                                <input
                                    type="text"
                                    value={createForm.name}
                                    onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                                    placeholder="e.g., it-operations"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Slug *
                                </label>
                                <input
                                    type="text"
                                    value={createForm.slug}
                                    onChange={(e) => setCreateForm({ ...createForm, slug: e.target.value.toLowerCase().replace(/\s+/g, '-') })}
                                    className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                                    placeholder="e.g., it-operations"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Description
                                </label>
                                <textarea
                                    value={createForm.description}
                                    onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                                    rows={3}
                                    placeholder="Optional description"
                                />
                            </div>
                            <div className="flex gap-3 pt-4">
                                <button
                                    onClick={() => setShowCreateModal(false)}
                                    className="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleCreate}
                                    className="flex-1 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors font-medium"
                                >
                                    Create
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Edit Modal */}
            {showEditModal && selectedBusinessUnit && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4 overflow-y-auto">
                    <div className="bg-white dark:bg-gray-900 rounded-2xl p-4 sm:p-6 max-w-md w-full border border-gray-200 dark:border-gray-800 my-4">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-xl font-bold text-gray-900 dark:text-white">Edit Business Unit</h2>
                            <button
                                onClick={() => setShowEditModal(false)}
                                className="p-1 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>
                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Name
                                </label>
                                <input
                                    type="text"
                                    value={editForm.name}
                                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                                    Description
                                </label>
                                <textarea
                                    value={editForm.description}
                                    onChange={(e) => setEditForm({ ...editForm, description: e.target.value })}
                                    className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                                    rows={3}
                                />
                            </div>
                            <div className="flex gap-3 pt-4">
                                <button
                                    onClick={() => setShowEditModal(false)}
                                    className="flex-1 px-4 py-2 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleUpdate}
                                    className="flex-1 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors font-medium"
                                >
                                    Save
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Members Modal */}
            {showMembersModal && selectedBusinessUnit && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                    <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-4xl border border-gray-200 dark:border-gray-800 h-[600px] flex flex-col">
                        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Manage Members</h3>
                                <p className="text-sm text-gray-500 dark:text-gray-400">{selectedBusinessUnit.name}</p>
                            </div>
                            <button
                                onClick={() => {
                                    setShowMembersModal(false);
                                    setSelectedBusinessUnit(null);
                                    setUserSearchQuery('');
                                    setSelectedUser(null);
                                    setShowUserDropdown(false);
                                    setAddMemberForm({ user_email: '', role_ids: [] });
                                }}
                                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-hidden flex flex-col md:flex-row">
                            {/* Available Users */}
                            <div className="flex-1 p-4 border-r border-gray-200 dark:border-gray-800 overflow-y-auto">
                                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Available Users</h4>

                                {/* Search Input */}
                                <div className="relative mb-3">
                                    <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                    <input
                                        type="text"
                                        placeholder="Search by name or email..."
                                        value={userSearchQuery}
                                        onChange={(e) => {
                                            setUserSearchQuery(e.target.value);
                                            setShowUserDropdown(true);
                                        }}
                                        className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-500"
                                    />
                                </div>


                                <div className="space-y-2" ref={userSearchRef}>
                                    {loadingMembers ? (
                                        <div className="flex items-center justify-center py-8 text-gray-500">
                                            <Loader className="w-6 h-6 animate-spin text-orange-600" />
                                        </div>
                                    ) : (() => {
                                        // Get member emails to filter them out (excluding pending removals)
                                        const memberEmails = new Set(members.map(m => m.user_email));
                                        const availableUsersList = allUsers.filter(user => 
                                            (!memberEmails.has(user.email) || pendingMemberChanges.toRemove.has(user.email)) &&
                                            !pendingMemberChanges.toAdd.has(user.email) &&
                                            (userSearchQuery === '' || 
                                             user.email.toLowerCase().includes(userSearchQuery.toLowerCase()) ||
                                             (user.full_name || '').toLowerCase().includes(userSearchQuery.toLowerCase()) ||
                                             (user.username || '').toLowerCase().includes(userSearchQuery.toLowerCase()))
                                        );

                                        return availableUsersList.length === 0 ? (
                                            <p className="text-sm text-gray-500 text-center py-8">
                                                {userSearchQuery ? 'No users found' : 'No available users'}
                                            </p>
                                        ) : (
                                            availableUsersList.map(user => {
                                                const isPendingAdd = pendingMemberChanges.toAdd.has(user.email);
                                                return (
                                                    <div
                                                        key={user.id}
                                                        className={`flex items-center justify-between p-3 rounded-lg border ${
                                                            isPendingAdd
                                                                ? 'bg-green-50 dark:bg-green-900/10 border-green-200 dark:border-green-900/30'
                                                                : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700'
                                                        }`}
                                                    >
                                                        <div className="flex-1 min-w-0">
                                                            <div className="flex items-center gap-2">
                                                                <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                                                    {user.full_name || user.username || 'Unknown'}
                                                                </p>
                                                                {isPendingAdd && (
                                                                    <span className="text-[10px] font-bold text-green-600 bg-green-100 dark:bg-green-900/40 px-1.5 py-0.5 rounded">NEW</span>
                                                                )}
                                                            </div>
                                                            <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
                                                        </div>
                                                        <button
                                                            onClick={() => handleStageAddMember(user.email)}
                                                            className={`p-1.5 rounded-lg transition-colors flex-shrink-0 ml-2 ${
                                                                isPendingAdd
                                                                    ? 'text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20'
                                                                    : 'text-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20'
                                                            }`}
                                                            title={isPendingAdd ? 'Cancel adding user' : 'Add user to business unit'}
                                                        >
                                                            {isPendingAdd ? <X className="w-4 h-4" /> : <UserPlus className="w-4 h-4" />}
                                                        </button>
                                                    </div>
                                                );
                                            })
                                        );
                                    })()}
                                </div>
                            </div>

                            {/* Current Members */}
                            <div className="flex-1 p-4 overflow-y-auto">
                                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Current Members</h4>
                                <div className="space-y-2">
                                    {loadingMembers ? (
                                        <div className="flex items-center justify-center py-8 text-gray-500">
                                            <Loader className="w-6 h-6 animate-spin text-orange-600" />
                                        </div>
                                    ) : (() => {
                                        // Group members by user_email to show all roles for each user
                                        const membersByUser = new Map<string, BusinessUnitMember[]>();
                                        members.forEach(member => {
                                            if (!membersByUser.has(member.user_email)) {
                                                membersByUser.set(member.user_email, []);
                                            }
                                            membersByUser.get(member.user_email)!.push(member);
                                        });

                                        const memberEntries = Array.from(membersByUser.entries());

                                        return (
                                            <>
                                                {/* Existing Members */}
                                                {memberEntries
                                                    .filter(([email]) => !pendingMemberChanges.toRemove.has(email))
                                                    .map(([email, userMembers]) => {
                                                        const matchingBU = businessUnits.find(bu => bu.id === selectedBusinessUnit.id);
                                                        const canManage = isAdmin || (matchingBU && matchingBU.can_manage_members === true);
                                                        
                                                        return (
                                                            <div
                                                                key={email}
                                                                className="p-3 bg-orange-50 dark:bg-orange-900/10 border border-orange-100 dark:border-orange-900/30 rounded-lg"
                                                            >
                                                                <div className="flex items-start justify-between">
                                                                    <div className="flex-1 min-w-0">
                                                                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                                                            {userMembers[0].user_name || email}
                                                                        </p>
                                                                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{email}</p>
                                                                        <div className="flex flex-wrap items-center gap-2 mt-2">
                                                                            {userMembers.filter(m => m.role_id != null).map((member) => (
                                                                                <div key={member.id} className="flex items-center gap-1.5">
                                                                                    <span className="px-2 py-0.5 text-xs font-medium bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400 rounded capitalize">
                                                                                        {member.role ? member.role.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) : 'Unknown'}
                                                                                    </span>
                                                                                </div>
                                                                            ))}
                                                                            {userMembers.filter(m => m.role_id != null).length === 0 && (
                                                                                <span className="px-2 py-0.5 text-xs font-medium bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 rounded">
                                                                                    No roles
                                                                                </span>
                                                                            )}
                                                                        </div>
                                                                        {canManage && (
                                                                            <button
                                                                                onClick={() => handleManageRoles(email, userMembers[0].user_id, userMembers)}
                                                                                className="mt-2 text-xs text-orange-600 dark:text-orange-400 hover:underline flex items-center gap-1"
                                                                            >
                                                                                <Shield className="w-3 h-3" />
                                                                                Manage Roles
                                                                            </button>
                                                                        )}
                                                                    </div>
                                                                    {canManage && (
                                                                        <button
                                                                            onClick={() => handleStageRemoveMember(email)}
                                                                            className="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors flex-shrink-0 ml-2"
                                                                            title="Remove user from business unit"
                                                                        >
                                                                            <UserMinus className="w-4 h-4" />
                                                                        </button>
                                                                    )}
                                                                </div>
                                                            </div>
                                                        );
                                                    })}
                                                
                                                {/* Pending Removals */}
                                                {memberEntries
                                                    .filter(([email]) => pendingMemberChanges.toRemove.has(email))
                                                    .map(([email, userMembers]) => (
                                                        <div
                                                            key={email}
                                                            className="p-3 bg-red-50 dark:bg-red-900/10 border border-red-100 dark:border-red-900/30 rounded-lg opacity-60"
                                                        >
                                                            <div className="flex items-start justify-between">
                                                                <div className="flex-1 min-w-0">
                                                                    <p className="text-sm font-medium line-through text-gray-500 truncate">
                                                                        {userMembers[0].user_name || email}
                                                                    </p>
                                                                    <p className="text-xs text-gray-500 truncate">{email}</p>
                                                                </div>
                                                                <button
                                                                    onClick={() => handleStageRemoveMember(email)}
                                                                    className="p-1.5 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors flex-shrink-0 ml-2"
                                                                    title="Cancel removal"
                                                                >
                                                                    <UserPlus className="w-4 h-4" />
                                                                </button>
                                                            </div>
                                                        </div>
                                                    ))}
                                                
                                                {/* Pending Additions */}
                                                {Array.from(pendingMemberChanges.toAdd).map(userEmail => {
                                                    const user = allUsers.find(u => u.email === userEmail);
                                                    if (!user) return null;
                                                    return (
                                                        <div
                                                            key={userEmail}
                                                            className="p-3 bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/30 rounded-lg"
                                                        >
                                                            <div className="flex items-start justify-between">
                                                                <div className="flex-1 min-w-0">
                                                                    <div className="flex items-center gap-2">
                                                                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                                                                            {user.full_name || user.username || 'Unknown'}
                                                                        </p>
                                                                        <span className="text-[10px] font-bold text-green-600 bg-green-100 dark:bg-green-900/40 px-1.5 py-0.5 rounded">NEW</span>
                                                                    </div>
                                                                    <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{userEmail}</p>
                                                                </div>
                                                                <button
                                                                    onClick={() => handleStageAddMember(userEmail)}
                                                                    className="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors flex-shrink-0 ml-2"
                                                                    title="Cancel adding user"
                                                                >
                                                                    <X className="w-4 h-4" />
                                                                </button>
                                                            </div>
                                                        </div>
                                                    );
                                                })}
                                                
                                                {memberEntries.length === 0 && pendingMemberChanges.toAdd.size === 0 && (
                                                    <p className="text-sm text-gray-500 text-center py-4">No members yet</p>
                                                )}
                                            </>
                                        );
                                    })()}
                                </div>
                            </div>
                        </div>

                        <div className="flex justify-between items-center p-6 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50">
                            <div className="text-sm">
                                {(pendingMemberChanges.toAdd.size > 0 || pendingMemberChanges.toRemove.size > 0) && (
                                    <span className="text-amber-600 dark:text-amber-400 font-medium flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                                        Unsaved changes
                                    </span>
                                )}
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => {
                                        setShowMembersModal(false);
                                        setSelectedBusinessUnit(null);
                                        setUserSearchQuery('');
                                        setSelectedUser(null);
                                        setShowUserDropdown(false);
                                        setAddMemberForm({ user_email: '', role_ids: [] });
                                        setPendingMemberChanges({ toAdd: new Set(), toRemove: new Set() });
                                    }}
                                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSaveMembers}
                                    disabled={pendingMemberChanges.toAdd.size === 0 && pendingMemberChanges.toRemove.size === 0}
                                    className={`px-4 py-2 text-sm font-medium text-white rounded-lg shadow-sm flex items-center gap-2 ${
                                        pendingMemberChanges.toAdd.size === 0 && pendingMemberChanges.toRemove.size === 0
                                            ? 'bg-gray-400 cursor-not-allowed'
                                            : 'bg-orange-600 hover:bg-orange-700 shadow-orange-500/20'
                                    }`}
                                >
                                    <Save className="w-4 h-4" /> Save Changes
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Manage Roles Modal for a Member */}
            {selectedMemberForRoles && selectedBusinessUnit && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                    <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-2xl border border-gray-200 dark:border-gray-800 h-[600px] flex flex-col">
                        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Manage Roles</h3>
                                <p className="text-sm text-gray-500 dark:text-gray-400">{selectedMemberForRoles.email}</p>
                            </div>
                            <button
                                onClick={() => {
                                    setSelectedMemberForRoles(null);
                                    setPendingRoleChanges({ toAdd: new Set(), toRemove: new Set() });
                                }}
                                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        <div className="flex-1 overflow-hidden flex flex-col md:flex-row">
                            {/* Available Roles */}
                            <div className="flex-1 p-4 border-r border-gray-200 dark:border-gray-800 overflow-y-auto">
                                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Available Roles</h4>
                                <div className="space-y-2">
                                    {availableRoles
                                        .filter(role => role.is_platform_role === false)
                                        .filter(role => {
                                            const hasRole = selectedMemberForRoles.currentRoles.some(m => m.role_id === role.id);
                                            const isPendingAdd = pendingRoleChanges.toAdd.has(role.id);
                                            const isPendingRemove = pendingRoleChanges.toRemove.has(role.id);
                                            return (!hasRole && !isPendingAdd) || isPendingRemove;
                                        })
                                        .map(role => (
                                            <div key={role.id} className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-800 rounded-lg">
                                                <div className="flex items-center gap-3">
                                                    <div className="p-1.5 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                                                        <Shield className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                                                    </div>
                                                    <div>
                                                        <p className="text-sm font-medium text-gray-900 dark:text-white">
                                                            {role.name.charAt(0).toUpperCase() + role.name.slice(1).replace(/-/g, ' ')}
                                                        </p>
                                                        {role.description && (
                                                            <p className="text-xs text-gray-500 line-clamp-1">{role.description}</p>
                                                        )}
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => handleStageAddRole(role.id)}
                                                    className="p-1.5 text-orange-600 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-lg transition-colors"
                                                >
                                                    <Plus className="w-4 h-4" />
                                                </button>
                                            </div>
                                        ))}
                                    {availableRoles.filter(role => {
                                        const hasRole = selectedMemberForRoles.currentRoles.some(m => m.role_id === role.id);
                                        const isPendingAdd = pendingRoleChanges.toAdd.has(role.id);
                                        const isPendingRemove = pendingRoleChanges.toRemove.has(role.id);
                                        return role.is_platform_role === false && (!hasRole && !isPendingAdd) || isPendingRemove;
                                    }).length === 0 && (
                                        <p className="text-sm text-gray-500 text-center py-8">No available roles</p>
                                    )}
                                </div>
                            </div>

                            {/* Current Roles */}
                            <div className="flex-1 p-4 overflow-y-auto">
                                <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Current Roles</h4>
                                <div className="space-y-2">
                                    {selectedMemberForRoles.currentRoles.filter(m => m.role_id != null).map(member => {
                                        const role = availableRoles.find(r => r.id === member.role_id);
                                        const isPendingRemove = pendingRoleChanges.toRemove.has(member.role_id!);
                                        return (
                                            <div
                                                key={member.id}
                                                className={`flex items-center justify-between p-3 rounded-lg border ${
                                                    isPendingRemove
                                                        ? 'bg-red-50 dark:bg-red-900/10 border-red-100 dark:border-red-900/30 opacity-60'
                                                        : 'bg-orange-50 dark:bg-orange-900/10 border-orange-100 dark:border-orange-900/30'
                                                }`}
                                            >
                                                <div className="flex items-center gap-3">
                                                    <div className="p-1.5 bg-orange-50 dark:bg-orange-900/20 rounded-lg">
                                                        <Shield className="w-4 h-4 text-orange-600 dark:text-orange-400" />
                                                    </div>
                                                    <div>
                                                        <p className={`text-sm font-medium ${isPendingRemove ? 'line-through text-gray-500' : 'text-gray-900 dark:text-white'}`}>
                                                            {role ? (role.name.charAt(0).toUpperCase() + role.name.slice(1).replace(/-/g, ' ')) : member.role}
                                                        </p>
                                                        {role?.description && (
                                                            <p className="text-xs text-gray-500 line-clamp-1">{role.description}</p>
                                                        )}
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => handleStageRemoveRole(member.role_id!)}
                                                    className={`p-1.5 rounded-lg transition-colors ${isPendingRemove
                                                        ? 'text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800'
                                                        : 'text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20'
                                                        }`}
                                                >
                                                    {isPendingRemove ? <Plus className="w-4 h-4" /> : <X className="w-4 h-4" />}
                                                </button>
                                            </div>
                                        );
                                    })}

                                    {/* Pending Additions */}
                                    {Array.from(pendingRoleChanges.toAdd).map(roleId => {
                                        const role = availableRoles.find(r => r.id === roleId);
                                        if (!role) return null;
                                        return (
                                            <div key={roleId} className="flex items-center justify-between p-3 bg-green-50 dark:bg-green-900/10 border border-green-100 dark:border-green-900/30 rounded-lg">
                                                <div className="flex items-center gap-3">
                                                    <div className="p-1.5 bg-green-50 dark:bg-green-900/20 rounded-lg">
                                                        <Shield className="w-4 h-4 text-green-600 dark:text-green-400" />
                                                    </div>
                                                    <div>
                                                        <div className="flex items-center gap-2">
                                                            <p className="text-sm font-medium text-gray-900 dark:text-white">
                                                                {role.name.charAt(0).toUpperCase() + role.name.slice(1).replace(/-/g, ' ')}
                                                            </p>
                                                            <span className="text-[10px] font-bold text-green-600 bg-green-100 dark:bg-green-900/40 px-1.5 py-0.5 rounded">NEW</span>
                                                        </div>
                                                        {role.description && (
                                                            <p className="text-xs text-gray-500 line-clamp-1">{role.description}</p>
                                                        )}
                                                    </div>
                                                </div>
                                                <button
                                                    onClick={() => handleStageAddRole(roleId)}
                                                    className="p-1.5 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                                                >
                                                    <X className="w-4 h-4" />
                                                </button>
                                            </div>
                                        );
                                    })}

                                    {selectedMemberForRoles.currentRoles.filter(m => m.role_id != null).length === 0 && pendingRoleChanges.toAdd.size === 0 && (
                                        <p className="text-sm text-gray-500 text-center py-4">No roles assigned</p>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Footer with Save Button */}
                        <div className="flex justify-between items-center p-6 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 rounded-b-xl">
                            <div className="text-sm">
                                {(pendingRoleChanges.toAdd.size > 0 || pendingRoleChanges.toRemove.size > 0) && (
                                    <span className="text-amber-600 dark:text-amber-400 font-medium flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                                        Unsaved changes
                                    </span>
                                )}
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => {
                                        setSelectedMemberForRoles(null);
                                        setPendingRoleChanges({ toAdd: new Set(), toRemove: new Set() });
                                    }}
                                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSaveRoleChanges}
                                    disabled={pendingRoleChanges.toAdd.size === 0 && pendingRoleChanges.toRemove.size === 0}
                                    className={`px-4 py-2 text-sm font-medium text-white rounded-lg shadow-sm flex items-center gap-2 ${
                                        pendingRoleChanges.toAdd.size === 0 && pendingRoleChanges.toRemove.size === 0
                                            ? 'bg-gray-400 cursor-not-allowed'
                                            : 'bg-orange-600 hover:bg-orange-700 shadow-orange-500/20'
                                    }`}
                                >
                                    <Save className="w-4 h-4" /> Save Changes
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Manage Roles Modal - Table view for scalability */}
            {showRolesModal && selectedBusinessUnit && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                    <div className="bg-white dark:bg-gray-900 rounded-xl shadow-xl w-full max-w-6xl border border-gray-200 dark:border-gray-800 h-[700px] flex flex-col">
                        <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-800">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Manage Roles</h3>
                                <p className="text-sm text-gray-500 dark:text-gray-400">{selectedBusinessUnit.name}</p>
                            </div>
                            <button
                                onClick={() => {
                                    setShowRolesModal(false);
                                    setSelectedBusinessUnit(null);
                                    setMemberRoleChanges(new Map());
                                    setRoleSearchQuery('');
                                }}
                                className="text-gray-400 hover:text-gray-500 dark:hover:text-gray-300"
                            >
                                <X className="w-5 h-5" />
                            </button>
                        </div>

                        {/* Search Bar */}
                        <div className="px-6 pt-4 pb-2">
                            <div className="relative">
                                <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
                                <input
                                    type="text"
                                    placeholder="Search members by name or email..."
                                    value={roleSearchQuery}
                                    onChange={(e) => setRoleSearchQuery(e.target.value)}
                                    className="w-full pl-9 pr-3 py-2 text-sm border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-orange-500"
                                />
                            </div>
                        </div>

                        {/* Table View */}
                        <div className="flex-1 overflow-auto px-6 pb-4">
                            {loadingMembers ? (
                                <div className="flex items-center justify-center py-12 text-gray-500">
                                    <Loader className="w-6 h-6 animate-spin text-orange-600" />
                                </div>
                            ) : (() => {
                                // Group members by user_email
                                const membersByUser = new Map<string, BusinessUnitMember[]>();
                                members.forEach(member => {
                                    if (!membersByUser.has(member.user_email)) {
                                        membersByUser.set(member.user_email, []);
                                    }
                                    membersByUser.get(member.user_email)!.push(member);
                                });

                                // Filter by search query
                                let memberEntries = Array.from(membersByUser.entries());
                                if (roleSearchQuery) {
                                    const query = roleSearchQuery.toLowerCase();
                                    memberEntries = memberEntries.filter(([email, userMembers]) => 
                                        email.toLowerCase().includes(query) ||
                                        (userMembers[0].user_name || '').toLowerCase().includes(query)
                                    );
                                }

                                if (memberEntries.length === 0) {
                                    return (
                                        <div className="text-center py-12">
                                            <p className="text-sm text-gray-500">
                                                {roleSearchQuery ? 'No members found' : 'No members yet'}
                                            </p>
                                        </div>
                                    );
                                }

                                return (
                                    <div className="overflow-x-auto">
                                        <table className="w-full text-sm">
                                            <thead>
                                                <tr className="border-b border-gray-200 dark:border-gray-700">
                                                    <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Member</th>
                                                    <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Current Roles</th>
                                                    <th className="text-left py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Add Role</th>
                                                    <th className="text-right py-3 px-4 font-medium text-gray-700 dark:text-gray-300">Actions</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {memberEntries.map(([email, userMembers]) => {
                                                    const memberChanges = memberRoleChanges.get(email) || { toAdd: new Set<string>(), toRemove: new Set<string>() };
                                                    const hasChanges = memberChanges.toAdd.size > 0 || memberChanges.toRemove.size > 0;
                                                    
                                                    return (
                                                        <tr
                                                            key={email}
                                                            className={`border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50 dark:hover:bg-gray-800/50 ${
                                                                hasChanges ? 'bg-amber-50/50 dark:bg-amber-900/10' : ''
                                                            }`}
                                                        >
                                                            <td className="py-3 px-4">
                                                                <div>
                                                                    <p className="text-sm font-medium text-gray-900 dark:text-white">
                                                                        {userMembers[0].user_name || email}
                                                                    </p>
                                                                    <p className="text-xs text-gray-500 dark:text-gray-400">{email}</p>
                                                                </div>
                                                            </td>
                                                            <td className="py-3 px-4">
                                                                <div className="flex flex-wrap gap-1.5">
                                                                    {/* Current Roles - filter out NULL-role memberships */}
                                                                    {userMembers.filter(m => m.role_id != null).map((member) => {
                                                                        const role = availableRoles.find(r => r.id === member.role_id);
                                                                        const isPendingRemove = memberChanges.toRemove.has(member.role_id!);
                                                                        return (
                                                                            <span
                                                                                key={member.id}
                                                                                className={`inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium ${
                                                                                    isPendingRemove
                                                                                        ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 line-through opacity-60'
                                                                                        : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
                                                                                }`}
                                                                            >
                                                                                <Shield className="w-3 h-3" />
                                                                                {role ? (role.name.charAt(0).toUpperCase() + role.name.slice(1).replace(/-/g, ' ')) : member.role}
                                                                                {!isPendingRemove && (
                                                                                    <button
                                                                                        onClick={() => handleStageRemoveRoleForMember(email, member.role_id!)}
                                                                                        className="ml-1 hover:bg-red-200 dark:hover:bg-red-900/50 rounded p-0.5 transition-colors"
                                                                                        title="Remove role"
                                                                                    >
                                                                                        <X className="w-3 h-3" />
                                                                                    </button>
                                                                                )}
                                                                            </span>
                                                                        );
                                                                    })}
                                                                    {/* Pending Additions */}
                                                                    {Array.from(memberChanges.toAdd).map(roleId => {
                                                                        const role = availableRoles.find(r => r.id === roleId);
                                                                        if (!role) return null;
                                                                        return (
                                                                            <span
                                                                                key={roleId}
                                                                                className="inline-flex items-center gap-1 px-2 py-1 rounded text-xs font-medium bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400"
                                                                            >
                                                                                <Shield className="w-3 h-3" />
                                                                                {role.name.charAt(0).toUpperCase() + role.name.slice(1).replace(/-/g, ' ')}
                                                                                <span className="text-[10px] font-bold bg-green-200 dark:bg-green-900/50 px-1 rounded">NEW</span>
                                                                                <button
                                                                                    onClick={() => handleStageAddRoleForMember(email, roleId)}
                                                                                    className="ml-1 hover:bg-red-200 dark:hover:bg-red-900/50 rounded p-0.5 transition-colors"
                                                                                    title="Cancel addition"
                                                                                >
                                                                                    <X className="w-3 h-3" />
                                                                                </button>
                                                                            </span>
                                                                        );
                                                                    })}
                                                                </div>
                                                            </td>
                                                            <td className="py-3 px-4">
                                                                <select
                                                                    value=""
                                                                    onChange={(e) => {
                                                                        if (e.target.value) {
                                                                            handleStageAddRoleForMember(email, e.target.value);
                                                                            e.target.value = '';
                                                                        }
                                                                    }}
                                                                    className="w-full max-w-xs px-2 py-1.5 text-xs border border-gray-300 dark:border-gray-700 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-orange-500"
                                                                >
                                                                    <option value="">Select role...</option>
                                                                    {availableRoles
                                                                        .filter(role => {
                                                                            const hasRole = userMembers.some(m => m.role_id === role.id);
                                                                            const isPendingAdd = memberChanges.toAdd.has(role.id);
                                                                            return role.is_platform_role === false && !hasRole && !isPendingAdd;
                                                                        })
                                                                        .map(role => (
                                                                            <option key={role.id} value={role.id}>
                                                                                {role.name.charAt(0).toUpperCase() + role.name.slice(1).replace(/-/g, ' ')}
                                                                            </option>
                                                                        ))}
                                                                </select>
                                                            </td>
                                                            <td className="py-3 px-4 text-right">
                                                                {hasChanges && (
                                                                    <span className="text-xs text-amber-600 dark:text-amber-400 font-medium">
                                                                        Unsaved
                                                                    </span>
                                                                )}
                                                            </td>
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    </div>
                                );
                            })()}
                        </div>

                        {/* Footer with Save Button */}
                        <div className="flex justify-between items-center p-6 border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-800/50 rounded-b-xl">
                            <div className="text-sm">
                                {Array.from(memberRoleChanges.values()).some(changes => changes.toAdd.size > 0 || changes.toRemove.size > 0) && (
                                    <span className="text-amber-600 dark:text-amber-400 font-medium flex items-center gap-2">
                                        <div className="w-2 h-2 rounded-full bg-amber-500 animate-pulse"></div>
                                        Unsaved changes
                                    </span>
                                )}
                            </div>
                            <div className="flex gap-3">
                                <button
                                    onClick={() => {
                                        setShowRolesModal(false);
                                        setSelectedBusinessUnit(null);
                                        setMemberRoleChanges(new Map());
                                    }}
                                    className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                                >
                                    Cancel
                                </button>
                                <button
                                    onClick={handleSaveAllRoleChanges}
                                    disabled={Array.from(memberRoleChanges.values()).every(changes => changes.toAdd.size === 0 && changes.toRemove.size === 0)}
                                    className={`px-4 py-2 text-sm font-medium text-white rounded-lg shadow-sm flex items-center gap-2 ${
                                        Array.from(memberRoleChanges.values()).every(changes => changes.toAdd.size === 0 && changes.toRemove.size === 0)
                                            ? 'bg-gray-400 cursor-not-allowed'
                                            : 'bg-orange-600 hover:bg-orange-700 shadow-orange-500/20'
                                    }`}
                                >
                                    <Save className="w-4 h-4" /> Save Changes
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

