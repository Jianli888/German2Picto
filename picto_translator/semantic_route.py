#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .picto_db import PictoDB


class SemanticRoute:
    """
    Class that stores the pictogram-synset database and that contains all necessary methods to translate via the
    semantic route, i.e. using GermaNet.
    """

    def __init__(self):
        self._picto_db = PictoDB('static/data/metacom_to_germanet.db')

    def _find_complex_pictos(self, synset, sentence_state):
        """
        Adds all potential translation candidates consisting of complex pictographs (i.e. pictographs translating more
        than one word) to the SentenceState.
        """
        # search for synset as head synset
        db_entry_complex = self._picto_db.check_if_synset_in_complex(synset.id)

        for row in db_entry_complex:

            dependent_synsets = list(eval(row[1]))
            picto_path = row[2]
            bw_picto_path = self._picto_db.get_bw_picto(row[3])

            all_synsets = dependent_synsets + [synset.id]

            sentence_indices, penalties = self._find_consecutive_synsets(sentence_state, all_synsets)

            if not sentence_indices is None and not penalties is None:
                for i, p in zip(sentence_indices, penalties):
                    sentence_state.candidate_translations[i].add_candidate(picto_path, p, 'complex', False, bw_picto_path)

        return sentence_state

    def _find_consecutive_synsets(self, sentence_state, complex_synsets):
        """
        Checks whether all synsets of the complex picto can be found in the document such that the words with the
        respective synsets are consecutive of each other.
        """
        double_synsets = dict()
        all_word_synsets = [synset.id for word_synsets in sentence_state.word_synsets for synset in word_synsets.synsets]
        for s in complex_synsets:
            if all_word_synsets.count(s) > 1:
                double_synsets[s] = [sentence_index
                                     for sentence_index, word_synsets in enumerate(sentence_state.word_synsets)
                                     for synset in word_synsets.synsets if synset.id == s]

        matched_complex = []
        sentence_indices = []
        penalties = []

        for word_index, word_synsets in enumerate(sentence_state.word_synsets):
            for synset_index, candidate_synset in enumerate(word_synsets.synsets):
                if candidate_synset.id in matched_complex:
                    continue

                elif candidate_synset.id in complex_synsets:
                    matched_complex.append(candidate_synset.id)
                    sentence_indices.append(word_index)
                    penalties.append(word_synsets.penalties[synset_index])
                    break

        if set(matched_complex) == set(complex_synsets):
            if sorted(sentence_indices) == list(range(min(sentence_indices), max(sentence_indices) + 1)):
                return sentence_indices, penalties

            else:
                for i, s in enumerate(sentence_indices):
                    synset = matched_complex[i]
                    if synset in double_synsets:
                        other_sentence_indices = double_synsets[synset]
                        for o in other_sentence_indices:
                            sentence_indices[i] = o
                            if sorted(sentence_indices) == list(range(min(sentence_indices), max(sentence_indices) + 1)):
                                return sentence_indices, penalties
                return None, None
        else:
            return None, None

    def semantic_route(self, doc):
        """
        Takes a document analysed by spaCy and adds all possible translations on the semantic route (i.e. via semantic
        relations of GermaNet) to the SentenceStates.
        """
        for sentence_state in doc.sentence_states:

            for word_index, synset_collection in enumerate(sentence_state.word_synsets):

                if len(synset_collection.synsets) > 0:

                    # check if any of the synsets is in the Picto DB
                    for synset_index, synset in enumerate(synset_collection.synsets):

                        # check morphology to get female or plural picto if necessary
                        if sentence_state.sentence[word_index].has_morph():
                            morph_dict = sentence_state.sentence[word_index].morph.to_dict()

                            is_fem = False
                            is_plur = False

                            if 'Gender' in morph_dict.keys():
                                if morph_dict['Gender'] == 'Fem':
                                    is_fem = True

                            if 'Number' in morph_dict.keys():
                                if morph_dict['Number'] == 'Plur':
                                    is_plur = True

                            # simple pictos
                            found_picto, found_picto_bw = self._picto_db.check_if_simple_picto(synset.id, is_fem, is_plur)

                            if not found_picto is None:
                                sentence_state.candidate_translations[word_index].add_candidate(found_picto,
                                                                                                synset_collection.penalties[
                                                                                                    synset_index], 'simple',
                                                                                                synset_collection.antonym[
                                                                                                    synset_index],
                                                                                                found_picto_bw)

                        else:
                            # simple pictos
                            found_picto, found_picto_bw = self._picto_db.check_if_simple_picto(synset.id)

                            if not found_picto is None:
                                sentence_state.candidate_translations[word_index].add_candidate(found_picto,
                                                                                                synset_collection.penalties[
                                                                                                    synset_index],
                                                                                                'simple',
                                                                                                synset_collection.antonym[
                                                                                                    synset_index],
                                                                                                found_picto_bw)

                        # complex pictos
                        sentence_state = self._find_complex_pictos(synset, sentence_state)
        return doc
