<template>
  <div id="header">
      <b-container class="bg-secondary text-white" fluid>
        <b-row>
          <h2 class="mx-auto">VOIP Phone Info Server</h2>
        </b-row>
        <b-row>
          <div v-if="this.$parent.isLoggedIn">User {{ username }} logged-in</div>
        </b-row>
        <b-row>
          <Logout v-if="this.$parent.isLoggedIn"></Logout>
        </b-row>
      </b-container>
  </div>
</template>

<script>

import Logout from '@/components/auth/Logout.vue'

export default {
  name: 'Header',
  components: {
    Logout
  },
  props: {
    username: String
  }
}

</script>