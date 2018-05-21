import numpy as np


def main():
    ts = generate_random_time_series(50000)
    write_to_file(ts, '/home/orphefs/Documents/Code/rolling_statistics/cpp/data/test2/in.txt')


def write_to_file(ts, path_to_file):
    with open(path_to_file, 'w') as outfile:
        for index, item in np.ndenumerate(ts):
            outfile.write("{},{}\n".format(index[0], item))


def generate_random_time_series(length):
    return np.random.normal(10, 2, length)


if __name__ == '__main__':
    main()
