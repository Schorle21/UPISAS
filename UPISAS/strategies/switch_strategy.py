from UPISAS.strategy import Strategy


class SwitchStrategy(Strategy):

    def analyze(self):
        return True

    def plan(self):
        return True
