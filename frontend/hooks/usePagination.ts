import { useState, useCallback } from 'react';

interface PaginationState {
    currentPage: number;
    itemsPerPage: number;
    totalItems: number;
}

interface UsePaginationReturn extends PaginationState {
    totalPages: number;
    skip: number;
    setPage: (page: number) => void;
    setItemsPerPage: (count: number) => void;
    setTotalItems: (count: number) => void;
    resetPage: () => void;
}

export function usePagination(initialItemsPerPage: number = 50): UsePaginationReturn {
    const [state, setState] = useState<PaginationState>({
        currentPage: 1,
        itemsPerPage: initialItemsPerPage,
        totalItems: 0
    });
    
    const totalPages = Math.ceil(state.totalItems / state.itemsPerPage);
    const skip = (state.currentPage - 1) * state.itemsPerPage;
    
    const setPage = useCallback((page: number) => {
        setState(prev => ({ ...prev, currentPage: page }));
    }, []);
    
    const setItemsPerPage = useCallback((count: number) => {
        setState(prev => ({ ...prev, itemsPerPage: count, currentPage: 1 }));
    }, []);
    
    const setTotalItems = useCallback((count: number) => {
        setState(prev => ({ ...prev, totalItems: count }));
    }, []);
    
    const resetPage = useCallback(() => {
        setState(prev => ({ ...prev, currentPage: 1 }));
    }, []);
    
    return {
        ...state,
        totalPages,
        skip,
        setPage,
        setItemsPerPage,
        setTotalItems,
        resetPage
    };
}
