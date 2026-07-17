<template>
  <div class="text-to-sql-container">
    <div class="card">
      <div class="card-header bg-primary text-white d-flex justify-content-between align-items-center">
        <h5 class="mb-0">
          <i class="bi bi-robot me-2"></i>Text-to-SQL Query
        </h5>
        <small class="text-white-50">Ask questions in plain English</small>
      </div>

      <div class="card-body">
        <!-- Query Input -->
        <div class="mb-3">
          <label class="form-label fw-bold">Your Question</label>
          <div class="input-group">
            <textarea
              v-model="question"
              class="form-control"
              rows="2"
              placeholder="e.g. Show me all unpaid invoices for ACI Logistics that are past due"
              :disabled="loading"
              @keydown.enter.ctrl="submitQuery"
            ></textarea>
            <button
              class="btn btn-primary px-4"
              :disabled="loading || !question.trim()"
              @click="submitQuery"
            >
              <i v-if="loading" class="bi bi-arrow-repeat spin me-1"></i>
              <i v-else class="bi bi-send me-1"></i>
              {{ loading ? 'Processing...' : 'Ask' }}
            </button>
          </div>
          <small class="text-muted">Press Ctrl+Enter to submit</small>
        </div>

        <!-- Options Row -->
        <div class="row g-2 mb-3">
          <div class="col-md-4">
            <label class="form-label">API Key Profile</label>
            <select v-model="apiKeyProfile" class="form-select form-select-sm" :disabled="loading">
              <option value="primary">Primary</option>
              <option value="fallback">Fallback</option>
            </select>
          </div>
          <div class="col-md-4">
            <label class="form-label">Max Rows</label>
            <input type="number" v-model.number="maxRows" class="form-control form-control-sm" min="10" max="5000" :disabled="loading">
          </div>
          <div class="col-md-4">
            <label class="form-label">Temperature</label>
            <input type="number" v-model.number="temperature" class="form-control form-control-sm" min="0" max="1" step="0.05" :disabled="loading">
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="errorMessage" class="alert alert-danger alert-dismissible fade show py-2" role="alert">
          <i class="bi bi-exclamation-triangle me-2"></i>{{ errorMessage }}
          <button type="button" class="btn-close py-2" @click="errorMessage = ''"></button>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="text-center py-4">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
          <p class="mt-2 text-muted">Generating SQL query and fetching results...</p>
        </div>

        <!-- Results Section -->
        <div v-if="result && !loading">
          <!-- Meta Info -->
          <div class="d-flex justify-content-between align-items-center mb-2">
            <div>
              <span class="badge bg-success me-2">{{ result.row_count }} rows</span>
              <span class="badge bg-info me-2">{{ result.execution_time_ms }}ms</span>
              <span class="badge bg-secondary me-2">{{ result.llm_provider }} / {{ result.llm_model }}</span>
              <span v-if="result.llm_tokens_used" class="badge bg-warning text-dark">{{ result.llm_tokens_used }} tokens</span>
            </div>
            <div>
              <button class="btn btn-sm btn-outline-secondary me-1" @click="showSQL = !showSQL">
                <i class="bi bi-code-slash me-1"></i>{{ showSQL ? 'Hide SQL' : 'Show SQL' }}
              </button>
              <button class="btn btn-sm btn-outline-primary" @click="copyResults">
                <i class="bi bi-clipboard me-1"></i>Copy
              </button>
            </div>
          </div>

          <!-- Generated SQL -->
          <div v-if="showSQL" class="mb-3">
            <div class="card bg-light">
              <div class="card-header py-1">
                <small class="fw-bold text-muted">Generated SQL</small>
              </div>
              <div class="card-body py-2">
                <pre class="mb-0" style="font-size: 0.8rem; white-space: pre-wrap; word-break: break-all;"><code>{{ result.executed_sql || result.generated_sql }}</code></pre>
              </div>
            </div>
          </div>

          <!-- Data Table -->
          <div class="table-responsive" style="max-height: 600px; overflow-y: auto;">
            <table class="table table-bordered table-striped table-hover table-sm mb-0">
              <thead class="table-dark" style="position: sticky; top: 0; z-index: 1;">
                <tr>
                  <th v-for="col in result.columns" :key="col" class="text-nowrap">{{ col }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, rowIdx) in result.rows" :key="rowIdx">
                  <td v-for="col in result.columns" :key="col" class="text-nowrap">{{ formatCell(row[col]) }}</td>
                </tr>
                <tr v-if="result.rows.length === 0">
                  <td :colspan="result.columns.length" class="text-center text-muted py-4">No results found</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from '@/plugins/axios'
import { useBranchStore } from '@/stores/branchStore'
import { useNotificationStore } from '@/stores/notificationStore'

const branchStore = useBranchStore()
const notificationStore = useNotificationStore()

const question = ref('')
const apiKeyProfile = ref('primary')
const maxRows = ref(500)
const temperature = ref(0.1)
const loading = ref(false)
const result = ref(null)
const errorMessage = ref('')
const showSQL = ref(false)

async function submitQuery() {
  if (!question.value.trim() || loading.value) return

  loading.value = true
  errorMessage.value = ''
  result.value = null
  showSQL.value = false

  try {
    const params = {}
    if (branchStore.selectedBranch) {
      params.branch = branchStore.selectedBranch
    }

    const response = await axios.post('/v1/chq/text-to-sql/', {
      question: question.value.trim(),
      api_key_profile: apiKeyProfile.value,
      max_rows: maxRows.value,
      temperature: temperature.value,
    }, { params })

    result.value = response.data
  } catch (err) {
    if (err.response?.data?.error_message) {
      errorMessage.value = err.response.data.error_message
    } else if (err.response?.data?.detail) {
      errorMessage.value = err.response.data.detail
    } else if (err.response?.data?.question) {
      errorMessage.value = err.response.data.error_message || 'Query processing failed'
    } else {
      errorMessage.value = err.message || 'An unexpected error occurred'
    }
    notificationStore.showError(errorMessage.value)
  } finally {
    loading.value = false
  }
}

function formatCell(value) {
  if (value === null || value === undefined) return '—'
  if (typeof value === 'number') {
    return Number(value).toLocaleString(undefined, {
      minimumFractionDigits: 2,
      maximumFractionDigits: 4
    })
  }
  return String(value)
}

function copyResults() {
  if (!result.value || !result.value.rows.length) return
  const headers = result.value.columns.join('\t')
  const rows = result.value.rows.map(r => result.value.columns.map(c => r[c] ?? '').join('\t')).join('\n')
  const text = headers + '\n' + rows

  navigator.clipboard.writeText(text).then(() => {
    notificationStore.showSuccess('Results copied to clipboard')
  }).catch(() => {
    notificationStore.showError('Failed to copy')
  })
}
</script>

<style scoped>
.spin {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.table td, .table th {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
}

pre {
  margin: 0;
  max-height: 200px;
  overflow-y: auto;
}
</style>