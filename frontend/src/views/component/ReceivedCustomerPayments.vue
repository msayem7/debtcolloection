<template>
  <div class="card">
    <div class="card-header">Received Cheques</div>
    <div class="card-body p-0">
      <table class="table table-bordered m-0">
        <thead>
          <tr>
            <th style="width: 15%">Instrument</th>
            <th style="width: 15%">Receipt No</th>
            <th style="width: 15%">Date</th>
            <th style="width: 35%">Details</th>
            <th style="width: 15%">Amount</th>
            <th style="width: 5%" class="text-center">X</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(cheque, index) in cheques" :key="index">            
            <td>
              <select
                v-model="cheque.instrument_type"
                class="form-control border-0"
              >
                <option :value="1">Cash</option>
                <option :value="2">Cheque</option>
                <option :value="3">Demand Draft</option>
                <option :value="4">EFT</option>
                <option :value="5">RTGS</option>
              </select>
            </td>
            <td>
              <input
                type="text"
                v-model="cheque.receipt_no"
                class="form-control border-0"
                :class="{ 'is-invalid': chequeErrors[index] }"
                placeholder="Receopt No"
                @input="validateReceiptNo(index)"
              >
              <div v-if="chequeErrors[index]" class="invalid-feedback">
                Receipt number must be unique
              </div>
            </td>
            <td>
              <input
                type="date"
                v-model="cheque.cheque_date"
                class="form-control border-0"
                @input="formatChequeDate(index)"
              >
            </td>
            <td>
              <input
                type="text"
                v-model="cheque.cheque_detail"
                class="form-control border-0"
                placeholder="Details"
              >
            </td>
            <td>
              <input
                type="text"
                v-model="localCheques[index].formatted_amount"
                @blur="formatChequeAmount(index)"
                class="form-control border-0 text-end"
                placeholder="Amount"
              >
            </td>
            <td class="text-center align-middle">
              <button 
                @click="removeCheque(index)"
                class="btn btn-danger btn-sm py-0 px-2"
                title="Remove Receipt"
                style="min-width: 28px;"
              >
                ×
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div class="p-2">
        <button @click="addCheque" class="btn btn-sm btn-secondary">
          Add
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect } from 'vue'
import { formatDate, parseDate, formatNumber, parseNumber } from '@/utils/ezFormatter'

// Add error state
const chequeErrors = ref([])

// eslint-disable-next-line no-undef
const props = defineProps(['cheques'])
// eslint-disable-next-line no-undef
const emit = defineEmits(['update:cheques'])
const localCheques = ref(props.cheques.map(c => ({
  ...c,
  formatted_amount: formatNumber(c.cheque_amount),
  instrument_type: c.instrument_type || 2 // Default to Cheque (2)
})))

function updateCheques() {
  emit('update:cheques', localCheques.value.map(c => ({
    receipt_no: c.receipt_no,
    instrument_type: c.instrument_type,
    cheque_date: c.cheque_date,
    cheque_detail: c.cheque_detail,
    cheque_amount: parseNumber(c.formatted_amount)
  })))
}

function validateReceiptNo(index) {
  const currentReceiptNo = localCheques.value[index].receipt_no
  const duplicates = localCheques.value.filter((chq, idx) => 
    chq.receipt_no === currentReceiptNo && idx !== index
  )
  
  chequeErrors.value[index] = duplicates.length > 0
  return !chequeErrors.value[index]
}

function addCheque() {
  const newCheque = {
    receipt_no: '',
    instrument_type: 2, // Default to Cheque
    cheque_date: new Date().toISOString().split('T')[0],
    cheque_detail: '',
    formatted_amount: formatNumber(0),
    cheque_amount: 0
  }
  
  // Add first then validate
  localCheques.value.push(newCheque)
  const newIndex = localCheques.value.length - 1
  // Validate before adding
  if (validateReceiptNo(newIndex)) {
    updateCheques()
  } else {
    alert('Duplicate cheque number detected')
    localCheques.value.splice(newIndex, 1) // Remove invalid entry
    updateCheques()
  }
}

function removeCheque(index) {
  localCheques.value.splice(index, 1)
  updateCheques()
}

function formatChequeDate(index) {
  const date = parseDate(localCheques.value[index].cheque_date)
  localCheques.value[index].cheque_date = date.toISOString().split('T')[0]
  updateCheques()
}

function formatChequeAmount(index) {
  const parsed = parseNumber(localCheques.value[index].formatted_amount)
  localCheques.value[index].formatted_amount = formatNumber(parsed)
  localCheques.value[index].cheque_amount = parsed
  updateCheques()
}

watchEffect(() => {
  localCheques.value = props.cheques.map(c => ({
    ...c,
    formatted_amount: formatNumber(c.cheque_amount),
    instrument_type: c.instrument_type || 2 // Default to Cheque (2)
  }))
})
</script>

<style scoped>
.table th {
  background-color: #f8f9fa;
  vertical-align: middle;
  font-size: 0.9rem;
}

.form-control {
  background: transparent;
  padding: 0.25rem;
  font-size: 0.9rem;
}

.form-control:focus {
  box-shadow: none;
  background: white;
}

.btn-danger {
  line-height: 1.2;
  font-size: 1.1rem;
}

select.form-control {
  appearance: auto;
  -webkit-appearance: auto;
}
</style>