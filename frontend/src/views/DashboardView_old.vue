<template>
  <div class="dashboard-container">
    <div class="col-4">      
      <div class="row">
        <div class="col-12">
          <div class="card">
            <div class="card-header d-flex justify-content-between align-items-center">
              <h5 class="mb-0">Due Details</h5>
              <div>
                Due: {{ formatNumber(totalDue) }}  
              </div>              
              <div>
                <input 
                  type="date" 
                  v-model="cutoffDate" 
                  @change="loadData" 
                  class="form-control"
                >
              </div>
              <div>
                <select v-model="sortBy" @change="loadData" class="form-select form-select-sm w-auto">
                  <option value="due">Sort by Due Amount</option>
                  <option value="name">Sort by Name</option>
                </select>
              </div>
            </div>
            <div class="card-body">
              <div class="table-responsive">
                <table class="table table-hover">
                  <thead>
                    <tr>
                      <th>Parent Organization</th>
                      <!-- <th class="text-end">Net Sales</th>
                      <th class="text-end">Received</th> -->
                      <th class="text-end">Due Amount</th>
                      <th class="text-end">Customers</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="org in parentOrgs" :key="org.parent_id" @click="viewParentDetails(org.parent_id)" class="clickable-row">
                      <td>{{ org.parent_org_name }}</td>
                      <!-- <td class="text-end">{{ formatNumber(org.net_sales) }}</td>
                      <td class="text-end">{{ formatNumber(org.received) }}</td> -->
                      <td class="text-end">
                        <span :class="{'text-danger': org.due > 0, 'text-success': org.due <= 0}">
                          {{ formatNumber(org.due) }}
                        </span>
                      </td>
                      <td class="text-end">{{ org.customer_count }}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>    
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useBranchStore } from '@/stores/branchStore'
import axios from '@/plugins/axios'
import { formatDate, formatNumber } from '@/utils/ezFormatter'
import { useRouter } from 'vue-router'

const branchStore = useBranchStore()
const router = useRouter()

const parentOrgs = ref([])
const cutoffDate = ref(new Date().toISOString().split('T')[0])
const sortBy = ref('due')
const isLoading = ref(false)

const totalDue = computed(() => {
  return parentOrgs.value.reduce((sum, org) => sum + parseFloat(org.due), 0)
})

onMounted(() => {
  if (branchStore.selectedBranch) {
    loadData()
  }
})

const loadData = async () => {
  if (!branchStore.selectedBranch) return
  
  try {
    isLoading.value = true
    const response = await axios.get('v1/chq/ParentDueReportView/', {
      params: {
        branch: branchStore.selectedBranch,
        cutoff_date: cutoffDate.value,
        sort_by: sortBy.value
      }
    })
    
    parentOrgs.value = response.data.data || []
  } catch (error) {
    console.error('Failed to load parent due report:', error)
    parentOrgs.value = []
  } finally {
    isLoading.value = false
  }
}

const viewParentDetails = (parentId) => {
  // router.push({
  //   name: 'ParentCustomerList',
  //   query: { 
  //     parent: parentId,
  //     branch: branchStore.selectedBranch
  //   }
  // })
}
</script>

<style scoped>
.dashboard-container {
  padding: 20px;
}

.summary-card {
  height: 100%;
  transition: transform 0.2s;
}

.summary-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.clickable-row {
  cursor: pointer;
}

.clickable-row:hover {
  background-color: #f8f9fa;
}

.table-responsive {
  max-height: 500px;
  overflow-y: auto;
}
</style>