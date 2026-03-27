import { createRouter, createWebHistory } from 'vue-router';
import Login from '../components/UserLogin.vue';
import ChequeListView from '../views/archive_vue/ChequeListView.vue';
import { useAuthStore } from '@/stores/authStore';
import DashboardView from '../views/DashboardView';
import CustomersView from '../views/CustomersView';
import DuePayementsView from '../views/DuePayementsView';
import PendingListView from '../views/PendingListView';
// import ChequeDepositedView from '../views/ChequeDepositedView';
// import InvoiceChequeRep from '@/reports/InvoiceChequeRep.vue';
import SalesDetailReport from '../views/SalesDetailReport';
import ChargesListView from '@/views/ChargesListView.vue';
import DiductionsView from '@/views/archive_vue/DiductionsView.vue';
import PaymentListView from '@/views/PaymentListView.vue';
import PaymentForm from '@/views/PaymentForm.vue';


const routes = [
    // { path: '/', redirect: '/login' },
    { path: '/', name: 'login', component: Login, meta: { hideNav: true }},
    { path: '/cheque-dashboard', name: 'cheque-dashboard', component: DashboardView, meta: {requiresAuth: true, hideNav: false} },
    { path: '/customers', name: 'customers', component: CustomersView, meta: {requiresAuth: true, hideNav: false} },
    { path: '/claims/',   name: 'Master-Claim', component: () => import('@/views/ClaimPage.vue'), meta: { requiresAuth: true, hideNav: false }},
    { path: '/customer/claims', name: 'customer-claims', component: DiductionsView, meta: {requiresAuth: true, hideNav: false} },
    { path: '/cheques', name: 'cheques', component: ChequeListView, meta: {requiresAuth: true, hideNav: false} },
    { path: '/operations/payment', name: 'parent-customer-payment', component: PaymentListView, meta: {requiresAuth: true, hideNav: false} },
    { path: '/operations/payment/create', name: 'parent-customer-payment-create', component: PaymentForm, meta: {requiresAuth: true, hideNav: false} },
    { path: '/operations/payment/edit/:id', name: 'parent-customer-payment-edit',  component: PaymentForm, meta: { requiresAuth: true, hideNav: false } },

    { path: '/cheques/pending', name: 'pending', component: PendingListView, meta: {requiresAuth: true, hideNav: false} },  //Check not yet deposited
    // { path: '/cheques/deposited', name: 'deposited', component: ChequeDepositedView, meta: {requiresAuth: true, hideNav: false} },
    //{ path: '/reports/invoice/cheque', name: 'invoice-report', component: InvoiceChequeRep, meta: {requiresAuth: true, hideNav: false} },
    { path: '/reports/sale/detail', name: 'sale-detail', component: SalesDetailReport, meta: {requiresAuth: true, hideNav: false} },
    {
      path: '/reports/claim-list-view', name: 'ClaimListView',  component: () => import('../views/ClaimListView.vue'),
      meta: {requiresAuth: true, hideNav: false} 
      // meta: { title: 'Claim Editor' }
    },
    { path: '/due-payements', name: 'due-payements', component: DuePayementsView, meta: {requiresAuth: true, hideNav: false} },
    {
      path: '/branches',
      name: 'branches',
      component: () => import('@/views/BranchListView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/branches/create',
      name: 'branch-create',
      component: () => import('@/views/BranchFormView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/branches/edit/:aliasId',
      name: 'branch-edit',
      component: () => import('@/views/BranchEditView.vue'),
      meta: { requiresAuth: true }
    },
    // Invoice routes
    {
      path: '/credit-invoices/create',
      name: 'CreditInvoiceCreate',
      component: () => import('@/views/CreditInvoiceEntry.vue'),
      meta: { requiresAuth: true, hideNav: false }
    },
    {
      path: '/credit-invoices/edit/:aliasId',
      name: 'CreditInvoiceEdit',
      component: () => import('@/views/CreditInvoiceEntry.vue'),
      meta: { requiresAuth: true, hideNav: false }
    },
    {
      path: '/credit-invoices',
      name: 'CreditInvoiceList',
      component: () => import('@/views/CreditInvoiceList.vue'),
      meta: { requiresAuth: true, hideNav: false }
    },
    // {
    //   path: '/cheques',
    //   name: 'cheques',
    //   component: () => import('@/views/ChequeListView.vue'),
    //   meta: { requiresAuth: true, hideNav: false }
    // },
    // {
    //   path: '/cheques/create',
    //   name: 'cheque-create',
    //   component: () => import('@/views/ChequeEntryView.vue'),
    //   meta: { requiresAuth: true, hideNav: false }
    // },
    // {
    //   path: '/cheques/edit/:aliasId',
    //   name: 'cheque-edit',
    //   component: () => import('@/views/ChequeEntryView.vue'),
    //   meta: { requiresAuth: true, hideNav: false }
    // },

    {
      path: '/cheques/customer/payments',
      name: 'customer-payments',
      component: () => import('@/views/PaymentFormold.vue'),
      meta: { requiresAuth: true, hideNav: false }
    },
    {
      path: '/reports/customer-statement',
      name: 'CustomerStatementReport',
      component: () => import('@/views/reports/CustomerStatementReport.vue'),
      meta: { requiresAuth: true }
    }
];

const router = createRouter({
    history: createWebHistory(),
    routes,
});

router.beforeEach((to, from, next) => {
  //const token = localStorage.getItem('token');
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.token)  { 
    next('/');
  } else {
    next();
  }
});

export default router;