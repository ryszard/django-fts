from django.db import models
import fts

class Blog(fts.SearchableModel):
    title = models.CharField(max_length=100)
    body = models.TextField()

    # Defining a SearchManager without fields will use all CharFields and TextFields
    # this is the default and you do not need to explicitly add the following line:
    # objects = fts.SearchManager()

    # You can pass a list of fields that should be indexed
    # objects = SearchManager( fields=('title','body') )
    
    # You may also specify fields as a dictionary, mapping each field to a weight for ranking purposes
    # see http://www.postgresql.org/docs/8.3/static/textsearch-features.html#TEXTSEARCH-MANIPULATE-TSVECTOR
    #objects = SearchManager( fields={
    #    'title': 'A',
    #    'body': 'B',
    #} )

    def __unicode__(self):
        return u"%s" % (self.title)
