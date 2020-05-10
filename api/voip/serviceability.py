import os
import logging
logger = logging.getLogger('api')

from api.Config import config

from api.crud import settings_management as crud

from lib.CUCM_Serviceability_API import CUCM_Serviceability_API

class Serviceability_Objects:
    """Class that stores Serviceability objects for CUCM cluster(s)
    used by other functions in this application when Serviceability needs to be queried
    """
    def __init__(self):
        """Call load_clusters method to load Serviceability objects into memory"""
        self.load_clusters()
        

    def load_clusters(self):
        """Load CUCM cluster(s) data from database and create Serviceability object for each cluster"""
        self.clusters = {}

        cucm_clusters = crud.get_cucm_clusters()

        for cucm_connection in cucm_clusters:

            logger.info(f"Creating Serviceability object for cluster {cucm_connection.cluster_name}")

            self.clusters[cucm_connection.cluster_name] = CUCM_Serviceability_API(
                server= cucm_connection.server,
                username= cucm_connection.username,
                password= cucm_connection.pd,
                ssl_verify_cert= cucm_connection.ssl_verification,
                ssl_ca_trust_file= None if cucm_connection.ssl_ca_trust_file == None else os.path.join(config.ca_certs_folder,cucm_connection.ssl_ca_trust_file)
            )


    def get_cluster(self, cluster_name: str) -> CUCM_Serviceability_API:
        """Retrieves Cisco Serviceability object based on cluster name
        
        Arguments:
            cluster_name {str} -- friendly name of CUCM cluster
        
        Raises:
            ValueError: If cluster_name is not provided
        
        Returns:
            [type] -- Cisco Serviceability object
        """

        if cluster_name == "":
            raise ValueError("Cluster name must be provided")

        if cluster_name in self.clusters:
            return self.clusters[cluster_name]
        else:
            raise ValueError("Unable to find cluster")


serviceability_clusters = Serviceability_Objects()