"Simple Fts backend"
import os
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import Q

from django.db import transaction

from fts.backends.base import BaseClass, BaseModel, BaseManager
from fts.models import IndexWord, Index

from fts.words.stop import FTS_STOPWORDS

try:
    from fts.words.snowball import Stemmer
except ImportError:
    from fts.words.porter import Stemmer
    
class SearchClass(BaseClass):
    def __init__(self, server, params):
        self.backend = 'simple'

class SearchManager(BaseManager):
    @transaction.commit_on_success
    def update_index(self, pk=None):
        if pk is not None:
            if isinstance(pk, (list,tuple)):
                items = self.filter(pk__in=pk)
            else:
                items = self.filter(pk=pk)
            items[0]._index.all().delete()
        else:
            items = self.all()
            model_type = ContentType.objects.get_for_model(self.model)
            Index.objects.filter(content_type__pk=model_type.id).delete()
        
        IW = {}
        for item in items:
            for field, weight in self._fields.items():
                for w in set(getattr(item, field).lower().split(' ')):
                    if w and w not in FTS_STOPWORDS[self.language_code]:
                        p = Stemmer(self.language_code)
                        w = p(w)
                        try:
                            iw = IW[w];
                        except KeyError:
                            iw = IndexWord.objects.get_or_create(word=w)[0]
                            IW[w] = iw
                        i = Index(content_object=item, word=iw)
                        i.save()

    def search(self, query, **kwargs):
        params = Q()
        for w in set(query.lower().split(' ')):
            if w and w not in FTS_STOPWORDS[self.language_code]:
                p = Stemmer(self.language_code)
                w = p(w)
                params |= Q(_index__word__word=w)
        return self.filter(params).distinct()

class SearchableModel(BaseModel):
    class Meta:
        abstract = True

    _index = generic.GenericRelation(Index)

    objects = SearchManager()
