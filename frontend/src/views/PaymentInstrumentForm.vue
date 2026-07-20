<template>
  <div class="container mt-4">
    <h2>{{ isEditing ? 'Edit' : 'Create' }} Payment Instrument</h2>

    <div v-if="!branchStore.isBranchSelected" class="alert alert-warning">
      <i class="bi bi-exclamation-triangle me-2"></i>
      Please select a working branch before creating or editing payment instruments.
    </div>

    <form v-else @submit.prevent="handleSubmit" class="mt-4">
      <div class="card shadow">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-md-6">
              <label class="form-label">Instrument Name <span class="text-danger">*</span></label>
              <input
                v-model="formData.instrument_name"
                type="text"
                class="form-control"
                :class="{ 'is-invalid': errors.instrument_name }"
                required
                maxlength="100"
                placeholder="e.g., Cheque, Cash, Bank Draft"
              />
              <div v-if="errors.instrument_name" class="invalid-feedback">{{ errors.instrument_name }}</div>
            </div>

            <div class="col-md-6">
              <label class="form-label">Instrument Type <span class="text-danger">*</span></label>
              <select
                v-model="formData.instrument_type"
                class="form-select"
                :class="{ 'is-invalid': errors.instrument_type }"
                required
              >
                <option value="" disabled>Select type...</option>
                <option v-for="type in instrumentTypes" :key="type.id" :value="type.id">
                  {{ type.type_name }} {{ type.is_cash_equivalent ? '(Cash Equivalent)' : '' }}
                </option>
              </select>
              <div v-if="errors.instrument_type" class="invalid-feedback">{{ errors.instrument_type }}</div>
            </div>

            <div class="col-12">
              <div class="form-check">
                <input
                  v-model="formData.is_active"
                  type="checkbox"
                  class="form-check-input"
                  id="isActive"
                />
                <label class="form-check-label" for="isActive">Active</label>
              </div>
              <small class="text-muted">
                Inactive instruments cannot be selected for new payments.
              </small>
            </div>
          </div>
        </div>
      </div>

      <div class="d-flex gap-2 mt-4">
        <button type="submit" class="btn btn-primary" :disabled="submitting">
          <span v-if="submitting" class="spinner-border spinner-border-sm me-2" role="status"></span>
          <i v-else :class="[isEditing ? 'bi bi-pencil' : 'bi bi-plus-circle', 'me-2']"></i>
          {{ isEditing ? 'Update' : 'Create' }} Instrument
        </button>
        <router-link to="/payment-instruments" class="btn btn-outline-secondary">
          Cancel
        </router-link>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/plugins/axios'
import { useBranchStore } from '@/stores/branchStore'
import { useNotificationStore } from '@/stores/notificationStore'

const route = useRoute()
const router = useRouter()
const branchStore = useBranchStore()
const notificationStore = useNotificationStore()

const isEditing = computed(() => !!route.params.id)
const submitting = ref(false)

const formData = ref({
  instrument_name: '',
  instrument_type: '',
  is_active: true,
  version: 1
})

const instrumentTypes = ref([])
const errors = ref({})

const fetchInstrumentTypes = async () => {
  try {
    const params = { branch: branchStore.selectedBranch }
    const { data } = await axios.get('/v1/chq/PaymentInstrumentType/', { params })
    instrumentTypes.value = data
  } catch (error) {
    notificationStore.showError('Failed to load instrument types')
  }
}

const loadInstrument = async (id) => {
  try {
    const params = { branch: branchStore.selectedBranch }
    const { data } = await axios.get(`/v1/chq/payment-instruments/${id}/`, { params })
    formData.value = {
      instrument_name: data.instrument_name,
      instrument_type: data.instrument_type,
      is_active: data.is_active,
      version: data.version
    }
  } catch (error) {
    notificationStore.showError('Failed to load instrument data')
    router.push('/payment-instruments')
  }
}

const handleSubmit = async () => {
  errors.value = {}
  submitting.value = true

  // Client-side validation
  if (!formData.value.instrument_name.trim()) {
    errors.value.instrument_name = 'Instrument name is required.'
  }
  if (!formData.value.instrument_type) {
    errors.value.instrument_type = 'Instrument type is required.'
  }
  if (Object.keys(errors.value).length > 0) {
    submitting.value = false
    return
  }

  try {
    const payload = {
      branch: branchStore.selectedBranch,
      instrument_name: formData.value.instrument_name.trim(),
      instrument_type: formData.value.instrument_type,
      is_active: formData.value.is_active,
      version: formData.value.version
    }

    if (isEditing.value) {
      await axios.put(`/v1/chq/payment-instruments/${route.params.id}/`, payload)
      notificationStore.showSuccess('Payment instrument updated successfully')
    } else {
      await axios.post('/v1/chq/payment-instruments/', payload)
      notificationStore.showSuccess('Payment instrument created successfully')
    }

    router.push('/payment-instruments')
  } catch (error) {
    if (error.response?.status === 409) {
      notificationStore.showError('Concurrency conflict. Please refresh and try again.')
    } else if (error.response?.data) {
      const serverErrors = error.response.data
      Object.keys(serverErrors).forEach(key => {
        if (Array.isArray(serverErrors[key])) {
          errors.value[key] = serverErrors[key][0]
        } else if (typeof serverErrors[key] === 'string') {
          errors.value[key] = serverErrors[key]
        }
      })
      if (Object.keys(errors.value).length === 0) {
        notificationStore.showError(Object.values(serverErrors).flat().join(', '))
      }
    } else {
      notificationStore.showError('An unexpected error occurred')
    }
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  await fetchInstrumentTypes()
  if (isEditing.value) {
    await loadInstrument(route.params.id)
  }
})
</script>