#!/bin/bash
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Juan Zuluaga-Gomez <jzuluaga@idiap.ch>
#
# SPDX-License-Identifier: MIT-License 

# Script to plot the metrics of the a given model on several files
# Evaluations are in the 'evaluations' folder for each dataset

# default folder with UWB-ATCC corpus (as it is free!)
evaluation_folder=experiments/results/baseline/bert-base-uncased/1234/uwb_atcc/evaluations

# with this we can parse options from CLI
. data/utils/parse_options.sh

# parse the files that has 'metrics' in their name, i.e., datasets that were evaluated
eval_datasets=$(ls $evaluation_folder | grep metrics | tr '\n' ' ')

echo -e "\n ****************************************************"
echo -e " ****** Results of model in $evaluation_folder *****"
echo -e "\nModel \t\t\t\t B-ATCO [f1] \t B-PILOT [f1] \t JER [%]"

for eval_d in $(echo $eval_datasets); do

    metrics_path=$evaluation_folder/${eval_d}
    metric_atco=$(grep ' B-atco ' $metrics_path | tr -s ' ' | cut -d ' ' -f5)
    metric_pilot=$(grep ' B-pilot ' $metrics_path | tr -s ' ' | cut -d ' ' -f5)
    metric_JER=$(grep ' JER - ' $metrics_path | tr -s ' ' | cut -d ' ' -f6)
    echo -e "$eval_d: \t\t $metric_atco \t \t $metric_pilot \t\t $metric_JER"
done

echo "******** DONE ********"
exit 0