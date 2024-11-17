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

from UPISAS.strategies.switch_strategy import SwitchStrategy
from UPISAS.exemplars.switch import SWITCH_Elasticsearch
from UPISAS.exemplars.switch import SWITCH_Kibana
from UPISAS.exemplars.switch import SWITCH_Backend
from UPISAS.exemplars.switch import SWITCH_Frontend


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
            data_columns=['utility']
        )
        output.console_log("create_run_table_model executed")
        return self.run_table_model

    def before_experiment(self) -> None:
        output.console_log("executing before_experiment")
        """Perform any activity required before starting the experiment here
        Invoked only once during the lifetime of the program."""

        output.console_log("Config.before_experiment() called!")


    def before_run(self) -> None:
        output.console_log("executing before_run")
        """Perform any activity required before starting a run.
        No context is available here as the run is not yet active (BEFORE RUN)"""
        # Attempt to initialize the exemplar and strategy

        exemplar_elasticsearch = SWITCH_Elasticsearch(auto_start=True)  
        exemplar_kibana = SWITCH_Kibana(auto_start=True)
        self.exemplar = SWITCH_Backend(auto_start=True)
        exemplar_front = SWITCH_Frontend(auto_start=True)

        self.strategy = SwitchStrategy(self.exemplar)
        
        time.sleep(180)

        # if not exemplar_elasticsearch.is_running():
        #     output.console_log("Elasticsearch is not running.")

        # if not exemplar_kibana.is_running():
        #     output.console_log("Kibana is not running.")

        # if not self.exemplar.is_running():
        #     output.console_log("Backend is not running.")

        # if not exemplar_front.is_running():
        #     output.console_log("Frontend is not running.")
        
        # time.sleep(3)
        output.console_log("Config.before_run() called!")

    def start_run(self, context: RunnerContext) -> None:
        output.console_log("executing start_run")
        """Perform any activity required for starting the run here.
        For example, starting the target system to measure.
        Activities after starting the run should also be performed here."""
        self.strategy.RT_THRESHOLD = float(context.run_variation['rt_threshold'])

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

        

        while time_slept < 10:
            self.strategy.get_adaptation_options()
            self.strategy.monitor(verbose=True)
            if self.strategy.analyze():
                if self.strategy.plan():
                    self.strategy.execute()

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
        self.exemplar.stop_container()
        output.console_log("Config.stop_run() called!")

    def populate_run_data(self, context: RunnerContext) -> Optional[Dict[str, SupportsStr]]:
        output.console_log("executing populate_run_data")
        """Parse and process any measurement data here.
        You can also store the raw measurement data under context.run_dir
        Returns a dictionary with keys self.run_table_model.data_columns and their values populated"""

        output.console_log("Config.populate_run_data() called!")

        basicRevenue = 1
        optRevenue = 1.5
        serverCost = 10
        
        precision = 1e-5
        mon_data = self.strategy.knowledge.monitored_data
        utilities = []
        print("MON DATA")
        print(mon_data)
        for i in range(len(mon_data["max_servers"])):

            maxServers = int(mon_data["max_servers"][i])
            arrivalRateMean = mon_data["arrival_rate"][i]
            dimmer = mon_data["dimmer_factor"][i]
            maxThroughput = maxServers * self.strategy.MAX_SERVICE_RATE
            avgServers = mon_data["servers"][i]
            avgResponseTime = (mon_data["basic_rt"][i] * mon_data["basic_throughput"][i] + mon_data["opt_rt"][i] * mon_data["opt_throughput"][i]) / (mon_data["basic_throughput"][i] + mon_data["opt_throughput"][i])

            Ur = (arrivalRateMean * ((1 - dimmer) * basicRevenue + dimmer * optRevenue))
            Uc = serverCost * (maxServers - avgServers)
            UrOpt = arrivalRateMean * optRevenue
            utility = 0

            if(avgResponseTime <= self.strategy.RT_THRESHOLD and Ur >= UrOpt - precision):
                utility = Ur + Uc
            else:                
                if(avgResponseTime <= self.strategy.RT_THRESHOLD):
                    utility = Ur
                else:
                    utility = min(0.0, arrivalRateMean - maxThroughput) * optRevenue
            utilities.append(utility)
        
        return {"utility" : utilities}

    def after_experiment(self) -> None:
        output.console_log("executing after_experiment")
        """Perform any activity required after stopping the experiment here
        Invoked only once during the lifetime of the program."""
        output.console_log("Config.after_experiment() called!")

    # ================================ DO NOT ALTER BELOW THIS LINE ================================
    experiment_path:            Path             = None