from pathlib import Path
from glob import glob

from allennlp.data import Vocabulary
from allennlp.common import Params

from adat.models import DeepLevenshtein, MaskedLanguageModel, BasicClassifierOneHotSupport


PROJECT_ROOT = (Path(__file__).parent / ".." / "..").resolve()


def test_deep_levenshtein_configs():

    paths = glob(str(PROJECT_ROOT / "training_config/levenshtein/*.jsonnet"))
    assert len(paths) > 0
    for config_path in paths:
        try:
            params = Params.from_file(
                str(config_path),
                ext_vars={
                    "DL_TRAIN_DATA_PATH": "",
                    "DL_VALID_DATA_PATH": "",
                    "LM_VOCAB_PATH": ""
                }
            )
            blank_vocab = Vocabulary()
            params["model"].pop("type")
            DeepLevenshtein.from_params(params=params["model"], vocab=blank_vocab)
        except Exception as e:
            raise AssertionError(f"unable to load params from {config_path}, because {e}")


def test_masked_lm_configs():

    paths = glob(str(PROJECT_ROOT / "training_config/lm/*.jsonnet"))
    assert len(paths) > 0
    for config_path in paths:
        try:
            params = Params.from_file(
                str(config_path),
                ext_vars={
                    "LM_TRAIN_DATA_PATH": "",
                    "LM_VALID_DATA_PATH": ""
                }
            )
            blank_vocab = Vocabulary(tokens_to_add={"tokens": ["@@MASK@@"]})
            params["model"].pop("type")
            MaskedLanguageModel.from_params(params=params["model"], vocab=blank_vocab)
        except Exception as e:
            raise AssertionError(f"unable to load params from {config_path}, because {e}")


def test_classifier_configs():

    paths = glob(str(PROJECT_ROOT / "training_config/classifier/*.jsonnet"))
    assert len(paths) > 0
    for config_path in paths:
        try:
            params = Params.from_file(
                str(config_path),
                ext_vars={
                    "CLS_TRAIN_DATA_PATH": "",
                    "CLS_VALID_DATA_PATH": "",
                    "CLS_NUM_CLASSES": "2",
                    "LM_VOCAB_PATH": ""
                }
            )
            blank_vocab = Vocabulary()
            params["model"].pop("type")
            BasicClassifierOneHotSupport.from_params(params=params["model"], vocab=blank_vocab)
        except Exception as e:
            raise AssertionError(f"unable to load params from {config_path}, because {e}")
