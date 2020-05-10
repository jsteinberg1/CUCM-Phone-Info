<template>
    <div v-if="tableData != null">
        <b-button @click="createItem" class="mb-2" variant="primary" size="sm">Create</b-button>

        <b-alert v-if="tableData.length == 0" show variant="warning">No Clusters are configured.  Please configure a new CUCM cluster.  Once a new CUCM cluster has been added you will need to sign out and then back into this server with a CUCM end user account.</b-alert>

        <b-table v-else striped hover  :items="tableData" :fields="columns">
            <template #cell(action)="data">
                <b-button @click="editItem(data.item)" variant="primary" size="sm">Edit</b-button>
                <b-button @click="deleteItem(data.item)" v-b-modal="'edit-modal'" variant="danger" size="sm">Delete</b-button>
            </template>
        </b-table>

        <b-modal v-model="modalShow" :title="formTitle" hide-footer size='lg'>
            <b-alert v-if="clusterChangeFailed" show variant="danger">Error encountering saving cluster. Please check settings/credentials and try again</b-alert>
            <b-form @submit.prevent="save">
                <slot :formdata="editedItem" name="input-fields">
                </slot>

                <b-button size="sm" variant="danger" @click="close" >
                    Cancel
                </b-button>

                <b-button type="submit" size="sm" variant="primary">
                    <b-spinner v-if="clusterChangeInProgress" small></b-spinner>
                    Save
                </b-button>
            </b-form>

        </b-modal>
    </div>
</template>

<script>
    export default {
        props:['endpoint','columns','formFields'],
        data() {
            return {
                editedItem: this.formFields,
                modalShow:false,
                editedIndex: -1,
                tableData : null,
                clusterChangeFailed: false,
                clusterChangeInProgress: false
            }
        },
        computed: {
            formTitle() {
                return this.editedIndex === -1 ? 'New Item' : 'Edit Item';
            },
            username: function() {
            return this.$store.getters.userName;
            }
        },
        methods: {
            createItem() {
                this.modalShow = true;
                this.editedItem = Object.assign({}, this.formFields);
                this.editedIndex = -1;
            },
            editItem(item) {
                this.modalShow = true;
                this.editedIndex = this.tableData.indexOf(item);
                this.editedItem = Object.assign({}, item);

                
                setTimeout(() => {  this.load(); }, 2000);
            },
            deleteItem(item) {
                const index = this.tableData.indexOf(item);
                confirm('Are you sure you want to delete this item?') && this.tableData.splice(index, 1);
                
                var vm = this

                this.$http({
                    method: 'delete',
                    url: this.endpoint+'/'+item.id,
                    timeout: 7500
                })
                .then(function () {
                        vm.load()
                    })
            },
            close() {
                this.modalShow = false;
                setTimeout(() => {
                    this.editedItem = Object.assign({}, this.formFields);
                    this.editedIndex = -1;
                }, 300);
            },
            save() {

                var vm = this

                vm.clusterChangeInProgress = true

                if (this.editedIndex > -1) {
                    Object.assign(this.tableData[this.editedIndex], this.editedItem);

                    this.$http({
                        method: 'put',
                        url: this.endpoint+'/'+this.editedItem.id,
                        data: this.editedItem,
                        timeout: 45000
                    })
                    .then(function (response) {
                        vm.clusterChangeInProgress = false

                        if (response.data.result == 'failed') {
                            vm.clusterChangeFailed = true
                        }
                        else {
                            vm.clusterChangeFailed = false
                            vm.$bvToast.toast(`Cluster updated successfully`, {
                                title: 'CUCM Cluster Settings',
                                variant: 'success',
                                toaster: 'b-toaster-top-center',
                                autoHideDelay: 5000
                            })
                            vm.close();
                        }
                        vm.load()
                    })

                } else {
                    this.tableData.push(this.editedItem);

                    this.$http({
                        method: 'post',
                        url: this.endpoint,
                        data: this.editedItem,
                        timeout: 45000
                    })
                    .then(function (response) {
                        
                        vm.clusterChangeInProgress = false
                        if (response.data.result == 'failed') {
                            vm.clusterChangeFailed = true
                            vm.load()
                        }
                        else {
                            vm.clusterChangeFailed = false
                            vm.close();                           
                         
                            vm.$bvToast.toast(`Cluster added successfully.`, {
                                title: 'CUCM Cluster Settings',
                                variant: 'success',
                                toaster: 'b-toaster-top-center',
                                autoHideDelay: 5000
                            })

                            vm.load()
                        }
                    })
                }
            },                     
            load() {
                var vm = this

                this.$http({
                    method: 'get',
                    url: this.endpoint,
                    timeout: 5000
                })
                .then(function (response) {
                    
                    vm.tableData = response.data
                })
            },
            logOutUser() {
                this.$store.dispatch("logout")
            }
        },
        created() {
            this.load()
        },

    }
</script>