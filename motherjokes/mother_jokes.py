import re
from itertools import chain

import pymorphy2
import mosestokenizer


class MotherJokeGenerator:
    """
    Generator for mother jokes in russian language
    """

    morph = pymorphy2.MorphAnalyzer()
    tokenizer = mosestokenizer.MosesTokenizer()
    detokenizer = mosestokenizer.MosesDetokenizer()

    joke_beginning = 'твоя мамка'

    duplicating_punctuation_remover = re.compile(r'(\W)\1+')
    punctuation_space_remover = re.compile(r'\s([.,:;?!](?:\s|$))')
    pair_punctuation_space_remover = re.compile(r'(["\[({<])\s*(.*?)\s*(["\])}>])')

    unsuitable_verbs = 'быть бывать'.split()
    suitable_verb_form = 'буду'.split()

    pronouns_p1 = 'я меня мне меня мной мы нас нам нас нами'.split()
    pronouns_p2 = 'ты тебя тебе тебя тобой вы вас вам вас вами'.split()

    prepositions_p1 = 'обо со'.split()
    prepositions_p2 = 'о с'.split()

    pronoun_flip_map = dict(chain(zip(pronouns_p1, pronouns_p2), zip(pronouns_p2, pronouns_p1)))
    preposition_flip_map = dict(chain(zip(prepositions_p1, prepositions_p2), zip(prepositions_p2, prepositions_p1)))

    preposition_flip_pronouns = set('мне тебе мной тобой'.split())

    def __init__(self, min_token_count=3, max_token_count=15, min_verb_length=3, min_words_after_verb=1):
        """
        :param min_token_count: do not process sentences that have less than that number of tokens
        :param max_token_count: do not process sentences that have more than that number of tokens
        :param min_verb_length: limits minimal verb length (saves some time skipping small words)
        :param min_words_after_verb: minimal words number after a verb (joke is usually better with some trailing words)
        """

        super().__init__()

        self.min_token_count = min_token_count
        self.max_token_count = max_token_count
        self.min_word_length = min_verb_length
        self.min_words_after_verb = min_words_after_verb

    def get_joke(self, sentence):
        """
        Generate a joke from the sentence if it contains verbs.
        Morphological analysis is performed to find verbs and transform them.
        :returns joke string or None if was unable to generate a joke
        """

        clean_sentence = self.duplicating_punctuation_remover.sub(r'\1', sentence.lower()).strip(',.!?;:')
        tokens = self.tokenizer(clean_sentence)

        tokens_count = len(tokens)
        if self.min_token_count > tokens_count or tokens_count > self.max_token_count:
            return None

        inflected_verb_index = -1
        inflected_verb = None

        # finding last verb in the sentence and changing it's form
        # starting enumeration from 1 for regular index calculation convenience
        for reverse_index, word in enumerate(reversed(tokens), 1):
            if len(word) < self.min_word_length:
                continue

            # taking the most probable morphological analysis result
            word_morph = self.morph.parse(word)[0]
            is_verb = word_morph.tag.POS == 'VERB'

            if not is_verb:
                continue

            if word_morph.normal_form in self.unsuitable_verbs and word not in self.suitable_verb_form:
                continue

            if reverse_index <= self.min_words_after_verb:
                break

            inflected_verb_morph = self._inflect_verb(word_morph)

            if inflected_verb_morph:
                inflected_verb_index = len(tokens) - reverse_index
                inflected_verb = inflected_verb_morph.word

            # last_good_verb might not exist here if failed to inflate the verb
            # will ignore sentence in such case
            break

        return self._compile_joke(tokens[inflected_verb_index+1:], inflected_verb) if inflected_verb else None

    @staticmethod
    def _inflect_verb(verb_morph):
        """
        Change the form of the verb to correlate with the beginning of the joke
        """

        tense = verb_morph.tag.tense
        inflected_verb_morph = (
            verb_morph.inflect({'VERB', 'femn'}) if tense == 'past'
            else verb_morph.inflect({'VERB', 'sing', '3per', tense}) if tense
            else None
        )
        return inflected_verb_morph

    def _flip_pronouns(self, rest_of_joke):
        """
        Reverse the pronouns, usually makes more sense this way round
        """

        for index, word in enumerate(rest_of_joke):
            if word in self.pronoun_flip_map:
                rest_of_joke[index] = self.pronoun_flip_map[word]
                prev_word = rest_of_joke[index-1]
                if index > 0 and word in self.preposition_flip_pronouns and prev_word in self.preposition_flip_map:
                    rest_of_joke[index-1] = self.preposition_flip_map[prev_word]

    def _compile_joke(self, remaining_tokens, inflected_verb):
        """
        Final preparations and formatting
        """

        self._flip_pronouns(remaining_tokens)
        joke_ending = self.detokenizer(remaining_tokens)
        joke = f'{self.joke_beginning} {inflected_verb} {joke_ending}'
        joke = self.punctuation_space_remover.sub(r'\1', joke)
        joke = self.pair_punctuation_space_remover.sub(r'\1\2\3', joke)
        return joke
