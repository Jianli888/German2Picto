#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .germanet import GermaNet
from .containers import SentenceState


class SentenceStateCreator:
    """
    Class that loads GermaNet and adds SentenceStates to the analysed input sentences. These are also filled with all
    matching synsets for the input words.
    """

    def __init__(self):
        self._germanet = GermaNet()

    def create_sentence_states(self, doc):
        """
        Adds a SentenceState to each analysed sentence of the input text and inserts data in WordSynsets within all
        SentenceStates; in other words, finds all matching synsets (direct, hypernyms, xpos, antonyms) for all input
        words with their penalties and an indication about whether the synset refers to an antonymic concept of the
        original input word.
        """
        for sentence in doc.sentence_list:
            sentence_state = SentenceState(sentence)

            for i, word in enumerate(sentence_state.sentence):

                # skip search for synsets if we have the non-verb part of a separable verb
                if sentence_state.word_synsets[i].separable_word_part is True:
                    continue

                separable_verb, separated_index = self._detect_separable_verbs(word)

                if separable_verb is not None:
                    synsets, penalties, is_antonym = self._germanet.get_synsets_and_penalties(word, separable_verb)
                    if len(synsets) == 0:
                        synsets, penalties, is_antonym = self._germanet.get_synsets_and_penalties(word)

                    else:
                        sentence_state.word_synsets[separated_index].separable_word_part = True

                else:
                    synsets, penalties, is_antonym = self._germanet.get_synsets_and_penalties(word)

                sentence_state.word_synsets[i].synsets = synsets
                sentence_state.word_synsets[i].penalties = penalties
                sentence_state.word_synsets[i].antonym = is_antonym

            doc.sentence_states.append(sentence_state)

    @staticmethod
    def _detect_separable_verbs(word):
        """
        If word is the verb part of a separable verb, returns the whole separable verb and the sentence index of the
        separated non-verb part.
        """
        dependent_words = [child for child in word.children]
        dependent_dep = [dep_word.dep_ for dep_word in dependent_words]
        if 'svp' in dependent_dep:
            separated_part = dependent_words[dependent_dep.index('svp')]
            whole_verb = str(separated_part.lemma_) + str(word.lemma_)
            separated_index = list(word.sent).index(separated_part)
            return whole_verb, separated_index
        else:
            return None, None
