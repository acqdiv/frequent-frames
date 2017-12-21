import pickle
from utils import *
import sys


def get_bigram_frames(u, position):
    """ Generate a diction of where key is a unigram and value is a list of unigrams that occur in its context

    :param u: list of lists of tuples, e.g. [[('w1', 'V'), ('w2', 'V')], [('w1', 'V'),...]]
    :return: bigrams_frames: dict where key is a unigram and value is a list of unigrams that occur in its context
    """
    # Test data and results
    # u = [[('w1', 'V'), ('w2', 'V')], [('w1', 'V'), ('w2', 'V')], [('w1', 'V'), ('w2', 'ADJ')], [('w3', 'ADV'), ('w4', 'N')]]
    # result1 = {('w1', 'V'):[('w2', 'V'),('w2', 'V'),('w2', 'ADJ')], ('w3', 'ADV'):[('w4', 'N')]}
    # position = False
    # result2 = {('w2', 'V'):[('w1', 'V'),('w1', 'V')],('w2', 'ADJ'):[('w1', 'V')],('w4', 'N'):[('w3', 'ADV')]}

    bigrams_frames = {}
    w1 = 0
    w2 = 1

    if not position:
        w1 = 1
        w2 = 0

    for i in u:
        # Create w1 frames, i.e. {(w1,l1):[(w2,l2),(w3,l1)...], {}:[], ...}
        if not i[w1] in bigrams_frames:
            bigrams_frames[i[w1]] = []
            bigrams_frames[i[w1]].append(i[w2])
        else:
            bigrams_frames[i[w1]].append(i[w2])

    # Test
    # print(bigrams_frames==result1)
    # print(bigrams_frames == result2)
    # print(bigrams_w2_frames==result2)

    return bigrams_frames


def process_dyads(morphemes, type):
    """ Process the parent-child dyads for bigrams probabilities. """
    # Choose a language:
    language = "Chintang"
    # language = "Russian"

    children = []
    if language=="Chintang":
        children = ['LDCh1', 'LDCh2', 'LDCh3', 'LDCh4']
    if language=="Russian":
        children = ['Child1', 'Child2', 'Child3', 'Child4']

    for child in children:
        print("Processing:", child)
        u = None

        if morphemes:
            u = get_columns_as_tuples('select utterance_id_fk, morpheme, gloss from ChintangMorphemes where child = "' + child + '"')

        else: # words
            if language=="Chintang":
                u = get_columns_as_tuples('select utterance_id_fk, word, pos from ChintangWords where child = "'+child+'"')
            if language=="Russian":
                u = get_columns_as_tuples('select utterance_id_fk, word, pos from RussianWords where child = "'+child+'"')
                
        u = get_utterances(u) # wonky: this call to utils populates utils global vars
        u = cut(u, 2) # clean the utterance and cut any that are length < N

        # Get lists of ngrams
        u = get_list_of_ngrams(u, 2)

        # Create bigram frames: {(w1,l1):[(w2,l1),(...)],...]
        bigrams_w1_frames = get_bigram_frames(u, position=True)
        bigrams_w2_frames = get_bigram_frames(u, position=False)

        # Containers to fill and pickle to disk.
        bigrams_w1_pr = {}
        bigrams_w2_pr = {}

        # For w1 in bigrams
        for k, v in bigrams_w1_frames.items():
            precision = get_accuracy(v)
            # recall = get_completeness(v, labels)
            recall = get_recall(v)
            bigrams_w1_pr[k] = (precision, recall)
        with open(child+'_'+type+'_w1.pickle', 'wb') as handle:
            pickle.dump(bigrams_w1_pr, handle)

        # For w2 in bigrams
        for k, v in bigrams_w2_frames.items():
            precision = get_accuracy(v)
            # recall = get_completeness(v, labels)
            recall = get_recall(v)
            bigrams_w2_pr[k] = (precision, recall)
        with open(child+'_'+type+'_w2.pickle', 'wb') as handle:
            pickle.dump(bigrams_w2_pr, handle)


def process_corpora(morphemes, type):
    """ Process the corpora for bigram frequencies """
    corpora = []
    if morphemes:
        corpora = ['Chintang', 'Inuktitut', 'Japanese_MiiPro', 'Sesotho', 'Turkish', 'Yucatec']
    else:
        corpora = ['Chintang', 'Inuktitut', 'Japanese_MiiPro', 'Russian', 'Sesotho', 'Turkish', 'Yucatec']

    for corpus in corpora:
        print("Processing:", corpus)
        u = None
        if morphemes:
            u = get_columns_as_tuples(
                'select utterance_id_fk, morpheme, gloss from morphemes where corpus = "' + corpus +'"')
        else: # words
            u = get_columns_as_tuples('select utterance_id_fk, word, pos from words where corpus = "' + corpus +'"')

        u = get_utterances(u) # wonky: this call to utils populates utils global vars
        u = cut(u, 2) # clean the utterance and cut any that are length < N

        # Get lists of ngrams
        u = get_list_of_ngrams(u, 2)

        # Create bigram frames: {(w1,l1):[(w2,l1),(...)],...]
        bigrams_w1_frames = get_bigram_frames(u, position=True)
        bigrams_w2_frames = get_bigram_frames(u, position=False)

        # Containers to fill and pickle to disk.
        bigrams_w1_pr = {}
        bigrams_w2_pr = {}

        # For w1 in bigrams
        for k, v in bigrams_w1_frames.items():
            precision = get_accuracy(v)
            # recall = get_completeness(v, labels)
            recall = get_recall(v)
            bigrams_w1_pr[k] = (precision, recall)

        with open(corpus+'_'+type+'_w1.pickle', 'wb') as handle:
            pickle.dump(bigrams_w1_pr, handle)

        # For w2 in bigrams
        for k, v in bigrams_w2_frames.items():
            precision = get_accuracy(v)
            # recall = get_completeness(v, labels)
            recall = get_recall(v)
            bigrams_w2_pr[k] = (precision, recall)
        with open(corpus+'_'+type+'_w2.pickle', 'wb') as handle:
            pickle.dump(bigrams_w2_pr, handle)


def main():
    setup()
    morphemes = 1
    type = None
    if morphemes == 0:
        type = "words"
    else:
        type = "morphemes-gloss" # to distinguish between (morpheme,pos) vs (morpheme,gloss) analyses

    # Process dyads or corpora
    process_dyads(morphemes, type)
    # process_corpora(morphemes, type)


if __name__ == '__main__':
    import time
    start_time = time.time()
    main()
    print("--- %s seconds ---" % (time.time() - start_time))
