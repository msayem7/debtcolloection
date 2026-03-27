<template>
  <div class="container">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <div class="container mt-3">
              <h2>Login</h2>
              <form class="mb-3" @submit.prevent="login">
                <div class="form-floating mb-3">
                  <input type="text" class="form-control" id="username" v-model="credentials.username"  placeholder="User Name" required>
                  <label for="username">Username</label>
                </div>
                <div class="form-floating mb-3">
                  <input type="password" class="form-control" id="password" v-model="credentials.password" placeholder="Password" required>
                  <label for="password">Password</label>
                </div>
                <button type="submit" class="btn btn-primary">Login</button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>


<script>
import { ref } from 'vue';
import { useAuthStore } from '@/stores/authStore';
import { useRouter } from 'vue-router';
import { useBranchStore } from '@/stores/branchStore'
import { useNotificationStore } from '@/stores/notificationStore'


export default {
  setup() {
    const credentials = ref({ username: '', password: '' });
    const notificationStore = useNotificationStore()
    const branchStore = useBranchStore();
    const authStore = useAuthStore();
    const router = useRouter();
    const login = async () => {
      try {
        await authStore.login(credentials.value)
        await branchStore.loadBranches()
        router.push('/cheque-dashboard')
      } catch (error) {
        notificationStore.showError(
          error.message || 'Login failed. Please check your credentials'
        )
      }
    }

    return { credentials, login }
  }
}
// export default {
//   setup() {
//     const credentials = ref({ username: '', password: '' });
//     const authStore = useAuthStore();
//     const branchStore = useBranchStore();
//     const router = useRouter();

//     const login = async () => {
//       await authStore.login(credentials.value);      
//       await branchStore.loadBranches();
//       router.push('/cheque-dashboard');
//     };

//     return { credentials, login };
//   },
// };
</script>