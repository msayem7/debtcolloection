<!-- DashboardView.vue -->
<template>
  <div class="dashboard-container">
    <div class="row">
      <div class="col-md-5">
        <ParentDueReport :branch-id="branchStore.selectedBranch" />
      </div>
      <!-- Add other dashboard components here -->
    </div>
  </div>
</template>

<script setup>
import { useBranchStore } from '@/stores/branchStore'
import ParentDueReport from '@/views/dashboard/ParentDueReport.vue'

const branchStore = useBranchStore()
</script>

<style>
.dashboard-container {
  padding: 20px;
}
</style>