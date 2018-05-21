import numpy as np


def generate_time_series(length):
    return np.random.normal(10, 1, length)


def compute_mean(time_series, window_length):
    # return [np.mean(time_series[i*window_length:(i+1)*window_length])
    #         for i in range(0,len(time_series)//window_length)]
    means = []
    m_new = 0
    for i in range(0, len(time_series)):
        if i >= window_length:
            m_new = np.mean(time_series[(i - window_length):i])
            means.append(m_new)
    return means


def compute_rolling_mean(time_series, window_length):
    m = np.mean(time_series[0:window_length])
    means = []
    means.append(m)
    for i in range(0, len(time_series)):
        if i >= window_length:
            m_new = m + (1 / (window_length)) * (time_series[i] - time_series[i - window_length])
            means.append(m_new)
            m = m_new
    return means


def compute_variance(time_series, window_length):
    variances = []
    v_new = 0
    for i in range(0, len(time_series)):
        if i >= window_length:
            v_new = np.var(time_series[(i - window_length):i])
            variances.append(v_new)
    return variances


def compute_rolling_variance(time_series, window_length):
    m = np.mean(time_series[0:window_length])
    # s = np.sum(time_series[0:window_length])
    means = []
    means.append(m)
    v = np.var(time_series[0:window_length])
    variances = []
    variances.append(v)
    for i in range(0, len(time_series)):
        if i >= window_length:
            m_new = m + (1 / (window_length)) * (time_series[i] - time_series[i - window_length])
            v_new = v + m**2 + (1/window_length)* (time_series[i]**2 - time_series[i - window_length]**2) - m_new**2
            m = m_new
            v = v_new
            variances.append(v_new)

    return variances


def main():
    length = 100
    window_length = 10
    ts = generate_time_series(length)
    means = compute_mean(ts, window_length)
    variances = compute_variance(ts, window_length)
    rolling_means = compute_rolling_mean(ts, window_length)
    rolling_variances = compute_rolling_variance(ts, window_length)

    print(means)
    print(len(means))
    print(rolling_means)
    print(len(rolling_means))


    print(variances)
    print(len(variances))
    print(rolling_variances)
    print(len(rolling_variances))



if __name__ == '__main__':
    main()
