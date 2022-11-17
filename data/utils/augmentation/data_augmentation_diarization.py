#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Juan Zuluaga-Gomez <jzuluaga@idiap.ch>
#
# SPDX-License-Identifier: MIT-License

"""
    Script to process data and apply data augmentation on the ATC dataset:
    In general, we apply data augmentation based on speaker labels. 
    We apply this augmenation on Either ATCO/PILOT 
    annotated data:
        1. Load the data with Huggingface load_dataset (data arrow)
        2. Get the tags and create two dictionaries with ATCO/Pilot sentences
        3. Go through these dictionaries and create new sentences
"""

import argparse
import os
import random
import sys


def extract_sentences_batch(dataset, utt_names="aug_data", min_sentence_len=3):
    """
    Extract a list of sentences with their respective tags.
    Each sentence is one speaker.
    We split the sentences by checking the 'B' in the tags.
    Each one demarks a new sentence.
    """

    #  if not isinstance(dataset, datasets.Dataset):
    #  return print('Error, please pass a datasets.Dataset in order to continue')

    max_lines = len(str(len(dataset))) + 1

    # Store the output dictionaries. One dictionary for each, pilot and atco
    sentence_tag_dict_atco = {}
    sentence_tag_dict_pilot = {}

    cnt = 0

    for utterance in dataset:
        sentence, tag_list = [], []  # Store the sentence

        # fetch/process i-th sample from dataset. [0] is utt_id, discard
        utterance = utterance.rstrip().split(";")
        text = utterance[1].rstrip().split(" ")
        tags = utterance[2].rstrip().split(",")

        # 'B-*' flag, either Pilot/ATCO
        b_flag = False
        # go throughtout each word
        for word, i_tag in zip(text, tags):
            # If this True, that means there is a second or third or ,..., sentence
            if b_flag == True and "B-" in i_tag:
                b_flag = False

                # check whether the sentence is longer than n-number of words
                if len(sentence) < min_sentence_len:
                    continue
                assert len(sentence) == len(
                    tag_list
                ), "The len() of sentence and tag list is not the same."
                # format utt_id name per each sample
                utt_id = "{}_{}".format(utt_names, str(cnt).zfill(max_lines))

                # Splitting the results depeding on the speaker
                sentence = " ".join(sentence)
                tag_list = ",".join(tag_list)
                if "atco" in tag_list:
                    sentence_tag_dict_atco[f"{utt_id}_atco"] = [sentence, tag_list]
                elif "pilot" in tag_list:
                    sentence_tag_dict_pilot[f"{utt_id}_pilot"] = [sentence, tag_list]

                sentence, tag_list = [], []
                cnt += 1

            if "B-" in i_tag:
                b_flag = True
            sentence.append(word)
            tag_list.append(i_tag)

        if len(sentence) > 0:
            # check whether the sentence is longer than n-number of words
            if len(sentence) < min_sentence_len:
                continue
            assert len(sentence) == len(
                tag_list
            ), "The len() of sentence and tag list is not the same."

            # format utt_id name per each sample
            utt_id = "{}_{}".format(utt_names, str(cnt).zfill(max_lines))
            # Splitting the results depeding on the speaker
            sentence = " ".join(sentence)
            tag_list = ",".join(tag_list)
            if "atco" in tag_list:
                sentence_tag_dict_atco[f"{utt_id}_atco"] = [sentence, tag_list]
            elif "pilot" in tag_list:
                sentence_tag_dict_pilot[f"{utt_id}_pilot"] = [sentence, tag_list]

        sentence, tag_list = [], []
        cnt += 1

    return sentence_tag_dict_atco, sentence_tag_dict_pilot


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--seed", type=int, default=1234, help="Seed for random")
    parser.add_argument(
        "--new-samples",
        type=int,
        default=1000,
        help="number of new utterances from the training dictionary",
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default="data_augmented",
        help="Suffix for each new sample in the new dataset <suffix_xxxx>",
    )

    parser.add_argument(
        "input_file",
        help="Input file with the speaker tags: The format used is: utt2text_tags <utt_id>;<text>;<tags>",
    )
    parser.add_argument(
        "output_file",
        help="Output folder with the speaker tags: The format to output is: utt2text_tags <utt_id>;<text>;<tags>",
    )

    return parser.parse_args()


def main(args):
    """main function to process data and save it in output_file"""

    # setting the seeds
    random.seed(args.seed)

    # define CLI variables
    text_tags = args.input_file
    output_dir = args.output_file

    # define some default vars
    samples_to_produce = args.new_samples
    utt_names = args.suffix

    # create the output directory
    os.makedirs(output_dir, exist_ok=True)

    # extracting the lists from training data
    f = open(text_tags, "r")
    atco_dict, pilot_dict = extract_sentences_batch(f.readlines(), utt_names=utt_names)

    # opening the output files:
    utt2text_tags_augmented = open(output_dir + "/utt2text_tags", "w")

    max_lines = len(str(samples_to_produce)) + 1  # number of digits

    # Getting the number of sentences per new utterance,
    # We do it only once for the sake of simplicity
    max_snt_per_utt = 2
    # the weights are the 'probabilities' of getting that number of sentences:
    # for 1 is 40%, 2 is 30%, 3 is 20%, etc
    list_sent_length = random.choices(
        list(range(1, max_snt_per_utt + 1)), weights=(70, 30), k=samples_to_produce
    )
    #  weights=(45, 35, 10, 5, 5), k=samples_to_produce)

    cnt = 0
    # The *for loop* already carries the number of sentences per new sample
    for lines, nb_sentences in zip(range(samples_to_produce), list_sent_length):
        selected_sentences, selected_tags = [], []

        # format utt_id name per each sample
        utt_id = "{}_{}".format(utt_names, str(cnt).zfill(max_lines))
        extra_id = "_"

        # fetch randomly from our defined dicts
        for i in range(nb_sentences):

            # select either True or False to pick from ATCO or PILOT sets
            flag = random.sample([True, False], 1)[0]
            if flag == True:
                extra_id += "C"
                _, sample_ = random.choice(list(atco_dict.items()))
            else:
                extra_id += "P"
                _, sample_ = random.choice(list(pilot_dict.items()))
            selected_sentences.append(sample_[0])
            selected_tags.append(sample_[1])

        # convert output lists to one new string: composed of 1 or more sentences
        selected_sentences = " ".join(selected_sentences)
        selected_tags = ",".join(selected_tags)

        # updating the utt_id with the speakers present in the new sample
        utt_id = utt_id + extra_id
        cnt += 1

        #  writing the output line in the file:
        line_to_write = f"{utt_id};{selected_sentences};{selected_tags}\n"
        utt2text_tags_augmented.write(line_to_write)

        if lines % 10000 == 0:
            print("Creating sample number: ", lines)

    # closing the files to avoid errors,
    utt2text_tags_augmented.close()

    return print("finished creating the samples in: ", output_dir)


if __name__ == "__main__":
    args = parse_args()
    main(args)
    sys.exit(0)
