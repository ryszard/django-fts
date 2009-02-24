"Base Fts class."

from django.db import transaction
from django.db import models
from django.conf import settings

from django.core.exceptions import ImproperlyConfigured

class InvalidFtsBackendError(ImproperlyConfigured):
    pass

class BaseClass(object):
    class Meta:
        abstract = True

class BaseManager(models.Manager):
    class Meta:
        abstract = True

    def __init__(self, **kwargs):
        super(BaseManager, self).__init__()
        self.fields = kwargs.get('fields')
        self.default_weight = kwargs.get('default_weight', '')
        self.language_code = kwargs.get('language_code')
        if not self.language_code:
            from django.utils import translation
            self.language_code = translation.get_language().split('-',1)[0].lower()
        
    def __call__(self, query, **kwargs):
        return self.search(query, **kwargs)

    def contribute_to_class(self, cls, name):
        # Instances need to get to us to update their indexes.
        setattr(cls, '_search_manager', self)
        super(BaseManager, self).contribute_to_class(cls, name)

        if not self.fields:
            self.fields = self._find_text_fields()
        
        if isinstance(self.fields, (list, tuple)):
            self._fields = {}
            for field in self.fields:
                self._fields[field] = self.default_weight
        else:
            self._fields = fields

    def update_index(self, pk=None):
        """
        Updates the full-text index for one, many, or all instances of this manager's model.
        """
        raise NotImplementedError

    def search(self, query, **kwargs):
        raise NotImplementedError

    def _find_text_fields(self):
        """
        Return the names of all CharField and TextField fields defined for this manager's model.
        """
        fields = [f for f in self.model._meta.fields if isinstance(f, (models.CharField, models.TextField))]
        return [f.name for f in fields]

class BaseModel(models.Model):
    """
    A convience Model wrapper that provides an update_index method for object instances,
    as well as automatic index updating. The index is stored as a tsvector column on the
    model's table. A model may specify a boolean class variable, _auto_reindex, to control
    whether the index is automatically updated when save is called.
    """
    class Meta:
        abstract = True

    def update_index(self):
        """
        Update the index.
        """
        if hasattr(self, '_search_manager'):
            self._search_manager.update_index(pk=self.pk)

    @transaction.commit_on_success
    def save(self, *args, **kwargs):
        super(BaseModel, self).save(*args, **kwargs)
        if hasattr(self, '_auto_reindex'):
            if self._auto_reindex:
                self.update_index()
        else:
            self.update_index()
