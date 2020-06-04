#!/usr/bin/env bash

# usage
# bash bin/adv_training.sh {ATTACKS_DIR} ${GPU_ID}

set -eo pipefail -v

ATTACKS_DIR=$1
default_gpu_id=0
GPU_ID=${2:-$default_gpu_id}

LOGS_DIR="logs"
DATASETS_DIR="datasets"


echo "Preparing NLP datasets"
data_type=nlp
for num in 5000 50 100 500 1000; do
    for result_dir in $(ls -d ${ATTACKS_DIR}/${data_type}/*); do
        dataset=$(basename ${result_dir})
        for dir in $(ls -d ${result_dir}/*); do
            alg_name=$(basename ${dir})
            echo ">>>> Preparing data for ${dataset} dataset, ${alg_name} algorithm, ${num} examples"
            PYTHONPATH=. python scripts/prepare_for_fine_tuning.py \
                --adversarial-dir ${dir} \
                --mix-with-path ${DATASETS_DIR}/${data_type}/${dataset}/target_clf/train.json \
                --num-examples ${num}

            export CLS_NUM_CLASSES=2
            export CLS_TRAIN_DATA_PATH=${dir}/fine_tuning_data_${num}.json
            export CLS_VALID_DATA_PATH=${DATASETS_DIR}/${data_type}/${dataset}/target_clf/valid.json

            clf_dif=${LOGS_DIR}/${data_type}/dataset_${dataset}/target_clf/${alg_name}_${num}
            allennlp train configs/models/classifier/gru_classifier_no_vocab.jsonnet \
                -s ${clf_dif} \
                --force \
                --include-package adat

            allennlp evaluate \
                ${clf_dif}/model.tar.gz \
                ${DATASETS_DIR}/${data_type}/${dataset}/target_clf/test.json \
                --include-package adat  \
                --output-file ${dir}/test_metrics_${num}.json \
                --cuda-device ${GPU_ID}

            PYTHONPATH=. python scripts/evaluate_attack.py \
                --adversarial-dir ${dir} \
                --classifier-dir ${clf_dif} \
                --cuda ${GPU_ID}
        done
    done
done