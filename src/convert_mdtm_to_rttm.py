#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Seyyed Saeed Sarfjoo <saeed.sarfjoo@idiap.ch>
#
# SPDX-License-Identifier: MIT-License
import argparse
import os
import shutil
import sys
from glob import glob

import numpy as np


def main():

    parser = argparse.ArgumentParser(description="Convert mdtm files to rttm")
    parser.add_argument("-i", "--input", required=True, help="The input mdtm file.")
    parser.add_argument("-o", "--output", required=True, help="The output rttm file.")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print("Input file does not exist!")

    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w") as wf:
        with open(args.input) as inf:
            lines = inf.readlines()
            for i, line in enumerate(lines):
                lineparts = line.strip().split()
                wf.write(
                    "SPEAKER "
                    + lineparts[0]
                    + " "
                    + lineparts[1]
                    + " "
                    + lineparts[2]
                    + " "
                    + lineparts[3]
                    + " <NA> <NA> "
                    + lineparts[7]
                    + " <NA> <NA>"
                    + os.linesep
                )
                if i % 1000 == 0:
                    sys.stdout.flush()


if __name__ == "__main__":
    main()
