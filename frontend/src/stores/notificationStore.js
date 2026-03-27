import { defineStore } from 'pinia'

export const useNotificationStore = defineStore('notification', {
  state: () => ({
    error: null,
    success: null
  }),
  actions: {
    showError(message) {
      this.error = message
      setTimeout(() => this.clearError(), 5000)
    },
    showSuccess(message) {
      this.success = message
      setTimeout(() => this.clearSuccess(), 5000)
    },
    clearError() {
      this.error = null
    },
    clearSuccess() {
      this.success = null
    }
  }
})