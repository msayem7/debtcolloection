<template>
  <div v-if="errorMessage" class="error-notification">
    {{ errorMessage }}
    <button @click="clear" class="close-button">&times;</button>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useNotificationStore } from '@/stores/notificationStore'

export default {
  setup() {
    const notificationStore = useNotificationStore()
    console.log('Notification Error : ', notificationStore.error)
    return {
      errorMessage: computed(() => notificationStore.error),
      clear: () => notificationStore.clearError()    
    }
  }
}
</script>

<style scoped>
.error-notification {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 15px 20px;
  background: #ff4444;
  color: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  gap: 15px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  z-index: 1000;
}

.close-button {
  background: none;
  border: none;
  color: white;
  font-size: 1.2em;
  cursor: pointer;
  padding: 0;
  margin-left: 10px;
}
</style>

<!-- <template>
    <div v-if="message" class="error-notification">
      {{ message }}
      <button @click="dismiss">×</button>
    </div>
  </template>
  
  <script>
  import { ref } from 'vue'
  import { useNotificationStore } from '@/stores/notificationStore'
  
  export default {
    setup() {
      const notificationStore = useNotificationStore()
      const message = ref('')
  
      notificationStore.$subscribe((mutation, state) => {
        message.value = state.errorMessage
      })
  
      const dismiss = () => {
        notificationStore.clearError()
      }
  
      return { message, dismiss }
    }
  }
  </script>
  
  <style>
  .error-notification {
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 15px;
    background: #ff4444;
    color: white;
    border-radius: 5px;
    display: flex;
    align-items: center;
    gap: 10px;
  }
  </style> -->