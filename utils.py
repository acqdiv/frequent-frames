import sys
import sqlite3
import json
from itertools import combinations
from collections import Counter
from collections import OrderedDict

# Globals
conn = None
words_labels = [] # all word label tuples (tokens)
words = [] # all word tokens
labels = [] # all label tokens
word_types = {} # all word types
label_types = {} # all label types


def setup():
    """ Setup globals and db connection. Globals populated by call to get_utterances()"""
    global conn, words, labels, words_labels
    conn = sqlite3.connect('data/cds.sqlite3')


def get_utterances_robert(u):
    """ Process fetch_all() output into a list of lists, where each list contains elements of a single utterance.
        Additionally create global Counters for word types and token counts and label types and label token counts.

    :param u: list of tuples, e.g. [(1, 'hi', V), (1, 'there', N), (2, 'high', N),...]
    :return results list of lists, e.g. [[('hi', V), ('there', N)], [('high', N),...]]

    """
    results = []
    utterance = []
    prev = u[0][0] # set utterance the index

    word_target = 1
    word_label = 2 # 2 is POS; 3 is GLOSS
    word_gloss = 3

    for t in u:
        words_labels.append((t[word_target], t[word_label], t[word_gloss]))
        words.append(t[word_target])
        labels.append(t[word_label])

        if t[0] == prev:
            # Concatenate words and their pos over multiple rows
            utterance.append((t[word_target], t[word_label], t[word_gloss]))
        else:
            results.append(utterance)
            utterance = [(t[word_target], t[word_label], t[word_gloss])]
            prev = t[0]

    # Get the global types Counter
    global word_types
    word_types = get_types(words)

    global label_types
    label_types = get_types(labels)
    results.append(utterance)
    return results


def get_utterances(u):
    """ Process fetch_all() output into a list of lists, where each list contains elements of a single utterance.
        Additionally create global Counters for word types and token counts and label types and label token counts.

    :param u: list of tuples, e.g. [(1, 'hi', V), (1, 'there', N), (2, 'high', N),...]
    :return results list of lists, e.g. [[('hi', V), ('there', N)], [('high', N),...]]

    """
    results = []
    utterance = []
    prev = u[0][0] # set utterance the index

    word_target = 1
    word_label = 2 # 2 is POS; 3 is GLOSS TODO FIX THIS FOR ROB'S ANALYSIS

    for t in u:
        words_labels.append((t[word_target], t[word_label]))
        words.append(t[word_target])
        labels.append(t[word_label])

        if t[0] == prev:
            # concatenate words and their pos over multiple rows
            utterance.append((t[word_target], t[word_label]))
        else:
            results.append(utterance)
            utterance = [(t[word_target], t[word_label])]
            prev = t[0]

    # Get the global types Counter
    global word_types
    #print("words:", words)
    #print("labels:", labels)
    word_types = get_types(words)
    #print(word_types)

    global label_types
    #print("lt:", label_types)
    #print("labels:", labels)
    label_types = get_types(labels)
    # print("lt:", label_types)
    results.append(utterance)

    return results


def to_json(list_of_tuples):
    """ Takes a list of (form, label) tuples and returns a json an object.

    :param list_of_tuples: [(word,pos), (word,pos)...]
    :return: json str: [{"form":"word", "label":"pos"}, {}...]
    """
    results = []
    for i, j in list_of_tuples:
        d = OrderedDict()
        d["form"] = i
        d["label"] = j
        # d = {"form": i, "label": j}
        results.append(d)
    return json.dumps(results)


def get_ngrams(input_list, n):
    """
    # [('al', 'V'), ('alınca', 'V'), ('bağrıyoruz', 'V')]
    """
    return zip(*[input_list[i:] for i in range(n)])


def get_ngrams_from_list(words, n):
    """
    :param words: a list of words, e.g. ['a', 'b', 'c', 'd']
    :return: list of tuples of ngrams where length == n, e.g. [('a', 'b', 'c'), ('b', 'c', 'd'), ...]
    """
    return list(zip(*[words[i:] for i in range(n)]))


def get_list_of_ngrams(list_of_lists, n):
    """ Transforms a list of lists, where each list is a set of tuples that represent a single utterance, into a list
        of lists og ngram tuples, where n is the length of the ngram.

    :param list_of_lists
    :param n
    :return list of lists of tuples of length n
    """
    result = []
    for i in list_of_lists:
        for j in get_ngrams(i, n):
            result.append(list(j))
    return result


def get_accuracy(targets, tokens=True, pprint=False):
    """ Mintz 2003: accuracy = hits / hits + false alarms == precision

    :return: precision value (float)
    """
    #if not tokens: # then types
    #   labels = set(labels)

    # Tests
    # labels = [('w1', 'l1')] # return 1.0
    # labels = [('w1', 'l1'), ('w2', 'l2'), ('w2', 'l1')] # return .33
    # labels = [('w1', 'l1'), ('w1', 'l1')] # return 1.0

    # In this case there is only one combination, e.g. (w1,l1):[w2,l2], so return accuracy of 1
    if len(targets) == 1:
        return 1.0

    # Check the pairwise tuples and collect points
    pairs = combinations(targets, 2)

    hits = 0
    false_alarms = 0

    for t in pairs:
        if t[0][1] == t[1][1]:
            hits += 1
        else:
            false_alarms += 1

    # We should never get this case
    # In this case there is no hit or no false alarm, e.g. (w1,l1),(w2,l2), so return accuracy of 0
    # if hits == 0 and false_alarms == 0:
    #    return 0.0

    accuracy = hits / (hits + false_alarms)

    if pprint:
        print("Hits:", str(hits))
        print("False alarms:", str(false_alarms))
        print("Accuracy:", str(accuracy))
        print()

    return accuracy


def cut(u, n):
    """ Throw out utterances (and labels) < length N. Methods assumes cleaned data, i.e. utterance and label lengths
        are the same. Incoming data structure: [[(w1,l1),(w2,l2)], []...]
    """
    results = []
    for i in u:
        if len(i) == 0 or len(i) < n:
            continue
        results.append(i)
    return results


def get_types(list):
    """
    :param list:
    :return:
    """
    return Counter(list)


def get_tokens(list, index=0):
    """
    :param list: list of tuples
    :param index: int index of which element to take in the tuple
    :return: list of elements
    """
    return [i[index] for i in list]


def get_columns_as_tuples(query_string):
    """ Fetchall() returns a list of tuples, where each tuple consists of selected columns in the sql query

    :param query_string: a SQL query on the database
    :return: a list of tuples, e.g. [(1, 'hap', 'V', 'NA'), (1, 'i', 'sfx', '1/2PL.S/P'), ...]
    """
    c = conn.cursor()
    c.execute(query_string)
    return c.fetchall()


def get_recall(targets):
    """
    Calculate recall over entire corpus: the number of times we see the total word_label types
    over all word_label types.
    """
    # Test data uses Cree as input
    # targets = [('tan', 'ADV'), ('tan', 'ADV')]
    # targets = [('tan', 'ADV'), ('ssh', 'INTJ')]

    # Get the types in the incoming targets.
    target_types = set(targets)
    # Get the labels for look up in the label_types Counter().
    target_labels = [x[1] for x in target_types]
    counts = get_types(target_labels)

    # Calculate the recall
    total = 0
    total_types = 0.0
    for k, v in counts.items():
        total += v
        total_types += label_types[k]
    recall = total/total_types

    # print(target_types)
    # print(target_labels)
    # print(counts)
    # print(label_types)
    # Test
    # print(recall==0.037037037037037035) # Should evaluate to True for Cree
    # print(recall==0.03773584905660377) # Should evaluate to True for Cree

    return recall


def clean(u, gloss, justgloss):
    """ Discard frames that contain unknown or missing data. """
    result = []
    crap = ["???", "NA", None, ""]

    if gloss and not justgloss:
        for i in u:
            left = i[0]
            center = i[1]
            right = i[2]

            # Morphemes-gloss: all (???, ???)
            if left[0] in crap and left[1] in crap:
                continue
            if center[0] in crap and center[1] in crap:
                continue
            if right[0] in crap and right[1] in crap:
                continue

            # Morphemes-gloss where gloss is ???
            """
            if left[1] in crap:
                continue
            if right[1] in crap:
                continue
            # Morphemes-gloss where morpheme is ???
            if left[0] in crap:
                continue
            if right[0] in crap:
                continue
            """
            # Morpheme-pos target where target pos is ???
            if center[1] in crap:
                continue
            result.append(i)
    else:
        for i in u:
            left = i[0]
            center = i[1]
            right = i[2]

            # Words or morphemes-pos: all (???, pos)
            if left[0] in crap or center[0] in crap or right[0] in crap:
                continue
            # Words or morphemes-pos: all (???, ???)
            if left[0] and left[1] in crap:
                continue
            if center[0] and center[1] in crap:
                continue
            if right[0] and right[1] in crap:
                continue
            # Words or morphemes-pos: target (word, ???)
            if center[1] in crap:
                continue
            result.append(i)
    return(result)


def get_trigram_count(corpus, u):
    """ Discard ??? or NA. """
    all = 0
    n = 0
    for i in u:
        all += 1
        # First element
        if i[0][0] == "???" or i[0][0] == "NA" or i[0][0] is None:
            continue
        if i[1][0] == "???" or i[1][0] == "NA" or i[1][0] is None:
            continue
        if i[2][0] == "???" or i[2][0] == "NA" or i[2][0] is None:
            continue
        # Second element
        if i[0][1] == "???" or i[0][1] == "NA" or i[0][1] is None:
            continue
        if i[1][1] == "???" or i[1][1] == "NA" or i[1][1] is None:
            continue
        if i[2][1] == "???" or i[2][1] == "NA" or i[2][1] is None:
            continue
        n += 1

    counts = [corpus, str(n), "count"]
    trigram_counts = [corpus, str(all), "trigrams"]
    return (counts, trigram_counts)


def get_counts(type, corpus):
    """ Create the counts for operationalization. """
    out = open("counts-"+type+".tsv", "a")
    # words = open('counts-words.tsv', 'a')
    u = None
    if type == "words":
        u = get_columns_as_tuples('select utterance_id_fk, word, pos from words where corpus = "' + corpus + '" ')
    else:
        u = get_columns_as_tuples(
            'select utterance_id_fk, morpheme, pos from morphemes where corpus = "' + corpus + '" ')
    u = get_utterances(u)

    # Utterance counts
    r = [corpus, str(len(u)), "utterances"]
    out.write("\t".join(r)+"\n")

    # Trigram counts (before and after cleaning)
    trigrams = cut(u, 3)  # excepts [[(w1,l1),(w2,l2)], []...]
    trigrams = get_list_of_ngrams(trigrams, 3)
    r = [corpus, str(len(trigrams)), "trigrams"]
    out.write("\t".join(r)+"\n")

    # This is to get the total number of trigrams minus the ones with the missing category
    clean_trigrams = clean(trigrams, 0)
    r = [corpus, str(len(clean_trigrams)), "count"]
    out.write("\t".join(r)+"\n")

    # Bigram counts
    bigrams = cut(u, 2)
    bigrams = get_list_of_ngrams(bigrams, 2)
    r = [corpus, str(len(bigrams)), "bigrams"]
    out.write("\t".join(r)+"\n")

    # Unigrams
    unigrams = cut(u, 1)
    unigrams = get_list_of_ngrams(unigrams, 1)
    r = [corpus, str(len(unigrams)), "unigrams"]
    out.write("\t".join(r) + "\n")

    out.close()


def main(type):
    """ Corpus-by-corpus analysis. """
    setup()
    corpora = []
    if type == "words":
        corpora = ['Chintang', 'Inuktitut', 'Japanese_MiiPro', 'Russian', 'Sesotho', 'Turkish', 'Yucatec']
    else:
        corpora = ['Chintang', 'Inuktitut', 'Japanese_MiiPro', 'Sesotho', 'Turkish', 'Yucatec']

    # corpora = ['Chintang', 'Inuktitut'] # test
    for corpus in corpora:
        print("Processing:"+corpus)
        get_counts(type, corpus)
        # get_counts_morphemes(corpus)


if __name__ == '__main__':
    # print counts (utterances, trigrams, bigrams) per corpus
    type = "words"
    type = "morphemes"
    main(type)
