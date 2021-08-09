import torch
import numpy as np
import pandas as pd
from torch.utils.data import TensorDataset, DataLoader, SequentialSampler
from transformers import BertTokenizer, BertForSequenceClassification

def fit(in_text):
  device = torch.device('cpu')
  batch_size = 3

  #df = pd.read_csv('data_t.csv')
  df = pd.DataFrame(in_text)

  print(type(df))
  print(df)

  possible_labels = ['marketing', 'project management', 'account management', 'leading', 'analytics', 'sales', 'communication management', 'social media management', 'business development', 'accounting']

  x_val = df.index.values

  tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)

  encoded_data_val = tokenizer.batch_encode_plus(
    df.text.values,
    add_special_tokens=True,
    return_attention_mask=True,
    return_tensors='pt',
    padding='max_length',
    max_length=256,
    truncation=True
  )

  input_ids_val = encoded_data_val['input_ids']
  attention_masks_val = encoded_data_val['attention_mask']
  dataset_val = TensorDataset(input_ids_val, attention_masks_val)
  dataloader_val = DataLoader(dataset_val, sampler=SequentialSampler(dataset_val), batch_size=batch_size)

  print('-- bert begin --')
  print()

  model = BertForSequenceClassification.from_pretrained("bert-base-uncased", num_labels=len(possible_labels), output_attentions=False, output_hidden_states=False)
  model.to(device)
  model.load_state_dict(torch.load('/opt/cv_data/skill_bert_weights/finetuned_BERT_epoch_5.model', map_location=torch.device('cpu')))
  model.eval()


  print()
  print('-- bert end --')
  print()

  predictions = []
  for batch in dataloader_val:
    batch = tuple(b.to(device) for b in batch)
    inputs = {'input_ids': batch[0], 'attention_mask': batch[1], 'labels': torch.tensor([0, 0, 0])} #batch[2]}

    with torch.no_grad():
      outputs = model(**inputs)
      logits = outputs[1]
      logits = logits.detach().cpu().numpy()
      predictions.append(logits)
    predictions = np.concatenate(predictions, axis=0)

  print(possible_labels)
  print()

  predictions = np.around(np.array(predictions),2)

  for i in range(len(df.text.values)):
    print(df.text.values[i])
    print(predictions[i])
    print()



  res = list(map(list, zip(*[possible_labels, predictions.tolist()[0]])))
  res = sorted(res, key = lambda x: x[1], reverse=True)

  print(res)
  return(res)

if __name__ == '__main__':
  fit(None)
