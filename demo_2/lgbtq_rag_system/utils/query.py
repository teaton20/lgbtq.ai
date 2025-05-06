# lgbtq_rag_system/utils/query.py

import re

# Simple set of stopwords; extend as needed.
STOPWORDS = set(['the', 'and', 'is', 'in', 'of', 'to', 'a'])

# Controlled synonym map for query expansion.
SYNONYM_MAP = {
    'affirming': ['safe', 'welcoming', 'supportive', 'inclusive'],
    'trans': ['transgender', 'transsexual', 'mtf', 'ftm', 'nonbinary', 'transmasc', 'transfem'],
    'queer': ['lgbtq', 'non-heterosexual', 'gay', 'lesbian', 'bi', 'lgbtqia+'],
    'healthcare': ['medical', 'treatment', 'doctor', 'clinic', 'transition care'],
    'hormone': ['hrt', 'estrogen', 'testosterone', 'puberty blockers'],
    'rights': ['legal', 'anti-discrimination', 'civil rights', 'equality'],
    'safety': ['safe', 'protected', 'welcoming', 'low risk', 'friendly'],
    'towns': ['cities', 'communities', 'places', 'locations'],
    'transition': ['gender transition', 'mtf', 'ftm', 'sex reassignment', 'top surgery', 'bottom surgery'],
}

def preprocess_query(query):
    """
    Preprocess the user query:
      - Lowercase the query.
      - Tokenize by splitting into words.
      - Remove stopwords.
      - Expand tokens using a synonym map.
    Returns a list of tokens.
    """
    query = query.lower()
    tokens = re.findall(r'\b\w+\b', query)
    tokens = [token for token in tokens if token not in STOPWORDS]
    expanded_tokens = []
    for token in tokens:
        expanded_tokens.append(token)
        if token in SYNONYM_MAP:
            expanded_tokens.extend(SYNONYM_MAP[token])
    return expanded_tokens