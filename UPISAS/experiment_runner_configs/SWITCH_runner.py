from EventManager.Models.RunnerEvents import RunnerEvents
from EventManager.EventSubscriptionController import EventSubscriptionController
from ConfigValidator.Config.Models.RunTableModel import RunTableModel
from ConfigValidator.Config.Models.FactorModel import FactorModel
from ConfigValidator.Config.Models.RunnerContext import RunnerContext
from ConfigValidator.Config.Models.OperationType import OperationType
from ExtendedTyping.Typing import SupportsStr
from ProgressManager.Output.OutputProcedure import OutputProcedure as output

from typing import Dict, List, Any, Optional
from pathlib import Path
from os.path import dirname, realpath
import time
import statistics
import requests

from UPISAS.strategies.switch_strategy import SwitchStrategy
from UPISAS.exemplars.switch import SWITCH_Elasticsearch
from UPISAS.exemplars.switch import SWITCH_Kibana
from UPISAS.exemplars.switch import SWITCH_Backend
from UPISAS.exemplars.switch import SWITCH_Frontend
from UPISAS.experiment_runner_configs.elastic import get_data_from_elastic

import pandas as pd

def upload_pics(file_path):
    print("Uploading files and starting processing...")

    # Determine the base directory of the script
    base_path = Path(__file__).resolve().parent.parent

    # Construct the paths dynamically
    zip_file_path = (base_path / file_path).resolve()
    csv_file_path = base_path / "images/intervals.csv"

    print("image path:", zip_file_path)

    #Upload the form data
    url = "http://localhost:3001/api/upload"
    files = {
        "zipFile": open(zip_file_path, "rb"),
        "csvFile": open(csv_file_path, "rb"),
    }
    data = {
        "approch": "NAIVE",  # Replace with the actual value of ⁠ selectedOption ⁠
        "folder_location": ""  # Replace with the actual value of ⁠ loc ⁠, or remove if None
    }

    # Send POST request
    response = requests.post(url, files=files, data=data)

    # Handle response
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

def SWITCH_bootup():
    #Sleep for 5 seconds give the system a bit of time
    time.sleep(5)
    #Run the scripts 
    print("Invoking process.py scripts...")
    url = "http://localhost:3001/execute-python-script"
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")

    print("Setting Naive model")
    url = "http://localhost:3001/useNaiveKnowledge"
    response = requests.post(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response Body: {response.text}")
    print("Waiting for switch to boot...")
    time.sleep(5)

def wait_for_connection():
    try:
        response = requests.get("http://localhost:8000/monitor")
        if response.status_code == 200:
            print("Success")
            print(response)
            return True
        else:
            print("Error")
            return False
    except Exception as e:
        return False


def unblock():
#Unblock the system rn
    f = open("./UPISAS/upisas.csv","w")
    f.seek(0)
    f.write("1")
    f.close()


class RunnerConfig:
    ROOT_DIR = Path(dirname(realpath(__file__)))

    # ================================ USER SPECIFIC CONFIG ================================
    """The name of the experiment."""
    name:                       str             = "new_runner_experiment"

    """The path in which Experiment Runner will create a folder with the name self.name, in order to store the
    results from this experiment. (Path does not need to exist - it will be created if necessary.)
    Output path defaults to the config file's path, inside the folder 'experiments'"""
    results_output_path:        Path            = ROOT_DIR / 'experiments'

    """Experiment operation type. Unless you manually want to initiate each run, use OperationType.AUTO."""
    operation_type:             OperationType   = OperationType.AUTO

    """The time Experiment Runner will wait after a run completes.
    This can be essential to accommodate for cooldown periods on some systems."""
    time_between_runs_in_ms:    int             = 1000

    exemplar = None
    strategy = None
    # Dynamic configurations can be one-time satisfied here before the program takes the config as-is
    # e.g. Setting some variable based on some criteria
    def __init__(self):
        """Executes immediately after program start, on config load"""
        output.console_log("executing init")

        EventSubscriptionController.subscribe_to_multiple_events([
            (RunnerEvents.BEFORE_EXPERIMENT, self.before_experiment),
            (RunnerEvents.BEFORE_RUN       , self.before_run       ),
            (RunnerEvents.START_RUN        , self.start_run        ),
            (RunnerEvents.START_MEASUREMENT, self.start_measurement),
            (RunnerEvents.INTERACT         , self.interact         ),
            (RunnerEvents.STOP_MEASUREMENT , self.stop_measurement ),
            (RunnerEvents.STOP_RUN         , self.stop_run         ),
            (RunnerEvents.POPULATE_RUN_DATA, self.populate_run_data),
            (RunnerEvents.AFTER_EXPERIMENT , self.after_experiment )
        ])
        self.run_table_model = None  # Initialized later

        output.console_log("Custom config loaded")

    def create_run_table_model(self) -> RunTableModel:
        output.console_log("executing create_run_table_model")
        """Create and return the run_table model here. A run_table is a List (rows) of tuples (columns),
        representing each run performed"""
        factor1 = FactorModel("rt_threshold", [0.75, 0.50, 0.25])
        self.run_table_model = RunTableModel(
            factors=[factor1],
            exclude_variations=[
            ],
            data_columns=['confidence','model_processing_time','image_processing_time','absolute_time_from_start','input_rate','model','average_confidence']
        )
        output.console_log("create_run_table_model executed")
        return self.run_table_model

    def before_experiment(self) -> None:
        output.console_log("executing before_experiment")
        """Perform any activity required before starting the experiment here
        Invoked only once during the lifetime of the program."""

        self.elasticsearch = SWITCH_Elasticsearch(auto_start=True)  
        self.kibana = SWITCH_Kibana(auto_start=True)
        self.exemplar = SWITCH_Backend(auto_start=True)
        self.front = SWITCH_Frontend(auto_start=True)
        self.strategy = SwitchStrategy(self.exemplar)
        
        while not wait_for_connection():
            print("Waiting for connection to open")
            time.sleep(5)

        SWITCH_bootup()

        output.console_log("Config.before_experiment() called!")


    def before_run(self) -> None:
        output.console_log("executing before_run")
        """Perform any activity required before starting a run.
        No context is available here as the run is not yet active (BEFORE RUN)"""
        # Attempt to initialize the exemplar and strategy
        
        # time.sleep(3)
        output.console_log("Config.before_run() called!")

    def start_run(self, context: RunnerContext) -> None:
        output.console_log("executing start_run")
        """Perform any activity required for starting the run here.
        For example, starting the target system to measure.
        Activities after starting the run should also be performed here."""

        urlArray = ["images/photos1.zip", "images/photos2.zip", "images/photos3.zip"]
        print("run_num: ", context.run_nr)
        upload_pics(urlArray[context.run_nr - 1])
        
        self.exemplar.start_run(self) #parameter should be App but its not used so i just put something so i dont get an error
        time.sleep(3)
        output.console_log("Config.start_run() called!")

    def start_measurement(self, context: RunnerContext) -> None:
        output.console_log("executing start_measurement")
        """Perform any activity required for starting measurements."""
        output.console_log("Config.start_measurement() called!")

    def interact(self, context: RunnerContext) -> None:
        output.console_log("executing interact")
        """Perform any interaction with the running target system here, or block here until the target finishes."""
        time_slept = 0
        self.strategy.get_monitor_schema()
        self.strategy.get_adaptation_options_schema()
        self.strategy.get_execute_schema()
        self.strategy.get_adaptation_options()
        
        

        while time_slept < 10:
            self.strategy.monitor(verbose=True)
            if self.strategy.analyze():
                adaptation = self.strategy.plan()
                if adaptation is not None:
                    self.strategy.execute(adaptation=adaptation)
                    unblock()
                    
            time.sleep(3)
            time_slept+=3


        output.console_log("Config.interact() called!")

    def stop_measurement(self, context: RunnerContext) -> None:
        output.console_log("executing stop_measurement")
        """Perform any activity here required for stopping measurements."""

        output.console_log("Config.stop_measurement called!")

    def stop_run(self, context: RunnerContext) -> None:
        output.console_log("executing stop_run")
        """Perform any activity here required for stopping the run.
        Activities after stopping the run should also be performed here."""
        output.console_log("Config.stop_run() called!")

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        output.console_log("executing populate_run_data")
        """Parse and process any measurement data here."""

        print("POPULATING DATA FIELDS")
        df = get_data_from_elastic()
        
        avg_confidence = df['confidence'].mean()  # Get the average confidence

        output.console_log("Config.populate_run_data() called!")

        filtered_df = df[['confidence', 'model_processing_time', 'image_processing_time', 'absolute_time_from_start']]
        
        return_dict = filtered_df.to_dict()

        return_dict['average_confidence'] = avg_confidence

        mon_data = self.strategy.knowledge.monitored_data
        return_dict.update(mon_data)
        
        print(return_dict)
        
        return return_dict

    def after_experiment(self) -> None:
        output.console_log("executing after_experiment")
        """Perform any activity required after stopping the experiment here
        Invoked only once during the lifetime of the program."""
        self.exemplar.stop_container()
        self.kibana.stop_container()
        self.elasticsearch.stop_container()
        self.front.stop_container()
        output.console_log("Config.after_experiment() called!")

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path:            Path             = None