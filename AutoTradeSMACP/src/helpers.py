# function computes SMA and EMA based on period fed to it
def simple_moving_average(p, closing_prices):
    SMA = []
    EMA = []
    for i in range(p - 1, len(closing_prices)):
        M = 2 / (p + 1)
        SMA.append((sum(closing_prices[i - p + 1:i + 1])) / p)
        EMA.append((closing_prices[i] - (EMA[i - 1])) * M + EMA[i - 1])

    return SMA, EMA