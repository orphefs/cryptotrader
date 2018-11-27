import glob
import os
from collections import defaultdict
from typing import List
import pandas as pd

from src.analysis_tools.generate_run_statistics import compute_all_statistics
from src.containers.portfolio import Portfolio
from src.definitions import DATA_DIR
from src.type_aliases import Path


def scan_folder(path_to_folder: Path) -> List[Path]:
    return [path_to_file for path_to_file in glob.glob(os.path.join(
        path_to_folder, "portfolio*.dill"))]


def assemble_dataframe(paths_to_portfolios: List[Path]) -> pd.DataFrame:
    d = defaultdict(list)
    for path_to_portfolio in paths_to_portfolios:
        print("Analyzing portfolio {}".format(path_to_portfolio))
        order_pairs, percentage_gains, index_performance, \
        classifier_time_window, testing_time_window = compute_all_statistics(path_to_portfolio)
        d["training_time_start"].append(classifier_time_window.start_datetime)
        d["training_time_end"].append(classifier_time_window.end_datetime)
        d["training_duration_days"].append(classifier_time_window.duration.total_seconds()/(24* 3600))
        d["testing_time_start"].append(testing_time_window.start_datetime)
        d["testing_time_end"].append(testing_time_window.end_datetime)
        d["testing_duration_days"].append(testing_time_window.duration.total_seconds()/(24*3600))
        d["index_performance"].append(index_performance.gains)
        d["percentage_gains"].append(percentage_gains.gains)
        net_gains = percentage_gains.gains - index_performance.gains
        d["net_gains"].append(net_gains)
        d["net_gains_per_day"].append(net_gains / (
                testing_time_window.duration.total_seconds() / (24*3600)))

    return pd.DataFrame(d)


def analyze_batch_run():
    paths_to_portfolios = scan_folder(DATA_DIR)
    df = assemble_dataframe(paths_to_portfolios)
    df.to_pickle(os.path.join(DATA_DIR, "batch_results.pkl"))
    print(df)


if __name__ == '__main__':
    analyze_batch_run()
