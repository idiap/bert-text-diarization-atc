#!/bin/bash
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Juan Zuluaga-Gomez <jzuluaga@idiap.ch>
#
# SPDX-License-Identifier: MIT-License 

# Base script to upload a BERT model fine-tuned on the token-classification task to HuggingFace hub
# This model has been fine-tuned on UWB-ATCC CORPUS,
set -euo pipefail

path_to_model="experiments/results/augmented/bert-base-uncased/1234/uwb_atcc/final_checkpoint"
output_folder=".cache/"
repository_name="bert-base-token-classification-for-atc-en-uwb-atcc"

. data/utils/parse_options.sh

output_folder=$output_folder/$repository_name
mkdir -p $output_folder

echo "*** Uploading model to HuggingFace hub ***"
echo "*** repository will be stored in: $output_folder ***"

python3 src/utils/upload_token_classification_model.py \
  --model "$path_to_model" \
  --output-folder "$output_folder" \
  --output-repo-name "$repository_name"

echo "Done uploading the model in ${path_to_model} with LM"
exit 0
