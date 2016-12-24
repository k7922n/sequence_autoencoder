from __future__ import absolute_import 
from __future__ import division
from __future__ import print_function

import gzip
import os
import re

from tensorflow.python.platform import gfile

# Define special symbols
_PAD = b"PAD"
_GO = b"GO"
_EOS = b"EOS"
_UNK = b"UNK"

_START_VOCAB = [_PAD, _GO, _EOS, _UNK]

PAD_ID = 0
GO_ID = 1
EOS_ID = 2
UNK_ID = 3

# Used to split and tokenize
WORD_SPLIT = re.compile(b"([.,!?\"':;)(])")
DIGIT_RE = re.compile(br"\d")

# Define basic tokenizer i.e. just split sentence
def default_tokenizer(sentence):
  words = []
  for split_sen in sentence.lower().strip().split():
    words.extend(WORD_SPLIT.split(split_sen))
  return [word for word in words if word]

# Form vocabulary file according to max vocabulary size
# input_path_1, 2 : original data
# output_path : where you want vocab mapping to save to
def form_voc(input_path_1, input_path_2, output_path, max_size, tokenizer = None):
  if gfile.Exists(output_path):
    print("%s has already existed! Directly read from it" % output_path)
  
  else:
 
    print("Reading data from %s and %s to %s" % (input_path_1, input_path_2, output_path))
    print("Max vocabulary size: %s" % max_size)

    vocab = {}
    with gfile.GFile(input_path_1, mode = 'rb') as f_1:
      with gfile.GFile(input_path_2, mode = 'rb') as f_2:
        f_list = [f_1, f_2]
        counter = 0
        for f in f_list:
          for line in f:
            counter += 1
            if counter % 100000 == 0:
              print("  Processing to line %s" % counter)
            tokens = tokenizer(line) if tokenizer else default_tokenizer(line)
      
            for word in tokens:
              if word in vocab:
                vocab[word] += 1
              else:
                vocab[word] = 1
          
        vocab_list = _START_VOCAB + sorted(vocab, key = vocab.get, reverse = True)
        if len(vocab_list) > max_size:
          vocab_list = vocab_list[:max_size]
        with gfile.GFile(output_path, 'wb') as vocab_file:
          for w in vocab_list:
            vocab_file.write(w + b"\n")

# Form mapping dictionary from file formed by form_voc function
# and return a list and a dict
# Dictionary: {"apple":1, "bird":2,...}
# List: ["apple", "bird",...]
# input_path : where you store mapping file
def form_map(input_path):
  if gfile.Exists(input_path):
    vocab_list = []
    with gfile.GFile(input_path, mode = 'rb') as f:
      vocab_list.extend(f.readlines())
    vocab_list = [line.strip() for line in vocab_list]
    vocab_dict = dict([(x, y) for (y, x) in enumerate(vocab_list)])
    return vocab_list, vocab_dict
    
  else:
    raise ValueError("Vocabulary file %s not found!", input_path)

# Convert sentence to tokens
# Input: string
# Output: list of ids
def convert_to_token(sentence, vocab_map, tokenizer=None):
  
  if tokenizer:
    words = tokenizer(sentence)
  else:
    words = default_tokenizer(sentence)
  
  return [vocab_map.get(w, UNK_ID) for w in words]

# Convert whole file into ids
def file_to_tokens(input_path, output_path, vocab_map, tokenizer = None):
  if gfile.Exists(output_path):
    print("IDs file %s has already exists!" % output_path)
  else:
    print("Tokenizing data from %s" % input_path)
    with gfile.GFile(input_path, 'rb') as data_file:
      with gfile.GFile(output_path, 'w') as token_file:
        counter = 0
        for line in data_file:
          counter += 1
          if counter % 100000 == 0:
            print("  Tokenizing line %s" % counter)
          token_ids = convert_to_token(line, vocab_map, tokenizer)

          token_file.write(" ".join([str(tok) for tok in token_ids]) + '\n')

# Prepare whole data, create only one vocabulary since it's dialogue system
# data_dir folder should contain corpus of both source and target
# data_dir path should be followed by / symbol
# for example : /data
def prepare_whole_data(data_dir, max_vocabulary_size, tokenizer = None):
  
  # data_dir folder should contain corpus of both source and target
  # you can change file name here
  training_data = data_dir + 'train'
  dev_data = data_dir + 'valid'
  
  # Form vocabulary file named vocab_target_path
  # Here will form two files, which are filename_1 and filename_2
  vocab_target_path = data_dir + 'all_vocab' + str(max_vocabulary_size)
  filename_1 = training_data + '.source'
  filename_2 = training_data + '.target'
  form_voc(filename_1, filename_2, vocab_target_path, max_vocabulary_size, tokenizer)
  
  # Read vocabulary file formed from previous function and get the mapping dictionary
  # and use mapping dictionary to form token to IDs file
  vocab_list, vocab_dict = form_map(vocab_target_path)

  # Training data part
  tokenized_training_data_1 = filename_1 + '.token'
  tokenized_training_data_2 = filename_2 + '.token'
  file_to_tokens(filename_1, tokenized_training_data_1, vocab_dict, tokenizer)
  file_to_tokens(filename_2, tokenized_training_data_2, vocab_dict, tokenizer)
  
  # Validation data part
  dev_data_1 = dev_data + '.source'
  dev_data_2 = dev_data + '.target'
  tokenized_dev_data_1 = dev_data_1 + '.token'
  tokenized_dev_data_2 = dev_data_2 + '.token'
  file_to_tokens(dev_data_1, tokenized_dev_data_1, vocab_dict, tokenizer)
  file_to_tokens(dev_data_2, tokenized_dev_data_2, vocab_dict, tokenizer)

  return tokenized_training_data_1, tokenized_training_data_2, tokenized_dev_data_1, tokenized_dev_data_2
if __name__ == '__main__':
  data_dir = 'corpus/'
  max_size = 60000
  tokenizer = None
  prepare_whole_data(data_dir, max_size, tokenizer)
