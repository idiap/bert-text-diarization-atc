#!/usr/bin/env python3
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Seyyed Saeed Sarfjoo <saeed.sarfjoo@idiap.ch>
#
# SPDX-License-Identifier: MIT-License
import argparse
import os
import sys
from glob import glob

import numpy as np


def main():

    parser = argparse.ArgumentParser(
        description="Create mdtm format diarization segments from NER and ASR hypothesis"
    )
    parser.add_argument(
        "-hp", "--hypothesis", required=True, help="ASR hypothesis in .ctm format."
    )
    parser.add_argument(
        "-t", "--tags", required=True, help="NER tags for ASR hypothesis"
    )
    parser.add_argument(
        "-s", "--segments", required=True, help="Kaldi format segment file"
    )
    parser.add_argument(
        "-o",
        "--output-file",
        default="output.mdtm",
        help="Output file address (Default: 'output.mdtm').",
    )
    parser.add_argument(
        "-sc",
        "--scale",
        type=int,
        default=1,
        help="If set scale the segment duration based on this patameter (Default: 1).",
    )

    args = parser.parse_args()
    for name in [args.hypothesis, args.tags, args.segments]:
        if not os.path.exists(name):
            print(name + " does not exist!")
            return
    seg_dic = {}
    tag_dic = {}
    with open(args.segments) as rf:
        lines = rf.readlines()
        for line in lines:
            line_parts = line.strip().split()
            seg_dic[line_parts[0]] = (float(line_parts[2]), float(line_parts[3]))
    with open(args.tags) as rf:
        lines = rf.readlines()
        for line in lines:
            line_parts = line.strip().split(";")
            words = line_parts[1].split()
            tags = line_parts[2].split(",")
            assert len(words) == len(
                tags
            ), "Number of words are different from number of tags"

            rem_idx = []
            # fix mismatch between NLP tags and CTM text
            for j in range(len(words)):
                if (
                    (words[j] == "'" or words[j] == "-")
                    and j > 0
                    and j < len(words) - 1
                ):
                    rem_idx.append(j)
                    rem_idx.append(j + 1)
                    words[j - 1] += words[j] + words[j + 1]
                if words[j] == ")" and j < len(words) - 1:
                    if j > 0 and words[j - 1] == "o":
                        pass
                    else:
                        rem_idx.append(j)
                        words[j + 1] = words[j] + words[j + 1]

            offset = 0
            for k in rem_idx:
                del words[k - offset]
                del tags[k - offset]
                offset += 1

            tag_dic[line_parts[0]] = []
            for i in range(len(words)):
                tag_dic[line_parts[0]].append((words[i], tags[i]))

    with open(args.output_file, "w") as wf:
        with open(args.hypothesis) as hf:
            lines = hf.readlines()
            prev_key = ""
            wrd_idx = 0
            prev_tag = ""
            seg_start = 0.0
            prev_wrd_end = 0.0
            for j, line in enumerate(lines):
                line_parts = line.strip().split()
                if line_parts[0] != prev_key:
                    if prev_key != "":
                        seg_end = seg_dic[prev_key][1]
                        wf.write(
                            prev_key
                            + " 1 "
                            + str(seg_start)
                            + " "
                            + str(seg_end - seg_start)
                            + " speaker NA unknown "
                            + prev_tag.replace("B-", "").replace("I-", "")
                            + os.linesep
                        )
                    prev_key = line_parts[0]
                    wrd_idx = 0
                    prev_tag = tag_dic[prev_key][0][1]
                    seg_start = 0.0
                    if line_parts[4] == "<unk>" or line_parts[4] == "<gbg>":
                        wrd_idx -= 1
                else:
                    wrd_idx += 1
                    if line_parts[4] != "<unk>" and line_parts[4] != "<gbg>":
                        assert (
                            tag_dic[prev_key][wrd_idx][0].lower()
                            == line_parts[4].lower()
                        ), "Mismatch in words and tags %s %s %s" % (
                            line_parts[0],
                            tag_dic[prev_key][wrd_idx][0],
                            line_parts[4],
                        )
                        if tag_dic[prev_key][wrd_idx][1].startswith("B") or (
                            tag_dic[prev_key][wrd_idx][1]
                            .replace("B-", "")
                            .replace("I-", "")
                            .lower()
                            != prev_tag.replace("B-", "").replace("I-", "").lower()
                            and prev_tag != ""
                        ):
                            seg_end = (
                                (prev_wrd_end + float(line_parts[2])) * args.scale / 2
                            )
                            wf.write(
                                prev_key
                                + " 1 "
                                + str(seg_start)
                                + " "
                                + str(seg_end - seg_start)
                                + " speaker NA unknown "
                                + prev_tag.replace("B-", "").replace("I-", "")
                                + os.linesep
                            )
                            seg_start = seg_end
                            prev_tag = tag_dic[prev_key][wrd_idx][1]
                    else:
                        wrd_idx -= 1
                prev_wrd_end = float(line_parts[2]) + float(line_parts[3])
            # apply for the last seg
            seg_end = seg_dic[prev_key][1]
            wf.write(
                prev_key
                + " 1 "
                + str(seg_start)
                + " "
                + str(seg_end - seg_start)
                + " speaker NA unknown "
                + prev_tag.replace("B-", "").replace("I-", "")
                + os.linesep
            )


if __name__ == "__main__":
    main()
