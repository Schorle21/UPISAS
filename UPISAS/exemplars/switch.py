from UPISAS.exemplar import Exemplar
import docker

network_name = "elk"


class SWITCH_Frontend(Exemplar):
    """
    A class which encapsulates a self-adaptive SWITCH exemplar run in a docker container.
    """
    def __init__(self, auto_start, container_name="switch-3_frontend_UPISAS"):
        docker_config = {
            "name":  container_name,
            "image": "schorle21/switch-3_frontend",
            "ports" : {3000:3000}}

        super().__init__("http://localhost:3003", docker_config, auto_start)

    def start_run(self, app):
        self.exemplar_container.exec_run(cmd = f' sh -c "cd /app/ && npm start" ', detach=True)


class SWITCH_Backend(Exemplar):
    """
    A class which encapsulates a self-adaptive SWITCH exemplar run in a docker container.
    """
    def __init__(self, auto_start, container_name="switch-3_backend_UPISAS"):
        docker_config = {
            "name":  container_name,
            "image": "schorle21/switch-3_backend",
            "ports" : {3001:3001,5001:5001,8000:8000,8089:8089},
            "environment":{"ELASTICSEARCH_HOST": "http://elasticsearch_UPISAS:9200"},
            "network":network_name,
            }


        super().__init__("http://localhost:8000", docker_config, auto_start,read_log=True)

    def start_run(self, app):
        self.exemplar_container.exec_run(cmd = f' sh -c "cd ~/app/ && chmod +x entrypoint.sh && ./entrypoint.sh"  ', detach=True)


class SWITCH_Kibana(Exemplar):
    """
    A class which encapsulates a self-adaptive SWITCH exemplar run in a docker container.
    """
    def __init__(self, auto_start, container_name="kibana_UPISAS"):
        docker_config = {
            "name":  container_name,
            "image": "kibana:7.9.1",
            "ports" : {5601:5601},
            "environment":{"ELASTICSEARCH_HOSTS":"http://elasticsearch_UPISAS:9200"},
            "network" : network_name,
        }
                        
        super().__init__("http://kibana:5601", docker_config, auto_start,read_log=False)

    def start_run(self, app):
        #self.exemplar_container.exec_run(cmd = f' sh -c "cd /usr/src/app && node {app}" ', detach=True)
        pass 



#Should set the ulimits
class SWITCH_Elasticsearch(Exemplar):
    """
    A class which encapsulates a self-adaptive SWITCH exemplar run in a docker container.
    """
    def __init__(self, auto_start, container_name="elasticsearch_UPISAS"):
        
        #Attempt to create the network bridge
        try:
            client = docker.from_env()
            client.networks.create(name=network_name,driver="bridge")
            print(f"Network '{network_name}' created successfully.")
        except:
            print(f"Network '{network_name}' exists already.")
        
        
        docker_config = {
            "name":  container_name,
            "image": "elasticsearch:7.9.1",
            "ports" : {9200:9200, 9300:9300},
            "environment" : {"discovery.type":"single-node"},
            "network":network_name,
            }

        super().__init__("http://localhost:9200", docker_config, auto_start,read_log=False)

    def start_run(self, app):
        #self.exemplar_container.exec_run(cmd = f' sh -c "cd /usr/src/app && node {app}" ', detach=True)
        pass

