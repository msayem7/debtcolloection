<template>
  <div class="received-claim-report-container">
    <div class="card">
      <div class="card-header bg-primary text-white">
        <h5 class="mb-0">Received and Claim Report</h5>
      </div>

      <div class="card-body">
        <!-- Filter Section -->
        <div class="row g-3 mb-4">
          <!-- Report Type Selection -->
          <div class="col-md-3">
            <label class="form-label">Report Type</label>
            <div class="d-flex gap-3 mt-1">
              <div class="form-check">
                <input class="form-check-input" type="radio" v-model="reportType" value="receive" id="typeReceive" @change="onReportTypeChange">
                <label class="form-check-label" for="typeReceive">Receive</label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="radio" v-model="reportType" value="claim" id="typeClaim" @change="onReportTypeChange">
                <label class="form-check-label" for="typeClaim">Claim</label>
              </div>
            </div>
          </div>

          <!-- Parent Organization -->
          <div class="col-md-3">
            <label class="form-label">Parent Organization</label>
            <select v-model="filters.parentCustomer" class="form-select" @change="onParentChange">
              <option value="">All Parent</option>
              <option v-for="p in parentOrganizations" :key="p.alias_id" :value="p.alias_id">
                {{ p.name }}
              </option>
            </select>
          </div>

          <!-- Instrument List -->
          <div class="col-md-3">
            <label class="form-label">Instrument</label>
            <select v-model="filters.instrumentId" class="form-select" @change="onInstrumentChange">
              <option value="">All Instrument</option>
              <option v-for="ins in instruments" :key="ins.id" :value="ins.id">
                {{ ins.instrument_name }}
              </option>
            </select>
          </div>

          <!-- Date Range -->
          <div class="col-md-3">
            <label class="form-label">From Date</label>
            <input type="date" v-model="filters.dateFrom" class="form-control">
          </div>
          <div class="col-md-3">
            <label class="form-label">To Date</label>
            <input type="date" v-model="filters.dateTo" class="form-control">
          </div>

          <!-- Date Mode (Claim only) -->
          <div v-if="reportType === 'claim'" class="col-md-3">
            <label class="form-label">Date Filter Mode</label>
            <div class="d-flex gap-3 mt-1">
              <div class="form-check">
                <input class="form-check-input" type="radio" v-model="filters.dateMode" value="received_date" id="modeReceivedDate">
                <label class="form-check-label" for="modeReceivedDate">Received Date</label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="radio" v-model="filters.dateMode" value="refund_date" id="modeRefundDate">
                <label class="form-check-label" for="modeRefundDate">Refund Date</label>
              </div>
            </div>
          </div>

          <!-- Refund Status (Claim only) -->
          <div v-if="reportType === 'claim'" class="col-md-3">
            <label class="form-label">Refund Status</label>
            <select v-model="filters.refundStatus" class="form-select">
              <option value="all">All</option>
              <option value="refunded">Refunded</option>
              <option value="pending">Pending</option>
            </select>
          </div>

          <!-- Checkboxes -->
          <div class="col-md-3 d-flex align-items-end gap-3 pb-1">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="filters.hasComments" id="chkComments">
              <label class="form-check-label" for="chkComments">
                {{ reportType === 'receive' ? 'Have comments only' : 'Have comments only' }}
              </label>
            </div>
          </div>

          <!-- Action Buttons -->
          <div class="col-md-12 d-flex justify-content-between align-items-end">
            <div>
              <button class="btn btn-primary me-2" @click="loadReport()" :disabled="loading">
                <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span>
                Generate Report
              </button>
            </div>
            <div>
              <button class="btn btn-outline-danger me-2" @click="exportPDF" :disabled="loading || !hasData">
                <i class="bi bi-file-earmark-pdf"></i> PDF
              </button>
              <button class="btn btn-outline-success me-2" @click="exportExcel" :disabled="loading || !hasData">
                <i class="bi bi-file-earmark-excel"></i> Excel
              </button>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <!-- Report Table (paginated) -->
        <div v-if="hasData" class="table-responsive mt-3">
          <!-- Receive Report Table -->
          <table v-if="reportType === 'receive'" class="table table-bordered table-hover table-sm">
            <thead class="table-dark">
              <tr>
                <th>Sl No</th>
                <th>Payment ID</th>
                <th>Received Date</th>
                <th>Organization Name</th>
                <th>Instrument Name</th>
                <th>Instrument Number</th>
                <th class="text-end">Amount</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in reportData" :key="idx">
                <td>{{ row.sl_no }}</td>
                <td>{{ row.payment_id || '-' }}</td>
                <td>{{ formatDate(row.received_date) }}</td>
                <td>{{ row.organization_name || '-' }}</td>
                <td>{{ row.instrument_name || '-' }}</td>
                <td>{{ row.instrument_number || '-' }}</td>
                <td class="text-end">{{ formatNumber(row.amount) }}</td>
                <td>{{ row.remarks || '-' }}</td>
              </tr>
            </tbody>
            <tfoot class="table-light fw-bold">
              <tr>
                <td colspan="6" class="text-end">Total:</td>
                <td class="text-end">{{ formatNumber(totals.total_amount) }}</td>
                <td></td>
              </tr>
            </tfoot>
          </table>

          <!-- Claim Report Table -->
          <table v-if="reportType === 'claim'" class="table table-bordered table-hover table-sm">
            <thead class="table-dark">
              <tr>
                <th>Sl No</th>
                <th>Claim ID</th>
                <th>Claim Date</th>
                <th>Organization Name</th>
                <th>Instrument Name</th>
                <th>Instrument Number</th>
                <th class="text-end">Amount</th>
                <th>Refund</th>
                <th>Refund Date</th>
                <th class="text-end">Refund Amount</th>
                <th class="text-end">Remaining Amount</th>
                <th>Remarks</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in reportData" :key="idx">
                <td>{{ row.sl_no }}</td>
                <td>{{ row.claim_id || '-' }}</td>
                <td>{{ formatDate(row.claim_date) }}</td>
                <td>{{ row.organization_name || '-' }}</td>
                <td>{{ row.instrument_name || '-' }}</td>
                <td>{{ row.instrument_number || '-' }}</td>
                <td class="text-end">{{ formatNumber(row.amount) }}</td>
                <td>{{ row.refund_amount && Number(row.refund_amount) > 0 ? 'Yes' : 'No' }}</td>
                <td>{{ row.refund_date ? formatDate(row.refund_date) : '-' }}</td>
                <td class="text-end">{{ formatNumber(row.refund_amount) }}</td>
                <td class="text-end">{{ formatNumber(row.remaining_amount) }}</td>
                <td>{{ row.remarks || '-' }}</td>
              </tr>
            </tbody>
            <tfoot class="table-light fw-bold">
              <tr>
                <td colspan="6" class="text-end">Total:</td>
                <td class="text-end">{{ formatNumber(totals.total_amount) }}</td>
                <td></td>
                <td></td>
                <td class="text-end">{{ formatNumber(totals.total_refund) }}</td>
                <td class="text-end">{{ formatNumber(totals.total_remaining) }}</td>
                <td></td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Standard Pagination -->
        <div v-if="hasData && totalPages > 1" class="d-flex justify-content-between align-items-center mt-3">
          <div class="d-flex align-items-center gap-2">
            <small>Page</small>
<input type="text" class="form-control form-control-sm" style="width: 50px;"
       v-model.number="currentPage" min="1" :max="totalPages"
       @keyup.enter="goToPage(currentPage)">
            <small>of {{ totalPages }} ({{ totalCount }} records)</small>
          </div>
          <div class="d-flex align-items-center gap-2">
            <small>Records per page:</small>
            <select class="form-select form-select-sm" style="width: 80px;" v-model.number="pageSize" @change="loadReport(1)">
              <option :value="25">25</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
              <option :value="200">200</option>
            </select>
            <button class="btn btn-sm btn-outline-primary me-1" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
              &laquo; Previous
            </button>
            <button class="btn btn-sm btn-outline-primary" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
              Next &raquo;
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import axios from '@/plugins/axios'
import { formatDate, formatNumber } from '@/utils/ezFormatter'
import { useBranchStore } from '@/stores/branchStore'
import { useNotificationStore } from '@/stores/notificationStore'

const branchStore = useBranchStore()
const notificationStore = useNotificationStore()

// State
const loading = ref(false)
const error = ref(null)
const reportData = ref([])
const totals = ref({})
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const pageSize = ref(50)
const parentOrganizations = ref([])
const instruments = ref([])

const reportType = ref('receive')

const filters = reactive({
  parentCustomer: '',
  instrumentId: '',
  dateFrom: '',
  dateTo: '',
  dateMode: 'received_date',
  refundStatus: 'all',
  hasComments: false,
})

// Computed
const hasData = computed(() => reportData.value.length > 0)

// Methods
const onReportTypeChange = () => {
  filters.instrumentId = ''
  filters.dateMode = 'received_date'
  filters.refundStatus = 'all'
  filters.hasComments = false
  reportData.value = []
  totals.value = {}
  currentPage.value = 1
  totalPages.value = 1
  totalCount.value = 0
  loadInstruments()
}

const onParentChange = () => {
  // no child customer loading needed, just filter
}

const onInstrumentChange = () => {
  // handled in loadReport
}

const loadParentOrganizations = async () => {
  if (!branchStore.selectedBranch) return
  try {
    const res = await axios.get('/v1/chq/customers/', {
      params: { branch: branchStore.selectedBranch, is_active: true, is_parent: true }
    })
    parentOrganizations.value = res.data
  } catch (err) {
    console.error('Error loading parent organizations:', err)
  }
}

const loadInstruments = async () => {
  if (!branchStore.selectedBranch) return
  try {
    const params = { branch: branchStore.selectedBranch, is_active: true }
    if (reportType.value === 'claim') {
      params.instrument_type_serial_no = 3
    }
    const res = await axios.get('/v1/chq/payment-instruments/', { params })
    instruments.value = res.data
  } catch (err) {
    console.error('Error loading instruments:', err)
    instruments.value = []
  }
}

const loadReport = async (page = 1) => {
  if (!branchStore.selectedBranch) {
    error.value = 'Please select a organization first.'
    return
  }

  loading.value = true
  error.value = null
  currentPage.value = page

  try {
    const params = {
      branch: branchStore.selectedBranch,
      report_type: reportType.value,
      page: currentPage.value,
      page_size: pageSize.value,
    }

    if (filters.parentCustomer) params.parent_customer = filters.parentCustomer
    if (filters.instrumentId) params.instrument_ids = String(filters.instrumentId)
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo
    if (reportType.value === 'claim') {
      params.date_mode = filters.dateMode
      params.refund_status = filters.refundStatus
    }
    if (filters.hasComments) params.has_comments = 'true'

    const response = await axios.get('/v1/chq/reports/received-claim/', { params })

    reportData.value = response.data.data
    totalCount.value = response.data.total_count
    totalPages.value = response.data.total_pages
    totals.value = response.data.totals
  } catch (err) {
    console.error('Error loading report:', err)
    error.value = err.response?.data?.detail || err.response?.data?.branch || 'Failed to load report'
    notificationStore.showError(error.value)
  } finally {
    loading.value = false
  }
}

const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    loadReport(page)
  }
}

const exportPDF = async () => {
  if (!hasData.value) return
  try {
    const params = {
      branch: branchStore.selectedBranch,
      export: 'pdf',
      report_type: reportType.value,
    }
    if (filters.parentCustomer) params.parent_customer = filters.parentCustomer
    if (filters.instrumentId) params.instrument_ids = String(filters.instrumentId)
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo
    if (reportType.value === 'claim') {
      params.date_mode = filters.dateMode
      params.refund_status = filters.refundStatus
    }
    if (filters.hasComments) params.has_comments = 'true'

    const response = await axios.get('/v1/chq/reports/received-claim/', {
      params,
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    const filename = reportType.value === 'receive' ? 'received_report.pdf' : 'claim_report.pdf'
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    notificationStore.showError('Failed to export PDF')
  }
}

const exportExcel = async () => {
  if (!hasData.value) return
  try {
    const params = {
      branch: branchStore.selectedBranch,
      export: 'excel',
      report_type: reportType.value,
    }
    if (filters.parentCustomer) params.parent_customer = filters.parentCustomer
    if (filters.instrumentId) params.instrument_ids = String(filters.instrumentId)
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo
    if (reportType.value === 'claim') {
      params.date_mode = filters.dateMode
      params.refund_status = filters.refundStatus
    }
    if (filters.hasComments) params.has_comments = 'true'

    const response = await axios.get('/v1/chq/reports/received-claim/', {
      params,
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    const filename = reportType.value === 'receive' ? 'received_report.xlsx' : 'claim_report.xlsx'
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    notificationStore.showError('Failed to export Excel')
  }
}

// Lifecycle
onMounted(() => {
  loadParentOrganizations()
  loadInstruments()
})

// Watchers
watch(() => branchStore.selectedBranch, () => {
  filters.parentCustomer = ''
  filters.instrumentId = ''
  loadParentOrganizations()
  loadInstruments()
})
</script>

<style scoped>
.received-claim-report-container {
  padding: 20px;
}

.form-label {
  font-weight: 500;
  margin-bottom: 5px;
}

.table th {
  white-space: nowrap;
  font-size: 0.85rem;
}

.table td {
  vertical-align: middle;
  font-size: 0.85rem;
}

.text-end {
  text-align: right;
}

.btn {
  min-width: 100px;
}
</style>