<template>
  <div class="working-branch-selector col-3 mb-3">
    <div class="row align-items-center g-2">
      <label class="col-6 col-form-label text-end">Office:</label>
      <div class="col-6">
        <select 
          v-model="branchStore.selectedBranch" 
          class="form-select form-select-lg"
          :class="{ 'flashing-bg': !branchStore.selectedBranch }"
          @change="updateWorkingBranch"
        >
          <option value="">Select a Office</option>
          <option 
            v-for="branch in branchStore.branches" 
            :key="branch.alias_id"
            :value="branch.alias_id"
          >
            {{ branch.name }}
          </option>
        </select>
      </div>
    </div>
  </div>
</template>



<script setup>
import { onMounted } from 'vue'; // Import onMounted
import { useBranchStore } from '@/stores/branchStore'

const branchStore = useBranchStore();

const updateWorkingBranch = () => {
  branchStore.setWorkingBranch(branchStore.selectedBranch);
};

// Load branches when the component mounts
onMounted(() => {
  branchStore.loadBranches();
  branchStore.selectedBranch = localStorage.getItem('workingOffice') || '';
});
</script>

<style>
.flashing-bg {
  animation: flash 1.5s infinite;
}

@keyframes flash {
  0% { background-color: rgba(255, 230, 0, 0.1); }
  50% { background-color: rgba(255, 230, 0, 0.4); }
  100% { background-color: rgba(255, 230, 0, 0.1); }
}

.working-branch-selector .form-select {
  transition: background-color 0.3s ease;
}
</style>