#!/bin/bash
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Juan Zuluaga-Gomez <jzuluaga@idiap.ch>
#
# SPDX-License-Identifier: MIT-License 

# Script to evaluate one text-based diarization system based on BERT
# The default database is UWB-ATCC, as it is completly free!

set -euo pipefail

# static vars
cmd='none'
DATA=experiments/data

# model related vars
batch_size=10

# vars of the model and input/output folder
input_model=bert-base-uncased
dataset=uwb_atcc
seed=1234
output_dir=experiments/results/baseline

# with this we can parse options to this script
. data/utils/parse_options.sh

# Evaluate on the given dataset.
# We evaluate the standard dataset. And the created with mixed speakers.
# Also, we evaluate by speaker role, to get a clear overview
test_set=$DATA/$dataset/test/diarization/utt2text_tags
test_set_mixed=$DATA/$dataset/test/diarization_acoustic/utt2text_tags
test_set_mixed_atco=$DATA/$dataset/test/diarization_acoustic/utt2text_tags_atco
test_set_mixed_pilot=$DATA/$dataset/test/diarization_acoustic/utt2text_tags_pilot

input_files="$test_set $test_set_mixed $test_set_mixed_atco $test_set_mixed_pilot"
test_names="$dataset ${dataset}_mixed ${dataset}_mixed_atco ${dataset}_mixed_pilot"

output_folder=$output_dir/$input_model/$seed/$dataset

# configure a GPU to use if we a defined 'CMD'
if [ ! "$cmd" == 'none' ]; then
  basename=evaluate_${dataset}_${seed}_${input_model}
  cmd="$cmd -N ${basename} ${output_folder}/evaluations/log/eval.log"
else
  cmd=''
fi

# running the command
$cmd python3 src/eval_diarization.py \
  --input-model "$output_folder/" \
  --batch-size $batch_size \
  --input-files "$input_files" --test-names "$test_names" \
  --output-folder $output_folder/evaluations

echo "Done evaluating the model with dataset: $dataset"
exit 0