<template>
  <b-card
    title="Login"
    style="max-width: 20rem;"
    class="mb-2"
    >
        <form class="login" @submit.prevent="login">
            <label>User ID</label>
            <input required v-model="user_id" autocomplete="username" type="string"/>
            <label>Password</label>
            <input required v-model="password" autocomplete="current-password" type="password"/>
            <hr/>
            <button type="submit">Login</button>
        </form>
</b-card>
</template>

<script>
export default {
    name: 'Login',
    data(){
        return {
            user_id : "",
            password : ""
        }
    },
    props: {
        current_user_id: String
    },
    methods: {
        login: function() {
            let user_id = this.user_id;
            let password = this.password;
            this.$store
                .dispatch("login", { user_id, password })
                .then(() => console.debug("logged in"))
                .catch(err => {
                    console.log(err);
                    var vm = this
                    vm.$bvToast.toast(`Please try again`, {
                        title: 'Login Failure',
                        variant: 'warning',
                        toaster: 'b-toaster-top-center',
                        autoHideDelay: 5000
                        })
                    }
                );
        },
    }      
}
</script>

<style>

</style>