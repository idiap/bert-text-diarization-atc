#!/bin/bash
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Juan Zuluaga-Gomez <jzuluaga@idiap.ch>
#
# SPDX-License-Identifier: MIT-License 

# This script is intended to format the ATCO2-test-set corpus for the diarization experiments:
#   1. Prepare the folder for diarization experiments
#   2. Perform data augmentation, see Section 3.4 in: https://arxiv.org/abs/2110.05781
#   3. Prepare the test folder for acoustic-based diarization
# You must run first data/databases/data_prepare_atco2_corpus.sh

set -euo pipefail

experiment_folder=experiments/data
new_samples=10000

. data/utils/parse_options.sh
############################################################################
# GET the tags for ATCO2-test-set corpus (format train/ and test/ folders) 
# ATCO2-test-set is already formatted, we just need to create the utt2text_tags file 

output="$experiment_folder/atco2_corpus"
# create folder if not present
[ -d $output/test/diarization ] || mkdir -p $output/test/diarization

cp $output/* $output/test/ && 

# filter the utterances that has speaker label
grep -v "unk" $output/utt2speaker_callsign > $output/test/diarization/utt2speakerid
cut -d' ' -f1 $output/test/diarization/utt2speakerid > $output/test/diarization/ids

perl data/utils/filter_scp.pl $output/test/diarization/ids \
  $output/text > $output/test/diarization/text

# generating the labels and the ner_tags  
python3 data/utils/get_tags_speaker.py $output/test/diarization $output/test/diarization

echo "done creating the experiments folder in $experiment_folder/atco2_corpus/{train,test}/diarization"
echo "****************************"

############################################################################
# Perform data augmentation on the audio-level for ATCO2-test-set corpus

output=$experiment_folder/atco2_corpus/test
if [ ! -d $output/diarization_acoustic ]; then
    echo "creating the diarization augmented (acoustic-level) data in $output/diarization_acoustic"
    mkdir -p $output/diarization_acoustic

    # generating new labels, data augmentation
    python3 data/utils/augmentation/generate_mixed_rttm_kaldi.py \
        --seed 1234 --min-sentence-len 2 \
        --wav-extension "wav" --sampling-rate 16000 \
        --suffix "atco2_mixed" \
        $output/ $output/diarization_acoustic

    # split by speaker role for evaluation:
    grep '_P;' $output/diarization_acoustic/utt2text_tags \
        > $output/diarization_acoustic/utt2text_tags_pilot
    grep '_C;' $output/diarization_acoustic/utt2text_tags \
        > $output/diarization_acoustic/utt2text_tags_atco
    grep -v '_P;\|_C;' $output/diarization_acoustic/utt2text_tags \
        > $output/diarization_acoustic/utt2text_tags_mixed

    echo "done performing data augmentation on the acousitc level for ATCO2-test-set corpus" 
    echo "See the output in: $output/diarization_acoustic"
    echo "****************************"
else
    echo "the $output/diarization_acoustic is already created, skipping it..."
fi
echo "****************************"

# ------
echo "ATCO2-test-set corpus was sucessfully formatted"
exit 0


