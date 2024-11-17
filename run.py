from UPISAS.strategies.swim_reactive_strategy import ReactiveAdaptationManager
from UPISAS.exemplar import Exemplar
from UPISAS.exemplars.switch import SWITCH_Frontend
from UPISAS.exemplars.switch import SWITCH_Backend
from UPISAS.exemplars.switch import SWITCH_Elasticsearch
from UPISAS.exemplars.switch import SWITCH_Kibana

import signal
import sys
import time

if __name__ == '__main__':
    #Make sure sysctls is set t o 262144
    exemplar_elasticsearch = SWITCH_Elasticsearch(auto_start=True)  
    exemplar_kibana = SWITCH_Kibana(auto_start=True)
    exemplar_back = SWITCH_Backend(auto_start=True)
    exemplar_front = SWITCH_Frontend(auto_start=True)
    time.sleep(90)
    
    #Add a loop here that tests for 


    try:
        strategy = ReactiveAdaptationManager(exemplar_back)

        #This works now 
        strategy.get_monitor_schema()
        strategy.get_adaptation_options_schema()
        strategy.get_execute_schema()

        while True:
            input("Try to adapt?")
            strategy.monitor(verbose=True)
            if strategy.analyze():              #Error occurrs here (NOT IMPLEMENTED)
                if strategy.plan():
                    strategy.execute()
            
    except (Exception, KeyboardInterrupt) as e:
        print(str(e))
        input("something went wrong")
        exemplar_elasticsearch.stop_container()
        exemplar_kibana.stop_container()
        exemplar_back.stop_container()
        exemplar_front.stop_container()
        sys.exit(0)