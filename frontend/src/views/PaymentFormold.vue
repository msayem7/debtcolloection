<template>
  <div class="container-fluid">
    <h3>Customer Payment</h3>
    <div class="row mt-4">
      <div class="col-md-2">
        <div class="form-floating">
          <input
            v-model="formData.received_date"
            type="date"
            class="form-control"
            :class="{ 'is-invalid': errors.received_date }"
            @input="formatDate('received_date')"
          >
          <label>Received Date</label>
          <div v-if="errors.received_date" class="invalid-feedback">
            {{ errors.received_date }}
          </div>
        </div>
      </div>
      <div class="col-md-4">
        <CustomerDropdown 
          v-model="formData.customer"
          :error="errors.customer"
        />
      </div>
    </div>
    <div class="row mt-4">
      <div class="col-md-6">
        <ReceivedCheques 
          :cheques="formData.cheques"
          @update:cheques="updateCheques"
        />
        <ExistingPayments
          ref="refreshComponentRef"
          :key="refreshComponentKey"
          :payments="existingPayments"
          :customer="formData.customer"
          :loading="loadingExistingPayments"
          @update:selectedPayments="updateExistingPayments"
        />        
      </div>
      <div class="col-md-6">
        <CustomerClaims
          :claims="formData.claims"
          @update:claims="updateClaims"
        />
      </div>      
    </div>
    <div class="row mt-4">
      <!-- <div class="col-md-12"> -->
      <InvoiceComponent
        ref="refreshComponentRef"
        :key="refreshComponentKey"
        :invoices="filteredInvoices"
        :cheques="formData.cheques"
        :claims="formData.claims"
        :existingPayments="selectedExistingPayments"  
        :loading="loadingInvoices"
        v-model="formData.allocations"
      />
      <!-- </div> -->
      <div v-if="loadingInvoices" class="mt-2">
        Loading invoices...
      </div>
      
      <div v-if="invoiceError" class="alert alert-danger mt-2">
        {{ invoiceError }}
      </div>
    </div>
    <button @click="submitPayment" class="btn btn-primary mt-3">
      Submit Payment
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, watchEffect } from 'vue'
import { useNotificationStore } from '@/stores/notificationStore'
import { useBranchStore } from '@/stores/branchStore'
import { formatDate, ServerDateFormat, formatNumber, parseNumber } from '@/utils/ezFormatter'
import ExistingPayments from '@/views/component/ExistingPayments.vue'
import ReceivedCheques from '@/views/component/ReceivedCustomerPayments.vue'
import CustomerClaims from '@/views/component/CustomerClaims.vue'
import CustomerDropdown from '@/components/CustomerDropdown.vue'
import InvoiceComponent from '@/views/component/InvoiceComponent.vue'
import axios from '@/plugins/axios'

const refreshComponentRef = ref(null)
const refreshComponentKey = ref(0)

const notificationStore = useNotificationStore()
const branchStore = useBranchStore()
const masterClaims = ref([])

const existingPayments = ref([])
const loadingExistingPayments = ref(false)
const selectedExistingPayments = ref([])


const formData = ref({
  received_date: formatDate(new Date()),
  customer: null,
  cheques: [],
  claims: [],
  allocations: {}
})

const filteredInvoices = ref([])
const loadingInvoices = ref(false)
const invoiceError = ref(null)

const errors = ref({})

watch(
  () => branchStore.selectedBranch,
  async (newBranch) => {
    // console.log('Branch changed:', newBranch)
    try {
      await resetClaim() // Now properly awaits the async function
      resetForm()
    } catch (error) {
      console.error('Branch change handling error:', error)
    }
  },
  { immediate: true }
)

// Update your watchEffect to also fetch existing payments
watchEffect(async () => {  
  if (formData.value.customer?.alias_id && branchStore.selectedBranch) {
    await fetchInvoices()
    await fetchExistingPayments()
  } else {
    filteredInvoices.value = []
    existingPayments.value = []
    loadingInvoices.value = false
    loadingExistingPayments.value = false
  }
})

function updateCheques(updatedCheques) {
  formData.value.cheques = updatedCheques
}

function updateClaims(updatedClaims) {
  // console.log('updatedClaims > Started > formData.value.claims :', updatedClaims)
  formData.value.claims = updatedClaims.map(claim => ({   
    claim_no: claim.claim_no,
    claim: claim.claim,
    claim_name: claim.claim_name, 
    prefix: claim.prefix, 
    next_number: claim.next_number, 
    claim_amount: parseNumber(claim.claim_amount),
    details: claim.details
  }))
  
  console.log ('updatedClaims> End > formData.value.claims:', formData.value.claims)
}

async function fetchExistingPayments() {
  if (formData.value.customer?.alias_id && branchStore.selectedBranch) {
    loadingExistingPayments.value = true
    try {
      
      const response = await axios.get('/v1/chq/unallocated-payments/', {
        params: {
          branch: branchStore.selectedBranch,
          customer: formData.value.customer.alias_id
        }
      })
      existingPayments.value = response.data
    } catch (error) {
      console.error('Error loading existing payments:', error)
    } finally {
      loadingExistingPayments.value = false
    }
  }
}

// Add this method to handle updates
function updateExistingPayments(payments) {
  selectedExistingPayments.value = payments
}

function resetForm() {
  formData.value.cheques = []
  formData.value.claims = masterClaims.value.map(claim => ({
    ...claim,
    prefix:claim.prefix,
    next_number:claim.next_number,
    claim_no: `${claim.prefix}${claim.next_number.toString().padStart(6, '0')}`,  // claim.prefix + claim.next_number,
    claim_amount: 0,
    details: ''
  }))
  console.log('resetForm > formData.value.claims:', formData.value.claims)
  console.log('resetForm > masterClaims.value:', masterClaims.value)
  formData.value.allocations = {}
  errors.value = {}
}


async function submitPayment() {
  try {
    // Check for duplicates before submission
   // Modified cheque/claim validation
   const receipt_nos = formData.value.cheques
      .map(c => c.receipt_no)
      .filter(n => n.trim() !== '')

    const claimNos = formData.value.claims
      .map(c => c.claim_no)
      .filter(n => n.trim() !== '')  // Add this filter
      
    if (new Set(receipt_nos).size !== receipt_nos.length) {
      throw new Error('Duplicate cheque numbers exist')
    }

    // if (new Set(claimNos).size !== claimNos.length) {
    //   throw new Error('Duplicate claim numbers exist')
    // }
    // Store customer ID before reset
    const customerAliasId = formData.value.customer?.alias_id
    const filteredClaims = formData.value.claims.filter(claim => {
      const amount = parseFloat(claim.claim_amount);
      return (
        claim.claim_no?.trim() &&
        !isNaN(amount) &&
        amount > 0 &&
        claim.claim // 👈 Ensure the "claim" field exists
      );
    });
    
    // console.log ('formData.value.allocations', formData.value.allocations)
    const validAllocations = Object.entries(formData.value.allocations)
      .filter(([invoiceId, allocation]) => {
        const chequeAllocations = Object.values(allocation.cheques || {}).reduce((sum, val) => sum + parseNumber(val || 0), 0)
        const claimAllocations = Object.values(allocation.claims || {}).reduce((sum, val) => sum + parseNumber(val || 0), 0)
        const existingPaymentAllocations = Object.values(allocation.existingPayments || {}).reduce((sum, val) => sum + parseNumber(val || 0), 0)
        
        return (chequeAllocations + claimAllocations + existingPaymentAllocations) > 0
      })
      .reduce((acc, [invoiceId, allocation]) => {
        acc[invoiceId] = allocation
        return acc
      }, {})
    
      
    // console.log ("validAllocations: ", Object.keys(validAllocations).entries())
    if (Object.keys(validAllocations).length === 0) {
      throw new Error('No valid allocations found')
    }

    // Update payload to use filtered existing payments
    const payload = {
      ...formData.value,
      received_date: formatDate(formData.value.received_date),
      branch: branchStore.selectedBranch,
      customer: formData.value.customer.alias_id,
      claims: filteredClaims,
      // existing_payments: filteredExisting.map(p => ({
      //   receipt_no: p.receipt_no,
      //   instrument_type: p.instrument_type,
      //   cheque_amount: p.cheque_amount
      // })),
      allocations: validAllocations
    };

    //console.log('Allocations:', JSON.parse(JSON.stringify(formData.value.allocations)))
    // console.log('Existing Payments:', filteredExisting.value)

    const response = await axios.post('/v1/chq/customer-payments/', payload);
  
    notificationStore.showSuccess('Payment recorded successfully');
    alert('Payment recorded successfully')
    refreshComponentKey.value++
    formData.value.allocations = {} // Reset allocations

    formData.value.customer = null
    resetClaim() // Reset claims after successful submission
    resetForm()


    // Reset invoice component state
    if (refreshComponentRef.value) {
      refreshComponentRef.value.resetState()
    } 

    // console.log('Reset invoice component state')

    // // Force reload invoices
    // refreshComponentKey.value++

    // await fetchInvoices()

    // console.log('Invoice fetched')
    // formData.value.allocations = {} // Reset allocations
    // selectedInvoices.value = [] // Clear selected invoices

    // // Add cache-buster to force fresh data
    // const timestamp = new Date().getTime()
    // const response1 = await axios.get('/v1/chq/credit-invoices/', {
    //   params: {
    //     branch: branchStore.selectedBranch,
    //     customer: customerAliasId,  // Use stored value
    //     _: timestamp
    //   }
    // })

    // filteredInvoices.value = JSON.parse(JSON.stringify(response1.data))
    
  } catch (error) {
    notificationStore.showError(error.response?.data?.error || error.message)
    if (error.response?.data) {
      errors.value = error.response.data
    }
  }
}


// Add this function to re-fetch invoices
async function fetchInvoices() {
  if (formData.value.customer?.alias_id && branchStore.selectedBranch) {
    loadingInvoices.value = true;
    try {
      const timestamp = new Date().getTime()
      const response = await axios.get('/v1/chq/credit-invoices/', {
        params: {
          branch: branchStore.selectedBranch,
          customer: formData.value.customer.alias_id,
          status: "true",  // 👈 Ensure active invoices are fetched
          _: timestamp
        }
      })
      
      // filteredInvoices.value = response.data;
      // filteredInvoices.value={}

      filteredInvoices.value = JSON.parse(JSON.stringify(response.data)); 
    } catch (error) {
      invoiceError.value = 'Failed to reload invoices';
    } finally {
      loadingInvoices.value = false;
    }
  }
}

async function resetClaim() {
  try {     
    // console.log('resetClaim > start:')
    const response = await axios.get('/v1/chq/master-claims/', {
      params: {
        branch: branchStore.selectedBranch // Will use current branch
      }
    })
    console.log('resetClaim > response.data:', response.data)
    masterClaims.value = response.data.map(item => ({
      claim: item.alias_id,
      claim_name: item.claim_name,
      prefix: item.prefix,
      next_number: item.next_number,
      claim_amount: 0,
      details: ''
    }))    
    console.log('resetClaim > masterClaims.value:', masterClaims.value)
    resetForm() // Reset form after claims update
  } catch (error) {
    invoiceError.value = 'Failed to reset claims'
    console.error('Claim reset error:', error)
  }
}

// Updated mounted hook
onMounted(async () => {
  try {    
    await resetClaim()
    resetForm() // Initialize claims with master data
  } catch (error) {
    console.error('Error loading master claims:', error)
    notificationStore.showError('Failed to load claim templates')
  }
})

</script>

<style scoped>
.is-invalid {
  border-color: #dc3545;
  background-image: url("data:image/svg+xml,%3csvg...");
}

.invalid-feedback {
  color: #dc3545;
  font-size: 0.875em;
  margin-top: 0.25rem;
}
</style>