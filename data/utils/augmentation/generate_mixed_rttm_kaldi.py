#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Juan Zuluaga-Gomez <jzuluaga@idiap.ch>
#
# SPDX-License-Identifier: MIT-License

"""
    Script that receives a KALDI formatted folder and creates a new folder with
    RTTM labels. We do:
        1. Load the data and split by speaker, ATCO or pilot
        2. create dictionaries for each speaker
        3. Sample from the dictionary and concatenate the respective WAV files
        4. Create a new test set with the concatenated files

    This script only works on datasets that have one speaker per sentence, either
    ATCO or pilot

    RTTM format for ATCO,
        # SPEAKER 2020-11-25__15-11-14-47_P 1 0.0 2.1750625 <NA> <NA> atco <NA> <NA> 
        or for pilot,
        # SPEAKER 2020-11-25__15-11-14-47_P 1 0.0 2.1750625 <NA> <NA> pilot <NA> <NA> 

"""

import argparse
import os
import random
import shutil
import sys

import numpy as np
import torch
import torchaudio
import torchaudio.transforms as T


def extract_sentences_batch(dataset, utt_names="aug_data", min_sentence_len=3):
    """
    Extract a list of sentences with their respective tags.
    Each sentence is one speaker.
    We split the sentences by checking the 'B' in the tags.
    Each one demarks a new sentence.
    """

    max_lines = len(str(len(dataset))) + 1

    # Store the output dictionaries. One dictionary for each, pilot and atco
    sentence_tag_dict_atco = {}
    sentence_tag_dict_pilot = {}

    cnt = 0

    for utterance in dataset:
        sentence, tag_list = [], []  # Store the sentence

        # fetch/process i-th sample from dataset. [0] is utt_id, discard
        utterance = utterance.rstrip().split(";")
        identifier = utterance[0]
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
                    sentence_tag_dict_atco[f"{utt_id}_atco"] = [
                        identifier,
                        sentence,
                        tag_list,
                    ]
                elif "pilot" in tag_list:
                    sentence_tag_dict_pilot[f"{utt_id}_pilot"] = [
                        identifier,
                        sentence,
                        tag_list,
                    ]

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
                sentence_tag_dict_atco[f"{utt_id}_atco"] = [
                    identifier,
                    sentence,
                    tag_list,
                ]
            elif "pilot" in tag_list:
                sentence_tag_dict_pilot[f"{utt_id}_pilot"] = [
                    identifier,
                    sentence,
                    tag_list,
                ]

        sentence, tag_list = [], []
        cnt += 1

    return sentence_tag_dict_atco, sentence_tag_dict_pilot


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("-s", "--seed", type=int, default=1234, help="Seed for random")
    parser.add_argument(
        "--wav-extension",
        type=str,
        default="sph",
        help="extension of the audio file. Default: sph",
    )
    parser.add_argument(
        "--sampling-rate",
        type=int,
        default=16000,
        help="Sampling rate for the new audio to create. Default=16000 Hz",
    )
    parser.add_argument(
        "--min-sentence-len",
        type=int,
        default=2,
        help="number of minimum words per sentence. Default=2",
    )
    parser.add_argument(
        "--suffix",
        type=str,
        default="data_augmented",
        help="Suffix for each new sample in the new dataset <suffix_xxxx>",
    )

    parser.add_argument(
        "input_folder",
        help="Input folder in Kaldi format, should have text, wav.scp and segments file",
    )
    parser.add_argument(
        "output_folder",
        help="Output folder in Kaldi format, will contain new text, wav.scp and segments file",
    )

    return parser.parse_args()


def main(args):
    """main function to process data and save it in output_file"""

    # setting the seeds
    random.seed(args.seed)
    np.random.seed(args.seed)

    # define CLI variables
    in_dir = args.input_folder
    out_dir = args.output_folder
    wav_new_path = os.path.join(out_dir, "wav_path")

    # create output folder in case it's needed
    os.makedirs(out_dir, exist_ok=True)

    # output files are:
    text_output = open(out_dir + "/text", "w")
    segment_output = open(out_dir + "/segments", "w")
    rttm_output = open(out_dir + "/rttm", "w")
    wav_scp_output = open(out_dir + "/wav.scp", "w")
    utt2text_tags_output = open(out_dir + "/utt2text_tags", "w")
    utt2ids = open(out_dir + "/utt2id", "w")

    # if the wav path exist, delete and create a new one
    if os.path.exists(wav_new_path) and os.path.isdir(wav_new_path):
        shutil.rmtree(wav_new_path)
        os.makedirs(wav_new_path, exist_ok=False)
    else:
        os.makedirs(wav_new_path, exist_ok=True)

    # define some default vars
    utt_names = args.suffix

    try:
        utt2text_tags = open(in_dir + "/diarization/utt2text_tags", "r").readlines()
    except:
        print("you need to first create the utt2text_tags in diarization folder")

    # reading segments
    wav_dict = {}
    segments_dict = {}

    with open(in_dir + "/wav.scp", "r") as f:
        for line in f:
            items = line.rstrip().split()
            recording_id = items[0]

            # go and check which element contains the path
            for item in items[0:]:
                if item.endswith(("." + args.wav_extension)):
                    if recording_id not in wav_dict:

                        # load the sample in memory
                        try:
                            waveform, sample_rate = torchaudio.load(item)
                        except:
                            waveform = torch.empty(0)
                            print(f"Problem reading file: {item}")
                            continue
                        # instantiate the Resampler
                        resampler = T.Resample(sample_rate, args.sampling_rate)

                        # add the element into the dictionary
                        wav_dict[recording_id] = [item, resampler(waveform)]

    # this dictionary contains utt_id: <recording_id> <begin> <end>
    with open(in_dir + "/segments", "r") as f:
        for line in f:
            items = line.rstrip().split()
            segments_dict[items[0]] = items[1:]

    # extracting the lists from training data
    atco_dict, pilot_dict = extract_sentences_batch(
        utt2text_tags, utt_names=utt_names, min_sentence_len=args.min_sentence_len
    )

    # calculating the number of samples to produce:
    atco_file, pilot_file = len(atco_dict), len(pilot_dict)
    total_files = atco_file + pilot_file
    max_lines = len(str(total_files)) + 1  # number of digits

    # Getting the number of sentences per new utterance,
    # We do it only once for the sake of simplicity

    max_snt_per_utt = 2
    # the weights are the 'probabilities' of getting n sentences: 1 is 70%, 2 is 30%
    list_sent_length = random.choices(
        list(range(1, max_snt_per_utt + 1)), weights=(70, 30), k=total_files
    )

    # we need to keep list that matches the exact number of samples in the dataset
    cnt = 1
    list_random = []
    for ele in list_sent_length:
        if cnt < total_files + 1000:
            cnt += ele
            list_random.append(ele)
        else:
            break

    # add the remaining elements
    for add_ in range(total_files - np.sum(list_random)):
        list_random.append(1)

    cnt = 0
    # The *for loop* already carries the number of sentences per new sample
    for nb_samples in list_sent_length:

        # list with information from dictionaries
        selected_sentences, selected_tags = [], []
        selected_ids = []

        # format utt_id name per each sample
        utt_id = "{}_{}".format(utt_names, str(cnt).zfill(max_lines))
        extra_id = "_"
        rttm_list = []

        sig = []
        signals_concatenated = torch.empty(0)
        global_ini_time = 0
        global_end_time = 0

        if len(atco_dict) == 0 and len(pilot_dict) == 0:
            continue

        already_pilot = False
        already_atco = False
        # fetch randomly from our defined dicts
        for i in range(nb_samples):

            # select either True or False to pick from ATCO or PILOT sets
            flag = random.sample([True, False], 1)[0]
            speaker = ""
            try:
                if (flag == True or already_pilot == True) and already_atco == False:
                    already_atco = True
                    _, sample_ = random.choice(list(atco_dict.items()))
                    atco_dict.pop(_)  # delete the element
                    speaker = "atco"
                    extra_id += "C"
                else:
                    already_pilot = True
                    _, sample_ = random.choice(list(pilot_dict.items()))
                    pilot_dict.pop(_)  # delete the element
                    speaker = "pilot"
                    extra_id += "P"
            except:
                print("Error: atco or pilot dictionary is empty")
                continue

            # now extract the data from the sample
            identifier = sample_[0]

            # extract data from segments dictionary
            segments = segments_dict[identifier]
            recording_id = segments[0]
            start_time = float(segments[1])
            end_time = float(segments[2])
            duration = round((end_time - start_time), 4)

            # update the end timing for the segment
            global_end_time += duration

            # extract the signal from the tensor with the whole recording
            if recording_id not in wav_dict:
                print(f"Recording id: {recording_id}, was not load succesfully")
                continue
            signal = wav_dict[recording_id][1][0][
                int(start_time * args.sampling_rate) : int(
                    end_time * args.sampling_rate
                )
            ]

            # check that the signal has the same desired duration
            try:
                assert duration == round(
                    signal.shape[0] / args.sampling_rate, 2
                ), "duration doesn't match"
            except:
                print("duration, does not match!")

            # concatenate the output tensor, only when several
            signals_concatenated = torch.cat((signals_concatenated, signal))

            # create the rttm style output:
            rttm_list.append(
                f"{global_ini_time} {duration} <NA> <NA> {speaker} <NA> <NA>"
            )

            # gather the ids, text and tags for new sample
            selected_ids.append(sample_[0])
            selected_sentences.append(sample_[1])
            selected_tags.append(sample_[2])

            # update the global_ini_time
            global_ini_time += duration

        # this ensures we don't add empty sentences
        if len(selected_ids) == 0:
            continue

        # updating the utt_id with the speakers present in the new sample
        utt_id = utt_id + extra_id
        cnt += 1

        # convert output lists to one new string: composed of 1 or more sentences
        selected_ids = ",".join(selected_ids)
        selected_sentences = " ".join(selected_sentences)
        selected_tags = ",".join(selected_tags)

        # where to store the new wav file
        path_to_save = os.path.realpath(wav_new_path) + f"/{utt_id}.wav"
        torchaudio.save(
            path_to_save,
            signals_concatenated[None, :],  # expanding the dim
            args.sampling_rate,
            bits_per_sample=16,
        )

        # we need to create this type of output:
        # SPEAKER 2020-11-25__15-11-14-47_P 1 0.0 2.1750625 <NA> <NA> pilot <NA> <NA>
        for item in rttm_list:
            rttm_output.write(f"SPEAKER {utt_id} 1 {item}\n")

        # update text and wav_scp_file
        text_output.write(f"{utt_id} {selected_sentences}\n")
        segment_output.write(f"{utt_id} {utt_id} 0 {global_end_time}\n")
        wav_scp_output.write(f"{utt_id} {path_to_save}\n")
        utt2text_tags_output.write(f"{utt_id};{selected_sentences};{selected_tags}\n")
        utt2ids.write(f"{utt_id} {selected_ids}\n")

    text_output.close()
    segment_output.close()
    rttm_output.close()
    wav_scp_output.close()
    utt2text_tags_output.close()
    utt2ids.close()

    return print("finished creating the samples in: ", out_dir)


if __name__ == "__main__":
    args = parse_args()
    main(args)
    sys.exit(0)
