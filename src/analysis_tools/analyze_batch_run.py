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


def assemble_dataframe(paths_to_portfolios: List[Path]) ->  pd.DataFrame:
    d = defaultdict(list)
    for path_to_portfolio in paths_to_portfolios:
        order_pairs, percentage_gains, index_performance, \
        classifier_time_window, testing_time_window = compute_all_statistics(path_to_portfolio)
        d["training_time_window"].append(classifier_time_window)
        d["training_duration"].append(classifier_time_window.duration)
        d["testing_time_window"].append(testing_time_window)
        d["testing_duration"].append(testing_time_window.duration)
        d["index_performance"].append(index_performance.gains)
        d["percentage_gains"].append(percentage_gains.gains)
        d["net_gains"].append(percentage_gains.gains - index_performance.gains)
    return pd.DataFrame(d)


def main():
    paths_to_portfolios = scan_folder(DATA_DIR)
    df = assemble_dataframe(paths_to_portfolios)
    print(df)

if __name__ == '__main__':
    main()
