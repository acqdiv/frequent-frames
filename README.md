# Frequent frames analysis pipeline

## Details

For more information about the ACQDIV project, see: [http://www.acqdiv.uzh.ch/](http://www.acqdiv.uzh.ch/). The research leading to these results has received funding from the European Union’s Seventh Framework Programme (FP7/2007-2013) under grant agreement no 615988 (PI Sabine Stoll).

## Pipeline

1. Generate the bigrams 

Run the script: `bigrams.py` to generate the bigram frequencies. Note this make take a long time.


2. Generate the trigram counts for each analysis

For words, morphemes, dyads, etc. This generates counts for the frequency calculation of the frames and for operationalization.

Call: `python3 utils.py`

Make sure to set the words or morphemes in the script!


3. For global recall (DB) get the word types:

Call: `sh get_types.sh`


4. Run the frames processing and PR analysis 

This step requires that the bigrams are calculated and pickled first. Then run the frames analysis with `frames.py`. The script outputs a TSV file to load into R.

Make sure to set words or morphemes (pos or glosses) in the script!


5. Statistical analysis with R scripts

The `frames-functions.R` file contains various functions for processing and plotting the frequent frames analyses. The words, morphemes and dyads analyses are in `words.R`, `morpheme-gloss-pos.R` and `dyads.R`.


