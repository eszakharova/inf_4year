
# coding: utf-8

# ## Функция ранжирования Okapi BM25

# Если у вас нет ассесоров, которые могут проставить оценки релевантности документам, вышепроделанный способ ранжирования вам не подходит. В этом случае можно использовать формулу *Okapi best match 25* ([Okapi BM25](https://ru.wikipedia.org/wiki/Okapi_BM25)). Пусть дан запрос $Q$, содержащий слова  $q_1, ... , q_n$, тогда функция BM25 даёт следующую оценку релевантности документа $D$ запросу $Q$:
# 
# $$ score(D, Q) = \sum_{i}^{n} \text{IDF}(q_i)*\frac{(k+1)*f(q_i,D)}{f(q_i,D)+k_1(1-b+b\frac{|D|}{avgdl})} $$ 
# где $f(q_i,D)$ - частота слова (TF) $q_i$ в документе $D$, $|D|$ - длина документа (количество слов в нём), а *avgdl* — средняя длина документа в коллекции. 
# $$$$
# $k_1$ и $b$ — свободные коэффициенты, обычно их выбирают как $k_1$=2.0 и $b$=0.75.
# $$$$
# $\text{IDF}(q_i)$ есть обратная документная частота (IDF) слова $q_i$: 
# $$\text{IDF}(q_i) = \log\frac{N-n(q_i)+0.5}{n(q_i)+0.5},$$
# где $N$ - общее количество документов в коллекции, а  $n(q_i)$ — количество документов, содержащих $q_i$. 

# In[1]:

from inv_index import InvIndex


# In[2]:

from os import listdir


# In[3]:

from IPython.display import HTML, display
from collections import defaultdict


# In[4]:

from math import log

k1 = 2.0
b = 0.75

def score_BM25(n, qf, N, dl, avdl):
    K = compute_K(dl, avdl)
    IDF = log((N - n + 0.5) / (n + 0.5))
    frac = ((k1 + 1) * qf) / (K + qf)
    return IDF * frac


def compute_K(dl, avdl):
    return k1 * ((1-b) + b * (float(dl)/float(avdl)))


# **Задание по проекту.** 
# Для его выполнения вам понадобится собранная коллекция документов и функция, составляющая обратный индекс по словам в коллекции.
# 
# Напишите функцию (или несколько отдельных логичный функций), которая по запросу $Q = q_1,..., g_n$ и коллекции $D$ сортирует выдачу подходящих документов. Будем считать документ подходящим, если он содержит хотя бы одно слово из запроса (из которого удалены стоп-слова). В качестве метрики используйте *Okapi BM25*.
# 
# Для проверки работы функции на вашем корпусе используйте запрос **каникулы на новый год и рождество**. Выведите ссылки в ipynb на первые десять докуменов в отсортированной выдаче(как во втором семинаре с помощью IPython.display) и их оценку BM25. Напомню, что ссылки на документы хрянятся в самих доках под тэгом @url.

# Про что не забыть:
# 1. Лемматизируем запрос, удаляем стоп-слова => запрос готов
# 2. Лемматизируем слова в документах => документы готовы к подсчетам статистик по запросу

# In[5]:

class Document:
    def __init__(self, lines):
        self.author = lines[0].strip('@au').strip()
        self.title = lines[1].strip(r'@ti').strip()
        self.date = lines[2].strip(r'@da').strip()
        self.topic = lines[3].strip(r'@topic').strip()
        self.url = lines[4].strip(r'@url').strip()
        self.text = lines[5].strip()
        self.tokens = None


# In[21]:

class SearchRank:
    def __init__(self, dir_path):
        self.maker = InvIndex('russian')
        self.read_documents(dir_path)
        
    def read_documents(self, dir_path):
        self.documents = []
        self.unique = []
        sum_dl = 0
        cnt = 1
        for filename in listdir(dir_path):
            f = open(''.join([dir_path, '/', filename]), encoding='utf-8')
            lines = f.readlines()
            doc = Document(lines)
            if doc.title not in self.unique:
                self.documents.append(doc)
                self.unique.append(doc.title)
        for document in self.documents:
            cnt += 1
            document.tokens = self.maker.tokenize(document.text)
            sum_dl += len(document.tokens)
        self.inv_idx = self.maker.inv_index([document.tokens for document in self.documents], defaultdict(set))
        self.N = len(self.documents)
        self.avdl = sum_dl/self.N
        
    def query(self, query, num_links=10, another_dir_path=None):
        query_tokens = self.maker.tokenize(query)
        ranking = defaultdict(int)
        if another_dir_path:
            self.read_documents(another_dir_path)
        if not self.documents:
            return None
        else:
            res = []
            for document in self.documents:
                has_query_words = False
                for q_token in query_tokens:
                    if q_token in self.inv_idx:
                        n = len(self.inv_idx[q_token])
                    else:
                        n = 0
                    qf = document.tokens.count(q_token)
                    if qf > 0:
                        has_query_words = True
                    dl = len(document.tokens)
                    ranking[document] += score_BM25(n, qf, self.N, dl, self.avdl)
                if not has_query_words:
                    ranking.pop(document, None)

            if len(ranking) < num_links:
                num_links = len(ranking)
        for doc in sorted(ranking, key=lambda x: ranking[x], reverse=True)[:num_links]:
            res.append((doc.url, doc.title,  ranking[doc]))
        return res
