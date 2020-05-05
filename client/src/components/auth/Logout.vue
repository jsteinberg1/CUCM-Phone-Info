<template>
    <b-link class="text-white" @click="logout">Logout</b-link>
</template>

<script>
export default {
    name: "Logout",
    methods: {
        logout: function() {
            this.$store.dispatch("logout")
                .then(() => {
                    console.debug("logout");
                })
        }
    }
}
</script>