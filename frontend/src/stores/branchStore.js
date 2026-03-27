
import { defineStore } from 'pinia';
import axios from '../plugins/axios';
import { useAuthStore } from './authStore';
import { useNotificationStore } from '@/stores/notificationStore'

export const useBranchStore = defineStore('credit', {   
    state: () => ({
        selectedBranch: localStorage.getItem('workingOffice') || null,        
        branches: [],        
        refreshTrigger: 0,
    }), 
    getters: {
        isBranchSelected: (state) => state.selectedBranch !== null,
    },
    actions: {
        
        async loadBranches() {
            const notificationStore = useNotificationStore()
            try {
                const authStore = useAuthStore();
                if (!authStore.user) return;
            
                const { data } = await axios.get('v1/chq/branches/');
                this.branches = data;
                
                // Validate selected branch
                if (this.selectedBranch && !this.branches.some(b => b.alias_id === this.selectedBranch)) {
                    this.resetBranchSelection();
                }
            } catch (error) {
                notificationStore.showError('Failed to load branches')
                throw error;
            }
        },
          
        resetBranchSelection() {
            const notificationStore = useNotificationStore()
            try{
                this.selectedBranch = null;
                localStorage.removeItem('workingOffice');
                notificationStore.showError('Previously selected branch is no longer available');
            } catch (error) {
                notificationStore.showError('Failed to reset branch selection')
                throw error;                
            }
        },
        setWorkingBranch(branch) {
            const notificationStore = useNotificationStore()
            try{
                this.selectedBranch = branch;
                localStorage.setItem('workingOffice', branch);
                this.refreshTrigger++; // Increment the refresh trigger
            }
            catch (error) {
                notificationStore.showError('Failed to set working branch')
                throw error;            
            }
        },
        // async loadBranches() {
        //     const authStore = useAuthStore();
        //     if (!authStore.user) return;
        //     const { data } = await axios.get('v1/chq/branches/');
        //     this.branches = data;
        //     if (this.selectedBranch && !this.branches.some(b => b.alias_id === this.selectedBranch)) {
        //         this.selectedBranch = null;
        //         localStorage.removeItem('workingOffice');
        //     }
        // },
        
    },
});


