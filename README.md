# Wordle Analysis Tool

Mostly just written for myself. A tool to run analysis on how good my wordle guesses were.

## Install

```sh
python3 -m venv venv
. venv/bin/activate
pip install maturin
cd ../wordle-rs
maturin develop --release
cd ../wordle
```

## Examples

### Post-game analysis

Compare an actual playthrough against a heuristic of reducing the remaining words as much as
possible.

```sh
$ python3 analysis.py analysis.py ph rales bound rainy
Post-hoc analysis of game with answer 'rainy', with a dictionary size 5522

Guess #1: 'rales'
At the time, the guess could be expected to leave 119.1 words (using a precalculated score)
After elimination, 19 words remain. Got lucky by 6.0x
Specifically: ['rabbi', 'rabic', 'rabid', 'radar', 'radii', 'radio', 'radix', 'radon', 'rainy', 'rajah', 'ranch', 'randy', 'rangy', 'rapid', 'ratio', 'ratty', 'ravin', 'rayon', 'razor']

Guess #2: 'bound'
At the time, the guess could be expected to leave 1.9 words
Skill score: 10.8/10
Skill score (easy mode): 7.3/10
Spectrum percent: 101.4%
   vs best 'bodhi' (easy) at 1.4 word est.
   vs best 'radio' at 2.1 word est.
   vs worst 'rajah' at 13.6 word est.
After elimination, 1 words remain. Got lucky by 1.5x
Specifically: ['rainy']

Guess #3: 'rainy'
At the time, the guess could be expected to leave 0.0 words
Found the final word. Got exactly the expected luck

Lucky game, by: 8.8x
```

In this example, "bound" was better than the best "hard mode" guess ("radio"). Hard mode
is the restriction that you must use letters that follow the rules you have found so far. But
"bound" was not as good as the best easy-mode guess of "bodhi".

### Heuristic-driven play

See how a simple algorithm ("AI" heh) would have tried to play the game. It tries to reduce the
remaining words as much as possible at each step.

```sh
$ python3 analysis.py ai mummy

Guess #1: 'rales'
358 more words found
Guess #2: 'tonic', with estimated 9.8 remaining
Specifically: {'kudzu', 'muzzy', 'fuzzy', 'guppy', 'vuggy', 'hudud', 'mummy', 'pudgy', 'bumpy', 'fuddy', 'muddy', 'jugum', 'buffy', 'hubby', 'dumpy', 'humpy', 'puppy', 'buggy', 'huffy', 'humph', 'muggy', 'gummy', 'jumpy', 'dummy', 'yummy', 'buddy', 'pygmy', 'puffy', 'buzzy', 'whump'}
30 more words found
Guess #3: 'bumpy', with estimated 2.8 remaining
Specifically: {'dummy', 'mummy', 'gummy', 'yummy'}
4 more words found
Guess #4: 'midge', with estimated 1.0 remaining
Specifically: {'mummy'}
Trivial guess #5: mummy
```

