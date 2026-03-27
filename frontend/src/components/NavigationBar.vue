<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-primary shadow-sm">
    <div class="container-fluid">
      <!-- Brand Logo -->
      <router-link to="/" class="navbar-brand">
        <img src="@/assets/logo.png" alt="Logo" class="brand-logo">
        Customer Payment Monitoring
      </router-link>

      <!-- Mobile Toggle -->
      <button 
        class="navbar-toggler" 
        type="button" 
        @click="toggleNavbar"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <!-- Navigation Items -->
      <div :class="['collapse navbar-collapse', { 'show': isNavbarCollapsed }]" id="mainNav">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li 
            v-for="(item, index) in menuItems" 
            :key="index" 
            class="nav-item dropdown"
            @mouseenter="handleHover(index)"
            @mouseleave="resetDropdowns"
          >
            <router-link
              v-if="!item.submenu"
              :to="item.link"
              class="nav-link"
              active-class="active"
              exact-active-class="exact-active"
            >
              <i v-if="item.icon" :class="`bi ${item.icon} me-2`"></i>
              {{ item.name }}
            </router-link>

            <a
              v-else
              class="nav-link dropdown-toggle"
              href="#"
              role="button"
              @click="toggleDropdown(index)"
            >
              <i v-if="item.icon" :class="`bi ${item.icon} me-2`"></i>
              {{ item.name }}
            </a>

            <ul 
              v-if="item.submenu" 
              :class="['dropdown-menu', { 'show': openDropdowns[index] }]"
            >
              <li v-for="(subItem, subIndex) in item.submenu" :key="subIndex">
                <router-link
                  :to="subItem.link"
                  class="dropdown-item"
                  active-class="active-submenu"
                >
                  <i v-if="subItem.icon" :class="`bi ${subItem.icon} me-2`"></i>
                  {{ subItem.name }}
                </router-link>
              </li>
            </ul>
          </li>
        </ul>

        <!-- Right Aligned Items -->
        <div class="d-flex align-items-center">
          <div class="dropdown">
            <a
              class="btn btn-light dropdown-toggle"
              href="#"
              role="button"
              @click="toggleUserDropdown"
            >
              <i class="bi bi-person-circle me-2"></i>
              {{ currentUser.name }}
            </a>
            <ul :class="['dropdown-menu dropdown-menu-end', { 'show': isUserDropdownOpen }]">
              <li><router-link to="/profile" class="dropdown-item">Profile</router-link></li>
              <li><hr class="dropdown-divider"></li>
              <li><LogOut class="dropdown-item text-danger"></LogOut></li>
              <!-- <li><button class="dropdown-item text-danger" @click="logout">Logout</button></li> -->
            </ul>
          </div>
        </div>
      </div>
    </div>
  </nav>
</template>
  
<script setup>
import { ref, reactive } from 'vue';
// import { useRouter } from 'vue-router';
import LogOut from './LogOut.vue';

// const router = useRouter();

// State management
const isNavbarCollapsed = ref(false);
const openDropdowns = reactive({});
const isUserDropdownOpen = ref(false);
const currentUser = reactive({ name: 'System Admin' });

// Menu configuration
const menuItems = ref([
  { 
    name: 'Dashboard', 
    link: '/cheque-dashboard', 
    icon: 'bi-speedometer2' 
  },
  {
    name: 'Configurations',
    icon: 'bi-currency-dollar',
    submenu: [ 
      {name: 'Offices', link: '/branches',  icon: 'bi-house-door'},
      // { name: 'Claims', link: '/claims', icon: 'bi bi-card-list'},
      // { name: 'Deductions', link: '/deductions', icon: 'bi bi-receipt-cutoff' },
     
    ]
  }
  ,
  {
    name: 'Operations',
    icon: 'bi-wallet2',
    submenu: [      
    { name: 'Customers', link: '/customers', icon: 'bi-people' },
    { name: 'Credit Invoice', link: '/credit-invoices', icon: 'bi-list-ul' }, ///claim/categories/
    { name: 'Customer Payment', link: '/operations/payment', icon: 'bi-cash-coin' },
    { name: 'Claims List', link: '/reports/claim-list-view', icon: 'bi-list-ul' },
    // { name: 'Cheques', link: '/cheques', icon: 'bi-list-ul' },
    // { name: 'Pending Cheque', link: '/cheques/pending', icon: 'bi-clock-history' },
    // { name: 'Deposited Cheque', link: '/cheques/deposited', icon: 'bi-check-circle' }
    ]
  },
  {
    name: 'Reports',
    icon: 'bi-bar-chart',
    submenu: [
    // { name: 'Customer Statement', link: '/reports/customer-statement', icon: 'bi-receipt' },   
    // { name: 'Payment Detail', link: '/reports/invoice/cheque', icon: 'bi-graph-up' },
    // { name: 'Customer Due Payements', link: '/due-payements', icon: 'bi-receipt' }
    ]
  }
]);


// Methods
const toggleNavbar = () => {
  isNavbarCollapsed.value = !isNavbarCollapsed.value;
};

const toggleDropdown = (index) => {
  openDropdowns[index] = !openDropdowns[index];
  // Close other dropdowns
  Object.keys(openDropdowns).forEach(key => {
    if (key !== index.toString()) openDropdowns[key] = false;
  });
};

const handleHover = (index) => {
  if (window.innerWidth > 992) { // Desktop hover
    openDropdowns[index] = true;
  }
};

const resetDropdowns = () => {
  if (window.innerWidth > 992) {
    Object.keys(openDropdowns).forEach(key => {
      openDropdowns[key] = false;
    });
  }
};

const toggleUserDropdown = () => {
  isUserDropdownOpen.value = !isUserDropdownOpen.value;
};

// const logout = () => {
//   // Add logout logic
//   router.push('/login');
// };
</script>

<style scoped>
.navbar {
  padding: 0.5rem 1rem;
}

.brand-logo {
  height: 40px;
  margin-right: 12px;
}

.nav-link {
  transition: all 0.3s ease;
  padding: 1rem 1.5rem !important;
}

.nav-link:hover {
  background-color: rgba(255, 255, 255, 0.1);
}

.active {
  font-weight: 600;
  background-color: rgba(255, 255, 255, 0.15);
}

.dropdown-menu {
  border: none;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.dropdown-item {
  padding: 0.75rem 1.5rem;
  transition: all 0.2s ease;
}

.dropdown-item:hover {
  background-color: #f8f9fa;
}

.active-submenu {
  font-weight: 500;
  color: #0d6efd;
  background-color: #e7f1ff;
}

@media (max-width: 992px) {
  .navbar-collapse {
    padding: 1rem 0;
  }
  
  .dropdown-menu {
    box-shadow: none;
    background-color: rgba(255, 255, 255, 0.05);
  }
  
  .dropdown-item {
    color: rgba(255, 255, 255, 0.75);
  }
}
</style>