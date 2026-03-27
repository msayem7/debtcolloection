<template>
    <div v-if="branch">
      <h2>Edit Office</h2>
      <BranchFormView
        :initial-data="branch" 
        :is-editing="true" 
        @submit="handleUpdate"
      />
    </div>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute } from 'vue-router'
  import axios from '@/plugins/axios'
  import BranchFormView from '@/views/BranchFormView.vue'
  
  const route = useRoute()
  const branch = ref(null)
  
  const loadBranch = async () => {
    const { data } = await axios.get(`/v1/chq/branches/${route.params.aliasId}/`)
    branch.value = data
  }
  
  const handleUpdate = async (formData) => {
    try {
      await axios.put(`/v1/chq/branches/${branch.value.alias_id}/`, formData)
      // Handle success (redirect or show message)
    } catch (error) {
      if (error.response?.data?.version) {
        alert(error.response.data.version)
        await loadBranch() // Refresh data
      }
    }
  }
  
  onMounted(loadBranch)
  </script>