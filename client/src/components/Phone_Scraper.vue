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
    name: 'Phone_Scraper',
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
                colHeaders: ['Name', 'Model', 'IPv4', 'Serial', 'Firmware', 'DN', 'kem1',  'kem2', 'Subnet', 'Gateway', 'DHCP', 'DHCP Server', 'Domain', 'DNS1', 
                'DNS2', 'Alt TFTP', 'TFTP 1', 'TFTP 2', 'op_vlan', 'admin_vlan', 'CDP Host', 'CDP IP', 'CDP Port', 'LLDP Port', 'LLDP Port', 'LLDP Port',  'CUCM 1', 
                'CUCM 2', 'CUCM 3', 'CUCM 4', 'CUCM 5', 'Info URL', 'Dir URL', 'SVC URL', 'IDLR URL', 'Info URL Time', 'Proxy URL', 'Auth URL', 'TVS', 'ITL', 
                'Last Scraped'
                ],
                columns: [
                    {data: "devicename",  readOnly: true},
                    {data: "model",  readOnly: true},
                    {data: "ip_address",  readOnly: true},

                    {data: "sn",  readOnly: true},
                    {data: "firmware",  readOnly: true},
                    {data: "dn",  readOnly: true},
                    {data: "kem1",  readOnly: true},
                    {data: "kem2",  readOnly: true},
                    {data: "subnetmask",  readOnly: true},
                    {data: "gateway",  readOnly: true},
                    {data: "dhcp",  readOnly: true},
                    {data: "dhcp_server",  readOnly: true},
                    {data: "domain_name",  readOnly: true},
                    {data: "dns1",  readOnly: true},
                    {data: "dns2",  readOnly: true},
                    {data: "alt_tftp",  readOnly: true},
                    {data: "tftp1",  readOnly: true},
                    {data: "tftp2",  readOnly: true},
                    {data: "op_vlan",  readOnly: true},
                    {data: "admin_vlan",  readOnly: true},
                    {data: "CDP_Neighbor_ID",  readOnly: true},
                    {data: "CDP_Neighbor_IP",  readOnly: true},
                    {data: "CDP_Neighbor_Port",  readOnly: true},
                    {data: "LLDP_Neighbor_ID",  readOnly: true},
                    {data: "LLDP_Neighbor_IP",  readOnly: true},
                    {data: "LLDP_Neighbor_Port",  readOnly: true},
                    {data: "cucm1",  readOnly: true},
                    {data: "cucm2",  readOnly: true},
                    {data: "cucm3",  readOnly: true},
                    {data: "cucm4",  readOnly: true},
                    {data: "cucm5",  readOnly: true},
                    {data: "info_url",  readOnly: true},
                    {data: "dir_url",  readOnly: true},
                    {data: "svc_url",  readOnly: true},
                    {data: "idle_url",  readOnly: true},
                    {data: "info_url_time",  readOnly: true},
                    {data: "proxy_url",  readOnly: true},
                    {data: "auth_url",  readOnly: true},
                    {data: "tvs",  readOnly: true},
                    {data: "ITL",  readOnly: true},
                    {data: "date_modified",  readOnly: true},
                ]
            },
            rowData: [],
            loadingData: false
        }
    },
    components: {
        HotTable
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
                filename: 'Phone-Scraper-CSV-file_[YYYY]-[MM]-[DD]',
                mimeType: 'text/csv',
            });
        },
        loadData() {
            var vm = this

            vm.loadingData = true
            
            this.$http({
                method: 'get',
                url: '/phonedata/scraper',
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