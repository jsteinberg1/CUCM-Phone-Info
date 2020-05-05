<template>
    <b-toast toaster="b-toaster-top-center" id="example-toast" title="Your session is about to expire." variant="warning" no-auto-hide visible solid>
      You are being timed out due to inactivity. You will be logged off automatically in {{ time }} seconds.
    </b-toast>
</template>

<script>

export default {
  name: 'IdleTimeout',
  data() {
		return {
      time: 30,
		}
	},
  methods: {
    logout: function() {
      this.$store.dispatch("logout")
        .then(() => {console.debug("logout");})
    },
  },

  created() {
  
    var vm = this

    let timerId = setInterval(() => {

      this.time -= 1;

      if (!vm.$store.state.idleVue.isIdle) {
        clearInterval(timerId);
      }
      
      if (vm.time < 1) {
        clearInterval(timerId);
        vm.logout();
      }

    }, 1000);
  }
}

</script>