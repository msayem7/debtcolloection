import { createApp } from 'vue';
import App from './App.vue';
import router from './router';
import { createPinia } from 'pinia';
import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap-icons/font/bootstrap-icons.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'bootstrap';
const app = createApp(App);
app.use(router);
app.use(createPinia());
// loadConfig().then(() => {
//   app.mount('#app');
// });
 app.mount('#app');