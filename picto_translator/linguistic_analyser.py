#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import spacy



class LinguisticAnalyser:
    """
    Class that stores spaCy model for shallow linguistic analysis
    """

    def __init__(self):
        self._nlp = spacy.load("de_core_news_lg")


    def analyse(self, string):
        """
        Returns spaCy Doc object of input string.
        """
        analysed_doc = self._nlp(string)
        return analysed_doc, [sentence for sentence in analysed_doc.sents]
    


# test lemmatization. 
    
# nlp = spacy.load("de_core_news_lg")
# doc = nlp("Ich habe Wasser. Er hat Wasser.")
# doc = nlp("Ich fange jetzt an. Er fängt jetzt an.")
# for token in doc:
#     print(token.text, token.lemma_)




