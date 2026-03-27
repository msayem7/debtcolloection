<template>
  <div class="card mt-4">
    <div class="card-header">
      Existing Unallocated Payments
    </div>
    <div class="card-body p-0">
      <table class="table table-bordered m-0">
        <thead>
          <tr>
            <th>
              <input 
                v-model="selectAll" 
                type="checkbox" 
                @change="toggleAllSelection"
              >
            </th>
            <th>Receipt No</th>
            <th>Payment Type</th>
            <th>Receive Date</th>
            <th>Amount</th>
            <th>Allocated</th>
            <th>Remaining</th>
          </tr>
        </thead>
        <tbody>          
          <tr v-for="(payment) in filteredPayments" :key="payment.receipt_no">
            <td>
              <input 
                v-model="selectedPayments" 
                type="checkbox" 
                :value="payment.receipt_no"
              >
            </td>
            <td>{{ payment.receipt_no }}</td>
            <td>{{ getPaymentType(payment.instrument_type) }}</td>
            <td>{{ formatDate(payment.cheque_date) }}</td>
            <td class="text-end">{{ formatNumber(payment.cheque_amount) }}</td>
            <td class="text-end">{{ formatNumber(payment.allocated || 0) }}</td>
            <td class="text-end">
              {{ formatNumber(payment.cheque_amount - (payment.allocated || 0)) }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { formatDate, formatNumber, parseNumber } from '@/utils/ezFormatter'

// eslint-disable-next-line
const props = defineProps({
  payments: Array,
  customer: Object,
  loading: Boolean
})

// eslint-disable-next-line
const emit = defineEmits(['update:selectedPayments'])

const selectedPayments = ref([])
const selectAll = ref(false)

const filteredPayments = computed(() => {
  return (props.payments || []).filter(payment => {
    const allocated = parseNumber(payment.allocated || 0)
    return parseNumber(payment.cheque_amount) - allocated > 0
  })
})

const paymentTypes = {
  1: 'Cash',
  2: 'Cheque',
  3: 'Demand Draft',
  4: 'EFT',
  5: 'RTGS'
}

function getPaymentType(type) {
  return paymentTypes[type] || 'Unknown'
}

function toggleAllSelection() {
  if (selectAll.value) {
    selectedPayments.value = filteredPayments.value.map(p => p.receipt_no)
  } else {
    selectedPayments.value = []
  }
}

watch(selectedPayments, (newVal) => {
  selectAll.value = newVal.length === filteredPayments.value.length
  emitSelectedPayments()
})

function emitSelectedPayments() {
  const selected = filteredPayments.value
    .filter(p => selectedPayments.value.includes(p.receipt_no))
    .map(p => ({
      receipt_no: p.receipt_no,
      instrument_type: p.instrument_type,
      cheque_date: p.cheque_date,
      cheque_detail: p.cheque_detail,
      cheque_amount: p.cheque_amount - (p.allocated || 0)
    }))
  
  emit('update:selectedPayments', selected)
}
</script>

<style scoped>
.table th {
  background-color: #f8f9fa;
  vertical-align: middle;
  font-size: 0.9rem;
}

input[type="checkbox"] {
  cursor: pointer;
  transform: scale(1.2);
}
</style>
