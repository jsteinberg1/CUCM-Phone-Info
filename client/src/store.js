import Vue from 'vue'
import Vuex from 'vuex'
import axios from 'axios'

Vue.use(Vuex)

export default new Vuex.Store({
  state: {
    status: '',
    token: '',
    username: ''
  },
  mutations: {
    auth_request(state) {
      state.status = 'loading'
    },
    auth_success(state, object) {
      state.status = 'success'
      state.token = object.token
      state.username = object.username
    },
    auth_error(state) {
      state.status = 'error'
    },
    logout(state) {
      state.status = ''
      state.token = ''
      state.username = ''
    },
  },
  actions: {
    login({ commit }, user) {
      return new Promise((resolve, reject) => {

        var LoginFormData = new FormData();
        LoginFormData.set('username', user.user_id);
        LoginFormData.set('password', user.password);

        commit('auth_request')
        axios({
            baseURL: process.env.VUE_APP_API_ROOT,
            url: '/auth/get_token', 
            data: LoginFormData, 
            method: 'POST' })
          .then(resp => {
            const token = resp.data.access_token
            const username = resp.data.user_name
            console.log("username is " + username);
            Vue.prototype.$http.defaults.headers.common['Authorization'] = "Bearer " + token
            commit('auth_success', {token: token, username: username})
            resolve(resp)
          })
          .catch(err => {
            commit('auth_error')
            reject(err)
          })
      })
    },
    logout({ commit }) {
      return new Promise((resolve) => {
        Vue.prototype.$http.defaults.headers.common['Authorization'] = ""
        commit('logout')
        resolve()
      })
    }
  },
  getters: {
    isLoggedIn: state => !!state.token,
    authStatus: state => state.status,
    userName: state => state.username,
    token: state => state.token
  }
})