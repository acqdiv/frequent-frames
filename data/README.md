# Frequent frames data

## Overview

Data provided come from these sources:

* [1] Chintang (Stoll et al., Unpublished) 
* [2] Inuktitut (Allen, Unpublished) 
* [3] Japanese (Miyata, 2012)
* [4] Russian (Stoll & Meyer, Unpublished) 
* [5] Sesotho (Demuth, 2015)
* [6] Turkish (Küntay et al., Unpublished) 
* [7] Yucatec (Pfeiler, Unpublished)

Corpora [3, 5] are available through CHILDES, see: [http://childes.talkbank.org/](http://childes.talkbank.org/). A great tool for accessing CHILDES data is `childes-db` available here: [http://childes-db.stanford.edu/](http://childes-db.stanford.edu/).

Corpora [1, 2, 4, 6, 7] may not be reused or republished in any way without explicit written permission. Access to corpora [1, 2, 4, 6, 7] may be granted to researchers upon request to PI Sabine Stoll. The corpora are not made publicly available in their original form because they contain sensitive data from unpublished subcorpora. For more information see: [http://www.acqdiv.uzh.ch/en/resources.html](http://www.acqdiv.uzh.ch/en/resources.html).


## References

[1] Stoll, Sabine, Elena Lieven, Goma Banjade, Toya Nath Bhatta, Martin Gaenszle, Netra P. Paudyal, Manoj Rai, Novel Kishor Rai, Ichchha P. Rai, Taras Zakharko, Robert Schikowski & Balthasar Bickel. Unpublished. Audiovisual corpus on the acquisition of Chintang by six children.

[2] Allen, Shanley. Unpublished. Allen Inuktitut Child Language Corpus.

[3] Miyata, Susanne. 2012. Japanese CHILDES: The 2012 CHILDES manual for Japanese. http://www2.aasa.ac.jp/people/smiyata/CHILDESmanual/chapter01.html.

[4] Stoll, Sabine & Roland Meyer. Unpublished. Audio-visional longitudinal corpus on the acquisition of
Russian by 5 children.

[5] Demuth, Katherine. 2015. Demuth Sesotho Corpus. http://childes.talkbank.org/access/
Other/Sesotho/Demuth.html.

[6] Küntay, Aylin C., Dilara Koçbaş & Süleyman Sabri Taşçı. Unpublished. Koç University Longitudinal Language Development Database on language acquisition of 8 children from 8 to 36 months of age.

[7] Pfeiler, Barbara. Unpublished. Pfeiler Yucatec Child Language Corpus.


## Data preparation

Run `combine-data.sh` to concatenate the large CSV files into single files.

Run `load-db.sh` to load the CSV files into a sqlite database.
