<template>
   <div>
       <b-card>
        <h3>CUCM Clusters</h3>

            <p>Please use dedicated CUCM App users for this server</p>

        <crud-table
                endpoint="/settings_management/cucm"
                :columns="[
                    {key: 'cluster_name', label: 'Cluster Name'},
                    {key: 'server', label: 'Server'},
                    {key: 'version', label: 'Version'},
                    {key: 'username', label: 'Username'},
                    {key: 'ssl_verification', label: 'SSL Verification'},
                    {key: 'action', label: 'Action'},
                ]"
                :form-fields="{
                    cluster_name: '',
                    server: '',
                    version: '',
                    username: '',
                    pd: '',
                    ssl_verification: false,
                    ssl_ca_trust_file_data: null
                }"
        >      
            
            <!-- your form input fields in this slot-->
            <template v-slot:input-fields="{formdata}">
                    <b-form-group id="input-group-2" label="Cluster Name:" label-for="input-name">
                        <b-form-input
                                id="input-name"
                                v-model="formdata.cluster_name"
                                required
                                placeholder="Enter cluster friendly name"
                        ></b-form-input>
                    </b-form-group>
                    <b-form-group id="input-group-server" label="CUCM (AXL) Server:" label-for="input-server">
                    <b-form-input
                            id="input-server"
                            v-model="formdata.server"
                            required
                            placeholder="Enter fully qualified domain name for CUCM server for AXL connection."
                    ></b-form-input>
                </b-form-group>
                    <b-form-group id="input-group-version" label="CUCM Version:" label-for="input-version">
                        <b-form-select v-model="formdata.version" :options="['10.5','11.0','11.5','12.0','12.5']"></b-form-select>
                    </b-form-group>
                    <b-form-group id="input-group-username" label="CUCM Application User Username:" label-for="input-username">
                    <b-form-input
                            id="input-username"
                            v-model="formdata.username"
                            required
                            placeholder="Enter username of dedicated app user."
                    ></b-form-input>
                </b-form-group>
                    <b-form-group id="input-group-pd" label="CUCM Application User Password:" label-for="input-pd">
                    <b-form-input
                            id="input-pd"
                            v-model="formdata.pd"
                            required
                            type="password"
                            placeholder="Enter password of above app user."
                    ></b-form-input>
                </b-form-group>
                <b-form-group id="input-group-ssl" label="SSL Certificate">
                    <b-form-checkbox v-model="formdata.ssl_verification" name="check-button" switch>
                        Verify SSL Certificate
                    </b-form-checkbox>
                    <b-form-textarea
                        id="textarea"
                        v-model="formdata.ssl_ca_trust_file"
                        placeholder="Paste base64 certificate if using self signed or non-trusted CA"
                        rows="3"
                        max-rows="100"
                        ></b-form-textarea>

                </b-form-group>
            </template>
        </crud-table>
       </b-card>
       <b-card>
            <h3>Sync Schedule</h3>
            <b-form-group id="cucm-sync-time-group" label="CUCM Updates on the hour at:" label-for="cucm-sync-time" label-cols="auto">
                <b-form-spinbutton
                    id="cucm-sync-time"
                    v-model="settings.cucm_update_minute" min=0 max=59
                >
                </b-form-spinbutton>
            </b-form-group>
            <b-form-group id="phone-scrape-time-group" label="Phone scrape runs daily at:" label-for="phone-scrape-time" label-cols="auto">
                <b-form-timepicker  
                    v-model="settings.phonescrape_update_time"
                    locale="en"
                ></b-form-timepicker>
            </b-form-group>
            <b-button variant="primary" v-on:click="save_settings">Update Scheduler</b-button>
            <p>Manual updates can be triggered from the job status page</p>
       </b-card>
       <b-card>
            <h3>CUCM Authorized Users</h3>
           <b-row>
               <b-col>
                   <b-form-group label="Add new user">
                        <b-form-input v-model="new_authorized_user" placeholder="Enter new CUCM user id"></b-form-input>
                   </b-form-group>
               </b-col>
               <b-col>
                    <b-form-group label="Authorized CUCM Users">
                        <b-form-select v-model="selected_authorized_cucm_users" :options="authorized_cucm_users" multiple :select-size="4"></b-form-select>
                    </b-form-group>
               </b-col>
           </b-row>
           <b-row>
               <b-col>
                    <b-button variant="primary" @click="add_cucm_users">Add -></b-button>
               </b-col>
               <b-col>
                    <b-button variant="primary" @click="remove_cucm_users">Remove</b-button>
               </b-col>
           </b-row>
           <br>
           <b-row>
            <p>Note: Users in the Authorized CUCM Users list can login to this application using their CUCM credentials.  The login will be authenticated against the first CUCM cluster defined above.</p>
           </b-row>
       </b-card>
        <b-card v-if="username=='localadmin'">
            <h3>Password Management</h3>
            <p>You can login to this application using an end user from the first CUCM cluster or the 'localadmin' account. You can change the localadmin password below.</p>
            <b-form-group id="current-localadmin-password-group" label="current 'localadmin' password:" label-for="current-localadmin-password" label-cols="auto">
                <b-form-input v-model="currentLocalAdminPassword" type="password" placeholder="Enter current password"></b-form-input>
            </b-form-group>
            <b-form-group id="new-localadmin-password-group" label="new 'localadmin' password:" label-for="new-localadmin-password" label-cols="auto">
                <b-form-input v-model="newLocalAdminPassword" type="password" placeholder="Enter new password"></b-form-input>
            </b-form-group>
            <b-form-group id="confirm-new-localadmin-password-group" label=" confirm new 'localadmin' password:" label-for="confirm-new-localadmin-password" label-cols="auto">
                <b-form-input
                    v-model="confirm_newLocalAdminPassword" 
                    type="password"
                    placeholder="Confirm new password"
                    :state="passwordValidation"
                    debounce="1500"
                ></b-form-input>
                <b-form-invalid-feedback>New passwords do not match</b-form-invalid-feedback>
            </b-form-group>
            <b-button variant="primary"
                v-on:click="updatePassword"
                :disabled="newLocalAdminPassword != confirm_newLocalAdminPassword || newLocalAdminPassword == '' || currentLocalAdminPassword == ''"
                >Update Password</b-button>
            <p>Do not lose this password.  It will be needed if this server loses connection to CUCM cluster #1.</p>
       </b-card>
   </div>
</template>

<script>
   import CrudTable from '@/components/crud-table.vue';

    export default {
        name: 'Settings_Management',
        components: {CrudTable},
        data() {
            return {
                cucmsyncminute: 0,
                phonescrapetime: null,
                settings: {},
                new_authorized_user: '',
                authorized_cucm_users: [],
                selected_authorized_cucm_users: [],
                currentLocalAdminPassword: '',
                newLocalAdminPassword: '',
                confirm_newLocalAdminPassword: ''
            }
        },
        mounted () {
            this.get_all_settings();
            this.get_all_cucm_users();
        },
        computed: {
            username: function() {
                return this.$store.getters.userName;
            },
            passwordValidation: function() {
                if (this.newLocalAdminPassword == '' || this.confirm_newLocalAdminPassword == '') {return null}
                else {
                    if (this.confirm_newLocalAdminPassword != this.newLocalAdminPassword) {return false}
                    else {return true}
                }
                    
            }
        },
        methods: {
            get_all_settings() {
                var vm = this

                this.$http({
                    method: 'get',
                    url: '/settings_management/settings',
                    timeout: 7500
                })
                .then(function (response) {
                    response.data['cucm_update_minute'] = parseInt(response.data['cucm_update_minute'])

                    vm.settings = response.data
                    
                })
            },
            save_settings() {
                var vm = this

                this.$http({
                    method: 'put',
                    url: '/settings_management/settings',
                    data: vm.settings,
                    timeout: 7500
                })
                .then(function (response) {               
                    response.data['cucm_update_minute'] = parseInt(response.data['cucm_update_minute'])

                    vm.settings = response.data
                    
                })
            },
            get_all_cucm_users() {
                var vm = this

                this.$http({
                    method: 'get',
                    url: '/settings_management/cucm_users',
                    timeout: 7500
                })
                .then(function (response) {
                    vm.authorized_cucm_users = response.data
                    
                })
            },
            add_cucm_users() {
                var vm = this

                this.authorized_cucm_users.push(this.new_authorized_user)

                this.$http({
                    method: 'post',
                    url: '/settings_management/cucm_users',
                    data: {'userid': vm.new_authorized_user},
                    timeout: 7500
                    })
                    .then(() => vm.get_all_cucm_users())
                    .catch(() => vm.get_all_cucm_users())

                this.new_authorized_user = ''
            },
            remove_cucm_users() {
                var vm = this
                
                this.selected_authorized_cucm_users.forEach(userid => {
                    const index = vm.authorized_cucm_users.indexOf(userid);
                    if (index > -1) {
                        vm.authorized_cucm_users.splice(index, 1);
                    }

                    this.$http({
                    method: 'delete',
                    url: '/settings_management/cucm_users/' + userid,
                    timeout: 7500
                    })
                    .then(() => vm.get_all_cucm_users())
                    .catch(() => vm.get_all_cucm_users())
                });

                this.selected_authorized_cucm_users = []
                
            },
            updatePassword() {
                var vm = this
                this.$http({
                    method: 'put',
                    url: '/settings_management/updatepw',
                    data: {
                        'current': vm.currentLocalAdminPassword,
                        'new': vm.newLocalAdminPassword
                    },
                    timeout: 7500
                })
                .then(function (response) {
                    if (response.data.result == 'Password successfully changed') {
                        vm.$bvToast.toast(`The localadmin password has been changed successfully.`, {
                                title: 'Password updated',
                                variant: 'success',
                                toaster: 'b-toaster-top-center',
                                autoHideDelay: 5000
                            })
                    }
                    else {
                            vm.$bvToast.toast(`Failed to change the localadmin password. Please try again.`, {
                                title: 'Password update failed',
                                variant: 'warning',
                                toaster: 'b-toaster-top-center',
                                autoHideDelay: 12000
                            })
                    }
                    
                })
            }
        }
   };
</script>