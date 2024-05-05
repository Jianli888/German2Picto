# Contributors
Here we acknowledge the contributions of those who have played a significant role in the development and maintenance of this project.

- **Helen Schaller**
  - GitHub: [Helen Schaller]( 
  - Contributions: text-to-pictogram translator, database design, ...
  
- **Jian Li**
  - GitHub: [Jian Li](https://github.com/Jianli888)
  - Contributions: Front-end development, back-end development, webapp development.


Files and their function:

Webapp_German2Picto                 # contains code for text-to-pictogram translator with code for web application
├── picto_translator                # contains code for text-to-pictogram translator (without code for interface)
│   ├── __init__.py                 # initialise as package
│   ├── containers.py               # classes storing information during translation process
│   ├── direct_route.py             # code for translating along direct route, i.e. using look-up dictionary
│   ├── germanet.py                 # code for loading, storing and searching GermaNet
│   ├── linguistic_analyser.py      # code for loading, storing and using spaCy model for shallow linguistic analysis
│   ├── optimal_path_searcher.py    # code for finding the pictogram translation with the lowest cost
│   ├── picto_db.py                 # code for connecting to and searching the pictogram-synset database
│   ├── semantic_route.py           # code for translating along semantic route, i.e. using GermaNet
│   ├── sentence_state_creator.py   # code that adds some of the containers to the analysed input sentences
│   └── translator.py               # high-level class wrapping up process of text-to-pictogram translation
├── static 
│   ├── data                        # data needed for text-to-pictogram translation
│   │   ├── GN_V160                 # contains GermaNet data !!!You will need to obtain license first.
│   │   │   └── ...
│   │   ├── METACOM_Symbole         # contains METACOM pictograms !!!You will need to obtain license first.
│   │   │   └── ...
│   │   ├── dictionary.csv          # look-up dictionary with direct links between tokens/lemmas and pictograms
│   │   └── metacom_to_germanet.db  # database with pictogram-synset links
│   ├── favcon.ico
│   ├── text2picto.css
│   ├── text2picto.js
│   ├── German2Picto.png 
├── templates
│   ├── index.html
├── app.py                          # code for web application
└── requirements.txt                # dependencies


Platform on which the program is executable:
operating system: Windows 10 Home, OS build 19044.1645
programming environment: Python 3.9.18
dependencies: cf. requirements.txt

Usage:
1. Navigate to the main folder of the project: cd .\webapp_German2Picto\
2. Install the requirements: python -m pip install -r requirements.txt
3. To run the webapp, run: flask run
