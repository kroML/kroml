import re
from collections import Counter
from utils.logger import Logger


class Spellcheck:

    def __init__(self, config, words_path=None, names_path=None, overrides_path=None):
        self.config = config
        self.words = Counter()
        self.names = {}
        self.overrides = {}
        # Loads words, names and overrides from files.
        if words_path is None:
            words_path = self.config.WORDS
        if names_path is None:
            names_path = self.config.NAMES
        if overrides_path is None:
            overrides_path = self.config.OVERRIDES
        # Represents list of words that have specific suggestions
        self.load_words(words_path)
        # Contains list of names with first letter capital
        self.load_names(names_path)
        # Contains list of words with their weights
        self.load_overrides(overrides_path)
        # Remove pattern other than letters
        self.rem_pattern = re.compile('[^A-Za-z]+')

    def load_words(self, path: str) -> None:
        """
        Loads words from input file into Counter self.words and saves them.
        :param path: Path to the file, that contains English words and its number of occurrences.
        :return: Counter of words with their occurrences.
        """
        source_file = open(path, "r")
        for line in source_file:
            wrd, count = line.split(' ')
            wrd = wrd.lower()
            self.words[wrd] = int(count.replace('\n', ''))

    def load_names(self, path: str) -> None:
        """
        Loads names from path into dictionary self.names with names in lower as keys and names with capital letters
        as values.
        :param path: Path to the file, that contains names.
        :return: Dictionary of names in lower as keys and names with capital letters as values.
        """
        names = open(path, "r")
        for line in names:
            wrd = line.replace('\n', '')
            self.names[wrd.lower()] = wrd

    def load_overrides(self, path: str) -> None:
        """
        Loads words with specific suggestions from path into dictionary self.overrides and returns it.
        :param path: Path to the file, that contains words that have specific suggestions.
        :return: Dictionary of words with specific suggestions.
        """
        over = open(path, "r")
        for line in over:
            wrd, count = line.split(';')
            self.overrides[wrd] = count.replace('\n', '')

    def probability(self, word: str) -> float:
        """
        Probability of the word `word`.
        Definition of function that will define probability of suggestion relevance.

        :param word: Word, whose probability of occurrence we want to know.
        :return: Probability of occurrence of the word 'word'.
        """
        n = sum(self.words.values())
        return self.words[word] / n

    def maxN(self, elements: list or set, n: int) -> list:
        """
        Definition of function that will pick best n items from list of elements.

        :param elements: Word, which is the function picking from.
        :param n: Number of best items, that will function return.
        :return: Returns best n items from list.
        """
        return sorted(elements, key=self.probability, reverse=True)[:n]

    def known(self, words: set or list) -> set:
        """
        Function will return the subset of `words` that appear in the dictionary of self.words.
        :param words: Words, that we want to know if they are in self.words.
        :return: Set of words that are in words and also in self.words.
        """
        return set(w for w in words if w in self.words)

    def candidates(self, word: str) -> set:
        """
        Function will pick all relevant candidates. Generate possible spelling corrections for word.
        :param word: Word, we are generating spelling corrections for.
        :return: Set of words, that are possible right spelled candidates for input word.
        """
        return self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word]

    def edits1(self, word: str) -> set:
        """
        Function will return edits that are one edit away from `word`
        :param word:  Word, we are generating possible edits for.
        :return: Set of edits that are one edit away from `word`.
        """
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word: str):
        """
        Function will return All edits that are two edits away from `word`.
        :param word: Word, we are generating possible edits for.
        :return: All edits that are two edits away from `word`
        """
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    def givename(self, words: list) -> list:
        """
        Function will loop trough an array of string and return same string but with capital letters on names
        :param words: List of words.
        :return: List of words with first letter capital.
        """
        result = []
        for word in words:
            if word in self.names:
                result.append(self.names[word])
            else:
                result.append(word)
        return result

    def remove_char(self, word: str) -> str:
        """
        Function will return word but only with letters. Deleting all other chars.
        :param word: Input word.
        :return: Word that consists only of letters.
        """
        return self.rem_pattern.sub('', word)

    def isInput(self, word: str) -> bool:
        """
        Function will determinate if it’s an relevant input for spellchecking.
        If there is more than 2 non letter items in, its not recognized as valid input.
        When word is only one char, returns false, also if word consists of 2 chars and one is other than letter,
        returns false.

        :param word: Input word.
        :return: If there is more than 2 non letter items in word returns false, when word is only one char, returns
        false, also if word consists of 2 chars and one is other than letter, returns false. Else true.
        """
        charcount = len(re.findall(r'[a-zA-Z]', word))
        if len(word) > 1:
            if charcount + 2 <= (len(word)):
                return False
            else:
                if len(word) == 2:
                    if charcount == 1:
                        return False
                else:
                    return True
        else:
            return False

    def isNameError(self, word: str) -> bool:
        """
        Returns true if there is another capital letter in a name, other than on the beginning of the name.

        :param word: Input word, name we want to check.
        :return: Returns true if there is another capital letter in a name, other than on the beginning of the name.
        """
        lowWord = word.lower()
        result = False
        if lowWord in self.names:
            if not (self.names[lowWord] == word):
                result = True
        return result

    def name_candidates(self, word: str) -> list:
        """
        Returns list of names (with only one name or zero names in it), which lower letters version is also in
        self.names.

        :param word: Input name.
        :return: Returns list of names (with only one name or zero names in it), which lower letters version is also in
        self.names.
        """
        result = []
        lowWord = word.lower()
        if lowWord in self.names:
            result.append(self.names[lowWord])
        return result

    def over_candidates(self, word: str) -> list:
        """
        Same as nameCandidates but with self.overrides.

        :param word:
        :return:
        """
        result = []
        lowWord = word.lower()
        if lowWord in self.overrides:
            result.append(self.overrides[lowWord])
        return result

    def best_candidates(self, word: str, n: int) -> list:
        """
        Function will return best n candidate suggestions.
        :param word: Word, we are looking best candidates for.
        :param n: Number of best candidates to return.
        :return: Returns best n candidate suggestions for 'word'.
        """
        result = []
        lowWord = word.lower()
        result = result + self.over_candidates(lowWord) + self.name_candidates(lowWord)
        spellCan = self.maxN(self.candidates(word), n)
        if len(spellCan) == 1:
            if spellCan[0] != word and spellCan[0] != lowWord:
                result = result + spellCan
        else:
            result = result + spellCan
        print(self.givename(result[:n]))
        return self.givename(result[:n])

    def is_error(self, word: str) -> bool:
        """
        Function will determinate if the word is relevant error.

        :param word: Input word, we want to determine if it is relevant error.
        :return: Returns true if word is relevant error.
        """
        result = False
        if self.isInput(word):
            word2 = self.remove_char(word)
            if not (word2.lower() in self.words):
                if word2.lower() in self.names:
                    if not (self.names[word2.lower()] == word2):
                        result = True
                else:
                    result = True
            else:
                if word2.lower() in self.names:
                    if not (self.names[word2.lower()] == word2):
                        result = True
        return result
