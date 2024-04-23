# -*- coding: utf-8 -*-
"""Copy of rte_bert_samad.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nHP4P7CS5X_9DYxZfmvTN28mPwt7gSNG
"""

import warnings
warnings.filterwarnings('ignore')

import numpy as np
import torch
import torch.nn as nn
import torchmetrics

from datasets import load_dataset
dataset = load_dataset("glue", "rte")

dataset

import pandas as pd

train_sentences1 = []
train_sentences2 = []
train_labels = []

for sentence in dataset["train"]["sentence1"]:
  train_sentences1.append(sentence)

for sentence in dataset["train"]["sentence2"]:
  train_sentences2.append(sentence)

for label in dataset["train"]["label"]:
  train_labels.append(label)

train_df = pd.DataFrame(list(zip(train_sentences1,train_sentences2, train_labels)), columns=["sentences1","sentences2", "labels"])

test_sentences1 = []
test_sentences2 = []
test_labels = []

for sentence in dataset["test"]["sentence1"]:
  test_sentences1.append(sentence)

for sentence in dataset["test"]["sentence2"]:
  test_sentences2.append(sentence)

for label in dataset["test"]["label"]:
  test_labels.append(label)

test_df = pd.DataFrame(list(zip(test_sentences1,test_sentences2, test_labels)), columns=["sentences1","sentences2", "labels"])

val_sentences1 = []
val_sentences2 = []
val_labels = []

for sentence in dataset["validation"]["sentence1"]:
  val_sentences1.append(sentence)

for sentence in dataset["validation"]["sentence2"]:
  val_sentences2.append(sentence)

for label in dataset["validation"]["label"]:
  val_labels.append(label)

val_df = pd.DataFrame(list(zip(val_sentences1,val_sentences2, val_labels)), columns=["sentences1","sentences2", "labels"])

len(train_df),len(test_df),len(val_df)

print(np.unique(train_df.labels))
# print(np.unique(test_df.labels))
# print(test_df.labels)
print(np.unique(val_df.labels))

from transformers import BertTokenizer, BertModel, BertConfig
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

train_df.head()

from torch import cuda
device = 'cuda' if cuda.is_available() else 'cpu'
import numpy as np
import pandas as pd
from sklearn import metrics
import transformers
import torch



from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler

class RTEDataset(Dataset):

  def __init__(self, dataframe, tokenizer, max_len):
    self.tokenizer = tokenizer
    self.data = dataframe
    self.sentences1 = self.data.sentences1
    self.sentences2 = self.data.sentences2
    self.targets = self.data.labels
    self.max_len = max_len

  def __len__(self):
    return len(self.sentences1)

  def __getitem__(self, index):
    # sentence = str(self.sentences1[index]) + str(self.sentences2[index])
    # sentence = " ".join(sentence.split())

    inputs1 = self.tokenizer.encode_plus(
        self.sentences1[index],
        self.sentences2[index],
        add_special_tokens=True,
        truncation="only_first",
        max_length=self.max_len,
        pad_to_max_length=True,
        return_token_type_ids=True,
    )



    ids = torch.tensor(inputs1['input_ids'])
    mask = torch.tensor(inputs1['attention_mask'])
    token_type_ids = torch.tensor(inputs1["token_type_ids"])

    # # ids = torch.cat((torch.tensor(ids1),torch.tensor(ids2)))
    # # mask = torch.cat((torch.tensor(mask1),torch.tensor(mask2)))
    # # token_type_ids = torch.cat((torch.tensor(token_type_ids1),torch.tensor(token_type_ids2)))

    # if len(ids)<self.max_len:
    #   padding = torch.zeros(self.max_len - len(ids), dtype=ids.dtype)
    #   ids = torch.cat((ids, padding), dim=0)
    #   mask = torch.cat((mask,padding),dim=0)
    #   token_type_ids = torch.cat((token_type_ids,padding),dim=0)
    # else:
    #   ids = ids[:self.max_len]
    #   mask = ids[:self.max_len]
    #   token_type_ids = token_type_ids[:self.max_len]
    return {
            'ids': torch.tensor(ids, dtype=torch.long),
            'mask': torch.tensor(mask, dtype=torch.long),
            'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long),
            'targets': torch.tensor(self.targets[index], dtype=torch.float)
           }

MAX_LEN = 128
TRAIN_BATCH_SIZE = 64
VALID_BATCH_SIZE = 64
TEST_BATCH_SIZE = 64
EPOCHS = 5
LEARNING_RATE = 0.0001

# from torch.utils.data import Dataset, DataLoader, RandomSampler, SequentialSampler

# class RTEDataset(Dataset):

#   def __init__(self, dataframe, tokenizer, max_len):
#     self.tokenizer = tokenizer
#     self.data = dataframe
#     self.sentences1 = self.data.sentences1
#     self.sentences2 = self.data.sentences2
#     self.targets = self.data.labels
#     self.max_len = max_len

#   def __len__(self):
#     return len(self.sentences1)

#   def __getitem__(self, index):
#     sentence1 = str(self.sentences1[index])
#     sentence1 = " ".join(sentence1.split())

#     inputs1 = self.tokenizer.encode_plus(
#         sentence1,
#         None,
#         add_special_tokens=True,
#         # max_length=self.max_len,
#         pad_to_max_length=False,
#         return_token_type_ids=True
#     )

#     sentence2 = str(self.sentences2[index])
#     sentence2 = " ".join(sentence2.split())
#     inputs2 = self.tokenizer.encode_plus(
#         sentence2,
#         None,
#         add_special_tokens=True,
#         # max_length=self.max_len,
#         pad_to_max_length=False,
#         return_token_type_ids=True
#     )

#     ids1 = inputs1['input_ids']
#     mask1 = inputs1['attention_mask']
#     token_type_ids1 = inputs1["token_type_ids"]

#     ids2 = inputs2['input_ids']
#     mask2 = inputs2['attention_mask']
#     token_type_ids2 = inputs2["token_type_ids"]

#     ids = torch.cat((torch.tensor(ids1),torch.tensor(ids2)))
#     mask = torch.cat((torch.tensor(mask1),torch.tensor(mask2)))
#     token_type_ids = torch.cat((torch.tensor(token_type_ids1),torch.tensor(token_type_ids2)))

#     if len(ids)<self.max_len:
#       padding = torch.zeros(self.max_len - len(ids), dtype=ids.dtype)
#       ids = torch.cat((ids, padding), dim=0)
#       mask = torch.cat((mask,padding),dim=0)
#       token_type_ids = torch.cat((token_type_ids,padding),dim=0)
#     else:
#       # pass
#       print('Greater than 128')
#       ids = ids[:self.max_len]
#       mask = ids[:self.max_len]
#       token_type_ids = token_type_ids[:self.max_len]
#     return {
#             'ids': torch.tensor(ids, dtype=torch.long),
#             'mask': torch.tensor(mask, dtype=torch.long),
#             'token_type_ids': torch.tensor(token_type_ids, dtype=torch.long),
#             'targets': torch.tensor(self.targets[index], dtype=torch.float)
#            }

train_set = RTEDataset(train_df, tokenizer, MAX_LEN)
val_set = RTEDataset(val_df, tokenizer, MAX_LEN)
test_set = RTEDataset(test_df, tokenizer, MAX_LEN)

train_set[435]

train_params = {'batch_size': TRAIN_BATCH_SIZE,
                'shuffle': True,
                'num_workers': 0
                }

val_params = {'batch_size': VALID_BATCH_SIZE,
                'shuffle': True,
                'num_workers': 0
                }

test_params = {'batch_size': TEST_BATCH_SIZE,
                'shuffle': True,
                'num_workers': 0
                }

training_loader = DataLoader(train_set, **train_params)
validation_loader = DataLoader(val_set, **val_params)
testing_loader = DataLoader(test_set, **test_params)

# classifier = torch.nn.Sequential(
# 	torch.nn.Dropout(0.3),
# 	torch.nn.Linear(768, 2),
# 	torch.nn.Softmax()
# )

classifier = torch.nn.Sequential(
    nn.Linear(768,512),
    nn.ReLU(),
    nn.Linear(512,128),
    nn.ReLU(),
    nn.Linear(128,2),
    nn.Softmax()
)

class BERTClass(torch.nn.Module):
    def __init__(self):
        super(BERTClass, self).__init__()
        self.l1 = transformers.BertModel.from_pretrained('bert-base-uncased')
        self.seq = classifier

    def forward(self, ids, mask, token_type_ids):
        _, output_1= self.l1(ids, attention_mask = mask, token_type_ids = token_type_ids, return_dict=False)
        #print("Output shape is ", output_1.shape)
        output_1 = self.seq(output_1)
        #output_2 = self.l2(output_1)
        #output = self.l3(output_2)
      	#output = self.l4(output)
        return output_1

model = BERTClass()
model.to(device)

def loss_fn(outputs, targets):
    return torch.nn.CrossEntropyLoss()(outputs.float(), targets)

optimizer = torch.optim.Adam(params =  model.parameters(), lr=LEARNING_RATE)

def train():
    model.train()
    print("Steps Completed : ")
    for _, data in enumerate(training_loader):
        if _%3==0:
          print(_,end=' ')
        print(_)
        optimizer.zero_grad()
        ids = data['ids'].to(device, dtype = torch.long)
        mask = data['mask'].to(device, dtype = torch.long)
        token_type_ids = data['token_type_ids'].to(device, dtype = torch.long)
        targets = data['targets'].to(device, dtype = torch.long)
        # # Figure out
        # print(ids[0].shape)
        # print(ids[0])
        # print(token_type_ids[0])
        # # break
        outputs = model(ids, mask, token_type_ids)
        # outputs = torch.argmax(outputs, dim=1)
        loss = loss_fn(outputs, targets)
        loss.backward()
        optimizer.step()

def validation(epoch):
    model.eval()
    # fin_targets=[]
    # fin_outputs=[]

    val_accuracy = torchmetrics.Accuracy(task="multiclass", num_classes=2).to('cuda')
    with torch.no_grad():
        for _, data in enumerate(validation_loader):
            ids = data['ids'].to(device, dtype = torch.long)
            mask = data['mask'].to(device, dtype = torch.long)
            token_type_ids = data['token_type_ids'].to(device, dtype = torch.long)
            targets = data['targets'].to(device, dtype = torch.long)
            outputs = model(ids, mask, token_type_ids)
            val_accuracy.update(outputs, targets)
    print("The validation accuracy is ", val_accuracy.compute())
            # fin_targets.extend(targets.cpu().detach().numpy().tolist())
            # fin_outputs.extend(outputs.cpu().detach().numpy().tolist())

# outputs, targets = validation(1)

# ff = torch.argmax(torch.tensor(outputs), dim=1).float()

# sss = sum(np.array(ff)==np.array(targets))
# print(sss)
# print(len(ff))
# print(148/277)

# print(targets)
# print(ff)



# from torchmetrics import Accuracy
# # accuracy = metrics.accuracy_score(targets, ff.int().tolist())
# accuracy = Accuracy(task="multiclass", num_classes=3)
# final_acc = accuracy(torch.tensor(targets), ff.int())
# print(targets)
# print(ff.int())
# f1_score_micro = metrics.f1_score(targets, outputs, average='micro')
# f1_score_macro = metrics.f1_score(targets, outputs, average='macro')
# print(f"\nScores : Accuracy Score = {accuracy}, F1 Score (Micro) = {f1_score_micro}, F1 Score (Macro) = {f1_score_macro}")
# print(final_acc)

# outputs

epochs = 5
for epoch in range(epochs):
    print("Epoch : ",epoch+1)
    train()
    validation(epoch)
    # outputs = torch.argmax(torch.tensor(outputs), dim=1).float()
    # accuracy = metrics.accuracy_score(targets, outputs)
    # f1_score_micro = metrics.f1_score(targets, outputs, average='micro')
    # f1_score_macro = metrics.f1_score(targets, outputs, average='macro')
    # print(f"\nScores : Accuracy Score = {accuracy}, F1 Score (Micro) = {f1_score_micro}, F1 Score (Macro) = {f1_score_macro}")
    # print()

# from transformers import AutoTokenizer

# tokenizer_lol = AutoTokenizer.from_pretrained("bert-base-uncased")
# sequences_lol = ["This is a long sequence.", "Short one."]

# # Longest first truncation with resulting list returned
# resulting_list = tokenizer_lol(sequences_lol, truncation=True, max_length=10, return_overflowing_tokens=True)
# print(resulting_list)

