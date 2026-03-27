<template>
  <div class="modal" style="display: block; background: rgba(0,0,0,0.5)">
    <div class="modal-dialog">
      <div class="modal-content">
        <div class="modal-header">
          <h5 class="modal-title">{{ isEdit ? 'Edit' : 'Add' }} customer</h5>
          <button type="button" class="btn-close" @click="closeForm"></button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="submitForm">
            <input type="hidden" v-model="formData.alias_id">
            <div class="mb-3">
              <label class="form-label">Name</label>
              <input v-model="formData.name" class="form-control" required>
            </div>
            
            <div class="mb-3 form-check">
              <input 
                type="checkbox" 
                v-model="formData.is_parent"
                class="form-check-input"
                @change="handleParentChange"
              >
              <label class="form-check-label">Is Parent</label>
            </div>
            
            <div class="mb-3" v-if="!formData.is_parent">
              <label class="form-label">Parent</label>
              <select 
                v-model="formData.parent" 
                class="form-select"
                required
                @change="updateGraceDaysFromParent"
              >
                <option v-for="mc in parents" :key="mc.alias_id" :value="mc.alias_id">
                  {{ mc.name}} (Grace: {{ mc.grace_days }} days)
                </option>
              </select>
            </div>
            <div class="mb-3">
              <label class="form-label">Grace in Days</label>
              <input 
                v-model="formData.grace_days" 
                class="form-control" 
                required
                type="number"
                min="0"
              >
            </div>
            <div class="mb-3 form-check">
              <input 
                type="checkbox" 
                v-model="formData.is_active"
                class="form-check-input"
                id="isActive"                    
              >
              <label class="form-check-label" for="isActive">Active</label>
            </div>
            
            
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" @click="closeForm">Cancel</button>
              <button type="submit" class="btn btn-primary">Save</button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>
  
<script setup>
import { useBranchStore } from '@/stores/branchStore'
import { ref, computed, watch } from 'vue'
import axios from '../plugins/axios'

const branchStore = useBranchStore()
/* eslint-disable no-undef */
const props = defineProps({
  customer: Object,
  parents: Array
})

const emit = defineEmits(['close'])
/* eslint-enable no-undef */

const formData = ref({
  alias_id: null,
  branch: branchStore.selectedBranch, // Auto-set from store,
  name: '',
  is_parent: false,
  parent: null,
  grace_days: 0,
  is_active: true
})

const isEdit = computed(() => !!props.customer?.alias_id)

const resetForm = () => {
  formData.value = {
    alias_id: null,
    name: '',
    is_parent: false,
    parent: null,
    grace_days: 0,
    is_active: true  
  }
}

const handleParentChange = () => {
  if (formData.value.is_parent) {
    formData.value.parent = null
  }
}

const updateGraceDaysFromParent = () => {
  if (!formData.value.parent) return
  
  // Find the selected parent from the parents list
  const selectedParent = props.parents.find(p => p.alias_id === formData.value.parent)
  if (selectedParent) {
    formData.value.grace_days = selectedParent.grace_days
  }
}

const submitForm = async () => {
  try {
    const url = formData.value.alias_id
      ? `/v1/chq/customers/${formData.value.alias_id}/`
      : '/v1/chq/customers/'
    const method = formData.value.alias_id ? 'put' : 'post'
    formData.value.branch = branchStore.selectedBranch
    await axios[method](url, formData.value)

    emit('close', true)

  } catch (error) {
    console.error('Error saving customer:', error)
  }
}

const closeForm = () => {
  resetForm()
  emit('close', false)
}

watch(() => props.customer, (newVal) => {
  if (newVal) {
    if (newVal.branch !== branchStore.selectedBranch) {
      emit('close', false)
      return
    }

    formData.value = { 
      ...newVal,
      branch: branchStore.selectedBranch, // Force current branch
    }
    
    // If editing and has a parent, set grace_days from parent
    if (newVal.parent && !newVal.is_parent) {
      const parent = props.parents.find(p => p.alias_id === newVal.parent)
      if (parent) {
        formData.value.grace_days = parent.grace_days
      }
    }
  } else {
    resetForm()
  }
}, { immediate: true })
</script>