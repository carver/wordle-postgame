from collections import Counter, defaultdict

from words import valid, answers

def best_guess(possible_answers):
    averages = [(guess, average_remaining(possible_answers, guess)) for guess in valid]
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

def calculate_remaining(candidate_answers, actual_answer, guess):
    filters = []
    actual_counts = Counter(actual_answer)
    for guess_letter, guess_count in Counter(actual_answer).items():
        actual_count = actual_counts[guess_letter]
        if actual_count == 0:
            # Discovered that letter is not in word
            # This test isn't strictly necessary, but ought to be a bit faster to filter
            filters.append(filter_eliminated(letter))
        elif guess_count > actual_count:
            filters.append(filter_exact_count(guess_letter, actual_count))
        else:
            filters.append(filter_min_count(guess_letter, guess_count))

    for idx, letter in enumerate(guess):
        if actual_answer[idx] == guess[idx]:
            # Found letter in correct position
            filters.append(filter_exact(idx, letter))

    remaining_answers = candidate_answers
    for f in filters:
        remaining_answers = set(filter(f, remaining_answers))
    return len(remaining_answers)


if __name__ == '__main__':
    assert calculate_remaining(["aoeuh"], "aoeuh", "") == 1
    assert calculate_remaining(["ab"], "ab", "ac") == 1  # Catch a bad closure
    assert calculate_remaining(["aoeuh"], "aoeuh", "aoeuh") == 1
    assert calculate_remaining(["aoeuh"], "aoeuh", "tnsgc") == 1
    assert calculate_remaining(["aoeuh"], "aoeuh", "hueoa") == 1
    assert calculate_remaining(["baa", "bac"], "baa", "aab") == 1  # Catch a bad closure
    assert calculate_remaining(["baac", "baaa"], "baac", "aaab") == 1  # Catch a bad closure
    assert calculate_remaining(["ab"], "ab", "cb") == 1  # Catch a bad closure
