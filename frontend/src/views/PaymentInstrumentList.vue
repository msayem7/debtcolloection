<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Payment Instruments</h2>
      <div class="d-flex gap-2">
        <select v-model="filterType" class="form-select" style="width: auto;">
          <option value="">All Types</option>
          <option v-for="type in instrumentTypes" :key="type.id" :value="type.id">
            {{ type.type_name }}
          </option>
        </select>
        <router-link to="/payment-instruments/create" class="btn btn-primary">
          <i class="bi bi-plus-circle me-2"></i>Create New Instrument
        </router-link>
      </div>
    </div>

    <div v-if="!branchStore.isBranchSelected" class="alert alert-warning">
      <i class="bi bi-exclamation-triangle me-2"></i>
      Please select a working branch to view payment instruments.
    </div>

    <div v-else-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else-if="instruments.length === 0" class="card">
      <div class="card-body text-center py-5">
        <i class="bi bi-wallet2 fs-1 text-muted"></i>
        <p class="mt-3 text-muted">No payment instruments found for this branch.</p>
        <router-link to="/payment-instruments/create" class="btn btn-primary">
          <i class="bi bi-plus-circle me-2"></i>Create First Instrument
        </router-link>
      </div>
    </div>

    <div v-else class="card shadow">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>#</th>
                <th>Instrument Name</th>
                <th>Type</th>
                <th>Cash Equivalent</th>
                <th>Status</th>
                <th>Last Updated</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="instrument in filteredInstruments" :key="instrument.id">
                <td>{{ instrument.serial_no }}</td>
                <td>{{ instrument.instrument_name }}</td>
                <td>
                  <span class="badge bg-info">{{ instrument.instrument_type_name }}</span>
                </td>
                <td>
                  <i v-if="instrument.is_cash_equivalent" class="bi bi-check-circle-fill text-success"></i>
                  <i v-else class="bi bi-x-circle-fill text-danger"></i>
                </td>
                <td>
                  <span :class="['badge', instrument.is_active ? 'bg-success' : 'bg-secondary']">
                    {{ instrument.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </td>
                <td>{{ formatDate(instrument.updated_at) }}</td>
                <td>
                  <router-link
                    :to="`/payment-instruments/edit/${instrument.id}`"
                    class="btn btn-sm btn-outline-secondary me-2"
                  >
                    <i class="bi bi-pencil"></i> Edit
                  </router-link>
                  <button
                    v-if="instrument.is_active"
                    @click="deactivateInstrument(instrument)"
                    class="btn btn-sm btn-outline-danger"
                  >
                    <i class="bi bi-x-circle"></i> Deactivate
                  </button>
                  <button
                    v-else
                    @click="activateInstrument(instrument)"
                    class="btn btn-sm btn-outline-success"
                  >
                    <i class="bi bi-check-circle"></i> Activate
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from '@/plugins/axios'
import { useBranchStore } from '@/stores/branchStore'
import { useNotificationStore } from '@/stores/notificationStore'

const branchStore = useBranchStore()
const notificationStore = useNotificationStore()

const instruments = ref([])
const instrumentTypes = ref([])
const loading = ref(false)
const filterType = ref('')

const filteredInstruments = computed(() => {
  if (!filterType.value) return instruments.value
  return instruments.value.filter(i => i.instrument_type === parseInt(filterType.value))
})

const fetchInstruments = async () => {
  if (!branchStore.selectedBranch) return
  loading.value = true
  try {
    const params = { branch: branchStore.selectedBranch, is_active: 'all' }
    const { data } = await axios.get('/v1/chq/payment-instruments/', { params })
    instruments.value = data
  } catch (error) {
    notificationStore.showError('Failed to load payment instruments')
  } finally {
    loading.value = false
  }
}

const fetchInstrumentTypes = async () => {
  try {
    const params = { branch: branchStore.selectedBranch }
    const { data } = await axios.get('/v1/chq/PaymentInstrumentType/', { params })
    instrumentTypes.value = data
  } catch (error) {
    console.error('Failed to load instrument types:', error)
  }
}

const deactivateInstrument = async (instrument) => {
  try {
    await axios.put(`/v1/chq/payment-instruments/${instrument.id}/`, {
      ...instrument,
      is_active: false,
      version: instrument.version
    })
    notificationStore.showSuccess(`"${instrument.instrument_name}" deactivated`)
    await fetchInstruments()
  } catch (error) {
    if (error.response?.status === 409) {
      notificationStore.showError('Concurrency conflict. Please refresh.')
    } else {
      notificationStore.showError('Failed to deactivate instrument')
    }
  }
}

const activateInstrument = async (instrument) => {
  try {
    await axios.put(`/v1/chq/payment-instruments/${instrument.id}/`, {
      ...instrument,
      is_active: true,
      version: instrument.version
    })
    notificationStore.showSuccess(`"${instrument.instrument_name}" activated`)
    await fetchInstruments()
  } catch (error) {
    notificationStore.showError('Failed to activate instrument')
  }
}

const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  return new Date(dateString).toLocaleDateString()
}

watch(() => branchStore.selectedBranch, () => {
  fetchInstruments()
  fetchInstrumentTypes()
})

onMounted(() => {
  fetchInstruments()
  fetchInstrumentTypes()
})
</script>