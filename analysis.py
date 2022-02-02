from collections import Counter, defaultdict

from words import valid, answers, likely, unlikely


# Consider using any word in the dictionary (ie~ "easy mode") when this many words are remaining in
# the valid set (or fewer). Otherwise, use hard mode.
CONSIDER_ALL_WORDS_MAXIMUM = 30

SCORE_UP_TO_SIZE = 432
LIST_WORDS_UP_TO = 110


def select_best_guess(possible_answers, possible_guesses):
    averages = guess_averages(possible_answers, possible_guesses)
    # score is the first element of the guess tuple, so we can just naively sort the results
    return min(averages)

def guess_averages(possible_answers, possible_guesses):
    return [(average_remaining(possible_answers, guess), guess) for guess in possible_guesses]

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

def calculate_remaining(possible_answers, answer, guess):
    if guess == answer:
        return 0
    else:
        return len(get_remaining(possible_answers, answer, guess))

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
    remaining = get_remaining(likely, actual, first_guess)

    while len(remaining) > 1:
        print(f"{len(remaining)} more words found")
        avg_remain, guess = select_best_guess(remaining, remaining)
        guess_count += 1
        print(f"Guess #{guess_count}: {guess!r}, with estimated {avg_remain:.1f} remaining")
        remaining = get_remaining(remaining, actual, guess)
        if len(remaining) < LIST_WORDS_UP_TO:
            print("Specifically:", remaining)

    if len(remaining) == 1 and guess not in remaining:
        guess_count += 1
        print(f"Trivial guess #{guess_count}: {remaining.pop()}")

def posthoc_analysis(actual, guesses):
    remaining = likely
    print(f"Post-hoc analysis of game with answer {actual!r}, with a dictionary size {len(remaining)}")

    total_luck_score = 1.0

    for idx, guess in enumerate(guesses):

        guess_count = idx + 1
        print(f"\nGuess #{guess_count}: {guess!r}")

        new_remaining = get_remaining(remaining, actual, guess)

        if idx == 0:
            precalculated = {"roate": 431.1, "irate": 485.8}
            if guess in precalculated:
                guess_score = precalculated[guess]
                print(
                    f"At the time, the guess could be expected to leave {guess_score:.1f} words"
                    " (using a precalculated score)"
                )
            else:
                print(f"No precalculated score is available for the starting word {guess!r}")
        elif len(remaining) < 1200:
            guess_score = average_remaining(remaining, guess)
            print(f"At the time, the guess could be expected to leave {guess_score:.1f} words")
        else:
            guess_score = None

        if len(remaining) < SCORE_UP_TO_SIZE:

            # TODO test how long it takes to run the averages, and offer to
            #   skip, instead of hard-code 300
            # TODO return the min/max from rust, to enable analysis of bigger data sets?
            if len(remaining) > CONSIDER_ALL_WORDS_MAXIMUM:
                guess_choices = remaining
            else:
                guess_choices = likely

            algo_guesses = guess_averages(remaining, guess_choices)
            best_score, best_guess = min(algo_guesses)
            worst_score, worst_guess = max(algo_guesses)

            # calculate skill score
            if guess_score is None:
                print("Can't calculate skill score if there's no guess score")
            else:
                if guess_score == 0:
                    print(f"Skill score: ∞/10")
                else:
                    # average word count that could be improved by choosing best algo word:
                    wasted_words = guess_score - best_score
                    # scale the waste to the score to guess a waste percentage
                    waste_fraction = wasted_words / guess_score
                    # invert in order to report the "happy stat"
                    skill_score = (1 - waste_fraction) * 10
                    print(f"Skill score: {skill_score:.1f}/10")

                # where are you on the best/worst range
                full_spectrum = (worst_score - best_score)
                if full_spectrum:
                    spectrum_percent = (worst_score - guess_score) / full_spectrum * 100
                else:
                    spectrum_percent = 100
                print(f"Spectrum percent: {spectrum_percent:.1f}%")

                print(f"   vs best {best_guess!r} at {best_score:.1f} word est.")
                print(f"   vs worst {worst_guess!r} at {worst_score:.1f} word est.")

        if guess == actual:
            print(f"Found the final word.", end=" ")
        else:
            print(f"After elimination, {len(new_remaining)} words remain.", end=" ")

        if guess_score is not None:
            actual_left = len(new_remaining)
            score_with_answer = (guess_score + 1)
            luck_score = score_with_answer / actual_left
            total_luck_score *= luck_score
            if actual_left < score_with_answer:
                print(f"Got lucky by {luck_score:.1f}x")
            elif actual_left == score_with_answer:
                print("Got exactly the expected luck")
            else:
                print(f"Got unlucky by {1 / luck_score:.1f}x")
        else:
            print("")

        remaining = new_remaining

        if len(remaining) < LIST_WORDS_UP_TO and guess != actual:
            print("Specifically:", remaining)

    print("")
    if total_luck_score > 1:
        print(f"Lucky game, by: {total_luck_score:.1f}x")
    else:
        print(f"Unlucky game, by: {1 / total_luck_score:.1f}x")


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
    elif len(args) >= 4 and args[1] == 'ph':
        guesses = args[2:]
        actual = args[-1]
        posthoc_analysis(actual, guesses)
    else:
        print("Invoke with test, ai, or ph")
