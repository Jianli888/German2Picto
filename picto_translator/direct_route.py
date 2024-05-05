#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import re

from .containers import MultiWord


class DirectRoute:
    """
    Class that translates along the direct route, i.e. using a lookup dictionary and morphological information, to
    translate to pictographs
    """

    def __init__(self):
        self.lookup_dict = pd.read_csv('static/data/dictionary.csv')
        self.multiword_tokens, self.multiword_tokens_bw = self._collect_multiwords('token')
        self.multiword_lemmas, self.multiword_lemmas_bw = self._collect_multiwords('lemma')

    def _collect_multiwords(self, column):
        """"
        Returns all lookup dictionary entries consisting of more than one token / lemma in a dict having as the key the
        multi-word expression (tokens in tuple) and as the value a MultiWord object. Options for column are ['token', 'lemma'].
        The dict is sorted by the number of tokens in the multi-word expressions (from large to small).
        """
        multiword_tokens = dict()
        multiword_tokens_bw = dict()
        multiword_row_indices = []

        for row_index, row in enumerate(self.lookup_dict.iterrows()):
            if pd.isna(row[1][column]) is False:
                # if bw is True:
                #     if pd.isna(row[1]['picto_bw']) is True:
                #         continue
                split_token = row[1][column].split(' ')
                split_token = tuple([token.lower() for token in split_token])
                if len(split_token) > 1:
                    multiword_row_indices.append(row_index)
                    multiword_token = MultiWord(split_token, row[1]['picto'], row[1]['tag'], row[1]['morph'])
                    multiword_tokens[split_token] = multiword_token
                    if pd.isna(row[1]['picto_bw']) is False:
                        multiword_token_bw = MultiWord(split_token, row[1]['picto_bw'], row[1]['tag'], row[1]['morph'])
                        multiword_tokens_bw[split_token] = multiword_token_bw

        self.lookup_dict.drop(multiword_row_indices, inplace=True)
        self.lookup_dict.reset_index(drop=True, inplace=True)

        # sort by length of multiword
        sorted_multiword_tokens = dict()
        for k in sorted(multiword_tokens, key=len, reverse=True):
            sorted_multiword_tokens[k] = multiword_tokens[k]

        sorted_multiword_tokens_bw = dict()
        for k in sorted(multiword_tokens_bw, key=len, reverse=True):
            sorted_multiword_tokens_bw[k] = multiword_tokens_bw[k]

        return sorted_multiword_tokens, sorted_multiword_tokens_bw

    def _multiword_searcher(self, sentence_state, word_type):
        """
        Adds candidate translations for multi-word expressions (i.e. pictograms that translate more than one word) to
        the SentenceState. Options for word_type are ['token', 'lemma'].
        """
        if word_type == 'token':
            sentence_list = [word.lower_ for word in sentence_state.sentence]
            multiword_dict = self.multiword_tokens
            multiword_dict_bw = self.multiword_tokens_bw

        else:
            sentence_list = [word.lemma_.lower() for word in sentence_state.sentence]
            multiword_dict = self.multiword_lemmas
            multiword_dict_bw = self.multiword_lemmas_bw

        for multiword_str in multiword_dict.keys():
            # check if sentence has all of multi-word token or lemma
            if all(word in sentence_list for word in multiword_str):
                corresponds = self._check_multiword_grammatical_correspondence(sentence_state.sentence,
                                                                               multiword_dict[multiword_str], word_type)
                if corresponds is False:
                    continue

                else:
                    multiword = multiword_dict[multiword_str]
                    if multiword.multiword in multiword_dict_bw.keys():
                        bw_picto = multiword_dict_bw[multiword_str].picto_path
                    else:
                        bw_picto = None


                    # check if words are next to each other
                    for index, sentence_word in enumerate(sentence_list):
                        if sentence_word == multiword.multiword[0]:
                            if sentence_list[index:index + len(multiword.multiword)] == list(multiword.multiword):
                                for word in multiword.multiword:
                                    sentence_state.candidate_translations[sentence_list.index(word)].add_candidate(
                                        multiword.picto_path, -8, 'complex', False, bw_picto)

        return sentence_state

    def _check_multiword_grammatical_correspondence(self, sentence_list, multiword, word_type):
        """
        Returns True if all feature values and the POS-tag specified in the dataframe entry correspond with the
        multi-words' morphological analysis. Options for word_type are ['token', 'lemma'].
        """
        for word in sentence_list:
            if word_type == 'lemma':
                check = word.lemma_.lower()
            else:
                check = word.lower_
            if check in multiword.multiword:
                multiword_word_index = multiword.multiword.index(check)
                corresponds = self._check_grammatical_correspondence(word, multiword.tags[multiword_word_index],
                                                                     multiword.morph[multiword_word_index])
                if corresponds is False:
                    return False
        return True

    @staticmethod
    def _check_morph(token_morph, df_morph):
        """
        Returns True if all feature values specified in dataframe entry correspond with the token's morphological
        analysis
        """
        if not type(df_morph) is dict:
            df_morph = eval(df_morph)  # interpret str as dict

        token_morph = token_morph.to_dict()

        # If we get through the for loop, then all features specified in dataframe correspond with the features of the
        # input token.
        for feature in df_morph:
            try:
                df_value = df_morph[feature]
                token_value = token_morph[feature]
                if df_value == token_value:
                    continue
                else:
                    return False
            except KeyError:
                return False
        return True

    @staticmethod
    def _check_tags(token_tag, df_tag):
        """
        Returns True if the token tag specified in the dataframe entry corresponds with the token's tag
        """
        if '{' in df_tag:
            df_tag = eval(df_tag)
        if isinstance(df_tag, str):
            if token_tag == df_tag:
                return True
        elif isinstance(df_tag, set):
            if token_tag in df_tag:
                return True
        else:
            return False

    def _check_grammatical_correspondence(self, word, tag_entry, morph_entry):
        """
        Returns True if all feature values and the POS-tag specified in the dataframe entry correspond with the token's
        morphological analysis
        """
        # string -> multi-word
        if type(tag_entry) is str:
            tag_corresponds = self._check_tags(word.tag_, tag_entry)
        # pandas cell -> single-word
        elif pd.isna(tag_entry) is False:
            tag_corresponds = self._check_tags(word.tag_, tag_entry)
        # None or empty pandas cell
        else:
            tag_corresponds = True

        # dict -> multiword
        if type(morph_entry) is dict and len(word.morph.to_dict()) != 0:
            morph_corresponds = self._check_morph(word.morph, morph_entry)
        # pandas cell -> single-word
        elif pd.isna(morph_entry) is False and len(word.morph.to_dict()) != 0:
            morph_corresponds = self._check_morph(word.morph, morph_entry)
        # None or empty pandas cell
        else:
            morph_corresponds = True

        if morph_corresponds is True and tag_corresponds is True:
            return True
        else:
            return False

    def _singleword_searcher(self, sentence_state, word_type):
        """
        Adds WordTranslationCandidates of matched single-word tokens or lemmas.
        """
        if word_type == 'token':
            for word_index, word in enumerate(sentence_state.sentence):
                for entry in self.lookup_dict[self.lookup_dict['token'] == word.lower_].iterrows():
                    corresponds = self._check_grammatical_correspondence(word, entry[1]['tag'], entry[1]['morph'])
                    if corresponds is True:
                        if pd.isna(entry[1]['picto_bw']):
                            sentence_state.candidate_translations[word_index].add_candidate(entry[1]['picto'], -8,
                                                                                            'simple', False, None)
                        else:
                            sentence_state.candidate_translations[word_index].add_candidate(
                                entry[1]['picto'], -8, 'simple', False, entry[1]['picto_bw'])

        elif word_type == 'lemma':
            for word_index, word in enumerate(sentence_state.sentence):

                # check if is time
                if re.match('\d\d:\d\d', word.text):
                    if word.text[0] == '0':
                        word.text = word.text[1:]
                        word.lemma_ = word.lemma_[1:]

                for entry in self.lookup_dict[self.lookup_dict['lemma'] == word.lemma_.lower()].iterrows():
                    corresponds = self._check_grammatical_correspondence(word, entry[1]['tag'], entry[1]['morph'])
                    if corresponds is True:
                        if pd.isna(entry[1]['picto_bw']):
                            sentence_state.candidate_translations[word_index].add_candidate(entry[1]['picto'], -8,
                                                                                            'simple', False, None)
                        else:
                            sentence_state.candidate_translations[word_index].add_candidate(
                                entry[1]['picto'], -8, 'simple', False, entry[1]['picto_bw'])

        return sentence_state

    def _check_words(self, sentence_state, word_type):
        """
        Adds candidate translations for multi-word expressions (i.e. pictograms that translate more than one word) and
        single-word expressions to the SentenceState. Options for word_type are ['token', 'lemma'].
        """
        word_types = ['token', 'lemma']
        if word_type not in word_types:
            raise ValueError('Invalid word type. Expected one of: %s' % word_types)

        # search multi-word expressions
        sentence_state = self._multiword_searcher(sentence_state, word_type)

        # search all words that are not part of multi-word expressions
        sentence_state = self._singleword_searcher(sentence_state, word_type)
        return sentence_state

    def direct_route(self, doc):
        """
        Takes a document analysed by spaCy and adds all possible translations on the direct route (i.e. via lookup
        dictionary) to the SentenceStates. Analysis in the direct route happens with all lower-cased tokens / lemmas.
        """
        for i in range(len(doc.sentence_states)):
            # get translation candidates
            doc.sentence_states[i] = self._check_words(doc.sentence_states[i], 'token')
            doc.sentence_states[i] = self._check_words(doc.sentence_states[i], 'lemma')

        return doc

