# Contains classes to call different spell checking libraries, and perform OCR spelling correction

from wordfreq import word_frequency
from textdistance import levenshtein

# Base class that gets a list of suggestions, possibly sorts them by
# word frequency, and filters out those which are too different from original word
class SpellChecker(object):
    def __init__(self, 
                 personal_dict   = None,
                 personal_subs   = None,
                 do_word_freqs   = True, 
                 max_diff_cutoff = 3, 
                 caching         = True):
        # If True, then we will sort suggestions by word frequency
        self.do_word_freqs   = do_word_freqs    
        
        # Disallows corrections which are more than max_diff_cutoff different from original
        self.max_diff_cutoff = max_diff_cutoff  
        
        # Dictionary of custom substitutions
        self.personal_subs   = personal_subs
        
        # List of words that are OK (in personal dictionary)
        self.personal_dict   = personal_dict
        
        if caching:  # Maintain cache of corrections
            self._cache = {}
            
    def check(self, s):
        if self.personal_dict and s.lower() in self.personal_dict:
            return True
        else:
            return self._check(s)
        
    def correct(self, s):
        if self.personal_subs and s in self.personal_subs:
            return self.personal_subs[s]
        
        if s not in self._cache:
            # Corrects things like "selfgovernance" to "self-governance"
            if s.startswith('self') and not s.startswith('self-') and self.check('self-'+s[4:]):
                self._cache[s] = 'self-'+s[4:]
                
            elif s == ']' or s=='[': # the OCR sometime reads in "I" as ']' and '['
                self._cache[s] = 'I'
                
            else:
                # get suggestions from spell checker
                suggestions = self.correction_suggestions(s)
                if len(suggestions) and self.do_word_freqs:
                    # Compute word frequencies for each suggestions
                    freqs = [(r, word_frequency(r, 'en')) for r in suggestions]
                    # Sorted by word frequency (in descending order)
                    suggestions = [r[0] for r in sorted(freqs, key=lambda x: -x[1])]
                if len(suggestions) and self.max_diff_cutoff:
                    # Filter out those suggestions which are not more than max_diff_cutoff away from original
                    suggestions = [r for r in suggestions 
                                   if levenshtein.distance(s, r)<= self.max_diff_cutoff]

                if len(suggestions): # Suggestion found
                    self._cache[s] = suggestions[0]
                else:                # Use original word
                    self._cache[s] = s
                
        return self._cache[s]

# The following classes provide interface spell checkers provided by different libraries
class HunspellChecker(SpellChecker):
    def __init__(self, **kwargs):
        import hunspell
        self.obj = hunspell.HunSpell('en_US.dic', 'en_US.aff')
        super().__init__(**kwargs)
        
    def _check(self, s):
        return self.obj.spell(s)
    
    def correction_suggestions(self, s):
        return self.obj.suggest(s)
        
        
class TextblobChecker(object):
    def __init__(self):
        import textblob
        self.obj = textblob
        
    def correct(self, s):
        t = self.obj.TextBlob(s) # Making our first textblob
        return t.correct()       # Correcting the text
    

class ASpellChecker(SpellChecker):
    def __init__(self, **kwargs):
        import aspell
        self.obj = aspell.Speller(('dict-dir', '/home/artemy/aspell6-en-2020.12.07-0'), )
        super().__init__(**kwargs)
    
    def correction_suggestions(self, s):
        return self.obj.suggest(s)
    
    
class SymspellChecker(SpellChecker):
    def __init__(self, **kwargs):
        import pkg_resources
        import symspellpy
        self.obj = symspellpy.SymSpell(max_dictionary_edit_distance=2, prefix_length=7)
        dictionary_path = pkg_resources.resource_filename(
            "symspellpy", "frequency_dictionary_en_82_765.txt")
        bigram_path = pkg_resources.resource_filename(
            "symspellpy", "frequency_bigramdictionary_en_243_342.txt")
        self.obj.load_dictionary(dictionary_path, term_index=0, count_index=1)
        self.obj.load_bigram_dictionary(bigram_path, term_index=0, count_index=2)
        self.verbosity = symspellpy.Verbosity.CLOSEST
        super().__init__(**kwargs)

    def correction_suggestions(self, s):
        suggestions = self.obj.lookup(s, self.verbosity, max_edit_distance=2)
        if not len(suggestions):
            suggestions = self.obj.lookup_compound(s, max_edit_distance=2)
        return suggestions[0].term

class JamspellChecker(object):
    def __init__(self):
        import jamspell

        self.obj = jamspell.TSpellCorrector()
        self.obj.LoadLangModel('en.bin')

    def correct(self, s):
        return self.obj.FixFragment(s)

    
class NeuspellChecker(object):
    def __init__(self):
        import neuspell
        self.obj=neuspell.CnnlstmChecker()
        self.obj.from_pretrained()
        
        import logging
        logger = logging.getLogger("spacy")
        logger.setLevel(logging.ERROR)

    def correct(self, s):
        return self.obj.correct(s)
        


ALL_CHECKERS = [
    HunspellChecker,
    TextblobChecker,
    ASpellChecker,
    SymspellChecker,
    JamspellChecker,
    NeuspellChecker]

