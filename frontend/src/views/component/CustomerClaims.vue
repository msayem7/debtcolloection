<template>
  <div class="card">
    <div class="card-header">Customer Claims</div>
    <div class="card-body p-0">
      <table class="table table-bordered m-0">
        <thead>
          <tr>
            <th style="width: 20%">Claims</th>
            <th style="width: 15%">Number</th>
            <th style="width: 50%">Details</th>
            <th style="width: 15%">Amount</th>
            <!-- <th style="width: 5%" class="text-center">X</th> -->
          </tr>
        </thead>
        <tbody>
          <tr v-for="(claim, index) in localClaims" :key="index">            
            <td>
              <input
                v-model="claim.claim_name"
                type="text"
                class="form-control border-0"
                placeholder="Claim Name"
                disabled
              >
            </td>
            <td>
              <input
                v-model="claim.claim_no"
                type="text"
                class="form-control border-0"
                :class="{ 'is-invalid': claimErrors[index] }"
                placeholder="Claim No"   
                disabled             
              >
            </td>
            <td>
              <input
                v-model="claim.details"
                type="text"
                class="form-control border-0"
                placeholder="Details"
              >
            </td>
            <td class="text-right align-middle">
              <input
                v-model="localClaims[index].formatted_amount"
                type="text"
                @blur="formatClaimAmount(index)"
                class="form-control border-0 text-end"
                placeholder="Amount"
              >
            </td>            
          </tr>
          <!-- Total row -->
          <tr class="table-active">
            <td colspan="3" class="fw-bold">Total</td>
            <td class="text-end fw-bold">{{ formatNumber(totalAmount) }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, watchEffect, computed } from 'vue'
import { formatNumber, parseNumber } from '@/utils/ezFormatter'
// eslint-disable-next-line
const props = defineProps(['claims'])
// eslint-disable-next-line
const emit = defineEmits(['update:claims'])

const localClaims = ref(props.claims.map(c => ({
  ...c,
  formatted_amount: formatNumber(c.claim_amount)
})))

const claimErrors = ref([])
// const claim_number = computed(()=>{
//   return props.claims.prefix + props.claims.next_number
// })

// Computed property for total amount
const totalAmount = computed(() => {
  return localClaims.value.reduce((sum, claim) => {
    return sum + (parseNumber(claim.formatted_amount) || 0)
  }, 0)
})

// Add this function
function handleClaimInput(index) {
  //validateClaimNo(index); // No need as this local claim  are now handling from server side
  updateClaims(); // Propagate changes immediately
}

// No need as this local value are now handling from server side
// function validateClaimNo(index) {
//   const currentClaimNo = localClaims.value[index].claim_no
//   const duplicates = localClaims.value.filter((clm, idx) => 
//     clm.claim_no === currentClaimNo && idx !== index
//   )
  
//   claimErrors.value[index] = duplicates.length > 0
//   return !claimErrors.value[index]
// }

function updateClaims() {
  emit('update:claims', localClaims.value.map(c => ({
    ...c,
    claim_name: c.claim_name,
    prefix: c.prefix,
    next_number: c.next_number,
    claim_no: c.claim_no,
    claim_amount: parseNumber(c.formatted_amount)
  })))
}


// function addClaim() {
//   const newClaim = {
//     claim_no: '',
//     claim_name: '',  // Default name
//     details: '',
//     formatted_amount: formatNumber(0),
//     claim_amount: 0,
//     claim: null  // Assuming this links to master claim
//   }

  // Validate before adding
//   const lastIndex = localClaims.value.length
//   if (validateClaimNo(lastIndex)) {
//     localClaims.value.push(newClaim)
//     updateClaims()
//   } else {
//     alert('Duplicate claim number detected')
//     // Remove if validation fails
//     localClaims.value.splice(lastIndex, 1)
//   }
// }

function formatClaimAmount(index) {
  const parsed = parseNumber(localClaims.value[index].formatted_amount)
  localClaims.value[index].formatted_amount = formatNumber(parsed)
  localClaims.value[index].claim_amount = parsed
  updateClaims()
}

watchEffect(() => {
  localClaims.value = props.claims.map(c => ({
    ...c,
    formatted_amount: formatNumber(c.claim_amount)
  }))
})
</script>

<style scoped>
/* Match the cheques table styling */
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

/* Disabled input styling */
.form-control:disabled {
  background: #f8f9fa;
  cursor: not-allowed;
}

/* Style for total row */
.table-active {
  background-color: rgba(0, 0, 0, 0.05);
}
</style>