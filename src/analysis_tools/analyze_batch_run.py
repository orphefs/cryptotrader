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
        run_statistics = compute_all_statistics(path_to_portfolio)

        d["training_time_start"].append(run_statistics.classifier_time_window.start_datetime)
        d["training_time_end"].append(run_statistics.classifier_time_window.end_datetime)
        d["training_duration_days"].append(
            run_statistics.classifier_time_window.duration.total_seconds() / (24 * 3600))
        d["testing_time_start"].append(run_statistics.testing_time_window.start_datetime)

        # TODO: investigate why .testing_time_window.end_datetime is not of type datetime
        d["testing_time_end"].append(run_statistics.testing_time_window.end_datetime)
        d["testing_duration_days"].append(
            run_statistics.testing_time_window.duration.total_seconds() / (24 * 3600))
        d["index_performance"].append(run_statistics.index_performance.gains)
        d["percentage_gains"].append(run_statistics.percentage_gains.gains)
        net_gains = run_statistics.percentage_gains.gains - run_statistics.index_performance.gains
        d["net_gains"].append(net_gains)
        d["net_gains_per_day"].append(net_gains / (
                run_statistics.testing_time_window.duration.total_seconds() / (24 * 3600)))

    return pd.DataFrame(d)


def analyze_batch_run():
    paths_to_portfolios = scan_folder(DATA_DIR)
    df = assemble_dataframe(paths_to_portfolios)
    df.to_pickle(os.path.join(DATA_DIR, "batch_results.pkl"))
    print(df)


if __name__ == '__main__':
    analyze_batch_run()
