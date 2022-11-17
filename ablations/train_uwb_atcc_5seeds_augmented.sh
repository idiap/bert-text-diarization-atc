#!/bin/bash
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Juan Zuluaga-Gomez <jzuluaga@idiap.ch>
#
# SPDX-License-Identifier: MIT-License 

# Script to train 5 models (different seeds) for text-based diarization system based on BERT WITH AUGMENTED DATA.
# We train 1 model (second row from Table 3: https://arxiv.org/abs/2110.05781)
#   1. UWB-ATCC corpus
# You can train a model using UWB-ATCC and LDC-ATCC data, by simply mixing the utt2text_tags files!
# If you merge these two databases, the results are in third row of Table 3 in: https://arxiv.org/abs/2110.05781

# You can pass a qsub command (SunGrid Engine)
#       :an example is passing --cmd "src/sge/queue.pl h='*'-V", add your configuration

set -euo pipefail

cmd='none'
DATA=experiments/data
output_dir=experiments/results/seed_augmented

# with this we can parse options from CLI
. data/utils/parse_options.sh

# we will run 5 times with different seeds
seeds="2222 3333 4444 5555 6666"

# control if error arises 
rm -rf $output_dir/logs.error

echo "********** Running experiments with different SEEDS **********"
for seed in $(echo $seeds); do
    
    echo "**********      Experiments using SEED: $seed       **********"
    ###############################################################################
    #  Train model with UWB-ATCC corpus
    echo "Training and evaluating (with data augmentation) model with UWB-ATCC corpus and seed: $seed"

    dataset="uwb_atcc"
    bash src/train_one_model.sh \
        --cmd "$cmd" \
        --seed $seed \
        --max-steps 6000 --warmup-steps 1000 \
        --train-batch-size 32 --gradient-accumulation-steps 4 \
        --dataset "$dataset" \
        --train-data $DATA/$dataset/train/diarization_augmented/utt2text_tags \
        --test-data $DATA/$dataset/test/diarization/utt2text_tags \
        --output-dir "$output_dir"

    bash src/eval_model.sh \
        --cmd "$cmd" \
        --seed $seed \
        --DATA $DATA \
        --batch-size 32 \
        --dataset "$dataset" \
        --output-dir "$output_dir"

done

echo "Done training the baselines + DATA AUGMENTATION, for UWB-ATCC corpus"
exit 0
