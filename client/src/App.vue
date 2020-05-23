<template>
  <div id="app">
    <!-- Header with logout -->
    <Header v-bind:username="username"/>
    <IdleTimeout v-if="isLoggedIn && isIdle"></IdleTimeout>
    <div v-if="isLoggedIn">
      <!-- Top level menu -->
      <b-container fluid>
        <b-row>
          <MainNavbar v-bind:MenuTabs="MenuTabs" @nav-selection="navChangeTop($event)"/>
        </b-row>

        <b-row>
          <b-col>
            <component v-bind:is="NavSelection"></component>
          </b-col>
        </b-row>
      </b-container>

    </div>
      
    <div v-else>
      <!-- login card -->
      <Login class="mx-auto"/>
    </div>

  </div>
</template>

<script>
import Header from './components/Header.vue'
import Login from './components/auth/Login.vue'
import MainNavbar from './components/MainNavbar.vue'
import IdleTimeout from '@/components/Idle_Timeout.vue'

import Phone_Info from '@/components/Phone_Info.vue'
import Phone_Scraper from '@/components/Phone_Scraper.vue'
import Phone_Combined from '@/components/Phone_Combined.vue'
import Settings_Management from '@/components/Settings_Management.vue'
import Job_Status from '@/components/Job_Status.vue'


export default {
  name: 'App',
  data () {
    return {
      MenuTabs: ["Phone Info", "Phone Scraper", "Phone Combined", "Settings Management", "Job Status"],
      NavSelection: "",
    }
  },
  components: {
    Header,
    Login,
    MainNavbar,
    Phone_Info,
    Phone_Scraper,
    Phone_Combined,
    Settings_Management,
    Job_Status,
    IdleTimeout
  },
  methods: {
    navChangeTop(event) {
      this.NavSelection=event.replace(" ","_")
    },
    localadminLogin() {
      if (this.NavSelection == '') {
        this.NavSelection = "Settings_Management"
      }
    },
  },
  computed: {
    isLoggedIn: function() {
      return this.$store.getters.isLoggedIn;
    },
    username: function() {
      return this.$store.getters.userName;
    },
    isIdle: function() {
			return this.$store.state.idleVue.isIdle;
		}
  },
  updated() {
    if (this.isLoggedIn && this.username == 'localadmin') {
      this.localadminLogin();
    }
  }
}
</script>

<style>

</style>
