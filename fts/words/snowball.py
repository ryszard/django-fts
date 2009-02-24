"""
Snowball
--------
Snowball <http://snowball.tartarus.org/> is a multi-language stemming library
with Python bindings.

<http://snowball.tartarus.org/wrappers/PyStemmer-1.0.1.tar.gz>
"""

from Stemmer import Stemmer as _Stemmer

class Stemmer(object):
    def __init__(self, language=''):
        if language:
            self.stemmer = _Stemmer(language)
        else:
            self.stemmer = None

    def __call__(self, word):
        if self.stemmer is None:
            return word.lower()
        return self.stemmer.stemWord(word).lower()
