from UPISAS.strategy import Strategy
import time

class SwitchStrategy(Strategy):

    def _init_(self, exemplar):
        super()._init_(exemplar)
        self.time = -1
        self.count = 0


    def analyze(self):
        data = self.knowledge.monitored_data

        input_rate = data["input_rate"][-1]  # Use the latest value
        model = data["model"][-1]

        model = str(model).replace('[', '').replace(']', '').replace("'", '')

        str_min = model + "_rate_min"
        str_max = model + "_rate_max"
        current_time = time.time()

        # Get the minimum and maximum threshold values for the current working model.
        min_val = self.knowledge.adaptation_options[str_min]
        max_val = self.knowledge.adaptation_options[str_max]

        print("in_rate: ", input_rate)

        if not (min_val <= input_rate <= max_val):
            if self.time == -1:
                self.time = current_time
            elif current_time - self.time > 0.25:
                self.count += 1
                return True
        else:
            self.time = -1
        return True

    def determine_adaptation(self, model, in_rate):
        min_key = f"{model}_rate_min"
        max_key = f"{model}_rate_max"
        min_val = self.knowledge.adaptation_options[min_key]
        max_val = self.knowledge.adaptation_options[max_key]

        if in_rate < min_val:
            return {"option": min_key, "new_value": in_rate}
        elif in_rate > max_val:
            return {"option": max_key, "new_value": in_rate}
        else:
            # Determine which threshold to adjust based on proximity
            if abs(in_rate - min_val) < abs(in_rate - max_val):
                return {"option": min_key, "new_value": in_rate}
            else:
                return {"option": max_key, "new_value": in_rate}

    def plan(self):
        print("Entering plan method")

        adaptation = None
        
        in_rate = self.knowledge.monitored_data["input_rate"][-1]
        print("in_rate:", in_rate)

        print("knowledge:", self.knowledge)

        # Check which model's threshold range the input rate is within and accordingly determine the adaptation.
        print("plan data:", self.knowledge.plan_data)

        if in_rate >= self.knowledge.adaptation_options["yolov5n_rate_min"] and in_rate <= self.knowledge.adaptation_options["yolov5n_rate_max"]:
            adaptation = self.determine_adaptation("yolov5n", in_rate)
        elif in_rate >= self.knowledge.adaptation_options["yolov5s_rate_min"] and in_rate <= self.knowledge.adaptation_options["yolov5s_rate_max"]:
            adaptation = self.determine_adaptation("yolov5s", in_rate)
        elif in_rate >= self.knowledge.adaptation_options["yolov5m_rate_min"] and in_rate <= self.knowledge.adaptation_options["yolov5m_rate_max"]:
            adaptation = self.determine_adaptation("yolov5m", in_rate)
        elif in_rate >= self.knowledge.adaptation_options["yolov5l_rate_min"] and in_rate <= self.knowledge.adaptation_options["yolov5l_rate_max"]:
            adaptation = self.determine_adaptation("yolov5l", in_rate)
        elif in_rate >= self.knowledge.adaptation_options["yolov5x_rate_min"] and in_rate <= self.knowledge.adaptation_options["yolov5x_rate_max"]:
            adaptation = self.determine_adaptation("yolov5x", in_rate)
        else:
            print("No adaptation plan generated")
            return None
        
        print("Generated adaptation:", adaptation)
        self.knowledge.plan_data = adaptation
        return adaptation