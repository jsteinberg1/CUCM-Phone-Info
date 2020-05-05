import Vue from 'vue'
import Vuex from 'vuex'
import App from './App.vue'
import { BootstrapVue } from 'bootstrap-vue'
import store from './store'
import axios from 'axios'
import IdleVue from "idle-vue";

Vue.config.productionTip = false

Vue.use(BootstrapVue)

Vue.prototype.$http = axios.create({
  baseURL: process.env.VUE_APP_API_ROOT,
  timeout: 5000, // indicates, 1000ms ie. 1 second
  });

Vue.prototype.$http.interceptors.response.use(function (response) {
  return response;
}, function (error) {
    console.log('http intercepter error code ' + error.response.status);
    if (401 === error.response.status) {
      console.log("logging user out due to 401");
      store.commit('logout')
    } else {
        return Promise.reject(error);
    }
});

import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap-vue/dist/bootstrap-vue.css'

Vue.use(Vuex)

const eventsHub = new Vue();

Vue.use(IdleVue, {
  eventEmitter: eventsHub,
  store,
  idleTime: 1800000, // 3 seconds,
  startAtIdle: false
});

new Vue({
  store,
  render: h => h(App),
}).$mount('#app')
