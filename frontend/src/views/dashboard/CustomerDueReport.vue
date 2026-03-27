<!-- ParentDueReport.vue -->
<template>
  <div class="due-report-container">
    <div class="card">
      <div class="card-header bg-primary text-white">
        Customer Due Report
        <div class="float-end">
          <input type="date" v-model="endDate" class="form-control form-control-sm">
        </div>
      </div>
      
      <div class="card-body">
        <table class="table table-hover table-sm">
          <thead>
            <tr>
              <th @click="sortBy('parent_name')">Parent Customer 
                <i class="bi" :class="sortIcon('parent_name')"></i>
              </th>
              <th @click="sortBy('matured_net_sales')">Matured Due
                <i class="bi" :class="sortIcon('matured_net_sales')"></i>
              </th>
              <th @click="sortBy('immature_net_sales')">Immature Due
                <i class="bi" :class="sortIcon('immature_net_sales')"></i>
              </th>
              <th @click="sortBy('due')">Total Due
                <i class="bi" :class="sortIcon('due')"></i>
              </th>
            </tr>
          </thead>
          <tbody>
            <template v-for="parent in sortedParents" :key="parent.alias_id">
              <!-- Parent Row -->
              <tr class="parent-row">
                <td>
                  <a href="#" @click.stop="toggleExpand(parent.alias_id)">
                    <i class="bi" :class="parent.expanded ? 'bi-caret-down-fill' : 'bi-caret-right-fill'"></i>
                    {{ parent.parent_name }}
                  </a>
                </td>
                <td>{{ formatNumber(parent.matured_net_sales) }}</td>
                <td>{{ formatNumber(parent.immature_net_sales) }}</td>
                <td>{{ formatNumber(parent.due) }}</td>
              </tr>

              <!-- Child Rows -->
              <div v-if="parent.expanded">
                <tr 
                  v-for="child in parent.customerwise_breakdown.customers"
                  :key="child.customer_alias_id"
                  class="child-row"
                >
                  <td class="ps-4">
                    <i class="bi bi-person-circle me-2"></i>
                    {{ child.customer_name }}
                  </td>
                  <td>{{ formatNumber(child.matured_net_sales) }}</td>
                  <td>{{ formatNumber(child.immature_net_sales) }}</td>
                  <td>{{ formatNumber(child.due) }}</td>
                </tr>              
              </div>
            </template>
          </tbody>
        </table>        
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useBranchStore } from '@/stores/branchStore'
import { formatNumber } from '@/utils/ezFormatter'
import { useNotificationStore } from '@/stores/notificationStore'
import axios from '@/plugins/axios' // Import your Axios instance

// eslint-disable-next-line
const props = defineProps({
  branchId: {
    type: Number,
    required: true
  }
})

const notificationStore = useNotificationStore()
const endDate = ref(new Date().toISOString().split('T')[0])
const parents = ref([])
const sortKey = ref('due')
const sortOrder = ref(-1) // 1 for asc, -1 for desc

const sortedParents = computed(() => {
  return [...parents.value].sort((a, b) => {
    if(a[sortKey.value] < b[sortKey.value]) return sortOrder.value
    if(a[sortKey.value] > b[sortKey.value]) return -sortOrder.value
    return 0
  })
})

const sortBy = (key) => {
  if(sortKey.value === key) {
    sortOrder.value *= -1
  } else {
    sortKey.value = key
    sortOrder.value = -1
  }
}

const sortIcon = (key) => {
  if(sortKey.value !== key) return 'bi-filter'
  return sortOrder.value === 1 ? 'bi-sort-up' : 'bi-sort-down'
}

const toggleExpand = (aliasId) => {
  parents.value = parents.value.map(p => ({
    ...p,
    expanded: p.alias_id === aliasId ? !p.expanded : p.expanded
  }))
  //console.log('Toggled expand for:', aliasId)

}

const fetchData = async () => {
  try {
    const response = await axios.get('/v1/chq/parent-customer-due/', {
      params: {
        branch_id: props.branchId,
        end_date: endDate.value
      }
    });

    parents.value = response.data.map(parent => {
      // Ensure customerwise_breakdown is properly structured
      const breakdown = typeof parent.customerwise_breakdown === 'string' 
        ? JSON.parse(parent.customerwise_breakdown)
        : parent.customerwise_breakdown || {};

      return {
        ...parent,
        expanded: false,
        customerwise_breakdown: {
          customers: breakdown.customers?.map(child => ({
            customer_alias_id: child.customer_alias_id,
            customer_name: child.customer_name,
            matured_net_sales: Number(child.matured_net_sales) || 0,
            immature_net_sales: Number(child.immature_net_sales) || 0,
            due: Number(child.due) || 0
          })) || []
        }
      };
    });

    console.log('Processed parent data:', parents.value);
  } catch (error) {
    notificationStore.showError(error.message);
  }
};

// const fetchData = async () => {
//   try {
//     const response = await axios.get('/v1/chq/parent-customer-due/', {
//       params: {
//         branch_id: props.branchId,
//         end_date: endDate.value
//       }
//     })
//     //console.log('Response:', response.data)
//     // Initialize expanded property for each parent
//     parents.value = response.data.map(parent => ({
//       ...parent,
//       expanded: false // Add this line
//     }))
    
//     for (const parent of parents.value) {
//       // Parse customerwise_breakdown if it is a string
//       if (typeof parent.customerwise_breakdown === 'string') {
//         parent.customerwise_breakdown = JSON.parse(parent.customerwise_breakdown);
//       }
      
//       // Ensure customerwise_breakdown and customers are initialized
//       parent.customerwise_breakdown = parent.customerwise_breakdown || {};
//       parent.customerwise_breakdown.customers = parent.customerwise_breakdown.customers || [];
      
//       // Iterate through the customers and set default values
//       parent.customerwise_breakdown.customers.forEach(customer => {
//         customer.matured_net_sales = customer.matured_net_sales || 0;
//         customer.immature_net_sales = customer.immature_net_sales || 0;
//         customer.due = customer.due || 0;
        
//         console.log("Child data of ", parent.customer_name, ": ", customer.matured_net_sales, customer.immature_net_sales, customer.due);
//       });
//     }

//     //console.log('Fetched Parents.value :', parents.value )
//   } catch (error) {
//     notificationStore.showError(error.message)
//   }
// }

// const fetchData = async () => {
//   try {
//     const response = await fetch(
//       `/v1/chq/parent-customer-due/?branch_id=${props.branchId}&end_date=${endDate.value}`
//     )
    
//     if(!response.ok) throw new Error('Failed to fetch data')
    
//     parents.value = await response.json()
//   } catch (error) {
//     notificationStore.showError(error.message)
//   }
// }

onMounted(fetchData)
</script>

<style scoped>
.due-report-container {
  max-height: 400px;
  overflow-y: auto;
}

.table {
  font-size: 0.9rem;
}

th {
  cursor: pointer;
  background-color: #f8f9fa;
}

.bi {
  font-size: 0.8rem;
}

a {
  text-decoration: none;
  color: inherit;
}

.ps-4 {
  padding-left: 2rem !important;
}

/* .child-row {
  background-color: #f8f9fa;
}

.child-row td {
  border-top: none;
  padding-top: 0.25rem;
  padding-bottom: 0.25rem;
}

.child-row:last-child td {
  border-bottom: 1px solid #dee2e6;
}
 */



/*  */
.parent-row {
  cursor: pointer;
  transition: background-color 0.2s;
}

.parent-row:hover {
  background-color: #f8f9fa;
}

.child-row td {
  border-top: none;
  padding: 0.25rem 1rem;
  background-color: #fafafa;
  font-size: 0.85em;
}

.child-row:last-child td {
  border-bottom: 2px solid #eee;
}

.ps-4 {
  padding-left: 2.5rem !important;
}

.bi-caret-right-fill, .bi-caret-down-fill {
  transition: transform 0.2s;
}

.bi-person-circle {
  color: #6c757d;
  font-size: 0.9em;
}
</style>