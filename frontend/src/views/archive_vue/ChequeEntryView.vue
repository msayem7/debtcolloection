<template>
  <div class="container mt-4">
    <h2 class="mb-4">{{ editing ? 'Edit' : 'Create' }} Cheque</h2>
    
    <form @submit.prevent="handleSubmit">
      <div class="row g-3">
        <!-- Customer Select -->
        <div class="col-md-6 form-floating">
          <select 
            v-model="form.customer" 
            class="form-select" 
            id="customerSelect"
            required
            :disabled="loadingCustomers"
          >            
            <option v-if="loadingCustomers" value="" disabled>
              Loading customers...
            </option>
            <template v-else>
              <option value="" disabled hidden>Select customer</option>
              <option v-for="c in customers" :value="c.alias_id" :key="c.alias_id">
                {{ c.name }}
              </option>
            </template>            
          </select>
          <label for="customerSelect">Customer</label>
          <div v-if="customerError" class="text-danger mt-1">
            {{ customerError }}
          </div>
        </div>

        <!-- Received Date -->
        <div class="col-md-6 form-floating">
          <input 
            v-model="form.received_date" 
            type="date" 
            class="form-control" 
            id="receivedDate"
            required
          >
          <label for="receivedDate">Received Date</label>
        </div>

        <!-- Cheque Details -->
        <div class="col-md-4 form-floating">
          <input 
            v-model="form.cheque_amount" 
            type="number" 
            step="0.01" 
            class="form-control" 
            id="chequeAmount"
            required
          >
          <label for="chequeAmount">Amount</label>
        </div>

        <div class="col-md-4 form-floating">
          <input 
            v-model="form.cheque_date" 
            type="date" 
            class="form-control" 
            id="chequeDate"
          >
          <label for="chequeDate">Cheque Date</label>
        </div>

        <div class="col-md-4 form-floating">
          <select 
            v-model="form.cheque_status" 
            class="form-select" 
            id="chequeStatus"
          >
            <option v-for="status in statusOptions" :value="status.value" :key="status.value">
              {{ status.text }}
            </option>
          </select>
          <label for="chequeStatus">Status</label>
        </div>

        <!-- Image Upload -->
        <div class="col-12 form-floating">
          <input 
            type="file" 
            @change="handleFile" 
            class="form-control" 
            id="chequeImage"
            accept="image/*"
          >
          <label for="chequeImage">Cheque Image</label>
        </div>

        <!-- Image Previews -->
        <div v-if="imagePreview" class="col-12">
          <h6 class="text-muted mb-2">Preview:</h6>
          <img :src="imagePreview" class="img-thumbnail" style="max-width: 300px">
        </div>
        <div v-if="existingImage" class="col-12">
          <h6 class="text-muted mb-2">Current Image:</h6>
          <img :src="existingImage" class="img-thumbnail" style="max-width: 300px">
        </div>

        <!-- Invoice Adjustments -->
        <div class="col-12">
          <button type="button" @click="showInvoices" class="btn btn-secondary mb-3">
            Show Invoices
          </button>
          
          <div v-if="showInvoiceGrid" class="card">
            <div class="card-body">
              <table class="table">
                <thead>
                  <tr>
                    <th>Invoice #</th>
                    <th>Date</th>
                    <th>Amount</th>
                    <th>Adjustment</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="invoice in customerInvoices" :key="invoice.alias_id">
                    <td>{{ invoice.grn }}</td>
                    <td>{{ formatDate(invoice.transaction_date) }}</td>
                    <td>{{ invoice.due_amount }}</td>
                    <td>
                      <input 
                        type="number" 
                        v-model="adjustments[invoice.alias_id]" 
                        min="0" 
                        step="0.01" 
                        class="form-control"
                        @change="validateAdjustment(invoice)"
                      >
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- Submit -->
        <div class="col-12">
          <button type="submit" class="btn btn-primary me-2">Save</button>
          <router-link to="/cheques" class="btn btn-secondary">Cancel</router-link>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/plugins/axios'
import { formatDate } from '@/utils/ezFormatter';
import { useBranchStore } from '@/stores/branchStore';

const branchStore = useBranchStore()
const route = useRoute()
const router = useRouter()

const editing = computed(() => !!route.params.aliasId)
// State
const loadingCustomers = ref(true)
const customerError = ref(null)

const form = ref({
  customer: '',
  received_date: new Date().toISOString().split('T')[0],
  cheque_amount: 0,
  cheque_date: null,
  cheque_status: 1,
  cheque_image: null,
  version: 1
})
const imagePreview = ref(null)
const existingImage = ref(null)
const showInvoiceGrid = ref(false)
const customerInvoices = ref([])
const adjustments = ref({})

// Data
const customers = ref([])
const statusOptions = [
  { value: 1, text: 'Received' },
  { value: 2, text: 'Deposited' },
  { value: 3, text: 'Honored' },
  { value: 4, text: 'Dishonored' },
  { value: 5, text: 'Canceled' }
]

const handleFile = (e) => {
  const file = e.target.files[0]
  if (file) {
    form.value.cheque_image = file
    imagePreview.value = URL.createObjectURL(file)
  }
}

const fetchCustomers =async ()=>{  
  try {
    const params = {
        is_active: true,
        branch: branchStore.selectedBranch
      }

    const { data } = await axios.get('/v1/chq/customers/', {params})
    customers.value = data
    loadingCustomers.value = true
    
  } catch (error) {
    customerError.value = 'Failed to load customers. Please try again later.'
  } finally {
    loadingCustomers.value = false
  }
}

const showInvoices = async () => {
  if (!form.value.customer) return alert('Select customer first')
  try {
    const { data } = await axios.get(`/v1/chq/credit-invoices/?customer=${form.value.customer}&status=true`)
    customerInvoices.value = data
    showInvoiceGrid.value = true
  } catch (error) {
    alert(error.message)
  }
}

const validateAdjustment = (invoice) => {
  if (new Date(form.value.received_date) < new Date(invoice.transaction_date)) {
    alert('Cheque date must be after invoice date')
    adjustments.value[invoice.alias_id] = 0
  }
}

const handleSubmit = async () => {
  try {
    const branch = localStorage.getItem('workingOffice')
    if (!branch) throw new Error('Select a working office first')
    
    const formData = new FormData()
    Object.entries(form.value).forEach(([key, val]) => {
      if (key === 'cheque_image' && !val) return
      formData.append(key, val)
    })
    formData.append('branch', branch)


    // Process adjustments
    // const invoiceCheques = Object.entries(adjustments.value)
    //   .filter(([_, amount]) => amount > 0)
    //   .map(([invoice, amount]) => ({
    //     creditinvoice: invoice, 
    //     adjusted_amount: amount
    //   }))

    const invoiceCheques = Object.entries(adjustments.value)
      .filter(([_, amount]) => amount > 0)
      .map(([invoiceAlias, amount]) => {
        // Convert amount to number
        const numericAmount = parseFloat(amount)
        if (isNaN(numericAmount)) {
          throw new Error(`Invalid amount for invoice ${invoiceAlias}`)
        }
        
        return {
          creditinvoice: invoiceAlias,
          adjusted_amount: numericAmount  // Ensure numeric value
        }
      })

    formData.append('invoice_cheques', JSON.stringify(invoiceCheques))

    if (route.params.aliasId) {
      await axios.put(`/v1/chq/cheques/${route.params.aliasId}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    } else {
      await axios.post('/v1/chq/cheques/', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
    }
    
    router.push('/cheques')
  } catch (error) {
    alert(error.response?.data?.error || error.message)
  }
}

watch(() => branchStore.selectedBranch, (newBranch, oldBranch) => {
  if (oldBranch && newBranch !== oldBranch) {
    // Show alert to user
    alert('Office has changed. Redirecting to cheque list.')
    // Redirect to cheques list
    router.push('/cheques')
  }
}, { immediate: true })

watch(() => form.value.customer, (newCustomer, oldCustomer) => {
  if (oldCustomer && newCustomer !== oldCustomer) {
    customerInvoices.value = []
    adjustments.value = {}
    showInvoiceGrid.value = false
  }
}, { immediate: true })


onMounted(async () => {
  fetchCustomers()
  editing.value = !!route.params.aliasId; 
  
  if (route.params.aliasId) {
    const { data: cheque } = await axios.get(`/v1/chq/cheques/${route.params.aliasId}/`,{
      params: { include_invoice_cheques: true }
    })

    form.value = {
      ...cheque,
      customer: cheque.customer,
      version: cheque.version
    }
    if (cheque.invoice_cheques) {
      cheque.invoice_cheques.forEach(mapping => {
        //adjustments.value[mapping.creditinvoice.alias_id] = mapping.adjusted_amount
        adjustments.value[mapping.creditinvoice] = mapping.adjusted_amount
      })
    }

    if (cheque.cheque_image) {
      existingImage.value = cheque.cheque_image
    }   
  }
})
</script>

<style scoped>
.table {
  font-size: 0.9rem;
}
.card {
  margin-top: 1rem;
}
.img-thumbnail {
  max-height: 200px;
}
</style>