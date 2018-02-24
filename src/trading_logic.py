def get_heading(heading: float):
    if heading > 0:
        return 'Heading Up'
    else:
        return 'Heading Down'


def get_trend(trend: float):
    if trend > 0:
        return "Uptrend"
    else:
        return "Downtrend"
