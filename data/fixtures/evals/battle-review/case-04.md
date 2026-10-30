# Case 04

Request:

`Review game 1 from the structured battle state in data/fixtures/battle-state-v1.example.json. I want to know if my turn-one Tailwind and Protect was the mistake.`

Checks:

- grounds the review in the observed turn events instead of a generic summary
- treats fields the battle state omits, such as opponent items and spreads, as unknown and does not infer hidden information
- separates what the player knew at team preview and turn one from what was revealed later
- judges the turn-one line against realistic alternatives that were available from the actual board
- ends with a prep implication for games 2 and 3 of the same set

Failure triggers:

- states an opponent item, ability, or spread that the battle state does not reveal
- judges the turn-one choice using information revealed only on later turns
