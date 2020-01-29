from typing import Iterator, List, Dict, Optional
from enum import Enum
import csv

from allennlp.data import Instance
from allennlp.data.fields import TextField, LabelField, Field
from allennlp.data.dataset_readers import DatasetReader
from allennlp.data.token_indexers import SingleIdTokenIndexer
from allennlp.data.tokenizers import Token, Tokenizer
from allennlp.common.file_utils import cached_path

from adat.masker import Masker


START_SYMBOL = '@start@'
END_SYMBOL = '@end@'


class Task(str, Enum):
    CLASSIFICATION = 'classification'
    SEQ2SEQ = 'seq2seq'
    MASKEDSEQ2SEQ = 'mask_seq2seq'
    ATTMASKEDSEQ2SEQ = 'att_mask_seq2seq'


class WhitespaceTokenizer(Tokenizer):
    def tokenize(self, text: str) -> List[Token]:
        return [Token(t) for t in text.split()]


class InsuranceReader(DatasetReader):
    def text_to_instance(self, sentence: str, label: int = None) -> Instance:
        if not isinstance(sentence, list):
            sentence = sentence.split()

        sentence_field = TextField([Token(word) for word in sentence], {"tokens": SingleIdTokenIndexer()})
        fields = {"tokens": sentence_field}

        if label is not None:
            label_field = LabelField(label=label, skip_indexing=True)
            fields["label"] = label_field

        return Instance(fields)

    def _read(self, file_path: str) -> Iterator[Instance]:
        text_path = file_path + '.text'
        labels_path = file_path + '.labels'

        with open(text_path) as text_f, open(labels_path) as labels_f:
            for line_t, line_l in zip(text_f, labels_f):
                sentence = line_t.strip()
                label = int(line_l.strip())
                yield self.text_to_instance(sentence, label)


class CsvReader(DatasetReader):
    def _read(self, file_path):
        with open(cached_path(file_path), "r") as data_file:
            tsv_in = csv.reader(data_file, delimiter=',')
            next(tsv_in, None)
            for row in tsv_in:
                # TODO: add self._tokenizer (TextClassifierPredictor bug)
                yield self.text_to_instance(sequence=row[0].split(), label=row[1])

    def text_to_instance(self,
                         sequence: List[str],
                         label: str = None) -> Instance:
        fields: Dict[str, Field] = dict()
        fields["tokens"] = TextField([Token(word) for word in sequence], {"tokens": SingleIdTokenIndexer()})
        if label is not None:
            fields['label'] = LabelField(int(label), skip_indexing=True)
        return Instance(fields)


class OneLangSeq2SeqReader(DatasetReader):

    def __init__(self, masker: Optional[Masker] = None, lazy: bool = False):
        super().__init__(lazy)
        self.masker = masker
        self._tokenizer = WhitespaceTokenizer()

    def _read(self, file_path):
        with open(cached_path(file_path), "r") as data_file:
            tsv_in = csv.reader(data_file, delimiter=',')
            next(tsv_in, None)
            for row in tsv_in:
                yield self.text_to_instance(text=row[0])

    def text_to_instance(
        self,
        text: str,
        maskers_applied: Optional[List[str]] = None
    ) -> Instance:
        fields: Dict[str, Field] = dict()
        fields["tokens"] = TextField(
            self._tokenizer.tokenize(text),
            {
                "tokens": SingleIdTokenIndexer(start_tokens=[START_SYMBOL], end_tokens=[END_SYMBOL])
            }
        )
        fields["target_tokens"] = fields["tokens"]
        if self.masker is not None:
            text, maskers_applied = self.masker.mask(text)
            maskers_applied = list(set(maskers_applied)) or ['Identity']
            fields["source_tokens"] = TextField(
                self._tokenizer.tokenize(text),
                {
                    "tokens": SingleIdTokenIndexer(start_tokens=[START_SYMBOL], end_tokens=[END_SYMBOL])
                 }
            )
        else:
            fields["source_tokens"] = fields["tokens"]
            maskers_applied = maskers_applied or ['Identity']

        fields['masker_tokens'] = TextField(
            [Token(masker) for masker in maskers_applied],
            {
                "tokens": SingleIdTokenIndexer(namespace='mask_tokens')
            }
        )

        return Instance(fields)
