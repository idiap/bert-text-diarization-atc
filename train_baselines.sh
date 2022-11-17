#!/bin/bash
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Juan Zuluaga-Gomez <jzuluaga@idiap.ch>
#
# SPDX-License-Identifier: MIT-License 

# Script to train the baselines models for text-based diarization system based on BERT
# We train 2 models (first two rows from Table 3: https://arxiv.org/abs/2110.05781)
#   1. UWB-ATCC corpus
#   2. LDC-ATCC corpus
# You can train a model using UWB-ATCC and LDC-ATCC data, by simply mixing the utt2text_tags files!
# If you merge these two databases, the results are in third row of Table 3 in: https://arxiv.org/abs/2110.05781

# You can pass a qsub command (SunGrid Engine)
#       :an example is passing --cmd "src/sge/queue.pl h='*'-V", add your configuration

set -euo pipefail

cmd='none'
DATA=experiments/data
output_dir=experiments/results/baseline

# with this we can parse options from CLI
. data/utils/parse_options.sh

###############################################################################
#  Train model with UWB-ATCC corpus
echo "Training, evaluating and inference (with default params) baseline model with UWB-ATCC corpus"

dataset="uwb_atcc"
bash src/train_one_model.sh \
  --cmd "$cmd" \
  --dataset "$dataset" \
  --max-steps 12000 --warmup-steps 500 --gradient-accumulation-steps 4 \
  --train-data $DATA/$dataset/train/diarization/utt2text_tags \
  --test-data $DATA/$dataset/test/diarization/utt2text_tags \
  --output-dir "$output_dir"

bash src/eval_model.sh \
  --cmd "$cmd" \
  --DATA $DATA \
  --batch-size 32 \
  --dataset "$dataset" \
  --output-dir "$output_dir"

bash src/run_inference.sh \
  --cmd "$cmd" \
  --DATA $DATA \
  --batch-size 32 \
  --dataset "$dataset" \
  --output-dir "$output_dir"

###############################################################################
#  Train model with LDC-ATCC corpus
echo "Training, evaluating and inference (with default params) baseline model with LDC-ATCC corpus"

dataset="ldc_atcc"
bash src/train_one_model.sh \
  --cmd "$cmd" \
  --dataset "$dataset" \
  --max-steps 12000 --warmup-steps 500 --gradient-accumulation-steps 4 \
  --train-data $DATA/$dataset/train/diarization/utt2text_tags \
  --test-data $DATA/$dataset/test/diarization/utt2text_tags \
  --output-dir "$output_dir"

bash src/eval_model.sh \
  --cmd "$cmd" \
  --DATA $DATA \
  --batch-size 32 \
  --dataset "$dataset" \
  --output-dir "$output_dir"

bash src/run_inference.sh \
  --cmd "$cmd" \
  --DATA $DATA \
  --batch-size 32 \
  --dataset "$dataset" \
  --output-dir "$output_dir"  

echo "Done training the baselines for UWB-ATCC and LDC-ATCC corpora"
exit 0
