#!/bin/bash
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Juan Zuluaga-Gomez <jzuluaga@idiap.ch>
#
# SPDX-License-Identifier: MIT-License 

# Script to train the baselines models for text-based diarization system based on BERT WITH AUGMENTED DATA.
# We train 1 model (first row from Table 3: https://arxiv.org/abs/2110.05781)
#   1. LDC-ATCC corpus
# You can train a model using UWB-ATCC and LDC-ATCC data, by simply mixing the utt2text_tags files!
# If you merge these two databases, the results are in third row of Table 3 in: https://arxiv.org/abs/2110.05781

# You can pass a qsub command (SunGrid Engine)
#       :an example is passing --cmd "src/sge/queue.pl h='*'-V", add your configuration

set -euo pipefail

cmd='none'
DATA=experiments/data
output_dir=experiments/results/augmented

# with this we can parse options from CLI
. data/utils/parse_options.sh

###############################################################################
#  Train model with LDC-ATCC corpus
echo "Training and evaluating (with data augmentation) baseline model with LDC-ATCC corpus"

dataset="ldc_atcc"
bash src/train_one_model.sh \
  --cmd "$cmd" \
  --max-steps 12000 --warmup-steps 1000 \
  --train-batch-size 32 --gradient-accumulation-steps 8 \
  --dataset "$dataset" \
  --train-data $DATA/$dataset/train/diarization_augmented/utt2text_tags \
  --test-data $DATA/$dataset/test/diarization/utt2text_tags \
  --output-dir "$output_dir"

bash src/eval_model.sh \
  --cmd "$cmd" \
  --DATA $DATA \
  --batch-size 32 \
  --dataset "$dataset" \
  --output-dir "$output_dir"

echo "Done training the baselines + DATA AUGMENTATION, for LDC-ATCC corpus"
exit 0
