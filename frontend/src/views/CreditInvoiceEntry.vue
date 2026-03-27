<template>
  <div class="container mt-4">
    <h2 class="mb-4">{{ editing ? 'Edit' : 'Create' }} Invoice</h2>
    
    <div v-if="loading" class="text-center">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading invoice data...</p>
    </div>

    <form v-else @submit.prevent="handleSubmit">
      <div class="row g-3">
        <!-- Invoice Number -->
        <div class="col-md-6 form-floating">
          <input 
            v-model="form.grn" 
            type="text" 
            class="form-control" 
            id="grn"
            placeholder="grn"
          >
          <label for="grn">GRN</label>
        </div>
        <div class="col-md-6">
          <CustomerDropdown
            v-model="form.customer"
            :error="customerError"
            required
          />
        </div>

        <!-- Transaction Date -->
        <div class="col-md-6 form-floating">
          <input 
            v-model="form.transaction_date" 
            type="date" 
            class="form-control" 
            id="transactionDate"
            placeholder=" "
            required
          >
          <label for="transactionDate">Transaction Date</label>
        </div>

        <!-- sales Amount -->
        <div class="col-md-6 form-floating">
          <input 
            v-model="formattedSalesAmount" 
            type="text" 
            class="form-control" 
            id="sales_amount"
            placeholder=" "
            required
            @blur="updateSalesAmount"
          >
          <label for="sales_amount">Sales Amount</label>
        </div>               
       
        <div class="col-md-6 form-floating">
          <input 
            v-model="formattedSalesReturn" 
            type="text" 
            class="form-control" 
            id="sales_return"
            placeholder=" "
            required
            @blur="updateSalesReturn"
          >
          <label for="sales_return">Sales Return</label>
        </div>

        <div class="col-md-6 form-floating">
          <input 
            :value="formattedNetSales" 
            type="text" 
            class="form-control" 
            id="net_sales"
            placeholder=" "
            readonly
          >
          <label for="net_sales">Net Sales</label>
        </div>

        <!-- Grace Days -->
        <div class="col-md-6 form-floating">
          <input 
            :value="graceDays" 
            type="number" 
            class="form-control" 
            id="graceDays"
            placeholder=" "
            readonly
          >
          <label for="graceDays">Grace Days</label>
        </div>
        
        <!-- Payment Date -->
        <div class="col-md-6 form-floating">
          <input 
            :value="paymentDate" 
            type="date" 
            class="form-control" 
            id="paymentDate"
            placeholder=" "
            readonly
          >
          <label for="paymentDate">Payment Date</label>
        </div>

        <!-- Image Upload & Preview -->
        <div class="col-12">
          <div class="form-floating">
            <input 
              type="file" 
              @change="handleFile" 
              class="form-control" 
              id="invoiceImage"
              placeholder=" "
              accept="image/*"
            >
            <label for="invoiceImage">Invoice Image</label>
          </div>
          
          <!-- Image Preview -->
          <div v-if="imagePreview" class="mt-3">
            <h6 class="text-muted mb-2">Preview:</h6>
            <img 
              :src="imagePreview" 
              class="img-thumbnail" 
              style="max-width: 300px; max-height: 200px"
              alt="Invoice preview"
            >
          </div>
          
          <!-- Existing Image -->
          <div v-if="existingImageUrl" class="mt-3">
            <h6 class="text-muted mb-2">Current Invoice Image:</h6>
            <img 
              :src="existingImageUrl" 
              class="img-thumbnail" 
              style="max-width: 300px; max-height: 200px"
              alt="Current invoice"
            >
          </div>          
        </div>
        <!-- <div class="col-12">
          <CustomerClaims
            ref="customerClaimsRef"
            v-if="form.grn"
            :customerAliasId="form.customer"
            :invoiceAliasId="invoiceId"
          />
        </div> -->

        <!-- Action Buttons -->
        <div class="col-12">
          <button type="submit" class="btn btn-primary me-2" :disabled="submitting">
            <span v-if="submitting" class="spinner-border spinner-border-sm" role="status"></span>
            {{ submitting ? 'Saving...' : 'Save' }}
          </button>
          <router-link to="/credit-invoices" class="btn btn-secondary">Cancel</router-link>
        </div>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from '@/plugins/axios'
import { useBranchStore } from '@/stores/branchStore'
import CustomerDropdown from '@/components/CustomerDropdown.vue'
// import CustomerClaims from '@/views/CustomerClaims.vue'
import { Number } from 'core-js'

import { formatNumber, parseNumber } from '@/utils/ezFormatter'

const store = useBranchStore()
const route = useRoute()
const router = useRouter()

// State management
const loading = ref(false)
const loadingCustomers = ref(true)
const submitting = ref(false)
const customerError = ref(null)
const imagePreview = ref(null)
const existingImageUrl = ref(null)

// Data refs
const editing = ref(false)
const invoiceId = ref(null)
const customers = ref([])


// Form data
const form = ref({
  grn: '',
  customer: '',
  transaction_date: '',
  sales_amount: 0,
  sales_return: 0,
  invoice_image: null,
  version: 1
})

// const customerClaimsRef = ref(null)
const formattedSalesAmount = ref('0.00')
const formattedSalesReturn = ref('0.00')
const formattedNetSales = computed(() => {
  return formatNumber(net_sales.value)
})

// Update the graceDays computed property to handle the object:
const graceDays = computed(() => {
  return form.value.customer?.grace_days || 0
})
const updateSalesAmount = () => {
  const num = parseNumber(formattedSalesAmount.value)
  form.value.sales_amount = num
  formattedSalesAmount.value = formatNumber(num)
}

const updateSalesReturn = () => {
  const num = parseNumber(formattedSalesReturn.value)
  form.value.sales_return = num
  formattedSalesReturn.value = formatNumber(num)
}



// Computed properties
// const graceDays = computed(() => {
//   const customer = customers.value.find(c => c.alias_id === form.value.customer)
//   return customer?.grace_days || 0
// })

const paymentDate = computed(() => {
  if (!form.value.transaction_date) return ''
  const date = new Date(form.value.transaction_date)
  if (graceDays.value) date.setDate(date.getDate() + graceDays.value)
  return date.toISOString().split('T')[0]
})


// Update the net_sales computed property
const net_sales = computed(() => {
  const sales = parseFloat(form.value.sales_amount) || 0
  const sales_return = parseFloat(form.value.sales_return) || 0
  return sales - sales_return
})

// const net_sales = computed(() => {
//   // Convert the input to floating-point numbers.
//   const sales = parseFloat(form.value.sales_amount) || 0;
//   const sales_return = parseFloat(form.value.sales_return) || 0;

//   // Calculate net sales. Optionally, fix it to two decimal places.
//   const netSales = sales - sales_return;
//   return parseFloat(netSales.toFixed(2)); // returns a number with two decimals
// });

// File handling
const handleFile = (e) => {
  const file = e.target.files[0]
  if (file) {
    form.value.invoice_image = file
    imagePreview.value = URL.createObjectURL(file)
    existingImageUrl.value = null
  }
}

const fetchCustomers = async () => {
  try {
    const params = {
      is_active: true,
      branch: store.selectedBranch
    }
    loadingCustomers.value = true

    const { data } = await axios.get('/v1/chq/customers/', { params })
    customers.value = data
    
    // If we're editing and have a customer ID, find and set it
    if (editing.value && invoiceId.value && form.value.customer) {
      const customerObj = data.find(c => c.alias_id === form.value.customer)
      if (customerObj) {
        form.value.customer = customerObj
      }
    }
  } catch (error) {
    customerError.value = 'Failed to load customers. Please try again later.'
  } finally {
    loadingCustomers.value = false
  }
}
// Data fetching
// const fetchCustomers = async () => {
//   try {
//     const params = {
//       is_active: true,
//       branch: store.selectedBranch
//     }
//     loadingCustomers.value = true

//     const { data } = await axios.get('/v1/chq/customers/', { params })
//     customers.value = data
//   } catch (error) {
//     customerError.value = 'Failed to load customers. Please try again later.'
//   } finally {
//     loadingCustomers.value = false
//   }
//}


// Update the fetchInvoice method to set the customer properly:
const fetchInvoice = async () => {
  try {
    loading.value = true
    const { data } = await axios.get(`/v1/chq/credit-invoices/${invoiceId.value}/`)
    
    // Find the customer object from the customers list
    const customerObj = customers.value.find(c => c.alias_id === data.customer)
    // console.log('Customer Object: ', customerObj)
    form.value = {
      ...data,
      customer: customerObj, //customers.value.find(c => c.alias_id === data.customer), // Find the customer object
      version: data.version
    }

    if (data.invoice_image) {
      existingImageUrl.value = data.invoice_image
    }

    // Verify customer exists in loaded list
    if (!customerObj) {
      customerError.value = 'Selected customer not found in current list'
    }
  } catch (error) {
    alert(error.response?.data?.error || 'Failed to load invoice')
    router.push('/credit-invoices')
  } finally {
    loading.value = false
  }
}

const handleSubmit = async () => {
  try {
    submitting.value = true
    const branch = localStorage.getItem('workingOffice')
    if (!branch) throw new Error('Select a working office first')
    
    const formData = new FormData()
    formData.append('version', form.value.version)
    
    // Handle customer - extract alias_id if it's an object
    const customerAliasId = form.value.customer?.alias_id || form.value.customer
    
     // Create a copy of form.value without the payment field if it's null
    const formDataToSend = {
      ...form.value,
      customer: customerAliasId
    }
    
    if (formDataToSend.payment === null) {
      delete formDataToSend.payment
    }

    Object.entries(formDataToSend).forEach(([key, val]) => {
      if (key === 'invoice_image') {
        if (val instanceof File) formData.append(key, val)
      } else if (key !== 'version') {
        formData.append(key, val)
      }
    })
    
    formData.append('branch', branch)

    // Object.entries({
    //   ...form.value,
    //   customer: customerAliasId
    // }).forEach(([key, val]) => {
    //   if (key === 'invoice_image') {
    //     if (val instanceof File) formData.append(key, val)
    //   } else if (key !== 'version') {
    //     formData.append(key, val)
    //   }
    // })
    
    // formData.append('branch', branch)

    const response = await axios({
      method: editing.value ? 'put' : 'post',
      url: editing.value ? `/v1/chq/credit-invoices/${invoiceId.value}/` : '/v1/chq/credit-invoices/',
      data: formData,
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    router.push('/credit-invoices')
  } catch (error) {
    alert(error.response?.data?.error || error.message)
  } finally {
    submitting.value = false
  }
}

// Update handleSubmit to send just the customer alias_id:
// const handleSubmit = async () => {
//   try {
//     submitting.value = true
//     const branch = localStorage.getItem('workingOffice')
//     if (!branch) throw new Error('Select a working office first')
    
//     const formData = new FormData()
//     formData.append('version', form.value.version)
    
//     // Convert customer object to just the alias_id for the API
//     const customerAliasId = form.value.customer?.alias_id || form.value.
//     // const customerAliasId = typeof form.value.customer === 'object' 
//     //   ? form.value.customer.alias_id 
//     //   : form.value.customer
      
//     Object.entries({
//       ...form.value,
//       customer: customerAliasId
//     }).forEach(([key, val]) => {
//       if (key === 'invoice_image') {
//         if (val instanceof File) formData.append(key, val)
//       } else if (key !== 'version') {
//         formData.append(key, val)
//       }
//     })
    
//     formData.append('branch', branch)

//     const response = await axios({
//       method: editing.value ? 'put' : 'post',
//       url: editing.value ? `/v1/chq/credit-invoices/${invoiceId.value}/` : '/v1/chq/credit-invoices/',
//       data: formData,
//       headers: { 'Content-Type': 'multipart/form-data' }
//     })

//     router.push('/credit-invoices')
//   } catch (error) {
//     alert(error.response?.data?.error || error.message)
//   } finally {
//     submitting.value = false
//   }
// }

// const fetchInvoice = async () => {
//   try {
//     loading.value = true
//     const { data } = await axios.get(`/v1/chq/credit-invoices/${invoiceId.value}/`)
    
//     form.value = {
//       ...data,
//       customer: data.customer, // Direct assignment of alias_id
//       version: data.version
//     }
//     // console.log('Form value: ',form.value)

//     if (data.invoice_image) {
//       existingImageUrl.value = data.invoice_image
//     }

//     // Verify customer exists in loaded list
//     await nextTick()
//     if (!customers.value.some(c => c.alias_id === form.value.customer)) {
//       customerError.value = 'Selected customer not found in current list'
//     }
//   } catch (error) {
//     alert(error.response?.data?.error || 'Failed to load invoice')
//     router.push('/credit-invoices')
//   } finally {
//     loading.value = false
//   }
// }

// // Form submission
// const handleSubmit = async () => {
//   try {
//     submitting.value = true
//     const branch = localStorage.getItem('workingOffice')
//     if (!branch) throw new Error('Select a working office first')
    
//     // Get claims data from child component
//     // const allClaims = customerClaimsRef.value?.claims || []
//     // const claimsToSave = allClaims.filter(c => {
//     //   // Filter out zero amounts and invalid claims
//     //   return Number(c.claim_amount) !== 0 && c.claim_amount !== ''
//     // }).map(c => ({
//     //   alias_id: c.alias_id,
//     //   claim_amount: c.claim_amount,
//     //   existing: c.existing
//     // }))

//     const formData = new FormData()
//     formData.append('version', form.value.version)
//     // formData.append('claims', JSON.stringify(claimsToSave))
    
//     Object.entries(form.value).forEach(([key, val]) => {
//       if (key === 'invoice_image') {
//         if (val instanceof File) formData.append(key, val)
//       } else if (key !== 'version') {
//         formData.append(key, val)
//       }
//     })
    
//     formData.append('branch', branch)

//     const response = await axios({
//       method: editing.value ? 'put' : 'post',
//       url: editing.value ? `/v1/chq/credit-invoices/${invoiceId.value}/` : '/v1/chq/credit-invoices/',
//       data: formData,
//       headers: { 'Content-Type': 'multipart/form-data' }
//     })

//     router.push('/credit-invoices')
//   } catch (error) {
//     alert(error.response?.data?.error || error.message)
//   } finally {
//     submitting.value = false
//   }
// }

// watch(() => store.selectedBranch, async () => {
//   await fetchCustomers()
// }, { immediate: true })

watch(() => store.selectedBranch, (newBranch, oldBranch) => {
  if (oldBranch && newBranch !== oldBranch) {
    // Show alert to user
    alert('Branch has changed. Redirecting to invoice list.')
    // Redirect to invoice list
    router.push('/credit-invoices')
  }
}, { immediate: true })

// this watcher to handle initial values
watch(() => form.value.sales_amount, (newVal) => {
  formattedSalesAmount.value = formatNumber(newVal)
}, { immediate: true })

watch(() => form.value.sales_return, (newVal) => {
  formattedSalesReturn.value = formatNumber(newVal)
}, { immediate: true })
// Initialization
onMounted(async () => {
  // First load customers
  await fetchCustomers()
  
  // Then check if we're editing and load invoice
  if (route.params.aliasId) {
    editing.value = true
    invoiceId.value = route.params.aliasId
    await fetchInvoice()
  }
})

</script>