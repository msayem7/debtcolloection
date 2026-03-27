import axios from 'axios';
import { jwtDecode } from 'jwt-decode'; 
import { useAuthStore } from '../stores/authStore';
import { useNotificationStore } from '@/stores/notificationStore'
// Add this
// console.log(`process.env.VUE_APP_API_BASE_URL: ${process.env.VUE_APP_API_BASE_URL}`)
// console.log(`process.env.baseURL: ${process.env}`)

const instance = axios.create({
  baseURL: `${process.env.VUE_APP_API_BASE_URL}`,
})

instance.interceptors.request.use((config)=>{
  const token = localStorage.getItem('token')
  if(token){
    // Check token expiration before sending requests
    const decoded = jwtDecode(token);
    if (decoded.exp * 1000 < Date.now()) {
      localStorage.removeItem('token');
      window.location.href = '/';  // Redirect to login
      return config;
    }
    config.headers.Authorization= `Bearer ${token}`;
  }
  return config;
  
});

// Add response interceptor // Error handling
instance.interceptors.response.use(
  response => response,
  error => {
    const notificationStore = useNotificationStore()
    const authStore = useAuthStore()
    
    if (error.response) {
      const { status, data } = error.response
      
      // Handle specific error codes
      switch (status) {
        case 401:
          authStore.logout()
          notificationStore.showError('Session expired. Please login again.')
          break
        case 403:
          notificationStore.showError('You don\'t have permission for this action')
          break
        case 404:
          notificationStore.showError('Requested resource not found')
          break
        case 400:
          notificationStore.showError(
            data.detail || 
            Object.values(data).flat().join(', ') || 
            'Invalid request'
          )
          break
        default:
          notificationStore.showError(data.detail || 'An unexpected error occurred')
      }
    } else {
      notificationStore.showError('Network error - please check your connection')
    }

    return Promise.reject(error)
  }
);

export default instance;