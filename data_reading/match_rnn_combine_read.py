import os

from data_reading.basic_read import *

def _truncate_seq_pair(tokens_a, tokens_b, max_length):
    """Truncates a sequence pair in place to the maximum length."""

    # This is a simple heuristic which will always truncate the longer sequence
    # one token at a time. This makes more sense than truncating an equal percent
    # of tokens from each, since if one sequence is very short then each token
    # that's truncated likely contains more information than a longer sequence.
    while True:
        total_length = len(tokens_a) + len(tokens_b)
        if total_length <= max_length:
            break
        if len(tokens_a) > len(tokens_b):
            tokens_a.pop()
        else:
            tokens_b.pop()


class InputExample(object):
    """A single training/test example for simple sequence classification."""

    def __init__(self, guid, text_a, text_b=None, label=None):
        """Constructs a InputExample.

        Args:
            guid: Unique id for the example.
            text_a: string. The untokenized text of the first sequence. For single
                sequence tasks, only this sequence must be specified.
            text_b: (Optional) string. The untokenized text of the second sequence.
                Only must be specified for sequence pair tasks.
            label: (Optional) string. The label of the example. This should be
                specified for train and dev examples, but not for test examples.
        """
        self.guid = guid
        self.text_a = text_a
        self.text_b = text_b
        self.label = label


class InputFeatures(object):
    """A single set of features of data."""

    def __init__(self, input_ids, input_mask, segment_ids, label_id,sen_length1,sen_length2,gather_index1,gather_index2):
        self.input_ids = input_ids
        self.input_mask = input_mask
        self.segment_ids = segment_ids
        self.label_id = label_id

        self.gather_index1 = gather_index1
        self.gather_index2 = gather_index2

        self.sen_length1 = sen_length1
        self.sen_length2 = sen_length2

        self._covert_to_dict()
    def _covert_to_dict(self):
        self.fd ={}
        self.fd["input_ids"] = self.input_ids
        self.fd["input_mask"] = self.input_mask
        self.fd["segment_ids"] = self.segment_ids
        self.fd["label_ids"] = self.label_id


        self.fd["gather_index1"] = self.gather_index1
        self.fd["gather_index2"] = self.gather_index2
        self.fd["sen_length1"] = self.sen_length1
        self.fd["sen_length2"] = self.sen_length2


class RnnMatchCombine(DataProcessor):
    """Processor for the CoLA data set (GLUE version)."""

    def get_train_examples(self, data_dir,fname=None):
        """See base class."""
        if fname!=None:
            return self._create_examples(
                self._read_tsv(os.path.join(data_dir, fname)), "train")
        return self._create_examples(
                self._read_tsv(os.path.join(data_dir, "train.txt.format")), "train")

    def get_dev_examples(self, data_dir,fname=None):
        """See base class."""
        if fname!=None:
            return self._create_examples(
                self._read_tsv(os.path.join(data_dir, fname)), "dev")
        return self._create_examples(
                self._read_tsv(os.path.join(data_dir, "dev.txt.format")), "dev")

    def get_test_examples(self, data_dir,fname=None):
        """See base class."""
        if fname!=None:
            return self._create_examples(
                self._read_tsv(os.path.join(data_dir, fname)), "test")
        return self._create_examples(
                self._read_tsv(os.path.join(data_dir, "test.txt.format")), "test")

    def get_labels(self):
        """See base class."""
        return ["0","1"]


    def _create_examples(self, lines, set_type):
        """Creates examples for the training and dev sets."""
        examples = []
        for (i, line) in enumerate(lines):
            guid = "%s-%s" % (set_type, i)
            text_a = tokenization.convert_to_unicode(line[1])
            text_b = tokenization.convert_to_unicode(line[2])
            label = tokenization.convert_to_unicode(line[3])
            examples.append(
                    InputExample(guid=guid, text_a=text_a, text_b=text_b, label=label))
        return examples

    def convert_examples_to_features(self,examples, label_list, max_seq_length, config):
        """Loads a data file into a list of `InputBatch`s."""
        tokenizer = tokenization.FullTokenizer(vocab_file=config.vocab_file, do_lower_case=config.do_lower_case)
        label_map = {}
        for (i, label) in enumerate(label_list):
            label_map[label] = i

        features = []
        for (ex_index, example) in enumerate(examples):
            tokens_a = tokenizer.tokenize(example.text_a)

            tokens_b = None
            if example.text_b:
                tokens_b = tokenizer.tokenize(example.text_b)


            if tokens_b:
                # Modifies `tokens_a` and `tokens_b` in place so that the total
                # length is less than the specified length.
                # Account for [CLS], [SEP], [SEP] with "- 3"
                _truncate_seq_pair(tokens_a, tokens_b, max_seq_length - 3)
            else:
                # Account for [CLS] and [SEP] with "- 2"
                if len(tokens_a) > max_seq_length - 2:
                    tokens_a = tokens_a[0:(max_seq_length - 2)]

            # The convention in BERT is:
            # (a) For sequence pairs:
            #	tokens:	 [CLS] is this jack ##son ##ville ? [SEP] no it is not . [SEP]
            #	type_ids: 0	 0	0		0		0		 0			 0 0		1	1	1	1	 1 1
            # (b) For single sequences:
            #	tokens:	 [CLS] the dog is hairy . [SEP]
            #	type_ids: 0	 0	 0	 0	0		 0 0
            #
            # Where "type_ids" are used to indicate whether this is the first
            # sequence or the second sequence. The embedding vectors for `type=0` and
            # `type=1` were learned during pre-training and are added to the wordpiece
            # embedding vector (and position vector). This is not *strictly* necessary
            # since the [SEP] token unambiguously separates the sequences, but it makes
            # it easier for the model to learn the concept of sequences.
            #
            # For classification tasks, the first vector (corresponding to [CLS]) is
            # used as as the "sentence vector". Note that this only makes sense because
            # the entire model is fine-tuned.
            tokens = []
            segment_ids = []
            tokens.append("[CLS]")
            segment_ids.append(0)
            for token in tokens_a:
                tokens.append(token)
                segment_ids.append(0)
            tokens.append("[SEP]")
            segment_ids.append(0)


            if tokens_b:
                for token in tokens_b:
                    tokens.append(token)
                    segment_ids.append(1)
                tokens.append("[SEP]")
                segment_ids.append(1)


            def get_match_input(tokens):
                import numpy as np
                gather_index1 = []
                gather_index2 = []

                is_first = True
                for i,tk in enumerate(tokens):
                    if tk =="[SEP]":
                        is_first=False
                    if is_first:
                        gather_index1.append([ex_index,i])
                    else:
                        gather_index2.append([ex_index,i])

                len1 = len(gather_index1)
                len2 = len(gather_index2)

                while len(gather_index1) < max_seq_length:
                    gather_index1.append([0,0])
                while len(gather_index2) < max_seq_length:
                    gather_index2.append([0,0])
                return len1,len2,gather_index1,gather_index2

            len1, len2, gather_index1, gather_index2 = get_match_input(tokens)


            input_ids = tokenizer.convert_tokens_to_ids(tokens)

            # The mask has 1 for real tokens and 0 for padding tokens. Only real
            # tokens are attended to.
            input_mask = [1] * len(input_ids)

            # Zero-pad up to the sequence length.
            while len(input_ids) < max_seq_length:
                input_ids.append(0)
                input_mask.append(0)
                segment_ids.append(0)

            assert len(input_ids) == max_seq_length
            assert len(input_mask) == max_seq_length
            assert len(segment_ids) == max_seq_length

            label_id = label_map[example.label]
            if ex_index < 5:
                tf.logging.info("*** Example ***")
                tf.logging.info("guid: %s" % (example.guid))
                tf.logging.info("tokens: %s" % " ".join(
                    [tokenization.printable_text(x) for x in tokens]))
                tf.logging.info("input_ids: %s" % " ".join([str(x) for x in input_ids]))
                tf.logging.info("input_mask: %s" % " ".join([str(x) for x in input_mask]))
                tf.logging.info(
                    "segment_ids: %s" % " ".join([str(x) for x in segment_ids]))
                tf.logging.info("label: %s (id = %d)" % (example.label, label_id))

            features.append(
                InputFeatures(
                    input_ids=input_ids,
                    input_mask=input_mask,
                    segment_ids=segment_ids,
                    label_id=label_id,
                    sen_length1=len1,
                    sen_length2=len2,
                    gather_index1=gather_index1,
                    gather_index2=gather_index2))
        return features