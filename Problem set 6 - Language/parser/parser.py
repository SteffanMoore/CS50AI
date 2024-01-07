import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> VP | NP VP | S Conj S
VP -> V | V NP | V P NP | Adv V | Adv V NP | V Adv
NP -> N | Det N | NP P NP | Det AP N | NP Adv
AP -> Adj | Adj AP
"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """

    word_list = []

    # Converts string to tokens and adds each token with at least one letter to the word list
    for word in nltk.tokenize.word_tokenize(sentence.lower()):
        for letter in word:
            if letter.isalpha():
                word_list.append(word)
                break

    return word_list


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """

    noun_phrase_chunks = []

    # Checks subtrees within the tree to ensure that they don't contain any NPs
    for subtree in tree.subtrees():
        if subtree.label() == "NP":
            lowest_level_NP = True

            first_item = True
            for contained_groups in subtree.subtrees():
                if contained_groups.label() == "NP" and first_item == False:
                    lowest_level_NP = False
                    break
                first_item = False

            if lowest_level_NP:
                noun_phrase_chunks.append(subtree)

    return noun_phrase_chunks


if __name__ == "__main__":
    main()
