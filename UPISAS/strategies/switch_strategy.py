from UPISAS.strategy import Strategy
import time

class SwitchStrategy(Strategy):

    def analyze(self):
        data = self.knowledge.monitored_data

        input_rate = data["input_rate"][-1]  # Use the latest value
        model = data["model"][-1]

        model = str(model).replace('[', '').replace(']', '').replace("'", '')

        str_min = model + "_rate_min"
        str_max = model + "_rate_max"
        current_time = time.time()

        # get's the minimum and maximum threshold values for the current working model.

        min_val = self.knowledge.adaptation_options[str_min]
        max_val = self.knowledge.adaptation_options[str_max]

        print("in_rate: ", input_rate)

        if ((max_val >= input_rate and min_val <= input_rate) == False):

            if (self.time == -1):
                self.time = current_time
            # if threshold sre violated for more than 0.25 sec, we create planner object to obtain the adaptation plan
            elif (current_time - self.time > 0.25):

                self.count += 1
                print("<25s true")
                return True
                # logger.info(    {'Component': "Analyzer" , "adaptation": "Creating Planner object" }  ) 
                # plan_obj = Planner(input_rate, model)
                # plan_obj.generate_adaptation_plan(self.count)

        else:
            self.time = -1
        print("return true")
        return True

    def plan(self):

        adaptation = ''
        
        # df = pd.read_csv('knowledge.csv', header=None)
        # array = df.to_numpy()

        in_rate = self.knowledge.monitored_data["input_rate"][-1]

        print("knowledge: ", self.knowledge)
        

        #check's which model's thershold range is input rate within and accordingly determines the adaptation.
        # logger.info(    {'Component': "Planner" , "adaptation": "Generating the adaptation plan" } )

        print("plan data: ", self.knowledge.plan_data)

        if( in_rate >= self.knowledge.adaptation_options["yolov5n_rate_min"] and in_rate <= self.knowledge.adaptation_options["yolov5n_rate_max"]):
            adaptation = {"option": "yolov5n_rate_min", "new_value": in_rate}
        elif( in_rate >= self.knowledge.adaptation_options["yolov5s_rate_min"] and in_rate <= self.knowledge.adaptation_options["yolov5s_rate_max"] ):
             adaptation = {"option": "yolov5s_rate_min", "new_value": in_rate}
        elif( in_rate >= self.knowledge.adaptation_options["yolov5m_rate_min"] and in_rate <= self.knowledge.adaptation_options["yolov5m_rate_max"] ):
             adaptation = {"option": "yolov5m_rate_min", "new_value": in_rate}
        elif( in_rate >= self.knowledge.adaptation_options["yolov5l_rate_min"] and in_rate <= self.knowledge.adaptation_options["yolov5l_rate_max"] ):
             adaptation = {"option": "yolov5l_rate_min", "new_value": in_rate}
        elif ( in_rate >= self.knowledge.adaptation_options["yolov5x_rate_min"]  and in_rate <= self.knowledge.adaptation_options["yolov5x_rate_max"]  ) : #and in_rate < array[4][2]
             adaptation = {"option": "yolov5x_rate_min", "new_value": in_rate}
        else:
            # logger.error(    {'Component': "Planner" , "adaptation": "No adaptation plan generated" }  ) 
            print("No adaptation plan generated")
            return
        
        return adaptation