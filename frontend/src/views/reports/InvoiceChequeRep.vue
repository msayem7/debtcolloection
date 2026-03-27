<template>
   <div class="container mt-4">
    <div class="card">
      <div class="card-header">
        <h3 class="mb-0">Credit Invoice Report</h3>
      </div>
      <div class="card-body">
        <div class="row mb-3 g-3">            
          <div class="col-md-3">
            <label class="form-label">From Sales Date</label>
            <input type="date" class="form-control" v-model="filters.date_from">
          </div>
          <div class="col-md-3">
            <label class="form-label">To Sales Date</label>
            <input type="date" class="form-control" v-model="filters.date_to">
          </div>
          <div class="col-md-3">
            <label class="form-label">TotalDue Amount Range</label>
            <div class="input-group">
              <input type="number" class="form-control" placeholder="Min" v-model="filters.min_amount">
              <input type="number" class="form-control" placeholder="Max" v-model="filters.max_amount">
            </div>
          </div>
        </div>
        <div class="filters">
          <div class="d-flex gap-2 mb-3">
            <button class="btn btn-primary" @click="loadReport">
              <i class="bi bi-search"></i> Generate
            </button>
            <button class="btn btn-success" @click="exportExcel">
              <i class="bi bi-file-earmark-excel"></i> Excel
            </button>
            <button class="btn btn-danger" @click="exportPDF">
              <i class="bi bi-file-earmark-pdf"></i> PDF
            </button>
          </div>
  
          <div v-if="loading" class="text-center">
            <div class="spinner-border text-primary" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </div>
        </div>
        <div v-if="reportData.length" class="table-responsive">
          <table class="table table-striped table-hover">
            <thead>
              <tr>
                <th>Shop Name</th>
                <th>GRN</th>
                <th>Sale Date</th>
                <th>Grace</th>
                <th>Sale Amount</th>
                <th>Return</th>
                <th>Net Sale</th>
                <th>Received</th>
                <th>Cleared</th>
                <th>Claims</th>
                <th>Total Due</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in reportData" :key="index">
                <td>{{ item.branch__name }}</td>
                <td>{{ item.invoice_no }}</td>
                <td>{{ formatDate(item.transaction_date) }}</td>
                <td>{{ item.payment_grace_days }}</td>
                <td>{{ formatNumber(item.due_amount) }}</td>
                <td>{{ formatNumber(item.sales_return) }}</td>
                <td>{{ formatNumber(item.net_sales) }}</td>
                <td>{{ formatNumber(item.received) }}</td>
                <td>{{ formatNumber(item.cleared) }}</td>
                <td>{{ formatNumber(item.total_claim) }}</td>
                <td :class="{ 'text-danger': item.total_due < 0 }">
                  {{ formatNumber(item.total_due)}}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'  // Make sure to import ref
import axios from '@/plugins/axios'
import { useBranchStore } from '@/stores/branchStore'
import { formatDate, formatNumber } from '@/utils/ezFormatter'

const reportData = ref([])
const loading = ref(false)
const branchStore = useBranchStore()

const filters = ref({
  date_from: '',
  date_to: '',
  min_amount: '',
  max_amount: ''
});

const loadReport = async () => {
  try {
    const params = {
      branch: branchStore.selectedBranch,
      date_from: filters.value.date_from,
      date_to: filters.value.date_to,
      min_amount: filters.value.min_amount,
      max_amount: filters.value.max_amount
    }
    const { data } = await axios.get('/v1/chq/reports/ci-vs-cheque', { params })
    //console.log('Report Data:', data)
    reportData.value = data
  } catch (error) {
    console.error('Error loading report:', error)
  }
};

const exportExcel = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('No authentication token found')
    }

    const baseURL = axios.defaults.baseURL || 'http://localhost:8000'
    
    const params = new URLSearchParams({
      ...filters.value,
      branch: branchStore.selectedBranch
    }).toString()

    // Use axios directly with proper headers
    const response = await axios({
      url: `/v1/chq/reports/ci-vs-cheque/export_excel/?${params}`,
      method: 'GET',
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    // Create and trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'invoice_report.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

  } catch (error) {
    console.error('Export error:', error)
    alert('Failed to export Excel file: ' + error.response?.data?.detail || error.message)
  }
}

const exportPDF = async () => {
  try {
    const token = localStorage.getItem('token')
    if (!token) {
      throw new Error('No authentication token found')
    }

    const baseURL = axios.defaults.baseURL || 'http://localhost:8000'
    
    const params = new URLSearchParams({
      ...filters.value,
      branch: branchStore.selectedBranch
    }).toString()

    // Use axios directly with proper headers
    const response = await axios({
      url: `/v1/chq/reports/ci-vs-cheque/export_pdf/?${params}`,
      method: 'GET',
      responseType: 'blob',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })

    // Create and trigger download
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'invoice_report.pdf')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

  } catch (error) {
    console.error('Export error:', error)
    alert('Failed to export PDF file: ' + error.response?.data?.detail || error.message)
  }
}


</script>