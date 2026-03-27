<template>
  <div class="container mt-4">
    <h2>Customer Management</h2>
    <button @click="openForm(null)" class="btn btn-primary mb-3">Add New</button>
    
    <table class="table table-striped">
      <thead>
        <tr>
          <th>Name</th>
          <th>Type</th>
          <th>Parent</th>
          <th>Grace Days</th>
          <th>Status</th>
          <th>Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="customer in customers" :key="customer.alias_id">
          <td>{{ customer.name }}</td>
          <td>{{ customer.is_parent ? 'Head office' : 'Office' }}</td>
          <td>{{ customer.parent_name || '-' }}</td>
          <td>{{ customer.grace_days || '-' }}</td>
          <td>{{ customer.is_active ? 'Active' : 'Inactive' }}</td>
          <td>
            <!-- <button @click="openForm(customer)" class="btn btn-sm btn-warning">Edit</button> -->
            <button @click="openForm(customer)" class="btn btn-sm btn-warning">
              <i class="bi-pencil-square"></i>
            </button>
          </td>
        </tr>
      </tbody>
    </table>

    <CustomerForm 
      v-if="showForm"
      :customer="selectedCus"
      :parents="parents"
      @close="handleFormClose"
    />
  </div>
</template>
  
<script setup>
import { ref, onMounted, watch } from 'vue'
import axios from '../plugins/axios'
import CustomerForm from './CustomerForm.vue'
//import { useBranchStore } from '@/stores/branchStore'
import { useBranchStore } from '@/stores/branchStore'


const branchStore = useBranchStore()
//const branchStore = useBranchStore()
const customers = ref([])
const parents = ref([])
const showForm = ref(false)
const selectedCus = ref(null)

const fetchData = async () => {
  try {
    //console.log('branchStore.selectedBranch: ',branchStore.selectedBranch)
    if (!branchStore.selectedBranch) {
      customers.value = []
      throw new Error('Select the working office first')
    }
    
    const params = {
      branch: branchStore.selectedBranch,
      is_parent: true // Only for parent request
    }

    const [customersRes, parentRes] = await Promise.all([
      axios.get('/v1/chq/customers/', { 
        params: { branch: branchStore.selectedBranch } 
      }),
      axios.get('/v1/chq/customers/', { params })
    ])
    customers.value = customersRes.data
    parents.value = parentRes.data
    //console.log('customers.value:', customers.value ,'customersRes.data: ', customersRes.data )


  } catch (error) {
    console.error('Error fetching data:', error)
  }
}

const openForm = (customer) => {    

  if (customer && customer.branch !== branchStore.selectedBranch) {
    alert('You can only edit customers from the current branch')
    return
  }

  selectedCus.value = customer || null
  showForm.value = true
}

const handleFormClose = (saved) => {

  showForm.value = false
  if (saved) fetchData()
}

onMounted(fetchData)
watch(
  () => branchStore.selectedBranch,
  () => {
    fetchData()
  },
  { immediate: true }
)
// watch(
//   branchStore.selectedBranch,
//   ()=>{
//     fetchData
//   }
// )
</script>