import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset
from transformers import AutoTokenizer, AutoModel
import numpy as np
from sklearn.neighbors import NearestNeighbors

HF_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
HF_MODEL_CACHE = "/opt/airflow/hf_model"

class TripletDataset(Dataset):
    def __init__(self, triplets, tokenizer, max_length=512):
        self.triplets = triplets
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __len__(self):
        return len(self.triplets)

    def __getitem__(self, idx):
        anchor, positive, negative = self.triplets[idx]
        return {
            'anchor': self.tokenizer(anchor, truncation=True, padding='max_length', max_length=self.max_length, return_tensors='pt'),
            'positive': self.tokenizer(positive, truncation=True, padding='max_length', max_length=self.max_length, return_tensors='pt'),
            'negative': self.tokenizer(negative, truncation=True, padding='max_length', max_length=self.max_length, return_tensors='pt'),
        }

class TripletNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(HF_MODEL_ID, cache_dir=HF_MODEL_CACHE)

    def forward(self, input_ids, attention_mask):
        outputs = self.encoder(input_ids=input_ids, attention_mask=attention_mask)
        return outputs.last_hidden_state[:, 0]  # CLS token

    def embed(self, batch):
        self.eval()
        with torch.no_grad():
            return self.forward(batch["input_ids"].squeeze(1), batch["attention_mask"].squeeze(1))

class TripletLoss(nn.Module):
    def __init__(self, margin=0.5):
        super().__init__()
        self.margin = margin

    def forward(self, anchor, positive, negative):
        pos_dist = F.pairwise_distance(anchor, positive)
        neg_dist = F.pairwise_distance(anchor, negative)
        return F.relu(pos_dist - neg_dist + self.margin).mean()

def get_triplet_dataset(texts, labels):
    from collections import defaultdict
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL_ID, cache_dir=HF_MODEL_CACHE)

    label_to_texts = defaultdict(list)
    for text, label in zip(texts, labels):
        label_to_texts[label].append(text)

    triplets = []
    for label in label_to_texts:
        positives = label_to_texts[label]
        negatives = [t for l, ts in label_to_texts.items() if l != label for t in ts]
        for anchor in positives:
            if len(positives) < 2 or not negatives:
                continue
            positive = np.random.choice([t for t in positives if t != anchor])
            negative = np.random.choice(negatives)
            triplets.append((anchor, positive, negative))

    return TripletDataset(triplets, tokenizer)

def encode_texts(model, tokenizer, texts, batch_size=16, device='cpu'):
    """
    Encode a list of texts into embeddings using the TripletNet.
    """
    model.eval()
    model.to(device)
    embeddings = []

    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        encoded = tokenizer(batch_texts, padding=True, truncation=True, return_tensors="pt", max_length=512)
        encoded = {k: v.to(device) for k, v in encoded.items()}
        with torch.no_grad():
            reps = model(encoded["input_ids"], encoded["attention_mask"])
        embeddings.append(reps.cpu().numpy())

    return np.vstack(embeddings)

class BatchMiner:
    def __init__(self, embeddings, labels, n_neighbors=20):
        self.embeddings = embeddings
        self.labels = labels
        self.n_neighbors = n_neighbors

        self.nn = NearestNeighbors(n_neighbors=n_neighbors, metric='cosine')
        self.nn.fit(embeddings)

    def get_hard_triplets(self):
        triplets = []
        for idx, emb in enumerate(self.embeddings):
            label = self.labels[idx]
            distances, indices = self.nn.kneighbors([emb])
            indices = indices.flatten()

            pos_idx = None
            neg_idx = None

            for i in indices[::-1]:  # farthest positive
                if i != idx and self.labels[i] == label:
                    pos_idx = i
                    break
            for i in indices:  # nearest negative
                if self.labels[i] != label:
                    neg_idx = i
                    break

            if pos_idx is not None and neg_idx is not None:
                triplets.append((idx, pos_idx, neg_idx))
        
        return triplets