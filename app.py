import os
import spacy
from flask import Flask, render_template, request, jsonify, g, url_for
from picto_translator.translator import Text2PictoTranslator
from picto_translator.picto_db import PictoDB
from picto_translator.germanet import GermaNet
from picto_translator.linguistic_analyser import LinguisticAnalyser
from sqlite3 import connect
from PIL import Image

germanet = GermaNet()
LinguisticAnalyser = LinguisticAnalyser()


app = Flask(__name__,static_folder='static')
translator = Text2PictoTranslator() # GermaNet and MetaComToGermaNet are loaded here
DATABASE = '/static/data/metacom_to_germanet.db'


@app.route('/version')
def version():
    return "Version 1.0.1, deployed on 2024-03-05"


def get_db():
    if 'db' not in g:
        g.db = connect(DATABASE,check_same_thread=False)
    return g.db

@app.teardown_request
def teardown_db(exception=None):
    picto_db = PictoDB(DATABASE)
    picto_db.close_conn()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get_pictos')
def get_pictos():
    table = request.args.get('table', 'simple_pictos')
    valid_tables = ['simple_pictos', 'complex_pictos', 'gendered_pictos', 'bw_colour_pictos', 'pictos', 'numbered_pictos']

    if table not in valid_tables:
        return jsonify({'error': 'Invalid table name'}), 400

    picto_db = PictoDB(DATABASE)
    conn = picto_db.get_conn()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    rows = cur.fetchall()
    return jsonify(rows)

def add_nichtkein(image_path):
    # Get the absolute path to the 'static' directory
    static_path = os.path.join(app.root_path, 'static')
    # add the redcross on top of the image
    image = Image.open(os.path.join(static_path, 'data', image_path))
    redcross = os.path.join(static_path, 'data', 'METACOM_Symbole/Symbole_PNG/PNG_ohne_Rahmen/Kleine_Worte/nichtkein.png')
    redcross = Image.open(redcross)
    image.paste(redcross, (0, 0), redcross)
    # Save the new image
    neg_path = image_path.replace('.png', '_negated.png')
    image.save(os.path.join(static_path, 'data', neg_path))
    
    return neg_path


@app.route('/translate', methods=['POST'])
def translate_text():
    data = request.json or request.form
    text = data['text']
    use_bw = data.get('use_bw', False)
    use_lemmas = data.get('use_lemmas', False)
    use_upper = data.get('use_upper', False)
    no_art = data.get('no_art', False)
    no_prep = data.get('no_prep', False)
    no_punct = data.get('no_punct', False)

    response_data = []

    for line in text.split('\n'):
        # Process each line
        translation, bw_translation, translated_words, further_translations = translator.translate(line)

        new_translated_words = []
        new_translations = []
        new_bw_translations = []
        new_further_translations = []

        for s, p_s, bw_p_s, f_s in zip(translated_words, translation, bw_translation, further_translations):
            sent = []
            t_sent = []
            bw_sent = []
            f_sent_filtered = []  # A new list to hold filtered alternatives

            for t, t_p_s, t_bw_p_s, t_f_s in zip(s, p_s, bw_p_s, f_s):
                # Determine if the token should be filtered
                if not any(should_filter(w, no_art, no_prep, no_punct) for w in t):
                    sent.append(t)
                    t_sent.append(t_p_s)
                    bw_sent.append(t_bw_p_s)

                    # Apply filter to each alternative in the alternatives list
                    filtered_alternatives = [alt for alt in t_f_s if not any(should_filter(w, no_art, no_prep, no_punct) for w in alt)]
                    f_sent_filtered.append(filtered_alternatives)

            new_translated_words.append(sent)
            new_translations.append(t_sent)
            new_bw_translations.append(bw_sent)
            new_further_translations.append(f_sent_filtered)

        # Use the filtered lists for further processing
        if use_bw:
            new_translations = new_bw_translations

        # Packaging the response
        negate_next_pictogram = False
        for sentence_translation, further_translations_list, translated_sentence in zip(new_translations, new_further_translations, new_translated_words):
            for i, (translation, other_translations, word) in enumerate(zip(sentence_translation, further_translations_list, translated_sentence)):
                
                image_path = translation.replace("\\", "/")if translation else None
                print (image_path)
                if tuple([str(w) for w in word]) == tuple(['#NEG#']) and 'nichtkein' in image_path:
                    negate_next_pictogram = True
                    neg_path = image_path
                    continue
                if negate_next_pictogram:
                    if translation:
                        neg_path = add_nichtkein(image_path)
                        # picto_url = url_for('static', filename=os.path.join('data', neg_path.replace("\\", "/")))
                        picto_url = 'static/data/' + neg_path.replace("\\", "/")
                        negate_next_pictogram = False

                    if isinstance(word, tuple):
                        word_text = [token.text for token in word if isinstance(token, spacy.tokens.token.Token)] 
                        word_text = ' '.join(word_text)
                    else:
                        word_text = word.text

                    doc = LinguisticAnalyser.analyse(word_text)[0]
                    token = next(iter(doc), None)

                    if token is not None:
                        synsets, penalties, is_antonym = germanet.get_synsets_and_penalties(token)
                        antonym_text = None
                        if any(is_antonym):
                            antonym_index = is_antonym.index(True)
                            antonym_synset = synsets[antonym_index]
                            antonym_lexunit = antonym_synset.lexunits[0]
                            antonym_text = antonym_lexunit.orthform
                            word_text = 'nicht ' + antonym_text
                        response_item = {
                            'text': word_text,
                            'src': picto_url,
                            
                        }
                        print (picto_url)
                        print (response_item)
                        response_data.append(response_item)
                        continue


                elif image_path:
                    # picto_url = url_for('static', filename=os.path.join('data', image_path.replace("\\", "/"))) 
                    picto_url = 'static/data/' + image_path.replace("\\", "/")

                else:
                    picto_url = None

                word_texts_serializable = [' '.join(w.text for w in word)] if not use_lemmas and not use_upper else [word[0].lemma_ if use_lemmas else ' '.join(w.text.upper() for w in word)]

                # alternatives = other_translations
                # alternatives_urls = [url_for('static', filename=os.path.join('data', alt_path.replace("\\", "/"))) for alt_path in other_translations] if picto_url else []
                alternatives_urls = ['static/data/' + alt_path.replace("\\", "/") for alt_path in other_translations] if picto_url else []
                response_item = {
                        'text': ' '.join(word_texts_serializable),
                    }
                
                if picto_url:
                    response_item['src'] = picto_url
                    if alternatives_urls:
                        response_item['alternatives'] = alternatives_urls
                else:
                    response_item['no_picto'] = True
                response_data.append(response_item)


        # Append a special marker for a line break                
        response_data.append({'line_break': True})

    return jsonify({'translations': response_data})


def should_filter(word, no_art, no_prep, no_punct):
    # Check if 'word' is a SpaCy Token and has the necessary properties
    if isinstance(word, spacy.tokens.Token):
        return ((no_art and word.tag_ == 'ART') or
                (no_prep and word.tag_ == 'APPR') or
                (no_punct and word.is_punct))
    # Return False as a default case if 'word' is not a Token (e.g., a string)
    return False

