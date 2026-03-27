<template>
  <div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h2>Cheque Management</h2>
      <router-link to="/cheques/create" class="btn btn-success">
        Create New
      </router-link>
    </div>

    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-md-3">
            <input 
              v-model="filters.dateFrom" 
              type="date" 
              class="form-control"
            >
          </div>
          <div class="col-md-3">
            <input v-model="filters.dateTo" type="date" class="form-control">
          </div>
          <div class="col-md-3">
            <select v-model="filters.customer" class="form-select">
              <option value="">All Customers</option>
              <option v-for="c in customers" :value="c.alias_id" :key="c.alias_id">{{ c.name }}</option>
            </select>
          </div>
          <div class="col-md-3">
            <button class="btn btn-primary w-100" @click="fetchCheques" >Filter</button>
          </div>
        </div>
      </div>
    </div>

    <table class="table table-striped">
      <thead>
        <tr>
          <th>Customer</th>
          <th>Amount</th>
          <th>Adjusted</th>   
          <th>Balance</th>            
          <th>Status</th> 
          <th>Received Date</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="cheque in cheques" :value="cheque.alias_id" :key="cheque.alias_id">
          <td>{{ cheque.customer_name }}</td> 
          <td>{{ cheque.cheque_amount }}</td>
          <td>{{ cheque.sum_adjustment }}</td>  
          <td>{{ cheque.cheque_amount - cheque.sum_adjustment }}</td>  
          <td>{{ getStatusText(cheque.cheque_status) }}</td>
          <td>{{ formatDate(cheque.received_date) }}</td>
          <td>
            <router-link 
              :to="{ name: 'cheque-edit', params: { aliasId: cheque.alias_id }}" 
              class="btn btn-sm btn-warning"
            >
              Edit
            </router-link>
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
  
<script setup>
import { ref, watch, onMounted } from 'vue'
import axios from '@/plugins/axios'
import { formatDate } from '@/utils/ezFormatter'; 
import { useBranchStore } from '@/stores/branchStore'
  
  
const store = useBranchStore()
const dateFormatter = { formatDate };
const cheques = ref([])
const customers = ref([])
const filters = ref({
  dateFrom: '',
  dateTo: '',
  customer: '',
  status: []
})
  
const statusOptions = [
  { value: 1, text: 'Received' },
  { value: 2, text: 'Deposited' },
  { value: 3, text: 'Honored' },
  { value: 4, text: 'Dishonored' },
  { value: 5, text: 'Canceled' }
]

const fetchCheques = async () => {
  try {
    
    if (!store.selectedBranch) {
      cheques.value = []
    throw new Error('Select a working office first')
  }
  // const branch = localStorage.getItem('workingOffice')
  // if (!branch) {
  //   cheques.value = []
  //   throw new Error('Select a working office first')
  // }
    
    const params = {
      branch: store.selectedBranch,
      date_from: filters.value.dateFrom,
      date_to: filters.value.dateTo,
      customer: filters.value.customer,
      status: filters.value.status
    }
    
    const { data } = await axios.get('/v1/chq/cheques/', { params })
    cheques.value = data
  } catch (error) {
    alert(error.message)
  }
}
  
const fetchCustomers = async () => {
  try{
    const params = {
    is_active: true,
    branch: store.selectedBranch
    }

    if (!store.selectedBranch) {
        customers.value = []
      }
    const { data } = await axios.get('/v1/chq/customers/',{ params})
    customers.value = data
  } catch (error) {
    console.error('error fetching customers', error)
  }
}

const getStatusText = (status) => {
  return statusOptions.find(s => s.value === status)?.text || 'Unknown'
}  
 
  
onMounted(() => {
  fetchCustomers()
  fetchCheques()
})

watch([
  () => store.selectedBranch,
  () => store.refreshTrigger
], ()=>{
  fetchCustomers()
  fetchCheques()
})

</script>
  