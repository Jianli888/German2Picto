#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from .containers import Document
from .direct_route import DirectRoute
from .linguistic_analyser import LinguisticAnalyser
from .optimal_path_searcher import OptimalPathSearcher
from .semantic_route import SemanticRoute
from .sentence_state_creator import SentenceStateCreator


class Text2PictoTranslator:
    """
    Wraps up the whole Text2Picto translation process including shallow linguistic analysis, direct route, semantic
    route and optimal path search.
    """

    def __init__(self):
        self._linguistic_analyser = LinguisticAnalyser()
        self._sentence_state_creator = SentenceStateCreator()
        self._direct_path = DirectRoute()
        self._semantic_path = SemanticRoute()
        self._optimal_path_searcher = OptimalPathSearcher()

    def translate(self, text, use_bw=False, hide_text=False, hide_inflection=False, capital_letter=False,hide_articles=False, hide_prepositions=False, hide_punctuations=False):
        """
        Takes any input text to be translated and returns a pictogram translation (list of sentence translations, these
        are lists of pictogram names).
        """
        doc = Document(text)
        doc.analysed_doc, doc.sentence_list = self._linguistic_analyser.analyse(doc.string)
        self._sentence_state_creator.create_sentence_states(doc)
        doc = self._direct_path.direct_route(doc)
        doc = self._semantic_path.semantic_route(doc)
        translation, bw_translation, translated_words, further_translations = self._optimal_path_searcher.find_best_path(doc)
        return translation, bw_translation, translated_words, further_translations  
      




