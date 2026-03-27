<template>
  <div class="container mt-4">
    <div class="card shadow-sm">
      <div class="card-header bg-primary text-white">
        <h3 class="mb-0">Claim Management</h3>
      </div>
      <div class="card-body">
        <!-- Filter Section - Improved -->
        <div class="row mb-4 g-3">
          <div class="col-md-4">
            <label class="form-label">Customer</label>
            <select v-model="filters.customer" class="form-select">
              <option value="">All Customers</option>
              <option v-for="cust in parentCustomers" :value="cust.alias_id" :key="cust.alias_id">
                {{ cust.name }}
              </option>
            </select>
          </div>

          <div class="col-md-4">
            <label class="form-label">Instrument</label>
            <select v-model="filters.instrument" class="form-select">
              <option value="">All Instruments</option>
              <option v-for="instrument in instrumentList" :key="instrument.id" :value="instrument.id">
                {{ instrument.instrument_name }}
              </option>
            </select>
          </div>

          <div class="col-md-4">
            <label class="form-label">Claim Date</label>
            <input type="date" class="form-control" v-model="filters.claim_date">
          </div>

          <div class="col-md-4">
            <label class="form-label">Claim Amount Range</label>
            <div class="input-group">
              <input type="number" class="form-control" v-model="filters.claim_amount_min" placeholder="Min">
              <span class="input-group-text">-</span>
              <input type="number" class="form-control" v-model="filters.claim_amount_max" placeholder="Max">
            </div>
          </div>

          <div class="col-md-4">
            <label class="form-label">Refund Amount Range</label>
            <div class="input-group">
              <input type="number" class="form-control" v-model="filters.refund_amount_min" placeholder="Min">
              <span class="input-group-text">-</span>
              <input type="number" class="form-control" v-model="filters.refund_amount_max" placeholder="Max">
            </div>
          </div>

          <div class="col-md-4">
            <label class="form-label">Remaining Amount Range</label>
            <div class="input-group">
              <input type="number" class="form-control" v-model="filters.remaining_amount_min" placeholder="Min">
              <span class="input-group-text">-</span>
              <input type="number" class="form-control" v-model="filters.remaining_amount_max" placeholder="Max">
            </div>
          </div>

          <div class="col-12 text-end mt-2">
            <button class="btn btn-primary" @click="applyFilters">
              <i class="bi bi-funnel me-1"></i> Apply Filters
            </button>
          </div>
        </div>

        <!-- Claims Table -->
        <div class="table-responsive">
          <table class="table table-hover table-striped">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Instrument</th>
                <th>Claim Serial</th>
                <th>Amount</th>
                <th>Claim Date</th>
                <th>Submitted</th>
                <th>Refund</th>
                <th>Refund Date</th>
                <th>Remaining</th>
                <th>Remarks</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="claim in claims" :key="claim.alias_id">
                <td>{{ claim.customer_name }}</td>
                <td>{{ claim.instrument_name }}</td>
                <td>{{ claim.claim_serial_no }}</td>
                <td>{{ formatNumber(claim.claim_amount) }}</td>
                <td>{{ formatDate(claim.claim_date) }}</td>
                <td>{{ claim.submitted_date ? formatDate(claim.submitted_date) : '-' }}</td>
                <td>{{ formatNumber(claim.refund_amount) }}</td>
                <td>{{ claim.refund_date ? formatDate(claim.refund_date) : '-' }}</td>
                <td>{{ formatNumber(claim.remaining_amount) }}</td>
                <td class="remarks">{{ claim.remarks || '-' }}</td>
                <td>
                  <button 
                    class="btn btn-sm btn-outline-primary"
                    @click="openEditModal(claim)"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                </td>
              </tr>
            </tbody>
            <tfoot>
              <tr style="font-weight: bold; background: #f8f9fa;">
                <td colspan="3" class="text-end">Total</td>
                <td>{{ formatNumber(totalClaimAmount) }}</td>
                <td></td>
                <td></td>
                <td>{{ formatNumber(totalRefundAmount) }}</td>
                <td></td>
                <td>{{ formatNumber(totalRemainingAmount) }}</td>
                <td colspan="2"></td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>
    </div>

    <!-- Edit Claim Modal -->
    <div class="modal fade" id="editClaimModal" tabindex="-1" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header bg-primary text-white">
            <h5 class="modal-title">Edit Claim</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="updateClaim">
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Submitted Date</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    v-model="editingClaim.submitted_date"
                    required
                  >
                  <div class="form-text text-muted">
                    Must be provided before refund details
                  </div>
                </div>
                <!-- <div class="col-md-6">
                  <label class="form-label">Refund Amount</label>
                  <input 
                    type="number" 
                    class="form-control" 
                    v-model="editingClaim.refund_amount"
                    :disabled="!editingClaim.submitted_date"
                    min="0"
                    :max="editingClaim.claim_amount"
                  >
                </div> -->
                <div class="col-md-6">
                  <label class="form-label">Refund Amount</label>
                  <input 
                    type="text"
                    class="form-control"
                    v-model="formatedRefundAmount"
                    :disabled="!editingClaim.submitted_date"
                    @blur="updateRefundAmount"
                  >
                </div>
              </div>
              
              <div class="row mb-3">
                <div class="col-md-6">
                  <label class="form-label">Refund Date</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    v-model="editingClaim.refund_date"
                    :disabled="!editingClaim.submitted_date"
                    :min="editingClaim.submitted_date"
                  >
                </div>
                <div class="col-md-6">
                  <label class="form-label">Remarks</label>
                  <textarea 
                    class="form-control" 
                    v-model="editingClaim.remarks"
                    rows="2"
                  ></textarea>
                </div>
              </div>
              
              <div class="alert alert-warning" v-if="validationError">
                {{ validationError }}
              </div>
              
              <div class="d-flex justify-content-end">
                <button type="button" class="btn btn-secondary me-2" data-bs-dismiss="modal">Cancel</button>
                <button type="submit" class="btn btn-primary">Save Changes</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import axios from '@/plugins/axios';
import { formatDate, formatNumber, parseNumber } from '@/utils/ezFormatter';
import { Modal } from 'bootstrap';
import { useBranchStore } from '@/stores/branchStore';

const branchStore = useBranchStore();

const claims = ref([]);
const editingClaim = ref({});
const editModal = ref(null);
const validationError = ref('');
const parentCustomers = ref([]);
const instrumentList = ref([]);

const formatedRefundAmount = ref('0'); // Initialize with formatted zero

const filters = ref({
  customer: '',
  instrument: '',
  claim_date: '',
  claim_amount_min: '',
  claim_amount_max: '',
  refund_amount_min: '',
  refund_amount_max: '0',
  remaining_amount_min: '',
  remaining_amount_max: '',
});

// Fixed computed properties
const totalClaimAmount = computed(() => 
  claims.value.reduce((sum, claim) => sum + parseFloat(claim.claim_amount || 0), 0)
);

const totalRefundAmount = computed(() => 
  claims.value.reduce((sum, claim) => sum + parseFloat(claim.refund_amount || 0), 0)
);

const totalRemainingAmount = computed(() => 
  claims.value.reduce((sum, claim) => sum + parseFloat(claim.remaining_amount || 0), 0)
);

// const updateRefundAmount = () => {
  
//   const num = parseNumber(formatedRefundAmount.value);
//   editingClaim.value.refund_amount = formatNumber(num);
// }

const updateRefundAmount = () => {
  
  const num = parseNumber(formatedRefundAmount.value);
  editingClaim.value.refund_amount = num;
  formatedRefundAmount.value = formatNumber(num);
  console.log('num',num,'Updated refund amount:', editingClaim.value.refund_amount, "formatedRefundAmount.value", formatedRefundAmount.value);
}

// const formatRefundAmount = (value) => {
//   // Handle zero value specifically
//   if (value === 0 || value === '0') return '0';

//   // Use your formatNumber function with 3 decimals for non-zero values
//   return formatNumber(value);
// };

// const handleRefundInput = (rawValue) => {
//   // Parse using your utility function
//   let num = parseNumber(rawValue);
  
//   // Apply constraints
//   num = Math.max(0, num);
//   num = Math.min(num, editingClaim.value.claim_amount);

//   // Round to 3 decimal places
//   num = parseFloat(num.toFixed(3));
  
//   // Update model (will trigger re-formatting)
//   this.editingClaim.refund_amount = num;
// };

const applyFilters = async () => {
  try {
    fetchClaims();
  } catch (error) {
    console.error('Error fetching claims:', error);
  }
};

onMounted(async () => {  
  await loadInstruments();
  await loadParentCustomers();
  const modalElement = document.getElementById('editClaimModal');
  if (modalElement) {
    editModal.value = new Modal(modalElement);
  }
  await fetchClaims();
});

async function fetchClaims() {
  try {
    const params = {
      branch_alias_id: branchStore.selectedBranch,
      ...filters.value
    };
    
    const response = await axios.get('v1/chq/claims/', { params });
    claims.value = response.data || [];
  } catch (error) {
    console.error('Error fetching claims:', error);
  }
}

function openEditModal(claim) {
  editingClaim.value = { 
    ...claim,
    refund_amount: claim.refund_amount || 0,
    refund_date: claim.refund_date || '',
    remarks: claim.remarks || ''
  };
  formatedRefundAmount.value = formatNumber(editingClaim.value.refund_amount) || '0';
  console.log('Editing claim.refund_amount:', formatNumber(editingClaim.value.refund_amount));
  console.log('formatedRefundAmount:', formatedRefundAmount);
  validationError.value = '';
  editModal.value.show();
}

function validateClaim() {
  if (editingClaim.value.submitted_date) {
    const refundAmount = parseFloat(editingClaim.value.refund_amount);
    const hasRefundAmount = refundAmount > 0;
    const hasRefundDate = !!editingClaim.value.refund_date;
    
    if (hasRefundAmount !== hasRefundDate) {
      return 'Both refund amount and refund date must be provided together';
    }
    
    if (hasRefundAmount && refundAmount > parseFloat(editingClaim.value.claim_amount)) {
      return 'Refund amount cannot exceed claim amount';
    }
    
    if (hasRefundDate && new Date(editingClaim.value.refund_date) < new Date(editingClaim.value.submitted_date)) {
      return 'Refund date cannot be before submitted date';
    }
  } else if (editingClaim.value.refund_amount || editingClaim.value.refund_date) {
    return 'Submitted date is required for refund details';
  }
  
  return '';
}

async function updateClaim() {
  validationError.value = validateClaim();
  if (validationError.value) return;
  
  try {
    const payload = {
      submitted_date: editingClaim.value.submitted_date,
      refund_amount: editingClaim.value.refund_amount || null,
      refund_date: editingClaim.value.refund_date || null,
      remarks: editingClaim.value.remarks
    };
    
    await axios.patch(
      `v1/chq/claims/${editingClaim.value.alias_id}/update_claim/`,
      payload
    );
    
    editModal.value.hide();
    fetchClaims();
  } catch (error) {
    validationError.value = error.response?.data?.detail || 'Failed to update claim';
  }
}

const loadParentCustomers = async () => {
  try {
    const response = await axios.get('/v1/chq/customers/', {
      params: {
        branch: branchStore.selectedBranch,
        is_parent: true,
        is_active: true
      }
    });
    parentCustomers.value = response.data;
  } catch (error) {
    console.error('Error loading customers:', error);
  }
};

const loadInstruments = async () => {
  try {
    const response = await axios.get(`/v1/chq/payment-instruments/?branch=${branchStore.selectedBranch}&instrument_type_serial_no=3`);
    instrumentList.value = response.data;
  } catch (error) {
    console.error("Error fetching instruments:", error);
  }
};
</script>

<style scoped>
.table th {
  background-color: #f8f9fa;
  font-weight: 600;
}

.modal-header {
  padding: 1rem 1.5rem;
}

.form-text {
  font-size: 0.85rem;
}

table {
  width: 100%;
}

th, td {
  word-wrap: break-word;
  white-space: nowrap;
  overflow: hidden;
}

td.remarks { 
  white-space: normal;
  word-break: normal;
  max-width: 200px;
}

/* Improved filter styling */
.input-group-text {
  background-color: #f8f9fa;
  border-color: #dee2e6;
}

.form-select, .form-control {
  border-radius: 0.25rem;
}

.btn-primary {
  background-color: #0d6efd;
  border-color: #0d6efd;
}

.btn-primary:hover {
  background-color: #0b5ed7;
  border-color: #0a58ca;
}

/* Remove increment buttons from number inputs */
input[type="number"]::-webkit-inner-spin-button,
input[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
  appearance: textfield;
  -webkit-appearance: textfield;
}
</style>