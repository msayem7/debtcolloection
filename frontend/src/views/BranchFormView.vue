<template>
  <div class="container mt-4">
    <h2>{{ isEditing ? 'Edit' : 'Create' }} Office</h2>
    
    <form @submit.prevent="handleSubmit">
      <div class="row g-3">
        <div class="col-md-6">
          <label class="form-label">Office Name</label>
          <input v-model="formData.name" type="text" class="form-control" required>
        </div>

        <div class="col-md-6">
          <label class="form-label">Office Type</label>
          <select v-model="formData.branch_type" class="form-select" required>
            <option v-for="(label, value) in branchTypeMap" 
                    :key="value" 
                    :value="value">
              {{ label }}
            </option>
          </select>
        </div>

        <div class="col-12">
          <label class="form-label">Head Office</label>
          <select v-model="formData.parent" class="form-select">
            <option :value="null">No Parent</option>
            <option v-for="branch in availableParents" 
                    :key="branch.alias_id" 
                    :value="branch.alias_id">
              {{ branch.name }}
            </option>
          </select>
        </div>
        <!-- Add address and contact fields -->
        <div class="col-12">
          <button type="submit" class="btn btn-primary">
            {{ isEditing ? 'Update' : 'Create' }} Office
          </button>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>

import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/plugins/axios'

const route = useRoute()
const router = useRouter()

const isEditing = computed(() => route.path.includes('/edit/'))
const branchTypeMap = { 1: 'Head Office', 2: 'Office' }

const formData = ref({
  name: '',
  branch_type: 2,
  parent: null,
  address: '',
  contact: '',
  version: 1
})

const branches = ref([])

const availableParents = computed(() => {
  return branches.value.filter(b => b.alias_id !== route.params.aliasId)
})

const loadBranches = async () => {
  try {
    const { data } = await axios.get('/v1/chq/branches/')
    branches.value = data
  } catch (error) {
    console.error('Error loading branches:', error)
  }
}

const handleSubmit = async () => {
  try {
    const payload = {
      ...formData.value,
      version: formData.value.version // Make sure to send current version
    }
    
    if (isEditing.value) {
      await axios.put(`/v1/chq/branches/${route.params.aliasId}/`, payload)
    } else {
      await axios.post('/v1/chq/branches/', payload)
    }
    router.push('/branches')

  } catch (error) {
    if (error.response?.status === 409) {
      alert('Concurrency conflict. Please refresh and try again.')
      await loadBranches() // Refresh data
    }
  }
}

onMounted(async () => {
  await loadBranches()
  if (isEditing.value) {
    const { data } = await axios.get(`/v1/chq/branches/${route.params.aliasId}/`)
    formData.value = data
  }
})
</script>