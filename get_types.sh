# Get word and morpheme types from the CDS database 
sqlite3 -header -csv data/cds.sqlite3 "select distinct corpus, word, pos from words;" > data/words-types.csv
sqlite3 -header -csv data/cds.sqlite3 "select distinct corpus, morpheme, pos from morphemes;" > data/morphemes-types.csv
sqlite3 -header -csv data/cds.sqlite3 "select distinct corpus, morpheme, gloss from morphemes;" > data/morphemes-gloss-types.csv
sqlite3 -header -csv data/cds.sqlite3 "select distinct corpus, word, pos from ChintangWords;" > data/words-chintang-types.csv
sqlite3 -header -csv data/cds.sqlite3 "select distinct corpus, word, pos from RussianWords;" > data/words-russian-types.csv
sqlite3 -header -csv data/cds.sqlite3 "select distinct corpus, morpheme, gloss from ChintangMorphemes;" > data/morphemes-gloss-chintang-types.csv
