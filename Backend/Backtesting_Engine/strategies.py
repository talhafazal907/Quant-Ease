class Ema_cross_over:
    def __init__(self, ema_short : int, ema_long : int, risk : float, reward : float):
        self.name = "double-ema"
        self.ema_short = ema_short
        self.ema_long = ema_long
        self.risk = risk
        self.reward = reward

class VWAP:
    def __init__(self):
        pass

    