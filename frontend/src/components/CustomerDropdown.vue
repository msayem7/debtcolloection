<template>
  <div class="customer-selector-container">
    <!-- Parent Company Selection -->
    <div class="dropdown-section">
      <label v-if="showLabels" class="dropdown-label">Parent Organization</label>
      <select
        v-model="selectedParent"
        class="form-select"
        :class="{ 'is-invalid': error }"
        @change="onParentChange"
        :disabled="loading"
      >
        <option value="">Select Parent Organization</option>
        <option 
          v-for="parent in parentOrganizations" 
          :key="parent.alias_id"
          :value="parent"  
        >
          {{ parent.name }} 
        </option>
      </select>
    </div>

    <!-- Customer Selection -->
    <div class="dropdown-section">
      <label v-if="showLabels" class="dropdown-label">Customer</label>
      <select
        v-model="selectedCustomer"
        class="form-select"
        :class="{ 'is-invalid': error }"
        :disabled="!selectedParent || loading"
        @change="onCustomerChange"
      >
        <option value="">Select Customer</option>
        <option 
          v-for="customer in filteredCustomers" 
          :key="customer.alias_id"
          :value="customer"  
        >
          {{ customer.name }} 
        </option>
      </select>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useBranchStore } from '@/stores/branchStore'
import axios from '@/plugins/axios'

// eslint-disable-next-line no-undef
const props = defineProps({ 
  modelValue: [Object, String],
  error: String,
  showLabels: {
    type: Boolean,
    default: true
  },
  layout: {
    type: String,
    default: 'side-by-side', // or 'stacked'
    //validator: (value) => ['side-by-side', 'stacked'].includes(value)
  }
})

// eslint-disable-next-line no-undef
const emit = defineEmits(['update:modelValue'])
const customers = ref([])
const parentOrganizations = ref([])
const selectedParent = ref(null)
const selectedCustomer = ref(null)
const branchStore = useBranchStore()
const loading = ref(false)

const filteredCustomers = computed(() => {
  // console.log("selectedParent.value :", selectedParent.value)
  // console.log("customers.value :", customers.value)
  if (!selectedParent.value) return []
  return customers.value.filter(customer => 
    customer.parent === selectedParent.value.alias_id // || 
    // customer.alias_id === selectedParent.value.alias_id
  )
})

const loadCustomers = async () => {
  try {
    loading.value = true
    if (branchStore.selectedBranch) {
      // Load all active customers
      const customersResponse = await axios.get('/v1/chq/customers/', {
        params: {
          is_active: true,
          branch: branchStore.selectedBranch
        }
      })
      customers.value = customersResponse.data

      // Load only parent organizations
      const parentsResponse = await axios.get('/v1/chq/customers/', {
        params: {
          is_active: true,
          branch: branchStore.selectedBranch,
          is_parent: true
        }
      })
      parentOrganizations.value = parentsResponse.data
    } else {
      customers.value = []
      parentOrganizations.value = []
    }
  } catch (error) {
    console.error('Error loading customers:', error)
  } finally {
    loading.value = false
  }
}

// const loadCustomers = async () => {
//   try {
//     if (branchStore.selectedBranch) {
//       // Load all active customers
//       const customersResponse = await axios.get('/v1/chq/customers/', {
//         params: {
//           is_active: true,
//           branch: branchStore.selectedBranch
//         }
//       })
//       customers.value = customersResponse.data

//       // Load only parent organizations
//       const parentsResponse = await axios.get('/v1/chq/customers/', {
//         params: {
//           is_active: true,
//           branch: branchStore.selectedBranch,
//           is_parent: true
//         }
//       })
//       parentOrganizations.value = parentsResponse.data
//     } else {
//       customers.value = []
//       parentOrganizations.value = []
//     }
//     resetSelections()
//   } catch (error) {
//     console.error('Error loading customers:', error)
//   }
// }

const resetSelections = () => {
  selectedParent.value = null
  selectedCustomer.value = null
  emit('update:modelValue', null)
}


const onParentChange = () => {
  selectedCustomer.value = null
  // emit('update:modelValue', null)
}

const onCustomerChange = () => {
  emit('update:modelValue', selectedCustomer.value)
}

onMounted(loadCustomers)
watch(() => props.modelValue, (newVal) => {
  // console.log("watch triggered - newVal:", newVal)
  // console.log("current customers:", customers.value)
  // console.log("current parentOrganizations:", parentOrganizations.value)

  if (!newVal) {
    resetSelections()
    return
  }

  const trySetSelections = () => {
    if (customers.value.length && parentOrganizations.value.length) {
      let customerObj = null
      
      if (typeof newVal === 'string') {
        customerObj = customers.value.find(c => c.alias_id === newVal)
        // console.log("found customer by string:", customerObj)
      } else if (newVal && typeof newVal === 'object') {
        customerObj = newVal
        // console.log("received customer object:", customerObj)
      }
      
      if (customerObj) {
        const parent = parentOrganizations.value.find(
          p => p.alias_id === customerObj.parent
        )
        // console.log("found parent:", parent)
        
        if (parent) {
          selectedParent.value = parent
          selectedCustomer.value = customerObj
          // console.log("selections set successfully")
        } 
        // else {
        //   console.log("parent not found for customer")
        // }
      }
    }
  }

  // Try immediately
  trySetSelections()
  
  // If data not loaded yet, watch for changes
  if (!customers.value.length || !parentOrganizations.value.length) {
    // console.log("data not loaded yet - setting up watchers")
    const unwatchCustomers = watch(customers, () => {
      if (customers.value.length) {
        trySetSelections()
        unwatchCustomers()
      }
    })
    
    const unwatchParents = watch(parentOrganizations, () => {
      if (parentOrganizations.value.length) {
        trySetSelections()
        unwatchParents()
      }
    })
  }
}, { immediate: true, deep: true })

// watch(() => props.modelValue, (newVal) => {
//   console.log("watch triggered - newVal:", newVal)
//   console.log("current customers:", customers.value)
//   console.log("current parentOrganizations:", parentOrganizations.value)

//   if (!newVal) {
//     resetSelections()
//     return
//   }

//   if (customers.value.length && parentOrganizations.value.length) {
//     let customerObj = null
    
//     if (typeof newVal === 'string') {
//       customerObj = customers.value.find(c => c.alias_id === newVal)
//       console.log("found customer by string:", customerObj)
//     } else if (newVal && typeof newVal === 'object') {
//       customerObj = newVal
//       console.log("received customer object:", customerObj)
//     }
    
//     if (customerObj) {
//       const parent = parentOrganizations.value.find(
//         p => p.alias_id === customerObj.parent
//       )
//       console.log("found parent:", parent)
      
//       if (selectedParent.value?.alias_id !== parent?.alias_id) {
//         console.log("setting parent to:", parent)
//         selectedParent.value = parent
//       }
//       if (selectedCustomer.value?.alias_id !== customerObj.alias_id) {
//         console.log("setting customer to:", customerObj)
//         selectedCustomer.value = customerObj
//       }
//     } else {
//       console.log("customer object not found")
//     }
//   } else {
//     console.log("customers or parents not loaded yet")
//   }
// }, { immediate: true, deep: true })
// watch(() => props.modelValue, (newVal) => {
//   console.log("watch triggered - newVal:", newVal)
//   console.log("current customers:", customers.value)
//   console.log("current parentOrganizations:", parentOrganizations.value)

//   if (!newVal) {
//     resetSelections()
//     return
//   }

//   // If we have customers loaded
//   if (customers.value.length) {
//     let customerObj = null
    
//     if (typeof newVal === 'string') {
//       // Find by alias_id
//       customerObj = customers.value.find(c => c.alias_id === newVal)
//     } else if (newVal && typeof newVal === 'object') {
//       // Already an object
//       customerObj = newVal
//     }
    
//     if (customerObj) {
//       // Find parent organization
//       const parent = parentOrganizations.value.find(
//         p => p.alias_id === customerObj.parent
//       )
      
//       // Only update if different to avoid infinite loops
//       if (selectedParent.value?.alias_id !== parent?.alias_id) {
//         selectedParent.value = parent
//       }
//       if (selectedCustomer.value?.alias_id !== customerObj.alias_id) {
//         selectedCustomer.value = customerObj
//       }
//     }
//   }
// }, { immediate: true, deep: true })

// watch(() => props.modelValue, (newVal) => {
//   if (typeof newVal === 'string') {
//     // If passed a string (alias_id), find the corresponding customer
//     const foundCustomer = customers.value.find(c => c.alias_id === newVal)
//     if (foundCustomer) {
//       selectedParent.value = parentOrganizations.value.find(
//         p => p.alias_id === foundCustomer.parent
//       )
//       selectedCustomer.value = foundCustomer
//     }
//   } else if (newVal && typeof newVal === 'object') {
//     // If passed a customer object
//     selectedParent.value = parentOrganizations.value.find(
//       p => p.alias_id === newVal.parent
//     )
//     selectedCustomer.value = newVal
//   }
// }, { immediate: true })

watch(() => branchStore.selectedBranch, loadCustomers, { immediate: true })
</script>

<style scoped>
.customer-selector-container {
  display: flex;
  gap: 20px;
  width: 100%;
}

.dropdown-section {
  flex: 1;
  min-width: 0;
}

.dropdown-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #333;
}

.form-select {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background-color: white;
}

.form-select:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.is-invalid {
  border-color: #dc3545;
}

.invalid-feedback {
  color: #dc3545;
  font-size: 0.875em;
  margin-top: 4px;
}

/* Stacked layout option */
.customer-selector-container.stacked {
  flex-direction: column;
  gap: 12px;
}
</style>