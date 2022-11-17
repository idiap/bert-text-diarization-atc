#!/bin/bash
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Juan Zuluaga-Gomez <jzuluaga@idiap.ch>
#
# SPDX-License-Identifier: MIT-License 

# This script is intended to format the UWB-ATCC corpus for the diarization experiments:
#   1. Prepare the folder for diarization experiments
#   2. Perform data augmentation, see Section 3.4 in: https://arxiv.org/abs/2110.05781
#   3. Prepare the test folder for acoustic-based diarization
# You must run first data/databases/data_prepare_uwb_atcc_corpus.sh

set -euo pipefail

experiment_folder=experiments/data
new_samples=100000

. data/utils/parse_options.sh
############################################################################
# GET the tags for UWB-ATCC corpus (format train/ and test/ folders) 
# UWB-ATCC is already formatted, we just need to create the utt2text_tags file 

train_test_sets="uwb_atcc/train uwb_atcc/test" 
for output in $(echo $train_test_sets); do
  # create folder if not present
  output=$experiment_folder/$output
  [ -d $output/diarization ] || mkdir -p $output/diarization

  # generating the labels and the ner_tags  
  paste -d' ' <(cut -d' ' -f1 $output/utt2speakerid) \
              <(cut -d';' -f2- $output/utt2speakerid | sed 's/ /,/g' | tr -s ' ') | \
              grep -v "B-none" >$output/diarization/utt2nertags

  # utt2text and utt2tags files,
  grep -v '_N' $output/text >$output/diarization/utt2text
  sed 's/B-\|I-//g' $output/diarization/utt2nertags > $output/diarization/utt2tags

  # creating the main file, utt2text_tags,
  paste -d';' <(cut -d' ' -f1 $output/utt2speakerid) \
              <(cut -d' ' -f3- $output/utt2speakerid | cut -d';' -f1) \
              <(cut -d';' -f2- $output/utt2speakerid | tr ' ' ',') | \
              grep -v "B-none" >$output/diarization/utt2text_tags
done
echo "done creating the experiments folder in $experiment_folder/uwb_atcc/{train,test}/diarization"
echo "****************************"

############################################################################
# Perform data augmentation on the text-level for UWB-ATCC
# create folder if not present

output=$experiment_folder/uwb_atcc/train
if [ ! -d $output/diarization_augmented ]; then
    echo "creating the diarization augmented (text-level) data in $output/diarization_augmented"
    mkdir -p $output/diarization_augmented

    # generating new labels, data augmentation
    python3 data/utils/augmentation/data_augmentation_diarization.py \
        --seed 1234 \
        --suffix "uwb_atcc_augmented" \
        --new-samples $new_samples \
        $output/diarization/utt2text_tags $output/diarization_augmented

    echo "done performing data augmentation on the text level for UWB-ATCC corpus" 
    echo "See the output in: $output/diarization_augmented"
else
    echo "the $output/diarization_augmented is already created, skipping it..."
fi
echo "****************************"

############################################################################
# Perform data augmentation on the audio-level for UWB-ATCC corpus

output=$experiment_folder/uwb_atcc/test
if [ ! -d $output/diarization_acoustic ]; then
    echo "creating the diarization augmented (acoustic-level) data in $output/diarization_acoustic"
    mkdir -p $output/diarization_acoustic/prep

    # Filter the overlapped segments from the utt2text_tags file.
    # In this way, we are sure that only one segment contains one speaker
    cp $output/diarization/utt2text_tags $output/diarization_acoustic/prep/utt2text_tags_mixed
    grep -v PIAT $output/diarization_acoustic/prep/utt2text_tags_mixed \
        >$output/diarization_acoustic/utt2text_tags

    # generating new labels, data augmentation
    python3 data/utils/augmentation/generate_mixed_rttm_kaldi.py \
        --seed 1234 --min-sentence-len 2 \
        --wav-extension "wav" --sampling-rate 16000 \
        --suffix "uwb_atcc_mixed" \
        $output/ $output/diarization_acoustic

    # split by speaker role for evaluation:
    grep '_P;' $output/diarization_acoustic/utt2text_tags \
        > $output/diarization_acoustic/utt2text_tags_pilot
    grep '_C;' $output/diarization_acoustic/utt2text_tags \
        > $output/diarization_acoustic/utt2text_tags_atco
    grep -v '_P;\|_C;' $output/diarization_acoustic/utt2text_tags \
        > $output/diarization_acoustic/utt2text_tags_mixed

    echo "done performing data augmentation on the acousitc level for UWB-ATCC corpus" 
    echo "See the output in: $output/diarization_acoustic"
    echo "****************************"
else
    echo "the $output/diarization_acoustic is already created, skipping it..."
fi
echo "****************************"

# ------
echo "UWB-ATCC corpus was sucessfully formatted"
exit 0


