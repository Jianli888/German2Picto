#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from germanetpy.germanet import Germanet
from germanetpy.synset import WordCategory


class GermaNet:
    """
    Class to load, store and search GermaNet.
    """

    def __init__(self):
        self.germanet = Germanet('static/data/GN_V160/GN_V160/GN_V160_XML')

    def get_synsets_and_penalties(self, word, separable_verb=None):
        """
        Returns all synsets, their penalties and antonymic relation connected to the search word.
        """
        if separable_verb is not None:
            search_word = separable_verb
            direct_synsets = self.germanet.get_synsets_by_orthform(search_word)
            if len(direct_synsets) == 0:
                search_word = word.lemma_
                direct_synsets = self.germanet.get_synsets_by_orthform(search_word)

        else:
            search_word = word.lemma_

        penalties = []
        direct_synsets = self.germanet.get_synsets_by_orthform(search_word)
        all_synsets = []

        # if there are no results for the search and the lemma has a double s "ss", retry the search with an Eszett "ß"
        if len(direct_synsets) == 0:
            eszett_word = search_word.replace('ss', 'ß')
            direct_synsets = self.germanet.get_synsets_by_orthform(eszett_word)

        if len(direct_synsets) == 0:
            return direct_synsets, penalties, []

        # check whether word category is correct
        for dir_syn in direct_synsets:
            corresponds = self._check_word_category(word, dir_syn)
            if corresponds:
                all_synsets.append(dir_syn)

        # add 0 penalty for direct matches
        for _ in all_synsets:
            penalties.append(0)

        # add hypernyms, antonyms, xpos synsets
        hypernyms, h_penalty = self._search_hypernyms(direct_synsets, 3)
        antonyms, a_penalty = self._search_antonyms(direct_synsets)
        xpos, x_penalty = self._search_xpos(direct_synsets)

        all_synsets += antonyms + xpos + hypernyms
        penalties += a_penalty + x_penalty + h_penalty
        is_antonym = [False] * len(direct_synsets) + [True] * len(antonyms) + [False] * (len(xpos) + len(hypernyms))

        return all_synsets, penalties, is_antonym

    def _check_word_category(self, original_word, found_synset):
        """
        Returns True if parts of speech of input word and found synset match, otherwise returns False.
        """
        spacy_pos = {'NN': 'NOUN', 'NE': 'NOUN', 'ADJD': 'ADJ', 'ADJA': 'ADJ', 'CARD': 'ADJ', 'VVFIN': 'VERB',
                     'VAFIN': 'VERB', 'VMFIN': 'VERB', 'VVIMIP': 'VERB', 'VAIMP': 'VERB', 'VVINF': 'VERB', 'VVIZU': 'VERB',
                     'VAINF': 'VERB', 'VMINF': 'VERB', 'VVPP': 'VERB', 'VMPP': 'VERB', 'VAPP': 'VERB', 'PIAT': 'ADJ',
                     'PIS': 'ADJ', 'ADV': 'ADJ'}
        synset_word_cat_dict = {WordCategory.nomen: 'NOUN', WordCategory.adj: 'ADJ', WordCategory.verben: 'VERB'}
        try:
            synset_word_category = synset_word_cat_dict[found_synset.word_category]
            orig_word_category = spacy_pos[original_word.tag_]
            if synset_word_category == orig_word_category:
                return True
            else:
                return False
        except KeyError:
            return False


    @staticmethod
    def _search_hypernyms(synsets, hypernym_levels):
        """
        Searches hypernyms and their penalties of input word's synsets. hypernym_levels refers to how many hypernymic
        levels should be considered.
        """
        found_hypernyms = []
        penalties = []
        for i in range(hypernym_levels):
            if i == 0:
                hypernyms = [hypernym for synset in synsets for hypernym in synset.direct_hypernyms]
                found_hypernyms += hypernyms
                penalties += [8 for _ in hypernyms]
            else:
                # hypernyms of hypernyms
                hypernyms = [hypernym for synset in hypernyms for hypernym in synset.direct_hypernyms]
                found_hypernyms += hypernyms
                penalties += [(i + 1) * 8 for _ in hypernyms]

        return found_hypernyms, penalties

    @staticmethod
    def _search_xpos(synsets):
        """
        Searches synsets of similar concepts but with different part-of-speech than input synsets.
        """

        found_xpos = []
        lexunits = [lexunit for synset in synsets for lexunit in synset.lexunits]

        for lexunit in lexunits:
            for relation, found_lexunits in lexunit.relations.items():
                if 'pertainym' in str(relation) or 'participle' in str(relation):
                    found_synsets = [found_lexunit.synset for found_lexunit in found_lexunits]
                    found_xpos += found_synsets

        penalties = [7 for _ in found_xpos]
        return found_xpos, penalties

    @staticmethod
    def _search_antonyms(synsets):
        """
        Searches antonyms of input synsets.
        """
        found_antonyms = []
        lexunits = [lexunit for synset in synsets for lexunit in synset.lexunits]

        for lexunit in lexunits:
            for relation, found_lexunits in lexunit.relations.items():
                if 'antonym' in str(relation):
                    found_synsets = [found_lexunit.synset for found_lexunit in found_lexunits]
                    found_antonyms += found_synsets

        penalties = [7 for _ in found_antonyms]

        return found_antonyms, penalties
