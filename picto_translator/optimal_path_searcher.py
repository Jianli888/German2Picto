#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import copy
import os


class OptimalPathSearcher:
    """
    Class for finding the translation with the lowest cost. By now, all words may have several translation candidates,
    but we want to take the overall path over the sentence that minimises the sum of the penalties of the translations.
    A* search algorithm was used for this (cf. Vandeghinste et al. 2015).
    """

    def __init__(self):
        self._negative_picto = os.path.normpath('METACOM_Symbole/Symbole_PNG/PNG_ohne_Rahmen/Kleine_Worte/nichtkein.png')

    def _extend_queue(self, path):
        """
        Takes the currently best path and extends it with all possible translations.
        """
        new_paths = []
        current_word_candidates = path.left_to_translate.candidate_translations.pop(0)

        # complex pictographs
        if 'complex' in current_word_candidates.translation_type:
            complex_candidate_indices = [i for i, t_type in enumerate(current_word_candidates.translation_type) if t_type == 'complex']

            for complex_candidate_index in complex_candidate_indices:
                complex_picto = current_word_candidates.picto_paths[complex_candidate_index]
                if isinstance(current_word_candidates.bw_picto_paths[complex_candidate_index], str):
                    complex_picto_bw = current_word_candidates.bw_picto_paths[complex_candidate_index]
                translated_words = [current_word_candidates.token]
                is_antonym = [current_word_candidates.antonym[complex_candidate_index]]
                other_complex_words = []
                current_cost = current_word_candidates.penalties[complex_candidate_index]

                # see for other words belonging to the complex picto
                for future_word_index, future_word in enumerate(path.left_to_translate.candidate_translations):
                    if complex_picto in future_word.picto_paths:
                        future_complex_index = future_word.picto_paths.index(complex_picto)
                        if future_word.antonym[future_complex_index] is True:
                            is_antonym.append(True)
                        else:
                            is_antonym.append(False)
                        other_complex_words.append(future_word_index)
                        translated_words.append(future_word.token)
                        current_cost += future_word.penalties[future_complex_index]

                if len(other_complex_words) > 0:
                    new_path = copy.copy(path)
                    new_path.left_to_translate.candidate_translations = [c for i, c in enumerate(
                        path.left_to_translate.candidate_translations) if i not in other_complex_words]

                    new_translated = path.translated.copy()
                    new_translated_bw = path.translated_bw.copy()

                    new_translated_words = path.translated_words.copy()

                    # assumption: it is unlikely that all synsets of the complex picto are in an antonymic relation
                    # with the input word; only one word can be in antonymic relation with input word
                    # (e.g. in 'hoher Blutdruck' -> only 'hoch' can have an antonym, i.e. 'tief', but not 'Blutdruck')
                    if True in is_antonym:
                        new_translated.append(self._negative_picto)
                        new_translated_words.append(tuple(['#NEG#']))

                    new_translated.append(complex_picto)

                    try:
                        if True in is_antonym:
                            new_translated_bw.append(self._negative_picto)
                        new_translated_bw.append(complex_picto_bw)
                    except NameError:
                        new_translated_bw.append(None)

                    new_translated_words.append(tuple(translated_words))

                    new_cost = path.cost + current_cost
                    new_path = Path(new_path.left_to_translate, new_translated, new_translated_bw, new_translated_words,
                                    new_cost)
                    new_paths.append(new_path)

        if 'simple' in current_word_candidates.translation_type:
            simple_indices = [i for i, t_type in enumerate(current_word_candidates.translation_type) if t_type == 'simple']
            for simple_candidate_index in simple_indices:

                new_translated = path.translated.copy()
                new_translated_bw = path.translated_bw.copy()
                new_translated_words = path.translated_words.copy()

                if current_word_candidates.antonym[simple_candidate_index] is True:
                    new_translated.append(self._negative_picto)
                    new_translated_words.append(tuple(['#NEG#']))

                new_translated.append(current_word_candidates.picto_paths[simple_candidate_index])

                try:
                    if current_word_candidates.antonym[simple_candidate_index] is True:
                        new_translated_bw.append(self._negative_picto)
                    new_translated_bw.append(current_word_candidates.bw_picto_paths[simple_candidate_index])
                except NameError:
                    new_translated_bw.append(None)

                new_translated_words.append(tuple([current_word_candidates.token]))
                new_cost = path.cost + current_word_candidates.penalties[simple_candidate_index]
                new_paths.append(Path(path.left_to_translate, new_translated, new_translated_bw, new_translated_words,
                                      new_cost))

        if len(new_paths) == 0:
            new_translated = path.translated.copy()
            new_translated_bw = path.translated_bw.copy()

            new_translated.append(None)
            new_translated_bw.append(None)
            new_paths.append(Path(path.left_to_translate, new_translated, new_translated_bw, path.translated_words +
                                  [tuple([current_word_candidates.token])], path.cost + 1))

        return new_paths, current_word_candidates.picto_paths

    def find_best_path(self, doc):
        """
        Returns the translation with the lowest cost.
        """
        sentence_translations = []
        bw_sentence_translations = []
        translated_sentences = []
        further_translations = []
        for sentence_state in doc.sentence_states:
            path_0 = Path(sentence_state, [], [], [], 0)
            queue = [path_0]
            further_sentence_translations = []

            while True:
                queue, further_translation_candidates = self._extend_queue(queue[0])
                queue.sort(key=self._take_cost)

                if len(queue[0].translated_words) >= 2:
                    if isinstance(queue[0].translated_words[-2][0], str):
                        if queue[0].translated_words[-2][0] == '#NEG#':
                            further_sentence_translations.append([])

                further_sentence_translations.append(further_translation_candidates)
                if len(queue[0].left_to_translate.candidate_translations) == 0:
                    break

            sentence_translations.append(queue[0].translated)
            bw_sentence_translations.append(queue[0].translated_bw)
            translated_sentences.append(queue[0].translated_words)
            further_translations.append(further_sentence_translations)
        return sentence_translations, bw_sentence_translations, translated_sentences, further_translations

    @staticmethod
    def _take_cost(path):
        return path.cost


class Path:
    """
    Used in OptimalPathSearcher to store sentence translation candidates. Stores which words still need to be translated
    (left_to_translate), the current translation (translated) and the current cost of the translation (cost).
    """

    def __init__(self, left_to_translate, translated, translated_bw, translated_words, cost):
        self.left_to_translate = left_to_translate  # of type SentenceState
        self.translated = translated
        self.translated_bw = translated_bw
        self.translated_words = translated_words
        self.cost = cost

