#!/bin/bash
sqlite3 cds.sqlite3 << EOF
.mode csv
.import words.csv words
.import morphemes.csv morphemes
.import RussianWords.csv RussianWords
.import ChintangWords.csv ChintangWords
.import ChintangMorphemes.csv ChintangMorphemes
UPDATE words SET pos=NULL WHERE pos='';
UPDATE words SET word=NULL WHERE word='';
UPDATE morphemes SET morpheme=NULL WHERE morpheme='';
UPDATE morphemes SET pos=NULL WHERE pos='';
UPDATE morphemes SET gloss=NULL WHERE gloss='';
UPDATE RussianWords SET word=NULL WHERE word='';
UPDATE ChintangWords SET word=NULL WHERE word='';
UPDATE ChintangWords SET pos=NULL WHERE pos='';
UPDATE ChintangMorphemes SET pos=NULL WHERE pos='';
UPDATE ChintangMorphemes SET morpheme=NULL WHERE morpheme='';
UPDATE ChintangMorphemes SET gloss=NULL WHERE gloss='';
EOF