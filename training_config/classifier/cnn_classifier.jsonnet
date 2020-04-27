{
  "dataset_reader": {
    "type": "text_classification_json",
    // DO NOT CHANGE token_indexers
    "token_indexers": {
        "tokens": {
            "type": "single_id",
            "start_tokens": ["<START>"],
            "end_tokens": ["<END>"]
        }
    },
    // DO NOT CHANGE tokenizer
    "tokenizer": {
        "type": "just_spaces"
    },
    "lazy": false
  },
  "train_data_path": "data/json_ins_class/train.json",
  "validation_data_path": "data/json_ins_class/test.json",

  // Make sure you load vocab from LM
  "vocabulary": {
     "type": "from_files",
     "directory": "exp_lm/vocabulary"
  },

  "model": {
    "type": "basic_classifier",
    "text_field_embedder": {
        "token_embedders": {
            "tokens": {
                "type": "embedding",
                "embedding_dim": 100,
                "trainable": true
          }
       }
     },
     "seq2vec_encoder": {
        "type": "cnn",
        "embedding_dim": 100,
        "num_filters": 32
     }
  },
  "data_loader": {
      "batch_size" : 32
  },
  "distributed": {
    "cuda_devices": [2, 3]
  },
  "trainer": {
    "num_epochs": 50,
    "patience": 3
  }
}
