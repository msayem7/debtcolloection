import { defineStore } from 'pinia';
import axios from '../plugins/axios';
import { jwtDecode } from 'jwt-decode';  // Add this

export const useAuthStore = defineStore('auth', {
    state: () => ({
        user: null,
        token: localStorage.getItem('token') || null,
    }),
    actions: {
        async initialize() {
            try {
                if (this.token) {                    
                    
                    // Check if token is expired
                    const decoded = jwtDecode(this.token);
                    if (decoded.exp * 1000 < Date.now()) {
                        this.logout();
                        return;
                    }
                    // Replace with your actual user endpoint
                    const response = await axios.get('/v1/chq/user/')
                    this.user = response.data
                    axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
                }
            } catch (error) {
                this.logout()
            }
        },    
        async login(credentials) {
            try {
                const response = await axios.post('/v1/chq/token/', credentials);

                if (!response.data.access) {
                    throw new Error('Invalid server response');
                  }
                
                // if (response.data.user) {
                this.token = response.data.access;
                // this.user = response.data.user;
                localStorage.setItem('token', this.token);
                axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`;// Fetch user data
                await this.fetchUser();
                return true;
                // }
                // throw new Error('Invalid response format');
            } catch (error) {
                // console.error('Login error:', error.response?.data || error.message);
                this.logout();
                if (error.response?.status === 401) {
                    throw new Error('Invalid username or password');
                  }
                  
                throw error; // Let global interceptor handle
            }
        },
        
        logout() {
            this.token = null;
            this.user = null;
            localStorage.removeItem('token');
            delete axios.defaults.headers.common['Authorization'];
        },
        async fetchUser() {
            try {
                const response = await axios.get('/v1/chq/user/');
                this.user = response.data;
            } catch (error) {
                console.error('Failed to fetch user:', error);
                this.logout();
                throw error;
            }
        }
    },
});