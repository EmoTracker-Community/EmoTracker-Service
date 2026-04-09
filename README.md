# EmoTracker-Service

This directory contains the EmoTracker SDK — schemas and documentation for building tracker packs.

---

## Item Properties

All item types share a common set of base properties defined in `sdk/schema/items.json`.

### `phonetic_substitutes` *(optional)*

An array of alternate phonetic phrases that the voice control system will recognise as this item's name.

This is useful when an item's name contains words that are not in the speech model's vocabulary. For example, the word *"hookshot"* is not a single vocabulary entry in the bundled Vosk model, so commands like *"hey tracker track hookshot"* may not be recognised. You can work around this with a phonetic substitute:

```json
{
  "name": "Hookshot",
  "type": "toggle",
  "img": "hookshot",
  "codes": "hookshot",
  "phonetic_substitutes": ["hook shot"]
}
```

The voice control extension automatically attempts to split unknown compound words into known sub-words (e.g. `hookshot` → `hook shot`), so explicit substitutes are only needed when the automatic heuristic produces a wrong or undesirable result, or when you want to support a completely different spoken alias for an item (e.g. `"bow"` as a substitute for `"fairy bow"`).

All substitutes are registered alongside the item's canonical name, so either form will trigger the same voice command.
