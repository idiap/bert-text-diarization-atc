#!/usr/bin/bash
#
# SPDX-FileCopyrightText: Copyright © <2022> Idiap Research Institute <contact@idiap.ch>
#
# SPDX-FileContributor: Seyyed Saeed Sarfjoo <saeed.sarfjoo@idiap.ch>
#
# SPDX-License-Identifier: MIT-License 

# Script to eval DER in an acoustic-based way. We align words to speech time and then we evaluate with this information

test_set="uwb_atcc_subset"
tag="only_uwb"

gt_name=${test_set}_mixed
python src/create_mdtm_file.py \
    -hp experiments/data/${test_set}/hyp.ctm \
    -t experiments/data/${test_set}/utt2text_tags.eval_inference \
    --scale 3 \
    -s experiments/data/${test_set}/segments \
    -o experiments/data/${test_set}/nlp_asr_$tag.mdtm

# converting the segments to rttm format,

python src/convert_mdtm_to_rttm.py \
    -i experiments/data/${test_set}/nlp_asr_$tag.mdtm \
    -o experiments/data/${test_set}/nlp_asr_$tag.rttm

# evaluating the darization,

#### information
# segments with _C tells that the segment only contains controller speech (speaker 1)
# segments with _C tells that the segment only contains controller speech (speaker 2)
# segments with _PC tells that the segment contains controller and pilot speech (speaker 1 and speaker 2)
#### information

echo "processing $test_set"
grep '_C ' experiments/data/${test_set}/nlp_asr_$tag.rttm > experiments/data/${test_set}/nlp_asr_${tag}_c.rttm
grep '_P ' experiments/data/${test_set}/nlp_asr_$tag.rttm > experiments/data/${test_set}/nlp_asr_${tag}_p.rttm
grep '_PC \|_CP ' experiments/data/${test_set}/nlp_asr_$tag.rttm > experiments/data/${test_set}/nlp_asr_${tag}_pc.rttm

echo "processing $tag NLP train-set"
grep '_C ' experiments/data/${test_set}/ref.rttm > experiments/data/${test_set}/ref_c.rttm
grep '_P ' experiments/data/${test_set}/ref.rttm > experiments/data/${test_set}/ref_p.rttm
grep '_PC \|_CP ' experiments/data/${test_set}/ref.rttm > experiments/data/${test_set}/ref_pc.rttm


python dscore/score.py \
    -r experiments/data/${test_set}/ref.rttm \
    -s  experiments/data/${test_set}/nlp_asr_${tag}.rttm \
    --collar 0.15 \
    --ignore_overlaps \
    > experiments/data/${test_set}/der_out_asr_${test_set}_${tag}

python dscore/score.py \
    -r experiments/data/${test_set}/ref_c.rttm \
    -s  experiments/data/${test_set}/nlp_asr_${tag}_c.rttm \
    --collar 0.15 \
    --ignore_overlaps \
    > experiments/data/${test_set}/der_out_asr_${test_set}_${tag}_c

python dscore/score.py \
    -r experiments/data/${test_set}/ref_p.rttm \
    -s experiments/data/${test_set}/nlp_asr_${tag}_p.rttm \
    --collar 0.15 \
    --ignore_overlaps \
    > experiments/data/${test_set}/der_out_asr_${test_set}_${tag}_p

python dscore/score.py \
    -r experiments/data/${test_set}/ref_pc.rttm \
    -s experiments/data/${test_set}/nlp_asr_${tag}_pc.rttm \
    --collar 0.15 \
    --ignore_overlaps \
    > experiments/data/${test_set}/der_out_asr_${test_set}_${tag}_pc

echo "All DER"
grep OVERALL experiments/data/${test_set}/der_out_asr_${test_set}_${tag}
echo "Controller DER"
grep OVERALL experiments/data/${test_set}/der_out_asr_${test_set}_${tag}_c
echo "Pilot DER"
grep OVERALL experiments/data/${test_set}/der_out_asr_${test_set}_${tag}_p
echo "Mixed DER"
grep OVERALL experiments/data/${test_set}/der_out_asr_${test_set}_${tag}_pc

echo "done evaluating the utt2text_tags file and the ground truth file"
exit 0