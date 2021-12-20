from collections import Counter, defaultdict

from words import valid, answers

def best_guess(possible_answers, possible_guesses):
    averages = [(guess, average_remaining(possible_answers, guess)) for guess in possible_guesses]
    return min(averages, key=lambda guess, avg_remaining: avg_remaining)

def average_remaining(possible_answers, guess):
    remaining = [calculate_remaining(possible_answers, answer, guess) for answer in possible_answers]
    return sum(remaining) / len(remaining)

def filter_exact(index, letter):
    return lambda word: word[index] == letter

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

def calculate_remaining(candidate_answers, actual_answer, guess):
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

    joined_filter = filter_intersection(filters)
    return len(set(filter(joined_filter, candidate_answers)))


if __name__ == '__main__':
    assert calculate_remaining(["aoeuh"], "aoeuh", "") == 1
    assert calculate_remaining(["ab"], "ab", "ac") == 1  # Catch a bad closure
    assert calculate_remaining(["aoeuh"], "aoeuh", "aoeuh") == 1
    assert calculate_remaining(["aoeuh"], "aoeuh", "tnsgc") == 1
    assert calculate_remaining(["aoeuh"], "aoeuh", "hueoa") == 1
    assert calculate_remaining(["baa", "bac"], "baa", "aab") == 1  # Catch a bad closure
    assert calculate_remaining(["baac", "baaa"], "baac", "aaab") == 1  # Catch a bad closure
    assert calculate_remaining(["ab"], "ab", "cb") == 1  # Catch a bad closure
