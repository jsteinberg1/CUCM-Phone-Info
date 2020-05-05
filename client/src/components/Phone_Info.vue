<template>
    <div>
        <div v-if="loadingData">
            <b-row align-h="center">
                    <b-spinner label="Loading..."></b-spinner>
            </b-row>
        </div>
        <div v-else>
            <b-row  align-h="center">
                <div v-if="rowData.length > 0" style="height: 100% display: flex; flex-direction: row overflow: hidden; flex-grow: 1">
                    <hot-table ref="hotTableComponent" :settings="hotSettings" :data="rowData"></hot-table>    
                </div>
                <div v-else >
                    <p>There is no data in the database.  Please run a manual sync from the Job Status tab.</p>
                </div>
                <hr>
            </b-row>
            <b-row align-h="center">
                <b-button @click="exportToCsv">Download as CSV</b-button>
                <p>   </p>
                <b-button @click="refreshGrid">Refresh</b-button>
            </b-row>
        </div>
    </div>
</template>

<script>
import { HotTable } from '@handsontable/vue';

export default {
    name: 'Phone_Info',
    data() {
        return {
            hotSettings: {
                licenseKey: 'non-commercial-and-evaluation',
                autoRowSize: false,
                height: 600,
                autoColumnSize: true,
                manualColumnResize: true,
                manualColumnMove: true,
                fixedColumnsLeft: 1,
                manualColumnFreeze: true,
                filters: true,
                dropdownMenu: ['remove_col', 'filter_by_condition', 'filter_action_bar'],
                columnSorting: true,
                colHeaders: ['Name', 'Pool', 'CSS', 'Description', 'Firmware', 'IPv4', 'Protocol', 'Model',
                    'First Seen', 'Last Seen', 'Regstamp', 'Cluster', 'EM Profile', 'EM Time'
                ],
                columns: [
                    {data: 'dname', readOnly: true},
                    {data: "dpool", readOnly: true },
                    {data: "dcss", readOnly: true },
                    {data: "descr", readOnly: true },
                    {data: "fw", readOnly: true },
                    {data: "ipv4", readOnly: true },
                    {data: "prot", readOnly: true },
                    {data: "model", readOnly: true },
                    {data: "fdate", readOnly: true },
                    {data: "ldate", readOnly: true },
                    {data: "regstamp", readOnly: true },
                    {data: "cluster", readOnly: true },    
                    {data: "em_profile", readOnly: true },
                    {data: "em_time", readOnly: true },
                ]
            },
            rowData: [],
            loadingData: false
        }
    },
    components: {
        HotTable,
    },
    beforeMount() {
        
    },
    mounted() { 
        this.loadData();
      },
    methods: {
        reSizeColumns(params) {
            console.log(params)
        },
        exportToCsv() {
            console.log("exporting to csv")
            var exportPlugin = this.$refs.hotTableComponent.hotInstance.getPlugin('exportFile');
            exportPlugin.downloadFile('csv', {
                columnHeaders: true,
                columnDelimiter: ',',
                fileExtension: 'csv',
                filename: 'Phone-Info-CSV-file_[YYYY]-[MM]-[DD]',
                mimeType: 'text/csv',
            });
        },
        loadData() {
            var vm = this
            
            vm.loadingData = true

            this.$http({
                method: 'get',
                url: '/phonedata/info',
                timeout: 15000
            })
            .then(function (response) {
                vm.rowData = response.data

                vm.loadingData = false
                
            })
            .catch(function (error) {
                console.log(error);
                vm.loadingData = false
            })
        },
        refreshGrid() {
            this.loadData();
        }
    }
}
</script>

<style src="../../node_modules/handsontable/dist/handsontable.full.css"></style>