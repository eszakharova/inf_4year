
# coding: utf-8

# In[1]:

from collections import defaultdict
from os import listdir
from string import punctuation
from nltk import word_tokenize
from nltk.corpus import stopwords
from pymystem3 import Mystem
mystem = Mystem()


# In[9]:

class InvIndex:
    def __init__(self, language):
        self.punctuation = punctuation
        self.stopwords = stopwords.words(language)
        self.inverted_index = defaultdict(set)
        self.last_doc_n = 0

    def tokenize(self, text, remove_stopwords=True, make_lemmas=True):
        text = text.lower()
        if remove_stopwords:
            tokens = [i.strip('\'«»`') for i in word_tokenize(text)
                      if i not in self.stopwords and i not in self.punctuation]
        else:
            tokens = [i.strip('\'«»') for i in word_tokenize(text) if i not in self.punctuation]
        tokens = [j for j in tokens if j]
        if make_lemmas:
            lemmas = [mystem.lemmatize(t)[0] for t in tokens]
        else:
            lemmas = tokens
        return lemmas

    def doc_collection(self, dir_path):
        tokenized_doc_collection = []
        for filename in listdir(dir_path):
            f = open(''.join([dir_path, '/', filename]), encoding='utf-8')
            text = f.read()
            tokens = self.tokenize(text)
            tokenized_doc_collection.append(tokens)
        return tokenized_doc_collection

    def inv_index(self, tokenized_doc_collection, inv_index):
        if not inv_index:
            for i, doc in enumerate(tokenized_doc_collection):
                for term in doc:
                    inv_index[term].add(i)
        else:
            for i, doc in enumerate(tokenized_doc_collection, start=self.last_doc_n):
                for term in doc:
                    inv_index[term].add(i)

        return inv_index

    def make(self, dir_path):
        """ Сделать обратный индекс по всем документам в папке 
        (без возможности потом его дополнить).
        """
        return self.inv_index(self.doc_collection(dir_path), defaultdict(set))

    def add(self, dir_path):
        """ При первом вызове - сделать обратный индекс по всем документам в папке,
            при последующих вызовах - дополнить обратный индекс документами из папки.
        """
        docs = self.doc_collection(dir_path)
        result = self.inv_index(docs, self.inverted_index)
        self.last_doc_n += len(docs)
        return result  


# In[10]:

# inv = InvIndex('russian')
# print(inv.tokenize('каникулы на новый год и рождество'))


# In[11]:

# inv.add('collection')


# In[12]:

# inv.add('collection2')


# In[13]:

# inv.make('collection')

