

<template>
  <ErrorNotification />
  <WorkingBranchSelector v-if="showNav" />
  <NavigationBar v-if="showNav" />
  <router-view v-slot="{ Component }">
    <component :is="Component" />
  </router-view>
</template>

<script setup>
// export default {
//   name: 'App',

// }
import ErrorNotification from '@/components/ErrorNotification.vue'
import { computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/authStore'
import { useBranchStore } from '@/stores/branchStore'

import { useRoute } from 'vue-router'
import NavigationBar from './components/NavigationBar.vue'
import WorkingBranchSelector from '@/components/WorkingBranchSelector.vue'

const route = useRoute()
const showNav = computed(() => !route.meta.hideNav)
  
const authStore = useAuthStore()
const branchStore = useBranchStore()

onMounted(async () => {
    await authStore.initialize() // Add this action to authStore (see next step)
    if (authStore.user) {
        await branchStore.loadBranches()
    }
})

</script>

<style>
/* #app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
} */
</style>

<style>
/* Global styles */
body {
  margin: 0;
  font-family: Arial, sans-serif;
}

#app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
</style>

