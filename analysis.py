from collections import Counter, defaultdict

from words import valid, answers

def best_guess(possible_answers, possible_guesses):
    averages = guess_averages(possible_answers, possible_guesses)
    return min(averages, key=lambda guess: guess[1])

def guess_averages(possible_answers, possible_guesses):
    return [(guess, average_remaining(possible_answers, guess)) for guess in possible_guesses]

def average_remaining(possible_answers, guess):
    remaining = [calculate_remaining(possible_answers, answer, guess) for answer in possible_answers]
    return sum(remaining) / len(remaining)

def filter_exact(index, letter):
    return lambda word: word[index] == letter

def filter_letter_elsewhere(index, letter):
    return lambda word: word[index] != letter

def filter_min_count(letter, min_occurrances):
    return lambda word: Counter(word)[letter] >= min_occurrances

def filter_exact_count(letter, exact_occurrances):
    return lambda word: Counter(word)[letter] == exact_occurrances

def filter_eliminated(letter):
    return lambda word: letter not in word

def filter_intersection(filters):
    def joined_filter(element):
        for f in filters:
            if not f(element):
                return False
        return True
    return joined_filter

def make_filters(actual_answer, guess):
    filters = []
    guessed_count = defaultdict(int)
    letter_count = Counter(actual_answer)
    for idx, letter in enumerate(guess):
        if letter in actual_answer:
            guessed_count[letter] += 1

            if actual_answer[idx] == guess[idx]:
                # Found letter in correct position
                filters.append(filter_exact(idx, letter))
            else:
                # Know that letter is *not* in this position
                filters.append(filter_letter_elsewhere(idx, letter))

            # Handle letter count, whether or not position was correct
            # For example, what if this was the 2nd repeat letter in correct
            # position, but the first was found out of place?
            if guessed_count[letter] <= letter_count[letter]:
                filters.append(filter_min_count(letter, guessed_count[letter]))
            else:
                filters.append(filter_exact_count(letter, letter_count[letter]))
        else:
            # Discovered that letter is not in word
            filters.append(filter_eliminated(letter))

    return filters

def apply_filters(candidate_answers, filters):
    joined_filter = filter_intersection(filters)
    return set(filter(joined_filter, candidate_answers))

def get_remaining(candidate_answers, actual_answer, guess):
    filters = make_filters(actual_answer, guess)
    return apply_filters(candidate_answers, filters)

def calculate_remaining(*args):
    return len(get_remaining(*args))

def top_positional_letters():
    # returns top_letters = [(0, 's'), (1, 'a'), (2, 'a'), (3, 'e'), (4, 's')]
    pos_c = [Counter(),Counter(),Counter(),Counter(),Counter()]
    for v in valid:
        for i in range(0,5):
            pos_c[i].update(v[i])
    return pos_c


def word_matches_positional_letters(word, positionals):
    for index, letter in positionals.items():
        if word[index] != letter:
            return False
    return True


def all_matching_positional_letters(words, positionals):
    return {w for w in words if word_matches_positional_letters(w, positionals)}

def most_positional_letters():
    from itertools import combinations
    top_letters = [(0, 's'), (1, 'a'), (2, 'a'), (3, 'e'), (4, 's')]
    for count in reversed(range(4)):
        combos = combinations(top_letters, count)
        matching_words = set()
        for positionals in combos:
            words_with_positionals = all_matching_positional_letters(valid, dict(positionals))
            matching_words.update(words_with_positionals)

        if matching_words:
            return (count, matching_words)

    return set()


def ai_play(actual):
    guess_count = 1
    first_guess = 'roate'
    print(f"Guess #{guess_count}: {first_guess!r}")
    remaining = get_remaining(valid, actual, first_guess)

    while len(remaining) > 1:
        print(f"{len(remaining)} more words found")
        guess, avg_remain = best_guess(remaining, valid)
        guess_count += 1
        print(f"Guess #{guess_count}: {guess!r}, with estimated {avg_remain:.1f} remaining")
        remaining = get_remaining(remaining, actual, guess)

    if len(remaining) == 1 and guess not in remaining:
        guess_count += 1
        print(f"Trivial guess #{guess_count}: {remaining.pop()}")

def posthoc_analysis(actual, guesses):
    print(f"Post-hoc analysis of game with answer {actual!r}")

    remaining = valid
    for idx, guess in enumerate(guesses):
        print(f"With hindsight, {len(remaining)} words remain")

        guess_count = idx + 1
        print(f"\nGuess #{guess_count}: {guess!r}")

        new_remaining = get_remaining(remaining, actual, guess)

        if remaining != valid:
            # These are too slow to calculate for the first guess, with the full valid set

            guess_score = average_remaining(remaining, guess)
            print(f"At the time, the guess could be expected to leave {guess_score:.1f} words")

            algo_guesses = guess_averages(remaining, valid)
            best_algo_guess = min(algo_guesses, key=lambda guess: guess[1])
            worst_algo_guess = max(algo_guesses, key=lambda guess: guess[1])
            print(f"best algo guess = {best_algo_guess}")
            print(f"worst algo guess = {worst_algo_guess}")

        remaining = new_remaining

    print(f"Words left: {len(remaining)}")
    if len(remaining) < 40:
        print(remaining)


if __name__ == '__main__':
    import sys
    args = sys.argv
    if len(args) > 1 and args[1] == 'test':
        assert calculate_remaining(["aoeuh"], "aoeuh", "") == 1
        assert calculate_remaining(["ab"], "ab", "ac") == 1  # Catch a bad closure
        assert calculate_remaining(["aoeuh"], "aoeuh", "aoeuh") == 1
        assert calculate_remaining(["aoeuh"], "aoeuh", "tnsgc") == 1
        assert calculate_remaining(["aoeuh"], "aoeuh", "hueoa") == 1
        assert calculate_remaining(["baa", "bac"], "baa", "aab") == 1  # Catch a bad closure
        assert calculate_remaining(["baac", "baaa"], "baac", "aaab") == 1  # Catch a bad closure
        assert calculate_remaining(["ab"], "ab", "cb") == 1  # Catch a bad closure
    elif len(args) == 3 and args[1] == 'ai':
        ai_play(args[2])
    else:
        actual = 'brake'
        guesses = ['roate', 'clung', 'wimps', 'drake']
        posthoc_analysis(actual, guesses)
