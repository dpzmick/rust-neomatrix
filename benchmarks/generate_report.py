#!/usr/bin/env python2
from collections import defaultdict
from matplotlib.backends.backend_pdf import PdfPages
import argparse
import csv
import matplotlib.pyplot as plt
import numpy as np
import os

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark report generator")
    parser.add_argument("input_dir", help="Directory containing benchmark CSVs")
    parser.add_argument("output_dir",
                        help="Directory in which output files generated")

    args = parser.parse_args()

    data = defaultdict(list)
    for file in os.listdir(args.input_dir):
        full_path = os.path.join(args.input_dir, file)

        if not os.path.isfile(full_path): continue
        split = os.path.splitext(os.path.basename(file))
        benchmark_pass = split[0]
        if split[1] != ".csv": continue

        with open(full_path, 'rb') as f:
            reader = csv.DictReader(f)
            for row in reader:
                pass_row = {"benchmark_pass": benchmark_pass}
                benchmark_data = data[row['test_name']]
                benchmark_data.append(pass_row)

                for k, v in row.iteritems():
                    if k == "test_name": continue
                    # ask forgives, not permission
                    try:
                        pass_row[k] = int(v)
                    except ValueError:
                        pass_row[k] = v

    plt.style.use("seaborn")
    pdf_pages = PdfPages(os.path.join(args.output_dir, "report.pdf"))

    i = 0
    c = (0,0)
    grid_size = (3,3)
    plots_per_page = grid_size[0] * grid_size[1]
    for benchmark, d in data.iteritems():
        if i % plots_per_page == 0:
            # create a new page
            fig = plt.figure(figsize=(11.69, 8.27), dpi=100)

        bar_width = 0.35

        pass_labels = []
        pass_nanos = []
        pass_var = []

        for e in d:
            p = e['benchmark_pass']
            pass_labels.append(p)
            pass_nanos.append(e['nanoseconds'])
            pass_var.append(e['variance'])

        index = np.arange(len(pass_labels))

        plt.subplot2grid(grid_size, c)
        plt.title(benchmark)
        plt.barh(index, pass_nanos, xerr=np.sqrt(pass_var))
        plt.yticks(index, pass_labels)
        plt.xticks(rotation=-15)

        if (c[1] + 1) % grid_size[1] == 0:
            c = (c[0] + 1, 0)
        else:
            c = (c[0], c[1] + 1)

        if (i + 1) % plots_per_page == 0 or (i + 1) == len(data):
            plt.tight_layout()
            pdf_pages.savefig(fig)
            c = (0, 0)

        i += 1

    pdf_pages.close()
