"Dummy Fts backend"

from fts.backends.base import BaseClass, BaseModel, BaseManager
from django.db.models import Q

from fts.words.stop import FTS_STOPWORDS

try:
    from fts.words.snowball import Stemmer
except ImportError:
    from fts.words.porter import Stemmer

class SearchClass(BaseClass):
    def __init__(self, server, params):
        self.backend = 'dummy'

class SearchManager(BaseManager):
    def update_index(self, pk=None):
        pass

    def search(self, query, **kwargs):
        params = Q()
        for w in set(query.lower().split(' ')):
            if w and w not in FTS_STOPWORDS[self.language_code]:
                p = Stemmer(self.language_code)
                w = p(w)
                for field in self._fields.keys():
                    params &= Q(**{'%s__icontains' % field: w})
        return self.filter(params)

class SearchableModel(BaseModel):
    class Meta:
        abstract = True

    objects = SearchManager()
