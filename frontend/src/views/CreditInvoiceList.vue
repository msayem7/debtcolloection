<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Credit Invoices</h2>
      <router-link to="/credit-invoices/create" class="btn btn-success">
        Create New
      </router-link>
    </div>
    
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <!-- Date filters -->
          <div class="col-md-2">
            <input type="date" v-model="filters.dateFrom" class="form-control">
          </div>
          <div class="col-md-2">
            <input type="date" v-model="filters.dateTo" class="form-control">
          </div>
          
          <!-- Customer filters -->
          <div class="col-md-2">
            <select v-model="filters.parentCustomer" class="form-select" @change="updateChildCustomers">
              <option value="">All Parent Customers</option>
              <option v-for="customer in parentCustomers" 
                      :value="customer.alias_id" 
                      :key="customer.alias_id">
                {{ customer.name }}
              </option>
            </select>
          </div>
          <div class="col-md-2">
            <select v-model="filters.childCustomer" class="form-select" :disabled="!filters.parentCustomer">
              <option value="">All Child Customers</option>
              <option v-for="customer in childCustomers" 
                      :value="customer.alias_id" 
                      :key="customer.alias_id">
                {{ customer.name }}
              </option>
            </select>
          </div>
          
          <!-- New filter options -->
          <div class="col-md-2">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="filters.showDueOnly" id="showDueOnly">
              <label class="form-check-label" for="showDueOnly">
                Show Due Only
              </label>
            </div>
            <div class="form-check" :class="{ 'text-muted': !filters.showDueOnly }">
              <input class="form-check-input" type="checkbox" v-model="filters.showMaturedOnly" 
                     id="showMaturedOnly" :disabled="!filters.showDueOnly" >
              <label class="form-check-label" for="showMaturedOnly">
                Show Matured Only
              </label>
            </div>
          </div>
          
          <div class="col-md-2">
            <button @click="fetchInvoices" class="btn btn-primary w-100">Filter</button>
          </div>
        </div>
      </div>
    </div>
    
    <div class="table-responsive">      
      <table class="table table-striped  table-hover">
        <thead>
          <tr>
            <th>GRN</th>
            <th>Customer</th>
            <th>Invoice Date</th>
            <th>Grace</th>
            <th>Payment Date</th>
            <th>Sale</th>
            <th>Return</th>
            <th>Net Sale</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>          
          <tr v-for="(invoice) in invoices" :key="invoice.alias_id">
            <td>{{ invoice.grn }} </td>
            <td>{{ invoice.customer_name }}</td>
            <td>{{ formatDate(invoice.transaction_date) }}</td>
            <td>{{ parseInt(invoice.payment_grace_days) }}</td>
            <td>{{ formatDate(calculatePaymentDate(invoice)) }}</td>
            <td>{{ formatNumber(invoice.sales_amount) }}</td>
            <td>{{ formatNumber(invoice.sales_return) }}</td>
            <td>{{ formatNumber(invoice.sales_amount -invoice.sales_return)}}</td>
            <td>
              <router-link 
                :to="{ name: 'CreditInvoiceEdit', params: { aliasId: invoice.alias_id }}" 
                class="btn btn-sm btn-warning"
              >
                Edit
              </router-link>
            </td>
          </tr> 
          <!-- Add empty state message -->
          <tr v-if="invoices.length === 0">
            <td colspan="6" class="text-center">No invoices found</td>
          </tr>
          <!-- Summary Row -->
          <tr v-if="invoices.length > 0" class="bg-light fw-bold">
            <td colspan="5">Total ({{ invoices.length }} invoices)</td>
            <td>{{ formatNumber(totalSales) }}</td>
            <td>{{ formatNumber(totalSalesReturn) }}</td>
            <td>{{ formatNumber(totalNetSales) }}</td>
            <td></td>
          </tr>
        </tbody>
      </table>    
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useBranchStore } from '@/stores/branchStore'
import axios from '@/plugins/axios'
import { formatDate, formatNumber, parseNumber } from '@/utils/ezFormatter'
// import CustomerDropdown from '@/components/CustomerDropdown.vue'

const store = useBranchStore()
const invoices = ref([])
const allCustomers = ref([])
const parentCustomers = ref([])
const childCustomers = ref([])
// const customers = ref([])

const filters = ref({
  dateFrom: '',
  dateTo: '',
  parentCustomer: '',
  childCustomer: '',
  showDueOnly: true,      // New filter
  showMaturedOnly: false   // New filter
})

// const filters = ref({
//   dateFrom: '',
//   dateTo: '',
//   parentCustomer: '',
//   childCustomer: ''
// })

// const fetchInvoices = async () => {
//   try {
//     if (!store.selectedBranch) {
//       invoices.value = []
//       throw new Error('Select a working office first')
//     }

//     // console.log("Filters value", filters.value)
    
//     const params = {
//       branch: store.selectedBranch,
//       transaction_date_after: filters.value.dateFrom,
//       transaction_date_before: filters.value.dateTo,
//       customer: filters.value.customer?.alias_id || filters.value.customer,
//       _t: new Date().getTime()
//     }
    
//     console.log('Invoice Filter params', params)

//     const { data } = await axios.get('/v1/chq/credit-invoices/', { params })
//     invoices.value = data    
//   } catch (error) {
//     console.error('Fetch error:', error)
//     alert('Credit Invoice: ' + error.message)
//   }
// }

// const fetchInvoices = async () => {
//   try {
//     if (!store.selectedBranch) {
//       invoices.value = []
//       throw new Error('Select a working office first')
//     }
    
//     const params = {
//       branch: store.selectedBranch,
//       transaction_date_after: filters.value.dateFrom,
//       transaction_date_before: filters.value.dateTo,
//       _t: new Date().getTime()
//     }

//     // If child customer is selected, use that
//     if (filters.value.childCustomer) {
//       params.customer = filters.value.childCustomer
//     } 
//     // If only parent customer is selected, the backend will handle getting all child invoices
//     else if (filters.value.parentCustomer) {
//       params.customer = filters.value.parentCustomer
//     }

//     const { data } = await axios.get('/v1/chq/credit-invoices/', { params })
//     invoices.value = data    
//   } catch (error) {
//     console.error('Fetch error:', error)
//     alert('Credit Invoice: ' + error.message)
//   }
// }

const fetchInvoices = async () => {
  try {
    if (!store.selectedBranch) {
      invoices.value = []
      throw new Error('Select a working office first')
    }
    
    const params = {
      branch: store.selectedBranch,
      transaction_date_after: filters.value.dateFrom,
      transaction_date_before: filters.value.dateTo,
      _t: new Date().getTime()
    }

    // Customer filters
    if (filters.value.childCustomer) {
      params.customer = filters.value.childCustomer
    } else if (filters.value.parentCustomer) {
      params.customer = filters.value.parentCustomer
    }

    // Due and matured filters
    if (filters.value.showDueOnly) {
      params.payment = 'unpaid'  // This tells the backend to show unpaid invoices only
      if (filters.value.showMaturedOnly) {
        // We'll need to calculate the current date to determine matured invoices
        params.report_date = new Date().toISOString().split('T')[0]
      }
    } else {
      params.payment = 'all'  // Show all invoices regardless of payment status
    }

    const { data } = await axios.get('/v1/chq/credit-invoices/', { params })
    invoices.value = data    
  } catch (error) {
    console.error('Fetch error:', error)
    alert('Credit Invoice: ' + error.message)
  }
}

// const fetchCustomers = async () => {
//   try{
//     const params = {
//       is_active: true,
//       branch: store.selectedBranch
//     }
//     const { data } = await axios.get('/v1/chq/customers/', { params })
//     customers.value = data
//   } catch (error) {
//     console.error('Error loading customers: ', error)
//     alert('Error loading customers: '+ error.message)
//   }
  
// }

const fetchCustomers = async () => {
  try {
    const params = {
      is_active: true,
      branch: store.selectedBranch
    }
    const { data } = await axios.get('/v1/chq/customers/', { params })
    allCustomers.value = data
    
    // Separate parent and child customers
    parentCustomers.value = data.filter(c => c.is_parent)
    updateChildCustomers()
  } catch (error) {
    console.error('Error loading customers: ', error)
    alert('Error loading customers: '+ error.message)
  }
}

const updateChildCustomers = () => {

  console.log('Updating child customers for parent:', filters.value.parentCustomer)
  if (filters.value.parentCustomer) {
    console.log('All customers:', allCustomers.value)
    // allCustomers.value.forEach(c => {
    //   console.log('c.Parent:', c.parent, c)
    //   // if (!c.parent) 
    //   //   console.log('c.Parent alias_id:', c.parent.alias_id, "filters.value.parentCustomer: ", filters.value.parentCustomer)
    //   // else 
    //   //   console.log('c.Parent is parent')
    // })

    childCustomers.value = allCustomers.value.filter(
      c => c.parent === filters.value.parentCustomer
      // c => c.parent && c.parent.alias_id === filters.value.parentCustomer
    )
  } else {
    childCustomers.value = []
  }
  // Reset child customer selection when parent changes
  filters.value.childCustomer = ''
}

// const updateChildCustomers = () => {
//   if (filters.value.parentCustomer) {
//     childCustomers.value = allCustomers.value.filter(
//       c => c.parent?.alias_id === filters.value.parentCustomer
//     )
//   } else {
//     childCustomers.value = []
//   }
//   // Reset child customer selection when parent changes
//   filters.value.childCustomer = ''
// }

const calculatePaymentDate = (invoice) => {
  if (!invoice.transaction_date) return ''
  const date = new Date(invoice.transaction_date)
  //console.log(invoice.grn, date, date.getDate(), parseInt(invoice.payment_grace_days))
  
  if (invoice.payment_grace_days) 
    date.setDate(date.getDate() + parseInt(invoice.payment_grace_days))
   return date.toISOString().split('T')[0]
}

const totalSales = computed(() => {
  return invoices.value.reduce((sum, invoice) => sum + (parseNumber(invoice.sales_amount)|| 0), 0)
})

const totalSalesReturn = computed(() => {
  return invoices.value.reduce((sum, invoice) => sum + (parseNumber(invoice.sales_return) || 0), 0)
})

const totalNetSales = computed(() => {
  return (parseNumber(totalSales.value) - parseNumber(totalSalesReturn.value))
})

onMounted(() => {
  fetchCustomers()
  fetchInvoices()
})
watch([
  () => store.selectedBranch
], () => {
  fetchInvoices()
  fetchCustomers()
}, { immediate: true })


watch([
  () => store.refreshTrigger
], () => {
  fetchInvoices()
  fetchCustomers()
}, { immediate: true })

</script>

<style scoped>
.table-responsive {
  overflow-x: auto;
  max-height: none; /* Remove any height restrictions */
}

.table {
  width: 100%;
  margin-bottom: 1rem;
  border-collapse: collapse;
}

tbody tr {
  cursor: pointer;
}

tbody tr:hover {
  background-color: rgba(0,0,0,.075);
}

.bg-light {
  background-color: #f8f9fa !important;
}
</style>
