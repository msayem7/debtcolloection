<template>
  <div class="customer-statement-container">
    <div class="card">
      <div class="card-header bg-primary text-white">
        <h5 class="mb-0">Customer Statement</h5>
      </div>
      
      <div class="card-body">
        <!-- Filter Section - Removed branch selector -->
        <div class="row mb-4">
          <div class="col-md-8">
            <label class="form-label">Customer</label>
            <CustomerDropdown 
              v-model="selectedCustomer"
              :error="customerError"
              @update:modelValue="handleCustomerChange"
            />
          </div>
        </div>
        
        <div class="row mb-4">
          <div class="col-md-3">
            <label class="form-label">From Date</label>
            <input 
              type="date" 
              class="form-control"
              v-model="dateFrom"
              :max="dateTo"
            >
          </div>
          
          <div class="col-md-3">
            <label class="form-label">To Date</label>
            <input 
              type="date" 
              class="form-control"
              v-model="dateTo"
              :min="dateFrom"
            >
          </div>
          
          <div class="col-md-3 d-flex align-items-end">
            <button 
              class="btn btn-primary"
              @click="loadStatement"
              :disabled="!canGenerate"
            >
              <span v-if="loading" class="spinner-border spinner-border-sm"></span>
              Generate Report
            </button>
          </div>
        </div>
        
        <!-- Error Message -->
        <div v-if="error" class="alert alert-danger">
          {{ error }}
        </div>
        
        <!-- Report Section -->
        <div v-if="statementData" class="report-section">
          <!-- Summary Cards -->
          <div class="row mb-4">
            <div class="col-md-4">
              <div class="card bg-light">
                <div class="card-body">
                  <h6 class="card-title">Opening Balance</h6>
                  <p class="card-text fs-4">{{ formatNumber(openingBalance) }}</p>
                </div>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="card bg-light">
                <div class="card-body">
                  <h6 class="card-title">Closing Balance</h6>
                  <p class="card-text fs-4">{{ formatNumber(closingBalance) }}</p>
                </div>
              </div>
            </div>
            
            <div class="col-md-4">
              <div class="card bg-light">
                <div class="card-body">
                  <h6 class="card-title">Net Change</h6>
                  <p class="card-text fs-4">{{ formatNumber(closingBalance - openingBalance) }}</p>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Statement Table -->
          <div class="table-responsive">
            <table class="table table-bordered table-hover">
              <thead class="table-dark">
                <tr>
                  <th>Date</th>
                  <th>Transaction Type</th>
                  <th>Particulars</th>
                  <th class="text-end">Net Sales</th>
                  <th class="text-end">Received</th>
                  <th class="text-end">Balance</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in statementData" :key="index"
                    :class="{
                      'table-info': item.transaction_type_id === 0,
                      'table-success': item.transaction_type_id === 1,
                      'table-warning': item.transaction_type_id === 2 || item.transaction_type_id === 3
                    }">
                  <td>{{ formatDate(item.date) }}</td>
                  <td>{{ item.transaction_type_name }}</td>
                  <td>{{ item.particular }}</td>
                  <td class="text-end">{{ formatNumber(item.net_sales) }}</td>
                  <td class="text-end">{{ formatNumber(item.received) }}</td>
                  <td class="text-end">{{ formatNumber(item.balance) }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          
          <!-- Export Buttons -->
          <div class="mt-4 d-flex justify-content-end gap-2">
            <button class="btn btn-outline-primary" @click="exportToPDF">
              <i class="bi bi-file-earmark-pdf"></i> Export to PDF
            </button>
            <button class="btn btn-outline-success" @click="exportToExcel">
              <i class="bi bi-file-earmark-excel"></i> Export to Excel
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import axios from '@/plugins/axios'
import { formatDate, formatNumber } from '@/utils/ezFormatter'
import CustomerDropdown from '@/components/CustomerDropdown.vue'
import { useBranchStore } from '@/stores/branchStore'
import { useNotificationStore } from '@/stores/notificationStore'
import { jsPDF } from 'jspdf'
import autoTable from 'jspdf-autotable'
import { saveAs } from 'file-saver'
import * as XLSX from 'xlsx'

// Stores
const branchStore = useBranchStore()
const notificationStore = useNotificationStore()

// Refs

const selectedCustomer = ref(null)
const dateFrom = ref(new Date().toISOString().split('T')[0].replace(/-/g, '/'))
const dateTo = ref(new Date().toISOString().split('T')[0].replace(/-/g, '/'))
const loading = ref(false)
const error = ref(null)
const customerError = ref(null)
const statementData = ref(null)
const openingBalance = ref(0)
const closingBalance = ref(0)

// Computed
const canGenerate = computed(() => {
  return branchStore.selectedBranch && selectedCustomer.value && dateFrom.value && dateTo.value
})

// Methods
const loadStatement = async () => {
  if (!canGenerate.value) return
  
  try {
    loading.value = true
    error.value = null
    
    const response = await axios.get('/v1/chq/customer-statement/', {
      params: {
        branch: branchStore.selectedBranch, // Using branch from store
        customer: selectedCustomer.value.alias_id,
        date_from: dateFrom.value,
        date_to: dateTo.value
      }
    })
    
    statementData.value = response.data.transactions
    openingBalance.value = response.data.opening_balance
    closingBalance.value = response.data.closing_balance
    
    notificationStore.showSuccess('Statement generated successfully')
  } catch (err) {
    console.error('Error loading statement:', err)
    error.value = err.response?.data?.error || 'Failed to load customer statement'
    notificationStore.showError(error.value)
  } finally {
    loading.value = false
  }
}

const handleCustomerChange = (customer) => {
  selectedCustomer.value = customer
  customerError.value = null
}

const exportToPDF = () => {
  if (!statementData.value) return
  
  const doc = new jsPDF()
  
  // Title
  doc.setFontSize(16)
  doc.text(`Customer Statement Report - ${selectedCustomer.value.name}`, 14, 15)
  
  // Period
  doc.setFontSize(12)
  doc.text(`Period: ${formatDate(dateFrom.value)} to ${formatDate(dateTo.value)}`, 14, 25)
  
  // Summary
  doc.setFontSize(10)
  doc.text(`Opening Balance: ${formatNumber(openingBalance.value)}`, 14, 35)
  doc.text(`Closing Balance: ${formatNumber(closingBalance.value)}`, 14, 45)
  
  // Table
  const headers = [
    'Date', 
    'Type', 
    'Particulars', 
    'Net Sales', 
    'Received', 
    'Balance'
  ]
  
  const data = statementData.value.map(item => [
    formatDate(item.date),
    item.transaction_type_name,
    item.particular,
    formatNumber(item.net_sales),
    formatNumber(item.received),
    formatNumber(item.balance)
  ])
  
  autoTable(doc, {
    startY: 55,
    head: [headers],
    body: data,
    styles: {
      fontSize: 8,
      cellPadding: 2
    },
    columnStyles: {
      3: { halign: 'right' },
      4: { halign: 'right' },
      5: { halign: 'right' }
    },
    headStyles: {
      fillColor: [52, 58, 64] // Dark color
    }
  })
  
  doc.save(`Customer_Statement_${selectedCustomer.value.name}_${dateFrom.value}_to_${dateTo.value}.pdf`)
}

const exportToExcel = () => {
  if (!statementData.value) return
  
  const data = [
    ['Customer Statement Report', selectedCustomer.value.name],
    ['Period', `${formatDate(dateFrom.value)} to ${formatDate(dateTo.value)}`],
    ['Opening Balance', formatNumber(openingBalance.value)],
    ['Closing Balance', formatNumber(closingBalance.value)],
    [], // Empty row
    ['Date', 'Type', 'Particulars', 'Net Sales', 'Received', 'Balance']
  ]
  
  // Add transaction data
  statementData.value.forEach(item => {
    data.push([
      formatDate(item.date),
      item.transaction_type_name,
      item.particular,
      formatNumber(item.net_sales),
      formatNumber(item.received),
      formatNumber(item.balance)
    ])
  })
  
  const ws = XLSX.utils.aoa_to_sheet(data)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Statement')
  
  // Auto-width columns
  const wscols = [
    { wch: 12 }, // Date
    { wch: 10 }, // Type
    { wch: 50 }, // Particulars
    { wch: 12 }, // Net Sales
    { wch: 12 }, // Received
    { wch: 12 }  // Balance
  ]
  ws['!cols'] = wscols
  
  // Format as table
  const range = XLSX.utils.decode_range(ws['!ref'])
  for (let C = range.s.c; C <= range.e.c; ++C) {
    const header = XLSX.utils.encode_cell({ r: 5, c: C })
    if (!ws[header]) continue
    ws[header].s = {
      font: { bold: true },
      fill: { fgColor: { rgb: "D3D3D3" } }
    }
  }
  
  XLSX.writeFile(wb, `Customer_Statement_${selectedCustomer.value.name}_${dateFrom.value}_to_${dateTo.value}.xlsx`)
}

// Watchers
watch(() => branchStore.selectedBranch, (newVal) => {
  branchStore.selectedBranch = newVal
}, { immediate: true })
</script>

<style scoped>
.customer-statement-container {
  padding: 20px;
}

.report-section {
  margin-top: 20px;
}

.table th {
  white-space: nowrap;
}

.table td {
  vertical-align: middle;
}

.text-end {
  text-align: right;
}

.btn {
  min-width: 120px;
}

.form-label {
  font-weight: 500;
  margin-bottom: 5px;
}
</style>