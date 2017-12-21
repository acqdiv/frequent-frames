""" Performs data manipulation and number crunching for frequent frames analysis. """

import random
import pickle
import logging
import operator
# import json
from utils import *

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(filemode='w')
logger = logging.getLogger(__name__)
handler = logging.FileHandler('errors.log')
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_category_proportions(frequent_frames):
    """ Get the category proportions. """
    for k, v in frequent_frames.items():
        labels = []
        for t in v:
            labels.append(t[1])
        counts = Counter(labels)
        for k, v in counts.items():
            print(k, str(v/len(labels)*100))
        print()


def get_frame_based_categories(frames, n=45, drop_none=True):
    """ Takes trigram frames as input and returns frame-based categories of length n.

    :param frames: list of lists of trigram tuples, e.g. [[('hap', 'V', 'NA'), ('i', 'sfx', '1/2PL.S/P'), (...)], [...]]
    :param n: int (number of frequent frames to keep
    :param drop_none: whether or not to drop frames that contain "???" in the middle
    :return: dict: key of tuples A__B in frame, value is list of tuples of the target forms
    """
    all_frames = {}
    for t in frames:

        left = t[0]
        center = t[1]
        right = t[2]

        if drop_none:
            if center[1] is None or center[1] == "???":
                print(t)
                sys.exit("Encountered None or ??? in the input!")

            # Get only the frames with nouns and verbs as the category
            # if not center[1] == "N" and not center[1] == "V":
            #    continue

        if not (left, right) in all_frames:
            all_frames[(left, right)] = []
            all_frames[(left, right)].append(center)
        else:
            all_frames[(left, right)].append(center)


    #frequent_frames = {}
    #for frame in sorted(all_frames, key=lambda k: len(all_frames[k]), reverse=True)[:n]:
    #    frequent_frames[frame] = all_frames[frame]
    #print(frequent_frames)
    #return frequent_frames

    return all_frames


def pprint(frequent_frames, counts=True):
    """
    Pretty print frequent frame data:

    mo_didi:
        na: gm

    bago_lo:
        thuli: n
        them: pro

    :return:
    """
    if counts:
        for k, v in frequent_frames.items():
            print(k[0][0]+"_"+k[1][0]+": "+str(len(v)))
            sorted(v)
            targets = Counter(v)
            for t, n in targets.items():
                print("\t"+t[0]+": "+t[1]+" ("+str(n)+")")
            print()
    else:
        for k, v in frequent_frames.items():
            print(k[0][0]+"_"+k[1][0]+":")
            # TODO: sensible sort
            sorted(v)
            for t in v:
                print("\t"+t[0]+": "+t[1])
            print()


def get_frames(u):
    """ Create frame input format. """
    results = []
    # call frames n return lists
    # [('al', 'V'), ('alınca', 'V'), ('bağrıyoruz', 'V')]

    results = []
    for t in u:
        words = t[0]
        labels = t[1]
        pairs = []
        for a, b in zip(words, labels):
            pairs.append((a,b))
        results.append(pairs)
    return results


def get_target_label_tokens(targets):
    """ Get the target label tokens. """
    target_labels = [x[1] for x in targets]
    counts = get_types(target_labels)
    return counts


def get_target_label_types(targets):
    """ Get the target label types. """
    target_types = set(targets)
    target_labels = [x[1] for x in target_types]
    counts = get_types(target_labels)
    return counts


def get_modal_category(cat_tokens):
    """ Get the modal category. """
    sorted_d = sorted(cat_tokens.items(), key=operator.itemgetter(1))
    sorted_d.reverse()
    return sorted_d[0][0]


def get_pos_gloss_pos(u):
    """ Take (morpheme, pos, gloss) and return pos gloss pos. """
    results = []
    for t in u:
        left = t[0]
        center = t[1]
        right = t[2]
        l = (left[0], left[2])
        m = (center[0], center[1])
        r = (right[0], right[2])
        result = [l,m,r]
        results.append(result)
    return results


def trigram_analysis(corpus, u, f1 ,f2, morphemes, gloss, justgloss):
    """ Analysis of frequent frames. """
    bigrams_w1_pr = pickle.load(f1)
    bigrams_w2_pr = pickle.load(f2)

    u = cut(u, 3) # excepts [[(w1,l1),(w2,l2)], []...]
    u = get_list_of_ngrams(u, 3)

    if gloss and not justgloss:
        u = get_pos_gloss_pos(u)

    u = clean(u, gloss, justgloss)
    frames = None
    frames = get_frame_based_categories(u, -1, drop_none=True)  # -1 is all of the frames
    """
    if gloss:
        if justgloss:
            frames = get_frame_based_categories(u, -1, drop_none=True)  # -1 is all of the frames
        else:
            frames = get_frame_based_categories_robert(u, -1, drop_none=True)  # -1 is all of the frames
    else:
        frames = get_frame_based_categories(u, -1, drop_none=True) # -1 is all of the frames
    """

    # Prune out the single item frames
    frequent_frames = {}
    for k, v in frames.items():
        if len(v) >= 2:
            frequent_frames[k] = v
        else:
            logger.info("Frequent frame length 1:") # {}".format(k, v)) # TODO: add corpus when in loop; get utterance counts

    # Loop to get precision and recall figures
    result = []
    for k, v in frequent_frames.items():
        wl = to_json(v)
        cat_types = dict(get_target_label_types(v))
        cat_tokens = dict(get_target_label_tokens(v))
        modal = get_modal_category(cat_tokens) # get the majority category
        precision = get_accuracy(v)
        recall = get_recall(v)

        # Get frame's wing elements
        frame_forms = str(k[0][0])+"_"+str(k[1][0])
        frame_pos = str(k[0][1])+"_"+str(k[1][1])

        # Get precison and recall of bigram analysis of w1 and w2
        w1_pr = bigrams_w1_pr[k[0]]
        w2_pr = bigrams_w2_pr[k[1]]
        # print(corpus, k, v, precision, recall)

        # header just for trigrams:
        # result = [corpus, str(precision), str(recall), str(len(v))]

        result = [corpus, str(precision), str(recall), str(len(v)), str(w1_pr[0]), str(w1_pr[1]), str(w2_pr[0]),
                  str(w2_pr[1]), str(k), str(frame_forms), str(frame_pos), modal, str(cat_types), str(cat_tokens), str(wl)]  # , str(v)]
        print("\t".join(result))


def main(morphemes, gloss, justgloss):
    """ Performs data manipulation and number crunching for frequent frames analysis. """
    setup()

    # Set analysis
    morphemes = morphemes
    gloss = gloss
    justgloss = justgloss

    # type = "gloss" # comment out if morphemes = 0

    corpora = []
    if morphemes:
        corpora = ['Chintang', 'Inuktitut', 'Japanese_MiiPro', 'Sesotho', 'Turkish', 'Yucatec']
    else:
        corpora = ['Chintang', 'Inuktitut', 'Japanese_MiiPro', 'Russian', 'Sesotho', 'Turkish', 'Yucatec']

    for corpus in corpora:
        u = None
        f1 = None
        f2 = None

        # Load pickled bigrams analyses
        if morphemes:
            if gloss:
                # morpheme-gloss
                if justgloss:
                    # if just morpheme and gloss
                    u = get_columns_as_tuples(
                        'select utterance_id_fk, morpheme, gloss from morphemes where corpus = "' + corpus + '"')
                    u = get_utterances(u)
                    f1 = open("bigrams/" + corpus + '_morphemes-gloss_w1.pickle', 'rb')
                    f2 = open("bigrams/" + corpus + '_morphemes-gloss_w2.pickle', 'rb')
                # morpheme-gloss-pos-gloss
                else:
                    u = get_columns_as_tuples(
                        'select utterance_id_fk, morpheme, pos, gloss from morphemes where corpus = "' + corpus + '"') # LIMIT 100
                    u = get_utterances_robert(u)
                    f1 = open("bigrams/"+corpus+'_morphemes-gloss_w1.pickle', 'rb')
                    f2 = open("bigrams/"+corpus+'_morphemes-gloss_w2.pickle', 'rb')
            # morpheme-pos
            else:
                u = get_columns_as_tuples(
                    'select utterance_id_fk, morpheme, pos from morphemes where corpus = "' + corpus + '"')
                u = get_utterances(u)
                f1 = open("bigrams/" + corpus + '_morphemes_w1.pickle', 'rb')
                f2 = open("bigrams/" + corpus + '_morphemes_w2.pickle', 'rb')
        # word-pos
        else:
            u = get_columns_as_tuples(
                'select utterance_id_fk, word, pos from words where corpus = "' + corpus + '"')  # words and pos
            u = get_utterances(u)
            f1 = open("bigrams/"+corpus+'_words_w1.pickle', 'rb')
            f2 = open("bigrams/"+corpus+'_words_w2.pickle', 'rb')


        trigram_analysis(corpus, u, f1, f2, morphemes, gloss, justgloss)

        f1.close()
        f2.close()


if __name__ == '__main__':
    import time
    start_time = time.time()

    header = ["Corpus", "Precision", "TotalRecall", "NumberFrames", "W1_Precision", "W1_Recall", "W2_Precision",
              "W2_Recall", "Frame", "FrameWords", "FramePOS", "ModalCategory", "TargetTypes", "TargetTokens", "Targets"]  # , "Categories"]
    print("\t".join(header))
    morphemes = 0 # words, 1 for morphemes
    gloss = 0 # pos, 1 for gloss
    justgloss = 0
    main(morphemes, gloss, justgloss)

    print("--- %s seconds ---" % (time.time() - start_time))
