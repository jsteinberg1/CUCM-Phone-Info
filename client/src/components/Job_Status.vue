<template>
<div>
    <table v-if="jobstatus != null"  class="table table-striped" v-show="jobstatus">
        <thead>
        <tr>
            <th>Name</th>
            <th>Last Start</th>
            <th>Result</th>
        </tr>
        </thead>
        <tbody>
        <tr v-for="(item,i) in jobstatus" :key="i">
            <th scope="row">{{ item.jobname  }}</th>
            <td>{{ item.laststarttime }}</td>
            
            <td v-if="item.jobname == 'phone scraper' && item.result=='running job..'">
                {{ item.result }} [ {{rq_status.current_size}} phones remaining ]
            </td>
            <td v-else>{{ item.result }}</td>
            
        </tr>
        </tbody>
    </table>
    <b-row v-else align-h="center">
            <b-spinner label="Loading..."></b-spinner>
    </b-row>
    <hr>
    <b-row align-h="center">
        <b-button @click="initiateManualSyncDataUpdate">Trigger CUCM sync</b-button>

        <b-button @click="loadJobStatusData">Refresh</b-button>
        <b-button @click="initiateManualPhoneScrapeUpdate">Trigger Phone Scraping</b-button>
    </b-row>
    <b-row align-h="center">
        <p>Only one background job will run at a time. Attempts to trigger a manual update while another task is running will be ignored.</p>
    </b-row>
</div>
</template>

<script>
export default {
    name: "Job_Status",
    data() {
        return {
        jobstatus: null,
        rq_status: Object,
        }
    },
    mounted() {
        this.loadJobStatusData()
    },
    methods: {
        loadJobStatusData() {
            var vm = this
            
            this.$http({
                method: 'get',
                url: '/phonedata/jobstatus',
                timeout: 5000
            })
            .then(function (response) {
                vm.jobstatus = response.data.Job_Status
                vm.rq_status = response.data.RQ_Status
            })
            .catch(function (error) {
                console.log(error);
            })
        },
        initiateManualPhoneScrapeUpdate() {
            var vm = this

            this.$http({
            method: 'get',
            url: '/phonedata/initiate_phone_scrape_now',
            timeout: 5000
            })
            .then(function () {
                vm.$bvToast.toast(`manual phone scrape has been triggered`, {
                    title: 'Sync Data',
                    variant: 'success',
                    toaster: 'b-toaster-top-center',
                    autoHideDelay: 5000
                    });
            })
            .catch(function (error) {
                console.log(error);
                vm.$bvToast.toast(`manual phone scrape has failed`, {
                    title: 'Sync Data',
                    variant: 'warning',
                    toaster: 'b-toaster-top-center',
                    autoHideDelay: 5000
                    })
            })
        },
        initiateManualSyncDataUpdate() {
            var vm = this

            this.$http({
            method: 'get',
            url: '/phonedata/poll_cucm_now',
            timeout: 5000
            })
            .then(function () {
                vm.$bvToast.toast(`manual sync has been triggered`, {
                    title: 'Sync Data',
                    variant: 'success',
                    toaster: 'b-toaster-top-center',
                    autoHideDelay: 5000
                    });
            })
            .catch(function (error) {
                console.log(error);
                vm.$bvToast.toast(`manual sync has failed`, {
                    title: 'Sync Data',
                    variant: 'warning',
                    toaster: 'b-toaster-top-center',
                    autoHideDelay: 5000
                    })
            })
        }
    },
}
</script>