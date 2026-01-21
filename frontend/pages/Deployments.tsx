import React, { useState, useEffect, useRef, useMemo } from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
    Server, ExternalLink, Clock, Search, Filter, X,
    AlertCircle, Loader2, User, Calendar, Building2,
    ChevronDown, LayoutGrid
} from 'lucide-react';
import api from '../services/api';
import { StatusBadge, PluginBadge } from '../components/Badges';
import { CloudProviderBadge, RegionBadge, MetadataTag } from '../components/CloudTags';
import { EnvironmentBadge } from '../components/EnvironmentBadge';
import { appLogger } from '../utils/logger';
import { Pagination } from '../components/Pagination';
import { useAuth } from '../contexts/AuthContext';
import { BusinessUnitWarningModal } from '../components/BusinessUnitWarningModal';

import { Deployment } from '../types';

export const DeploymentsPage: React.FC = () => {
    const { user, isAdmin, isOwner, activeBusinessUnit, hasBusinessUnitAccess, businessUnits, isLoadingBusinessUnits } = useAuth();
    const location = useLocation();

    // State
    const [deployments, setDeployments] = useState<Deployment[]>([]);
    const [filteredDeployments, setFilteredDeployments] = useState<Deployment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');
    const [providerFilter, setProviderFilter] = useState<string>('all');
    const [environmentFilter, setEnvironmentFilter] = useState<string>('all');
    const [userFilter, setUserFilter] = useState<string>('all');
    const [dateFromFilter, setDateFromFilter] = useState<string>('');
    const [dateToFilter, setDateToFilter] = useState<string>('');
    const [tagFilters, setTagFilters] = useState<Record<string, string>>({});
    const [showFilters, setShowFilters] = useState(false);

    // Pagination
    const [currentPage, setCurrentPage] = useState(1);
    const [itemsPerPage, setItemsPerPage] = useState(50);
    const [totalItems, setTotalItems] = useState(0);

    // BU Filtering (from Catalog.tsx)
    const [selectedBusinessUnitFilter, setSelectedBusinessUnitFilter] = useState<string | null>(null);
    const [isBusinessUnitDropdownOpen, setIsBusinessUnitDropdownOpen] = useState(false);
    const [businessUnitSearchQuery, setBusinessUnitSearchQuery] = useState('');
    const [showBusinessUnitWarning, setShowBusinessUnitWarning] = useState(false);

    const businessUnitDropdownRef = useRef<HTMLDivElement>(null);
    const businessUnitSearchInputRef = useRef<HTMLInputElement>(null);
    const isFilterResetRef = useRef(false);

    // Fetching data
    const fetchDeployments = async (skipPolling = false, overridePage?: number) => {
        if (isLoadingBusinessUnits) return;

        // Check BU access for regular users
        if (!isAdmin && (!activeBusinessUnit || !hasBusinessUnitAccess)) {
            setShowBusinessUnitWarning(true);
            setLoading(false);
            return;
        }

        const effectivePage = overridePage !== undefined ? overridePage : currentPage;

        if (!skipPolling) setLoading(true);

        try {
            const skip = (effectivePage - 1) * itemsPerPage;
            const params: Record<string, string | number> = {
                skip,
                limit: itemsPerPage
            };

            if (searchQuery.trim()) params.search = searchQuery.trim();
            if (statusFilter !== 'all') params.status = statusFilter;
            if (providerFilter !== 'all') params.cloud_provider = providerFilter;
            if (environmentFilter !== 'all') params.environment = environmentFilter;

            // User filter (only for admins)
            if (userFilter !== 'all' && userFilter && isAdmin) {
                params.user_id = userFilter;
            } else if (!isAdmin && user?.id) {
                // Should regular users only see their own? In Catalog it was filtered by active BU + user_id sometimes
                // But typically Deployments page is team-wide. 
                // However, Catalog.tsx (original) had params.user_id = String(user.id);
                // If the user wants ONE page, we should keep the logic consistent.
                // params.user_id = String(user.id); 
            }

            // BU Logic
            const queryParams = new URLSearchParams(window.location.search);
            const urlBuId = queryParams.get('business_unit_id');

            if (urlBuId) {
                params.business_unit_id = urlBuId;
            } else if (selectedBusinessUnitFilter) {
                params.business_unit_id = selectedBusinessUnitFilter;
            } else if (activeBusinessUnit?.id && !isAdmin) {
                params.business_unit_id = activeBusinessUnit.id;
            }

            // Tags
            if (Object.keys(tagFilters).length > 0) {
                const tagPairs = Object.entries(tagFilters)
                    .filter(([k, v]) => k && v)
                    .map(([k, v]) => `${k}:${v}`);
                if (tagPairs.length > 0) {
                    params.tags = tagPairs.join(',');
                }
            }

            const response = await api.listDeployments(params);

            let items: Deployment[] = [];
            if (Array.isArray(response)) {
                items = response;
                setTotalItems(response.length);
            } else {
                items = response.deployments || [];
                setTotalItems(response.total || response.deployments?.length || 0);
            }

            // Client side date filtering
            let filtered = items;
            if (dateFromFilter) {
                const fromDate = new Date(dateFromFilter);
                filtered = filtered.filter(d => new Date(d.created_at) >= fromDate);
            }
            if (dateToFilter) {
                const toDate = new Date(dateToFilter);
                toDate.setHours(23, 59, 59, 999);
                filtered = filtered.filter(d => new Date(d.created_at) <= toDate);
            }

            setDeployments(filtered);
            setTotalItems(response.total || filtered.length);
        } finally {
            setLoading(false);
        }
    };

    // Effects
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (businessUnitDropdownRef.current && !businessUnitDropdownRef.current.contains(event.target as Node)) {
                setIsBusinessUnitDropdownOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    // Initial load and URL param handling
    useEffect(() => {
        const queryParams = new URLSearchParams(location.search);
        const buId = queryParams.get('business_unit_id');
        const status = queryParams.get('status');
        const env = queryParams.get('environment');

        if (buId && (isAdmin || isOwner)) setSelectedBusinessUnitFilter(buId);
        if (status) setStatusFilter(status);
        if (env) setEnvironmentFilter(env);

        // fetchDeployments is triggered by filters effect
    }, [isAdmin, isOwner, location.search]);

    // Instant client-side filtering + memoized results
    const filteredResults = useMemo(() => {
        if (!searchQuery.trim()) return deployments;

        const query = searchQuery.toLowerCase();
        return deployments.filter(d =>
            (d.name && d.name.toLowerCase().includes(query)) ||
            (d.plugin_id && d.plugin_id.toLowerCase().includes(query)) ||
            (d.stack_name && d.stack_name.toLowerCase().includes(query)) ||
            (d.github_repo_name && d.github_repo_name.toLowerCase().includes(query)) ||
            (d.region && d.region.toLowerCase().includes(query))
        );
    }, [searchQuery, deployments]);

    // Active Filter Count (including search)
    const activeFilterCount = useMemo(() => {
        return [
            searchQuery.trim() !== '',
            statusFilter !== 'all',
            providerFilter !== 'all',
            environmentFilter !== 'all',
            userFilter !== 'all',
            !!dateFromFilter,
            !!selectedBusinessUnitFilter
        ].filter(Boolean).length;
    }, [searchQuery, statusFilter, providerFilter, environmentFilter, userFilter, dateFromFilter, selectedBusinessUnitFilter]);

    // Debounced filter effect for full backend results
    useEffect(() => {
        // If we have deployments, we can filter them instantly, but we still want to fetch
        // full results from the backend in case there are matching items on other pages.
        const timeoutId = setTimeout(() => {
            isFilterResetRef.current = true;
            setCurrentPage(1);
            fetchDeployments(true, 1);
        }, 300);
        return () => clearTimeout(timeoutId);
    }, [searchQuery, statusFilter, providerFilter, environmentFilter, userFilter, tagFilters, selectedBusinessUnitFilter, activeBusinessUnit?.id]);

    // Pagination effect
    useEffect(() => {
        if (isFilterResetRef.current && currentPage === 1) {
            isFilterResetRef.current = false;
            return;
        }
        fetchDeployments();
    }, [currentPage, itemsPerPage]);

    const clearAllFilters = () => {
        setSearchQuery('');
        setStatusFilter('all');
        setProviderFilter('all');
        setEnvironmentFilter('all');
        setUserFilter('all');
        setDateFromFilter('');
        setDateToFilter('');
        setTagFilters({});
        setSelectedBusinessUnitFilter(null);
    };

    const hasActiveFilters = searchQuery.trim() || statusFilter !== 'all' ||
        providerFilter !== 'all' || environmentFilter !== 'all' ||
        userFilter !== 'all' || dateFromFilter || dateToFilter ||
        Object.keys(tagFilters).length > 0 || selectedBusinessUnitFilter;

    if (loading && deployments.length === 0) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header section with Glassmorphism */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div>
                    <h1 className="text-4xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-400 tracking-tight">
                        Deployments
                    </h1>
                    <p className="text-gray-500 dark:text-gray-400 mt-2 font-medium">
                        {isAdmin ? 'Manage and monitor infrastructure across the entire organization.' : 'Manage and monitor your active infrastructure.'}
                    </p>
                </div>
                <Link to="/services" className="relative group">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-600 to-orange-400 rounded-xl blur opacity-30 group-hover:opacity-100 transition duration-500"></div>
                    <button className="relative flex items-center gap-2 px-6 py-3 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-xl font-bold transition-all duration-300 hover:scale-[1.02] active:scale-[0.98]">
                        <Server className="w-5 h-5" />
                        New Deployment
                    </button>
                </Link>
            </div>

            {/* Filter Section with Glassmorphism */}
            <div className="relative group z-10">
                <div className="absolute -inset-0.5 bg-gradient-to-r from-gray-200 to-gray-100 dark:from-gray-800 dark:to-gray-900 rounded-3xl blur-sm opacity-50"></div>
                <div className="relative bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200 dark:border-gray-800 rounded-3xl p-6 shadow-2xl transition-all duration-500">
                    <div className="flex flex-col lg:flex-row gap-4">
                        {/* Search Bar */}
                        <div className="flex-1 relative group/search">
                            <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400 group-focus-within/search:text-orange-500 transition-colors w-5 h-5" />
                            <input
                                type="text"
                                placeholder="Search by name, plugin, stack, region..."
                                value={searchQuery}
                                onChange={(e) => setSearchQuery(e.target.value)}
                                className={`w-full pl-12 pr-12 py-3.5 bg-gray-50/50 dark:bg-gray-800/50 border-2 rounded-2xl text-gray-900 dark:text-white placeholder-gray-400 focus:outline-none transition-all duration-300 ${searchQuery ? 'border-orange-500/20 shadow-lg shadow-orange-500/5' : 'border-transparent'
                                    }`}
                            />
                            <div className="absolute right-4 top-1/2 -translate-y-1/2 flex items-center gap-2">
                                {loading && searchQuery && (
                                    <Loader2 className="w-4 h-4 text-orange-500 animate-spin" />
                                )}
                                {searchQuery && (
                                    <button onClick={() => setSearchQuery('')} className="p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded-full transition-colors">
                                        <X className="w-4 h-4 text-gray-400" />
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Right side controls */}
                        <div className="flex flex-wrap items-center gap-3">
                            {/* BU Selector for Admins */}
                            {(isAdmin || isOwner) && (
                                <div ref={businessUnitDropdownRef} className="relative">
                                    <button
                                        onClick={() => setIsBusinessUnitDropdownOpen(!isBusinessUnitDropdownOpen)}
                                        className={`flex items-center gap-2 px-5 py-3.5 rounded-2xl font-bold transition-all duration-300 border-2 ${selectedBusinessUnitFilter
                                            ? 'bg-orange-500/10 border-orange-500/30 text-orange-600 dark:text-orange-400'
                                            : 'bg-gray-50/50 dark:bg-gray-800/50 border-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                                            }`}
                                    >
                                        <Building2 className="w-5 h-5" />
                                        <span className="max-w-[150px] truncate">
                                            {selectedBusinessUnitFilter
                                                ? businessUnits.find(bu => bu.id === selectedBusinessUnitFilter)?.name || 'Select BU'
                                                : 'All Business Units'}
                                        </span>
                                        <ChevronDown className={`w-4 h-4 transition-transform duration-300 ${isBusinessUnitDropdownOpen ? 'rotate-180' : ''}`} />
                                    </button>

                                    {/* BU Dropdown */}
                                    {isBusinessUnitDropdownOpen && (
                                        <div className="absolute right-0 mt-3 w-80 bg-white/95 dark:bg-gray-900/95 backdrop-blur-2xl border border-gray-200 dark:border-gray-800 rounded-3xl shadow-2xl z-50 overflow-hidden animate-in fade-in slide-in-from-top-2 duration-300">
                                            <div className="p-4 border-b border-gray-100 dark:border-gray-800">
                                                <div className="relative">
                                                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                                    <input
                                                        ref={businessUnitSearchInputRef}
                                                        type="text"
                                                        placeholder="Search business units..."
                                                        value={businessUnitSearchQuery}
                                                        onChange={(e) => setBusinessUnitSearchQuery(e.target.value)}
                                                        className="w-full pl-9 pr-4 py-2 bg-gray-50 dark:bg-gray-800 border-none rounded-xl text-sm focus:ring-2 focus:ring-orange-500/50 outline-none"
                                                    />
                                                </div>
                                            </div>
                                            <div className="max-h-72 overflow-y-auto p-2">
                                                <button
                                                    onClick={() => {
                                                        setSelectedBusinessUnitFilter(null);
                                                        setIsBusinessUnitDropdownOpen(false);
                                                    }}
                                                    className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-colors ${!selectedBusinessUnitFilter ? 'bg-orange-500/10 text-orange-600' : 'hover:bg-gray-50 dark:hover:bg-gray-800'}`}
                                                >
                                                    <div className="flex flex-col items-start">
                                                        <span className="font-bold text-sm text-gray-900 dark:text-white">All Business Units</span>
                                                        <span className="text-xs text-gray-500">Global organization view</span>
                                                    </div>
                                                    {!selectedBusinessUnitFilter && <div className="w-2 h-2 rounded-full bg-orange-500"></div>}
                                                </button>
                                                {businessUnits.filter(bu =>
                                                    bu.name.toLowerCase().includes(businessUnitSearchQuery.toLowerCase()) ||
                                                    bu.slug.toLowerCase().includes(businessUnitSearchQuery.toLowerCase())
                                                ).map(bu => (
                                                    <button
                                                        key={bu.id}
                                                        onClick={() => {
                                                            setSelectedBusinessUnitFilter(bu.id);
                                                            setIsBusinessUnitDropdownOpen(false);
                                                        }}
                                                        className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-colors ${selectedBusinessUnitFilter === bu.id ? 'bg-orange-500/10 text-orange-600' : 'hover:bg-gray-50 dark:hover:bg-gray-800'}`}
                                                    >
                                                        <div className="flex flex-col items-start">
                                                            <span className="font-bold text-sm text-gray-900 dark:text-white capitalize">{bu.name}</span>
                                                            <span className="text-xs text-gray-500 capitalize">/{bu.slug}</span>
                                                        </div>
                                                        {selectedBusinessUnitFilter === bu.id && <div className="w-2 h-2 rounded-full bg-orange-500"></div>}
                                                    </button>
                                                ))}
                                            </div>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Advanced Filters Toggle */}
                            <button
                                onClick={() => setShowFilters(!showFilters)}
                                className={`flex items-center gap-2 px-5 py-3.5 rounded-2xl font-bold transition-all duration-300 border-2 ${showFilters || hasActiveFilters
                                    ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900 border-transparent shadow-lg shadow-gray-500/20'
                                    : 'bg-gray-50/50 dark:bg-gray-800/50 border-transparent text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                                    }`}
                            >
                                <Filter className="w-5 h-5" />
                                <span>Filters</span>
                                {activeFilterCount > 0 && (
                                    <span className="ml-1 w-5 h-5 flex items-center justify-center bg-orange-500 text-white text-[10px] rounded-full">
                                        {activeFilterCount}
                                    </span>
                                )}
                            </button>
                        </div>
                    </div>

                    {/* Expandable Advanced Filters */}
                    {showFilters && (
                        <div className="mt-6 pt-6 border-t border-gray-100 dark:border-gray-800 animate-in fade-in slide-in-from-top-4 duration-500">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                                {/* Status Filter */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Status</label>
                                    <select
                                        value={statusFilter}
                                        onChange={(e) => setStatusFilter(e.target.value)}
                                        className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-sm focus:outline-none transition-all"
                                    >
                                        <option value="all">All Statuses</option>
                                        <option value="active">Active</option>
                                        <option value="provisioning">Provisioning</option>
                                        <option value="failed">Failed</option>
                                        <option value="deleted">Deleted</option>
                                    </select>
                                </div>

                                {/* Cloud Provider Filter */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Cloud Provider</label>
                                    <select
                                        value={providerFilter}
                                        onChange={(e) => setProviderFilter(e.target.value)}
                                        className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-sm focus:outline-none transition-all"
                                    >
                                        <option value="all">All Providers</option>
                                        <option value="aws">AWS</option>
                                        <option value="gcp">GCP</option>
                                        <option value="azure">Azure</option>
                                    </select>
                                </div>

                                {/* Environment Filter */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Environment</label>
                                    <select
                                        value={environmentFilter}
                                        onChange={(e) => setEnvironmentFilter(e.target.value)}
                                        className="w-full px-4 py-3 bg-gray-50 dark:bg-gray-800 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-sm focus:outline-none transition-all"
                                    >
                                        <option value="all">All Environments</option>
                                        <option value="development">Development</option>
                                        <option value="staging">Staging</option>
                                        <option value="production">Production</option>
                                    </select>
                                </div>

                                {/* User Filter - Only for Admins */}
                                {isAdmin && (
                                    <div className="space-y-2">
                                        <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Created By</label>
                                        <div className="relative">
                                            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                            <select
                                                value={userFilter}
                                                onChange={(e) => setUserFilter(e.target.value)}
                                                className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-800 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-sm focus:outline-none transition-all"
                                            >
                                                <option value="all">All Users</option>
                                                {/* In a real app we'd fetch users list. For now, keep as 'all' or specific ID from URL */}
                                                {userFilter !== 'all' && <option value={userFilter}>Current Filter User</option>}
                                            </select>
                                        </div>
                                    </div>
                                )}

                                {/* Date Filter */}
                                <div className="space-y-2">
                                    <label className="text-xs font-bold text-gray-500 uppercase tracking-wider ml-1">Date Created</label>
                                    <div className="relative">
                                        <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                                        <input
                                            type="date"
                                            value={dateFromFilter}
                                            onChange={(e) => setDateFromFilter(e.target.value)}
                                            className="w-full pl-10 pr-4 py-3 bg-gray-50 dark:bg-gray-800 border-2 border-transparent focus:border-orange-500/20 rounded-xl text-sm focus:outline-none transition-all"
                                        />
                                    </div>
                                </div>
                            </div>

                            {/* Clear Filters Button */}
                            {hasActiveFilters && (
                                <div className="mt-6 flex justify-end">
                                    <button
                                        onClick={clearAllFilters}
                                        className="flex items-center gap-2 px-4 py-2 text-sm font-bold text-orange-600 dark:text-orange-400 hover:bg-orange-500/5 rounded-xl transition-all"
                                    >
                                        <X className="w-4 h-4" />
                                        Clear all filters
                                    </button>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>

            {/* Content Section */}
            {error && (
                <div className="bg-red-500/10 border-2 border-red-500/20 p-4 rounded-2xl flex items-center gap-3 text-red-600 dark:text-red-400 animate-in fade-in duration-300">
                    <AlertCircle className="w-5 h-5 flex-shrink-0" />
                    <p className="font-bold">{error}</p>
                </div>
            )}

            {loading && deployments.length === 0 ? (
                <div className="flex flex-col items-center justify-center h-96 space-y-4">
                    <Loader2 className="w-12 h-12 text-orange-500 animate-spin" />
                    <p className="text-gray-500 font-bold animate-pulse">Syncing deployments...</p>
                </div>
            ) : filteredResults.length === 0 ? (
                <div className="bg-white/50 dark:bg-gray-900/50 backdrop-blur-sm border-2 border-dashed border-gray-200 dark:border-gray-800 rounded-3xl p-16 text-center animate-in fade-in zoom-in-95 duration-700">
                    <div className="w-20 h-20 bg-gray-100 dark:bg-gray-800 rounded-2xl flex items-center justify-center mx-auto mb-6">
                        <LayoutGrid className="w-10 h-10 text-gray-400" />
                    </div>
                    <h3 className="text-2xl font-black text-gray-900 dark:text-white mb-2">No deployments found</h3>
                    <p className="text-gray-500 dark:text-gray-400 mb-8 max-w-sm mx-auto font-medium">
                        Try adjusting your filters or create a new deployment to get started.
                    </p>
                    <button onClick={clearAllFilters} className="px-8 py-3 bg-orange-500 hover:bg-orange-600 text-white rounded-2xl font-bold transition-all shadow-xl shadow-orange-500/20">
                        Reset Filters
                    </button>
                </div>
            ) : (
                <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-xl border border-gray-200 dark:border-gray-800 rounded-3xl overflow-hidden shadow-2xl">
                    <div className="overflow-x-auto">
                        <table className="w-full text-left border-collapse">
                            <thead>
                                <tr className="border-b border-gray-100 dark:border-gray-800 bg-gray-50/50 dark:bg-gray-800/50">
                                    <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-wider">Deployment</th>
                                    <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-wider">Status</th>
                                    <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-wider">Environment</th>
                                    <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-wider">Provider</th>
                                    <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-wider">Est. Cost</th>
                                    <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-wider">Created</th>
                                    <th className="px-6 py-4 text-xs font-black text-gray-500 uppercase tracking-wider text-right">Actions</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-gray-100 dark:divide-gray-800">
                                {filteredResults.map((deploy) => (
                                    <tr
                                        key={deploy.id}
                                        className="hover:bg-gray-50/80 dark:hover:bg-gray-800/80 transition-colors group"
                                    >
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-orange-400 to-orange-600 flex items-center justify-center flex-shrink-0 shadow-lg shadow-orange-500/10 transition-transform group-hover:scale-105">
                                                    <Server className="w-5 h-5 text-white" />
                                                </div>
                                                <div className="min-w-0">
                                                    <Link
                                                        to={`/deployment/${deploy.id}`}
                                                        className="text-sm font-bold text-gray-900 dark:text-white hover:text-orange-600 dark:hover:text-orange-400 transition-colors block truncate"
                                                    >
                                                        {searchQuery ? (
                                                            deploy.name.split(new RegExp(`(${searchQuery})`, 'gi')).map((part, i) =>
                                                                part.toLowerCase() === searchQuery.toLowerCase() ?
                                                                    <span key={i} className="text-orange-600 dark:text-orange-400 group-hover:bg-orange-100 dark:group-hover:bg-orange-900/30 rounded px-0.5">{part}</span> : part
                                                            )
                                                        ) : deploy.name}
                                                    </Link>
                                                    <div className="flex items-center gap-1.5 mt-0.5">
                                                        <PluginBadge pluginId={deploy.plugin_id} provider={deploy.cloud_provider} size="xs" />
                                                        <span className="text-[10px] text-gray-500 font-bold uppercase tracking-tight">v{deploy.version || '1.0.0'}</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <StatusBadge status={deploy.status} />
                                        </td>
                                        <td className="px-6 py-4">
                                            {deploy.environment && <EnvironmentBadge environment={deploy.environment} size="sm" />}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-2">
                                                <CloudProviderBadge provider={deploy.cloud_provider || 'aws'} size="xs" />
                                                <span className="text-xs font-bold text-gray-700 dark:text-gray-300 uppercase">{deploy.cloud_provider || 'AWS'}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="text-sm font-bold text-green-600 dark:text-green-400">
                                                {(deploy as any).estimated_monthly_cost ? `$${parseFloat((deploy as any).estimated_monthly_cost).toFixed(2)}` : '-'}
                                            </span>
                                            <span className="text-xs text-gray-500 dark:text-gray-400 ml-1">/mo</span>
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-1.5 text-xs text-gray-500 font-bold">
                                                <Clock className="w-3.5 h-3.5" />
                                                <span>{new Date(deploy.created_at).toLocaleDateString()}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <Link
                                                to={`/deployment/${deploy.id}`}
                                                className="inline-flex items-center gap-1 text-xs font-black text-orange-600 dark:text-orange-400 uppercase tracking-widest opacity-0 group-hover:opacity-100 transition-all transform translate-x-1 group-hover:translate-x-0"
                                            >
                                                Details
                                                <ExternalLink className="w-3 h-3" />
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}

            {/* Modals and Pagination */}
            <BusinessUnitWarningModal

                isOpen={showBusinessUnitWarning}
                onClose={() => setShowBusinessUnitWarning(false)}
                onSelectBusinessUnit={() => {
                    const selector = document.querySelector('[data-business-unit-selector]');
                    if (selector) (selector as HTMLElement).click();
                }}
                action="view deployments"
            />

            {
                totalItems > 0 && (
                    <div className="mt-8">
                        <Pagination
                            currentPage={currentPage}
                            totalPages={Math.ceil(totalItems / itemsPerPage)}
                            totalItems={totalItems}
                            itemsPerPage={itemsPerPage}
                            onPageChange={setCurrentPage}
                            onItemsPerPageChange={setItemsPerPage}
                            showItemsPerPage={true}
                        />
                    </div>
                )
            }
        </div >
    );
};
