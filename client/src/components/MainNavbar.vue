<template>
    <b-nav tabs>
        <b-nav-item
        v-for="tab in MenuTabs"
        v-bind:key="tab"
        v-on:click="click(tab)"
        >
        {{ tab.replace(/_/g, " ") }}
        </b-nav-item>
    </b-nav>
</template>

<script>
export default {
    name: 'MainNavbar',
    props: {
        MenuTabs: {},
        NavSelection: String
    },
    methods: {
        click (tab) {
            this.$emit('nav-selection', tab)
        }
    }
}
</script>

<style>

</style>