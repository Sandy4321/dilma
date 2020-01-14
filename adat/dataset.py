from typing import Iterator, List, Dict, Optional
import csv

from allennlp.data import Instance
from allennlp.data.fields import TextField, LabelField, Field
from allennlp.data.dataset_readers import DatasetReader
from allennlp.data.token_indexers import SingleIdTokenIndexer
from allennlp.data.tokenizers import Token, Tokenizer
from allennlp.common.util import END_SYMBOL, START_SYMBOL
from allennlp.common.file_utils import cached_path

from adat.masker import Masker


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
                yield self.text_to_instance(sequence=row[0], label=row[1])

    def text_to_instance(self,
                         sequence: str,
                         label: str = None) -> Instance:
        fields: Dict[str, Field] = {}
        tokenized = sequence.split()
        fields["tokens"] = TextField([Token(word) for word in tokenized], {"tokens": SingleIdTokenIndexer()})
        if label is not None:
            fields['label'] = LabelField(int(label), skip_indexing=True)
        return Instance(fields)


class OneLangSeq2SeqReader(DatasetReader):

    def __init__(self, masker: Optional[Masker] = None, lazy: bool = False):
        super().__init__(lazy)
        self.masker = masker

    def _read(self, file_path):
        with open(cached_path(file_path), "r") as file:
            for line in file:
                yield self.text_to_instance(line.strip())

    def text_to_instance(
        self,
        text: str
    ) -> Instance:
        fields: Dict[str, Field] = {}
        tokenized = [START_SYMBOL] + text.split() + [END_SYMBOL]
        fields["original_tokens"] = TextField([Token(word) for word in tokenized], {"tokens": SingleIdTokenIndexer()})
        fields["target_tokens"] = fields["original_tokens"]
        if self.masker is not None:
            text = self.masker.mask(text)
            tokenized = [START_SYMBOL] + text.split() + [END_SYMBOL]
            fields["source_tokens"] = TextField(
                [Token(word) for word in tokenized],
                {"tokens": SingleIdTokenIndexer()}
            )
        else:
            fields["source_tokens"] = fields["original_tokens"]
        return Instance(fields)
