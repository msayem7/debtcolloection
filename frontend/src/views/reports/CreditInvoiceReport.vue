<template>
  <div class="credit-invoice-report-container">
    <div class="card">
      <div class="card-header bg-primary text-white">
        <h5 class="mb-0">Invoice and payment information</h5>
      </div>

      <div class="card-body">
        <!-- Filter Section -->
        <div class="row g-3 mb-4">
          <!-- Invoice Status -->
          <div class="col-md-3">
            <label class="form-label">Invoice Status</label>
            <select v-model="filters.status" class="form-select" @change="onStatusChange">
<option value="all">All Invoices</option>
              <option value="due">Due</option>
              <option value="immature_due">Immature Due</option>
              <option value="matured_due">Matured Due</option>
              <option value="paid">Paid</option>
            </select>
          </div>

          <!-- Customer Hierarchy -->
          <div class="col-md-3">
            <label class="form-label">Parent Organization</label>
            <select v-model="filters.parentCustomer" class="form-select" @change="onParentChange">
              <option value="">All Parent</option>
              <option v-for="p in parentOrganizations" :key="p.alias_id" :value="p.alias_id">
                {{ p.name }}
              </option>
            </select>
          </div>
          <div class="col-md-3">
            <label class="form-label">Customer</label>
            <select v-model="filters.childCustomer" class="form-select" :disabled="!filters.parentCustomer">
              <option value="">All Customers</option>
              <option v-for="c in childCustomers" :key="c.alias_id" :value="c.alias_id">
                {{ c.name }}
              </option>
            </select>
          </div>

          <!-- Date Mode -->
          <div class="col-md-3">
            <label class="form-label">Date Filter Mode</label>
            <div class="d-flex gap-3 mt-1">
              <div class="form-check">
                <input class="form-check-input" type="radio" v-model="filters.dateMode" value="transaction_date" id="modeTrans">
                <label class="form-check-label" for="modeTrans">Trans. Date</label>
              </div>
              <div class="form-check">
                <input class="form-check-input" type="radio" v-model="filters.dateMode" value="due_date" id="modeDue">
                <label class="form-check-label" for="modeDue">Due Date</label>
              </div>
              <div class="form-check" :title="receivedDateDisabledTooltip">
                <input class="form-check-input" type="radio" v-model="filters.dateMode" value="received_date" id="modeReceived" :disabled="isReceivedDateDisabled">
                <label class="form-check-label" :class="{'text-muted': isReceivedDateDisabled}" for="modeReceived">
                  Received Date
                </label>
              </div>
            </div>
            <small v-if="isReceivedDateDisabled" class="text-warning d-block">
              Received Date filter not applicable for Due/Matured statuses.
            </small>
          </div>

          <!-- Date Range -->
          <div class="col-md-3">
            <label class="form-label">From Date</label>
            <input type="date" v-model="filters.dateFrom" class="form-control">
          </div>
          <div class="col-md-3">
            <label class="form-label">To Date</label>
            <input type="date" v-model="filters.dateTo" class="form-control" :max="filters.reportDate">
          </div>

          <!-- Checkboxes -->
          <div class="col-md-3 d-flex align-items-end gap-3 pb-1">
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="filters.showInstrumentNumbers" id="chkInstruments">
              <label class="form-check-label" for="chkInstruments">Show instruments numbers</label>
            </div>
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="filters.showRemarks" id="chkRemarks">
              <label class="form-check-label" for="chkRemarks">Show Remarks</label>
            </div>
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="filters.returnOnly" id="chkReturn">
              <label class="form-check-label" for="chkReturn">Return Only</label>
            </div>
            <div class="form-check">
              <input class="form-check-input" type="checkbox" v-model="filters.interactiveEnabled" id="chkInteractive" :disabled="!isInteractiveAvailable">
              <label class="form-check-label" for="chkInteractive">Inter Active Report</label>
            </div>
          </div>

          <!-- Report Date -->
          <div class="col-md-3">
            <label class="form-label">Report Date</label>
            <input type="date" v-model="filters.reportDate" class="form-control">
          </div>

          <!-- Action Buttons -->
          <div class="col-md-12 d-flex justify-content-between align-items-end">
            <div>
              <button class="btn btn-primary me-2" @click="loadReport()" :disabled="loading">
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
              <button class="btn btn-outline-secondary" @click="exportCSV" :disabled="loading || !hasData">
                <i class="bi bi-file-earmark-text"></i> CSV
              </button>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="alert alert-danger">{{ error }}</div>

        <!-- Standard Report Table (paginated) -->
        <div v-if="hasData && !showInteractive" class="table-responsive mt-3">
          <table class="table table-bordered table-hover table-sm">
            <thead class="table-dark">
              <tr>
                <th>Sl No</th>
                <th>Parent Org</th>
                <th>Customer</th>
                <th>Trans Date</th>
                <th>Grace Days</th>
                <th>Due Date</th>
                <th>Received Date</th>
                <th class="text-end">Sales Amt</th>
                <th class="text-end">Sales Return</th>
                <th class="text-end">Net Sales</th>
                <th v-if="filters.showInstrumentNumbers">Cheque No</th>
                <th v-if="showPaymentInfo" class="text-end">Cheque/Cash</th>
                <th v-if="filters.showInstrumentNumbers">Claim No</th>
                <th v-if="showPaymentInfo" class="text-end">Claim Amt</th>
                <th v-if="showPaymentInfo" class="text-end">Shortage</th>
                <th class="text-end">Days Overdue</th>
                <th v-if="filters.showRemarks">Remarks</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(row, idx) in reportData" :key="idx"
                  :class="{'table-warning': row.payment_id === null}">
                <td>{{ row.sl_no }}</td>
                <td>{{ row.parent_organization || '-' }}</td>
                <td>{{ row.customer_name || '-' }}</td>
                <td>{{ formatDate(row.transaction_date) }}</td>
                <td>{{ row.grace_days }}</td>
                <td>{{ row.due_date ? formatDate(row.due_date) : '-' }}</td>
                <td>{{ row.received_date ? formatDate(row.received_date) : '-' }}</td>
                <td class="text-end">{{ formatNumber(row.sales_amount) }}</td>
                <td class="text-end">{{ formatNumber(row.sales_return) }}</td>
                <td class="text-end">{{ formatNumber(row.net_sales) }}</td>
                <td v-if="filters.showInstrumentNumbers">{{ row.cheque_numbers || '-' }}</td>
                <td v-if="showPaymentInfo" class="text-end">{{ formatNumber(row.cheque_cash_amount) }}</td>
                <td v-if="filters.showInstrumentNumbers">{{ row.claim_numbers || '-' }}</td>
                <td v-if="showPaymentInfo" class="text-end">{{ formatNumber(row.claim_amount) }}</td>
                <td v-if="showPaymentInfo" class="text-end">{{ formatNumber(row.shortage_amount) }}</td>
                <td class="text-end">{{ row.days_overdue }}</td>
                <td v-if="filters.showRemarks">{{ row.remarks || '-' }}</td>
              </tr>
            </tbody>
            <tfoot class="table-light fw-bold">
              <tr>
                <td colspan="7" class="text-end">Totals:</td>
                <td class="text-end">{{ formatNumber(totals.total_sales_amount) }}</td>
                <td class="text-end">{{ formatNumber(totals.total_sales_return) }}</td>
                <td class="text-end">{{ formatNumber(totals.total_net_sales) }}</td>
                <td v-if="filters.showInstrumentNumbers"></td>
                <td v-if="showPaymentInfo"></td>
                <td v-if="filters.showInstrumentNumbers"></td>
                <td v-if="showPaymentInfo"></td>
                <td v-if="showPaymentInfo"></td>
                <td></td>
                <td v-if="filters.showRemarks"></td>
              </tr>
            </tfoot>
          </table>
        </div>

<!-- Standard Pagination -->
        <div v-if="hasData && !showInteractive" class="d-flex justify-content-between align-items-center mt-3">
          <div class="d-flex align-items-center gap-2">
            <small class="me-2">Page {{ currentPage }} of {{ totalPages }} ({{ totalCount }} records)</small>
            <label class="form-label mb-0 me-1" style="font-size:0.85rem;">Per page:</label>
            <input type="number" v-model.number="pageSize" class="form-control form-control-sm" style="width:80px;" min="1" @change="onPageSizeChange" />
          </div>
          <div class="d-flex align-items-center gap-2">
            <button class="btn btn-sm btn-outline-primary" :disabled="currentPage <= 1" @click="goToPage(currentPage - 1)">
              &laquo; Previous
            </button>
            <input type="number" v-model.number="pageInput" class="form-control form-control-sm" style="width:70px;" min="1" :max="totalPages" @keyup.enter="goToPageInput" placeholder="Page" />
            <button class="btn btn-sm btn-outline-primary" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)">
              Next &raquo;
            </button>
          </div>
        </div>
        <!-- Interactive Report - Split Pane Layout -->
        <div v-if="showInteractive && interactiveData.length > 0" class="split-pane-container mt-3">
          <!-- Left Pane: Payment Information -->
          <div class="split-pane-left" :style="{ width: leftPaneWidth + 'px' }">
            <div class="split-pane-header">
              <h6 class="mb-0">Payment Information</h6>
            </div>
            <div class="split-pane-body">
              <table class="table table-bordered table-hover table-sm">
                <thead class="table-dark">
                  <tr>
                    <th v-for="col in leftColumns" :key="col.key"
                        :style="{ width: col.width + 'px', position: 'relative' }"
                        :class="[col.align === 'right' ? 'text-end' : '', col.sortable ? 'sortable-th' : '']"
                        @click="col.sortable && toggleSort(col.key)">
                      <span class="sort-label">{{ col.label }}</span>
                      <span v-if="col.sortable && sortKey === col.key" class="sort-indicator">{{ sortAsc ? ' ▲' : ' ▼' }}</span>
                      <div v-if="col.resizable" class="col-resizer" @mousedown.stop.prevent="onColResizerMouseDown($event, 'left', col)"></div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in sortedLeftData" :key="idx"
                      @click="selectInvoice(row)"
                      :class="{'table-primary': selectedInvoice && selectedInvoice.sl_no === row.sl_no, 'cursor-pointer': true}">
                    <td v-for="col in leftColumns" :key="col.key"
                        :class="col.align === 'right' ? 'text-end' : ''">
                      <template v-if="col.key === 'received_date' || col.key === 'due_date'">
                        {{ row[col.key] ? formatDate(row[col.key]) : '-' }}
                      </template>
                      <template v-else-if="col.key === 'cheque_cash_amount' || col.key === 'claim_amount' || col.key === 'shortage_amount'">
                        {{ formatNumber(row[col.key]) }}
                      </template>
                      <template v-else>
                        {{ row[col.key] || '-' }}
                      </template>
                    </td>
                  </tr>
                </tbody>
                <tfoot class="table-light fw-bold">
                  <tr>
                    <td v-for="(col, i) in leftColumns" :key="col.key"
                        :class="col.align === 'right' ? 'text-end' : ''">
                      <template v-if="i === 0">Totals</template>
                      <template v-else-if="col.key === 'cheque_cash_amount'">{{ formatNumber(leftTotals.cheque_cash) }}</template>
                      <template v-else-if="col.key === 'claim_amount'">{{ formatNumber(leftTotals.claim) }}</template>
                      <template v-else-if="col.key === 'shortage_amount'">{{ formatNumber(leftTotals.shortage) }}</template>
                      <template v-else></template>
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>

          <!-- Draggable Divider -->
          <div class="split-pane-divider"
               @mousedown.prevent="onDividerMouseDown">
          </div>

          <!-- Right Pane: Credit Sales Information -->
          <div class="split-pane-right">
            <div class="split-pane-header">
              <h6 class="mb-0">Credit Sales Information</h6>
              <span v-if="relatedInvoicesWithSl.length > 1" class="badge bg-info text-dark">{{ relatedInvoicesWithSl.length }} invoices</span>
            </div>
            <div class="split-pane-body">
              <div v-if="!selectedInvoice" class="text-muted text-center p-4">
                Click a row in the left pane to view its credit sales details.
              </div>
              <div v-else>
                <table class="table table-bordered table-hover table-sm">
                  <thead class="table-dark">
                    <tr>
                      <th v-for="col in rightColumns" :key="col.key"
                          :style="{ width: col.width + 'px', position: 'relative' }"
                          :class="col.align === 'right' ? 'text-end' : ''">
                        {{ col.label }}
                        <div v-if="col.resizable" class="col-resizer" @mousedown.stop.prevent="onColResizerMouseDown($event, 'right', col)"></div>
                      </th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="inv in relatedInvoicesWithSl" :key="inv.payment_sl">
                      <td>{{ inv.payment_sl }}</td>
                      <td>{{ inv.customer_name || '-' }}</td>
                      <td>{{ formatDate(inv.transaction_date) }}</td>
                      <td>{{ inv.grace_days }}</td>
                      <td>{{ inv.due_date ? formatDate(inv.due_date) : '-' }}</td>
                      <td class="text-end">{{ formatNumber(inv.sales_amount) }}</td>
                      <td class="text-end">{{ formatNumber(inv.sales_return) }}</td>
                      <td class="text-end">{{ formatNumber(inv.net_sales) }}</td>
                      <td class="text-end">{{ inv.days_overdue }}</td>
                    </tr>
                  </tbody>
                  <tfoot class="table-light fw-bold">
                    <tr>
                      <td colspan="3" class="text-end">Totals:</td>
                      <td></td>
                      <td></td>
                      <td class="text-end">{{ formatNumber(rightTotals.sales_amount) }}</td>
                      <td class="text-end">{{ formatNumber(rightTotals.sales_return) }}</td>
                      <td class="text-end">{{ formatNumber(rightTotals.net_sales) }}</td>
                      <td></td>
                    </tr>
                  </tfoot>
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
import { ref, reactive, computed, onMounted, onBeforeUnmount, watch } from 'vue'
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
const totals = ref({ total_sales_amount: 0, total_sales_return: 0, total_net_sales: 0 })
const currentPage = ref(1)
const totalPages = ref(1)
const totalCount = ref(0)
const pageSize = ref(25)
const pageInput = ref('')
const parentOrganizations = ref([])
const childCustomers = ref([])

const today = new Date().toISOString().split('T')[0]

const filters = reactive({
  status: 'all',
  parentCustomer: '',
  childCustomer: '',
  dateMode: 'transaction_date',
  dateFrom: '',
  dateTo: '',
  showInstrumentNumbers: false,
  showRemarks: false,
  returnOnly: false,
  reportDate: today,
  interactiveEnabled: false,
})

// Interactive Report State
const showInteractive = ref(false)
const interactiveData = ref([])
const selectedInvoice = ref(null)
const leftPaneWidth = ref(550)
const minLeftWidth = 350
const maxLeftWidth = 1400
const isDragging = ref(false)

// Sorting state
const sortKey = ref('')
const sortAsc = ref(true)

// Column definitions (reactive for resizing)
const SL_COL_WIDTH = 60

const baseLeftColumns = [
  { key: 'parent_organization', label: 'Parent Org', width: 140, sortable: true, align: 'left', resizable: true },
  { key: 'received_date', label: 'Received Date', width: 120, sortable: true, align: 'left', resizable: true },
]

const leftColumns = computed(() => {
  const cols = [...baseLeftColumns]
  if (filters.showInstrumentNumbers) {
    cols.push({ key: 'cheque_numbers', label: 'Cheque No', width: 150, sortable: true, align: 'left', resizable: true })
    if (showPaymentInfo.value) {
      cols.push({ key: 'cheque_cash_amount', label: 'Cheque/Cash', width: 110, sortable: true, align: 'right', resizable: true })
    }
    cols.push({ key: 'claim_numbers', label: 'Claim No', width: 150, sortable: true, align: 'left', resizable: true })
    if (showPaymentInfo.value) {
      cols.push({ key: 'claim_amount', label: 'Claim Amt', width: 100, sortable: true, align: 'right', resizable: true })
    }
  } else {
    if (showPaymentInfo.value) {
      cols.push({ key: 'cheque_cash_amount', label: 'Cheque/Cash', width: 110, sortable: true, align: 'right', resizable: true })
      cols.push({ key: 'claim_amount', label: 'Claim Amt', width: 100, sortable: true, align: 'right', resizable: true })
    }
  }
  if (showPaymentInfo.value) {
    cols.push({ key: 'shortage_amount', label: 'Shortage', width: 100, sortable: true, align: 'right', resizable: true })
  }
  if (filters.showRemarks) {
    cols.push({ key: 'remarks', label: 'Remarks', width: 150, sortable: true, align: 'left', resizable: true })
  }
  return cols
})

const rightColumns = reactive([
  { key: 'payment_sl', label: 'SL', width: SL_COL_WIDTH, sortable: false, align: 'left', resizable: true },
  { key: 'customer_name', label: 'Customer', width: 140, sortable: false, align: 'left', resizable: true },
  { key: 'transaction_date', label: 'Trans Date', width: 110, sortable: false, align: 'left', resizable: true },
  { key: 'grace_days', label: 'Grace Days', width: 100, sortable: false, align: 'left', resizable: true },
  { key: 'due_date', label: 'Due Date', width: 110, sortable: false, align: 'left', resizable: true },
  { key: 'sales_amount', label: 'Sales Amt', width: 110, sortable: false, align: 'right', resizable: true },
  { key: 'sales_return', label: 'Sales Return', width: 110, sortable: false, align: 'right', resizable: true },
  { key: 'net_sales', label: 'Net Sales', width: 110, sortable: false, align: 'right', resizable: true },
  { key: 'days_overdue', label: 'Days Overdue', width: 110, sortable: false, align: 'right', resizable: true },
])

// Column resizing state
const colResizing = ref({ pane: null, col: null, startX: 0, startWidth: 0 })

// Computed
const hasData = computed(() => reportData.value.length > 0)
const isReceivedDateDisabled = computed(() => {
  return filters.status === 'due' || filters.status === 'immature_due' || filters.status === 'matured_due'
})
const receivedDateDisabledTooltip = computed(() => {
  return isReceivedDateDisabled.value ? 'Received Date filter not applicable for Due/Immature Due/Matured statuses.' : ''
})
const isInteractiveAvailable = computed(() => {
  return filters.status === 'paid'
})

const showPaymentInfo = computed(() => {
  return filters.status === 'all' || filters.status === 'paid'
})

const uniquePayments = computed(() => {
  const seen = new Set()
  return interactiveData.value.filter(r => {
    if (seen.has(r.payment_alias_id)) return false
    seen.add(r.payment_alias_id)
    return true
  })
})

const sortedLeftData = computed(() => {
  const data = [...uniquePayments.value]
  if (!sortKey.value) return data
  data.sort((a, b) => {
    let va = a[sortKey.value]
    let vb = b[sortKey.value]
    if (va == null) va = ''
    if (vb == null) vb = ''
    if (typeof va === 'string') va = va.toLowerCase()
    if (typeof vb === 'string') vb = vb.toLowerCase()
    if (va < vb) return sortAsc.value ? -1 : 1
    if (va > vb) return sortAsc.value ? 1 : -1
    return 0
  })
  return data
})

const leftTotals = computed(() => {
  let cheque_cash = 0, claim = 0, shortage = 0
  for (const r of uniquePayments.value) {
    cheque_cash += Number(r.cheque_cash_amount) || 0
    claim += Number(r.claim_amount) || 0
    shortage += Number(r.shortage_amount) || 0
  }
  return { cheque_cash, claim, shortage }
})

const rightTotals = computed(() => {
  let sales_amount = 0, sales_return = 0, net_sales = 0
  for (const r of relatedInvoicesWithSl.value) {
    sales_amount += Number(r.sales_amount) || 0
    sales_return += Number(r.sales_return) || 0
    net_sales += Number(r.net_sales) || 0
  }
  return { sales_amount, sales_return, net_sales }
})

const relatedInvoicesWithSl = computed(() => {
  if (!selectedInvoice.value) return []
  const group = interactiveData.value.filter(r => r.payment_alias_id === selectedInvoice.value.payment_alias_id)
  return group.map((r, i) => ({ ...r, payment_sl: i + 1 }))
})

// Methods
const toggleSort = (key) => {
  if (sortKey.value === key) {
    sortAsc.value = !sortAsc.value
  } else {
    sortKey.value = key
    sortAsc.value = true
  }
}

const onStatusChange = () => {
  if (isReceivedDateDisabled.value && filters.dateMode === 'received_date') {
    filters.dateMode = 'transaction_date'
  }
  if (!isInteractiveAvailable.value) {
    filters.interactiveEnabled = false
  }
}

const onParentChange = () => {
  filters.childCustomer = ''
  loadChildCustomers()
}

const loadChildCustomers = async () => {
  if (!filters.parentCustomer || !branchStore.selectedBranch) {
    childCustomers.value = []
    return
  }
  try {
    const res = await axios.get('/v1/chq/customers/', {
      params: { branch: branchStore.selectedBranch, is_active: true }
    })
    childCustomers.value = res.data.filter(c => c.parent === filters.parentCustomer)
  } catch (err) {
    console.error('Error loading child customers:', err)
    childCustomers.value = []
  }
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

const loadReport = async (page = 1) => {
  if (!branchStore.selectedBranch) {
    error.value = 'Please select a organization first.'
    return
  }

  loading.value = true
  error.value = null
  currentPage.value = page
  selectedInvoice.value = null
  sortKey.value = ''
  sortAsc.value = true

  const isInteractive = filters.interactiveEnabled

  try {
    const params = {
      branch: branchStore.selectedBranch,
      status: filters.status,
      date_mode: filters.dateMode,
      report_date: filters.reportDate,
      show_instrument_numbers: filters.showInstrumentNumbers ? 'true' : 'false',
      show_remarks: filters.showRemarks ? 'true' : 'false',
      return_only: filters.returnOnly ? 'true' : 'false',
      page: isInteractive ? 1 : currentPage.value,
      page_size: isInteractive ? 1000 : pageSize.value,
    }

    if (filters.parentCustomer) params.parent_customer = filters.parentCustomer
    if (filters.childCustomer) params.child_customer = filters.childCustomer
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo

    const response = await axios.get('/v1/chq/reports/invoice/', { params })

    if (isInteractive) {
      interactiveData.value = response.data.data || []
      reportData.value = []
      showInteractive.value = true
    } else {
      reportData.value = response.data.data
      totalCount.value = response.data.total_count
      totalPages.value = response.data.total_pages
      totals.value = response.data.totals
      interactiveData.value = []
      showInteractive.value = false
    }
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

const onPageSizeChange = () => {
  currentPage.value = 1
  pageInput.value = ''
  loadReport(1)
}

const goToPageInput = () => {
  const p = parseInt(pageInput.value, 10)
  if (!isNaN(p) && p >= 1 && p <= totalPages.value) {
    goToPage(p)
    pageInput.value = ''
  }
}

const selectInvoice = (row) => {
  selectedInvoice.value = row
}

// Divider drag logic (left/right pane split)
const onDividerMouseDown = (e) => {
  isDragging.value = true
  const startX = e.clientX
  const startWidth = leftPaneWidth.value

  const onMouseMove = (ev) => {
    if (!isDragging.value) return
    const delta = ev.clientX - startX
    const newWidth = startWidth + delta
    leftPaneWidth.value = Math.max(minLeftWidth, Math.min(maxLeftWidth, newWidth))
  }

  const onMouseUp = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    document.body.style.userSelect = ''
    document.body.style.cursor = ''
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'col-resize'
}

// Column resizer drag logic
const onColResizerMouseDown = (e, pane, col) => {
  colResizing.value = { pane, col, startX: e.clientX, startWidth: col.width }

  const onMouseMove = (ev) => {
    const state = colResizing.value
    if (!state.col) return
    const delta = ev.clientX - state.startX
    const newWidth = Math.max(40, state.startWidth + delta)
    state.col.width = newWidth
  }

  const onMouseUp = () => {
    colResizing.value = { pane: null, col: null, startX: 0, startWidth: 0 }
    document.removeEventListener('mousemove', onMouseMove)
    document.removeEventListener('mouseup', onMouseUp)
    document.body.style.userSelect = ''
    document.body.style.cursor = ''
  }

  document.addEventListener('mousemove', onMouseMove)
  document.addEventListener('mouseup', onMouseUp)
  document.body.style.userSelect = 'none'
  document.body.style.cursor = 'col-resize'
}

const exportPDF = async () => {
  if (!hasData.value) return
  try {
    const params = {
      branch: branchStore.selectedBranch,
      export: 'pdf',
      status: filters.status,
      date_mode: filters.dateMode,
      report_date: filters.reportDate,
      show_instrument_numbers: filters.showInstrumentNumbers ? 'true' : 'false',
      show_remarks: filters.showRemarks ? 'true' : 'false',
      return_only: filters.returnOnly ? 'true' : 'false',
    }
    if (filters.parentCustomer) params.parent_customer = filters.parentCustomer
    if (filters.childCustomer) params.child_customer = filters.childCustomer
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo

    const response = await axios.get('/v1/chq/reports/invoice/', {
      params,
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'credit_invoice_report.pdf')
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
      status: filters.status,
      date_mode: filters.dateMode,
      report_date: filters.reportDate,
      show_instrument_numbers: filters.showInstrumentNumbers ? 'true' : 'false',
      show_remarks: filters.showRemarks ? 'true' : 'false',
      return_only: filters.returnOnly ? 'true' : 'false',
    }
    if (filters.parentCustomer) params.parent_customer = filters.parentCustomer
    if (filters.childCustomer) params.child_customer = filters.childCustomer
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo

    const response = await axios.get('/v1/chq/reports/invoice/', {
      params,
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'credit_invoice_report.xlsx')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    notificationStore.showError('Failed to export Excel')
  }
}

const exportCSV = async () => {
  if (!hasData.value) return
  try {
    const params = {
      branch: branchStore.selectedBranch,
      export: 'csv',
      status: filters.status,
      date_mode: filters.dateMode,
      report_date: filters.reportDate,
      show_instrument_numbers: filters.showInstrumentNumbers ? 'true' : 'false',
      show_remarks: filters.showRemarks ? 'true' : 'false',
      return_only: filters.returnOnly ? 'true' : 'false',
    }
    if (filters.parentCustomer) params.parent_customer = filters.parentCustomer
    if (filters.childCustomer) params.child_customer = filters.childCustomer
    if (filters.dateFrom) params.date_from = filters.dateFrom
    if (filters.dateTo) params.date_to = filters.dateTo

    const response = await axios.get('/v1/chq/reports/invoice/', {
      params,
      responseType: 'blob'
    })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', 'credit_invoice_report.csv')
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    notificationStore.showError('Failed to export CSV')
  }
}

// Lifecycle
onMounted(() => {
  loadParentOrganizations()
})

onBeforeUnmount(() => {
  isDragging.value = false
  colResizing.value = { pane: null, col: null, startX: 0, startWidth: 0 }
  document.body.style.userSelect = ''
  document.body.style.cursor = ''
})

// Watchers
watch(() => branchStore.selectedBranch, () => {
  filters.parentCustomer = ''
  filters.childCustomer = ''
  childCustomers.value = []
  loadParentOrganizations()
})
</script>

<style scoped>
.credit-invoice-report-container {
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

.table-warning {
  background-color: #fff3cd;
}

/* ===== Split Pane Layout ===== */
.split-pane-container {
  display: flex;
  flex-direction: row;
  align-items: stretch;
  border: 1px solid #dee2e6;
  border-radius: 4px;
  overflow: hidden;
  min-height: 450px;
  max-height: 650px;
}

.split-pane-left {
  flex-shrink: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.split-pane-right {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.split-pane-divider {
  width: 6px;
  cursor: col-resize;
  background: #e9ecef;
  flex-shrink: 0;
  transition: background 0.15s;
  position: relative;
  z-index: 1;
}

.split-pane-divider:hover {
  background: #adb5bd;
}

.split-pane-divider::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 2px;
  height: 32px;
  background: #6c757d;
  border-radius: 1px;
}

.split-pane-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  flex-shrink: 0;
}

.split-pane-body {
  flex: 1;
  overflow: auto;
  padding: 0;
}

.split-pane-body .table {
  margin-bottom: 0;
  font-size: 0.8rem;
}

.split-pane-body .table th {
  position: sticky;
  top: 0;
  z-index: 1;
  white-space: nowrap;
}

.cursor-pointer {
  cursor: pointer;
}

.cursor-pointer:hover {
  background-color: #f0f7ff;
}

/* ===== Column Resizer ===== */
.col-resizer {
  position: absolute;
  top: 0;
  right: -3px;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  z-index: 2;
}

.col-resizer:hover {
  background: rgba(0, 0, 0, 0.15);
}

/* ===== Column Sorting ===== */
.sortable-th {
  cursor: pointer;
  user-select: none;
}

.sortable-th:hover {
  background-color: #3a5a7a;
}

.sort-label {
  display: inline;
}

.sort-indicator {
  font-size: 0.7rem;
  margin-left: 2px;
}
</style>

<style>
/* Hide native number input spinners for page/pageSize inputs (unscoped to reach pseudo-elements) */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type="number"] {
  -moz-appearance: textfield;
}
</style>
