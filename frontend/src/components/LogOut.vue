<template>
    <button @click="logout" class="btn btn-danger">Logout</button>
</template>

<script setup>
import {useAuthStore} from '@/stores/authStore';
import { useRouter } from 'vue-router';

// const authStore = useAuthStore();
// const router = useRouter();

const authStore = useAuthStore();
const router = useRouter();

const logout = ()=>{
    authStore.logout;
    router.push('/');
};

</script>
