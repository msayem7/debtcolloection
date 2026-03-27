<template>
  <div class="container mt-4">
    <div class="card">
      <div class="card-header d-flex justify-content-between align-items-center flex-wrap">
        <h5>Customer Due</h5>
        <div class="d-flex align-items-center header-controls">
          <input
            type="date"
            v-model="reportDate"
            class="form-control date-input"
            @change="loadReport"
          >
          <button
            class="btn btn-primary excel-export-btn ms-2"
            @click="exportToExcel"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
            Export Excel
          </button>
        </div>
      </div>

      <div class="card-body">
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>

        <template v-else>
          <div class="table-responsive">
            <table class="table table-bordered table-hover">
              <thead class="table-light">
                <tr>
                  <th @click="sortBy('name')" class="sortable">
                    Customer
                    <i v-if="sortColumn === 'name'"
                       :class="['bi', sortDirection === 'asc' ? 'bi-sort-alpha-down' : 'bi-sort-alpha-up']">
                    </i>
                    <i v-else class="bi bi-sort-alpha-down-alt sort-icon-placeholder"></i>
                  </th>
                  <th @click="sortBy('matured_due')" class="text-end sortable">
                    Matured
                    <i v-if="sortColumn === 'matured_due'"
                       :class="['bi', sortDirection === 'asc' ? 'bi-sort-numeric-down' : 'bi-sort-numeric-up']">
                    </i>
                    <i v-else class="bi bi-sort-numeric-down-alt sort-icon-placeholder"></i>
                  </th>
                  <th @click="sortBy('immature_due')" class="text-end sortable">
                    Immature
                    <i v-if="sortColumn === 'immature_due'"
                       :class="['bi', sortDirection === 'asc' ? 'bi-sort-numeric-down' : 'bi-sort-numeric-up']">
                    </i>
                    <i v-else class="bi bi-sort-numeric-down-alt sort-icon-placeholder"></i>
                  </th>
                  <th @click="sortBy('total_due')" class="text-end sortable">
                    Total
                    <i v-if="sortColumn === 'total_due'"
                       :class="['bi', sortDirection === 'asc' ? 'bi-sort-numeric-down' : 'bi-sort-numeric-up']">
                    </i>
                    <i v-else class="bi bi-sort-numeric-down-alt sort-icon-placeholder"></i>
                  </th>
                </tr>
              </thead>
              <tbody>
                <template v-for="parent in sortedAndFilteredParents" :key="parent.alias_id"> <tr
                    class="parent-row"
                    :class="{ 'cursor-pointer': parent.children.length > 0 }"
                    @click="toggleParent(parent.alias_id)"
                  >
                    <td>
                      <div class="d-flex align-items-center">
                        <span v-if="parent.children.length > 0" class="me-2">
                          <i
                            class="bi"
                            :class="expandedParents.includes(parent.alias_id) ? 'bi-dash-square' : 'bi-plus-square'"
                          >
                          </i>
                        </span>
                        <router-link
                          :to="`/customers/${parent.alias_id}`"
                          class="text-decoration-none"
                          @click.stop
                        >
                          <strong>{{ parent.name }}</strong>
                        </router-link>
                      </div>
                    </td>
                    <td class="text-end">
                      {{ formatNumber(parent.matured_due) }}
                    </td>
                    <td class="text-end">
                      {{ formatNumber(parent.immature_due) }}
                    </td>
                    <td class="text-end">
                      {{ formatNumber(parent.total_due) }}
                    </td>
                  </tr>
                  <template v-if="expandedParents.includes(parent.alias_id)">
                    <tr
                      v-for="child in parent.children.filter(c => c.total_due > 0)"
                      :key="child.alias_id"
                      class="child-row"
                    >
                      <td class="ps-5">
                        <router-link
                          :to="`/customers/${child.alias_id}`"
                          class="text-decoration-none"
                        >
                          <i class="bi bi-arrow-return-right me-2"></i>
                          {{ child.name }}
                        </router-link>
                      </td>
                      <td class="text-end">
                        {{ formatNumber(child.matured_due) }}
                      </td>
                      <td class="text-end">
                        {{ formatNumber(child.immature_due) }}
                      </td>
                      <td class="text-end">
                        {{ formatNumber(child.total_due) }}
                      </td>
                    </tr>
                  </template>
                </template>
                <tr class="table-secondary">
                  <td><strong>Grand Total</strong></td>
                  <td class="text-end">
                    <strong>{{ formatNumber(reportData.grand_totals.matured_due) }}</strong>
                  </td>
                  <td class="text-end">
                    <strong>{{ formatNumber(reportData.grand_totals.immature_due) }}</strong>
                  </td>
                  <td class="text-end">
                    <strong>{{ formatNumber(reportData.grand_totals.total_due) }}</strong>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import axios from '@/plugins/axios'
import { formatDate, formatNumber } from '@/utils/ezFormatter'
import { useNotificationStore } from '@/stores/notificationStore'
import { useBranchStore } from '@/stores/branchStore'

const notificationStore = useNotificationStore()
const branchStore = useBranchStore()

const reportDate = ref(new Date().toISOString().split('T')[0])
const loading = ref(false)
const reportData = ref({
  report_date: '',
  data: [],
  grand_totals: {
    matured_due: 0,
    immature_due: 0,
    total_due: 0
  }
})
const expandedParents = ref([])

// --- Sorting State ---
const sortColumn = ref('name') // Default sort column
const sortDirection = ref('asc') // Default sort direction

// Computed property to get current branch name
const currentBranchName = computed(() => {
  if (!branchStore.selectedBranch) return 'All Branches'
  const branch = branchStore.branches.find(b => b.alias_id === branchStore.selectedBranch)
  return branch ? branch.name : 'Selected Branch'
})

// Filter parents with total_due > 0 or with children having due amounts
const filteredParents = computed(() => {
  return reportData.value.data.filter(parent => {
    // Show parent if it has any due amount
    if (parent.total_due > 0) return true

    // Or if any of its children have due amounts
    return parent.children.some(child => child.total_due > 0)
  })
})

// --- New Computed Property for Sorted and Filtered Parents ---
const sortedAndFilteredParents = computed(() => {
  const parents = [...filteredParents.value]; // Create a shallow copy to avoid mutating original array
  if (!sortColumn.value) {
    return parents; // No sorting if no column is selected
  }

  return parents.sort((a, b) => {
    let valA = a[sortColumn.value];
    let valB = b[sortColumn.value];

    // Handle string comparison (case-insensitive for names)
    if (typeof valA === 'string' && typeof valB === 'string') {
      valA = valA.toLowerCase();
      valB = valB.toLowerCase();
    }

    if (valA < valB) return sortDirection.value === 'asc' ? -1 : 1;
    if (valA > valB) return sortDirection.value === 'asc' ? 1 : -1;
    return 0; // Values are equal
  });
});


const toggleParent = (parentId) => {
  const index = expandedParents.value.indexOf(parentId)
  if (index === -1) {
    expandedParents.value.push(parentId)
  } else {
    expandedParents.value.splice(index, 1)
  }
}

// --- New Sorting Method ---
const sortBy = (column) => {
  if (sortColumn.value === column) {
    // If clicking the same column, toggle direction
    sortDirection.value = sortDirection.value === 'asc' ? 'desc' : 'asc';
  } else {
    // If clicking a new column, set it and default to ascending
    sortColumn.value = column;
    sortDirection.value = 'asc';
  }
};


const loadReport = async () => {
  try {
    loading.value = true
    expandedParents.value = [] // Reset expanded parents when loading new data
    const params = {
      date: reportDate.value
    }

    if (branchStore.selectedBranch) {
      params.branch = branchStore.selectedBranch
    }

    const response = await axios.get('/v1/chq/parent-customer-due-report/', {
      params
    })
    reportData.value = response.data
  } catch (error) {
    notificationStore.showError('Failed to load due report')
    console.error('Error loading report:', error)
  } finally {
    loading.value = false
  }
}

const exportToExcel = async () => {
  try {
    loading.value = true
    const params = {
      date: reportDate.value
    }

    if (branchStore.selectedBranch) {
      params.branch = branchStore.selectedBranch
    }

    const response = await axios.get('/v1/chq/parent-customer-due-report/export/', {
      params,
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `customer_due_report_${reportDate.value}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error) {
    notificationStore.showError('Failed to export report')
    console.error('Export error:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadReport()
})
</script>