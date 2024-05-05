#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd


class Document:
    """
    Class to store input string and all its analysis states.
    """

    def __init__(self, string):
        self.string = string
        self.analysed_doc = None
        self.sentence_list = []
        self.sentence_states = []

class MultiWord:
    """
    Class objects store all multi-word expressions found in the lookup dictionary with their pictograms, info on whether
    the words have to be concatenated in the input (concat) and grammatical info (tags, morph).
    """

    def __init__(self, multiword_list, picto_path, tags_entry, morph_entry):
        self.multiword = multiword_list
        self.picto_path = picto_path
        self.tags = []
        self.morph = []

        if pd.isna(tags_entry) is False:
            tags_dict = eval(tags_entry)  # interpret str as dict
            tags_dict = {k.lower(): v for k, v in tags_dict.items()}
            for word in self.multiword:
                if word in tags_dict.keys():
                    self.tags.append(tags_dict[word])
                else:
                    self.tags.append(None)

        else:
            for _ in self.multiword:
                self.tags.append(None)

        if pd.isna(morph_entry) is False:
            morph_dict = eval(morph_entry)  # interpret str as dict
            morph_dict = {k.lower(): v for k, v in morph_dict.items()}
            for word in self.multiword:
                if word in morph_dict.keys():
                    self.morph.append(morph_dict[word])
                else:
                    self.morph.append(None)

        else:
            for _ in self.multiword:
                self.morph.append(None)


class SentenceState:
    """
    Container class used to return values in DirectRoute.direct_route().
    """

    def __init__(self, analysed_sentence):
        self.sentence_string = analysed_sentence.text
        self.sentence = analysed_sentence
        self.word_synsets = [WordSynsets() for _ in self.sentence]
        self.candidate_translations = [WordTranslationCandidates(word) for word in self.sentence]


class WordSynsets:
    """
    Class that stores all synsets connected to an input word, the penalties associated with the synsets and whether the
    synsets are in an antonymic relation with the input word.
    """

    def __init__(self):
        self.synsets = []
        self.penalties = []
        self.antonym = []
        self.separable_word_part = False


class WordTranslationCandidates:
    """
    Class that holds all possible (black-and-white) pictogram translations for an input word, their penalties, info on
    whether the pictogram is simple or complex and whether the input word is in an antonymic relation with a pictogram.
    """
    def __init__(self, token):
        self.token = token
        self.picto_paths = []
        self.penalties = []
        self.translation_type = []  # each item ∈ {'simple', 'complex'}
        self.antonym = []  # each item ∈ {True, False}
        self.bw_picto_paths = []

    def add_candidate(self, picto_path, penalty, translation_type, is_antonym, bw_picto_path):
        """
        Adds a translation candidate to the class.
        """
        if picto_path not in self.picto_paths:
            self.picto_paths.append(picto_path)
            self.penalties.append(penalty)
            self.translation_type.append(translation_type)
            self.antonym.append(is_antonym)
            self.bw_picto_paths.append(bw_picto_path)
