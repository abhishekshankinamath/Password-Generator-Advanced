"""Secure password and passphrase generation helpers.

Uses Python's secrets module for cryptographically secure randomness.
No generated password is written to disk.
"""

from __future__ import annotations

import math
import secrets
import string
from typing import Iterable


UPPERCASE = string.ascii_uppercase
LOWERCASE = string.ascii_lowercase
DIGITS = string.digits
SYMBOLS = "!@#$%^&*()-_=+[]{};:,.?"
AMBIGUOUS = set("O0Il1|`'\"{}[]()")

# A built-in word list means passphrase generation works offline and needs no
# downloaded dictionary. Words are intentionally easy to type and distinguish.
WORDS = tuple("""amber anchor apple apricot arch arrow artist autumn badge bamboo beacon berry birch blossom blue breeze brook cactus candle canyon castle cedar cherry circle citrus cloud clover coast cocoa comet coral cosmos cotton cricket crystal daisy dawn delta desert diamond dolphin dragon dream drift eagle earth echo elm ember engine evening falcon feather fern field figure finch flame forest fossil fountain fox galaxy garden garlic gem glacier glow gold granite grape grass harbor harmony hazel heart hill honey horizon island ivory jade jazz journey kernel kettle kiwi lagoon lantern lavender leaf lemon lilac linen lizard lotus lunar maple marble meadow melon memory meteor midnight mint mirror mist monarch moon moss mountain museum music navy nectar nest nickel north novel oak ocean olive omega onion opal orange orchid otter oyster paper peach pearl pebble pepper picnic pine planet plum pocket poetry pond poppy prairie prism pumpkin quartz quest quiet rabbit radar rainbow raven reed reef ribbon river robin rocket rose ruby saffron sail salmon sapphire satin scarlet season shadow shell silver skylark smile smoke snow solar sparrow spice spring spruce star stone storm summer sunset swan sweater swift temple thunder timber topaz torch travel tulip tunnel twilight valley velvet velvet violet vision walnut water wheat willow window winter wisdom wolf wonder wren yellow zephyr""".split())


def _clean_charset(characters: str, exclude_ambiguous: bool) -> str:
    if exclude_ambiguous:
        characters = "".join(ch for ch in characters if ch not in AMBIGUOUS)
    # Preserve order while removing duplicates.
    return "".join(dict.fromkeys(characters))


def build_character_sets(
    *,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
) -> list[str]:
    """Return the enabled character groups after applying ambiguity filtering."""
    sets: list[str] = []
    if use_uppercase:
        sets.append(_clean_charset(UPPERCASE, exclude_ambiguous))
    if use_lowercase:
        sets.append(_clean_charset(LOWERCASE, exclude_ambiguous))
    if use_digits:
        sets.append(_clean_charset(DIGITS, exclude_ambiguous))
    if use_symbols:
        sets.append(_clean_charset(SYMBOLS, exclude_ambiguous))
    return [characters for characters in sets if characters]


def generate_password(
    length: int = 20,
    *,
    use_uppercase: bool = True,
    use_lowercase: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    exclude_ambiguous: bool = False,
    no_repeats: bool = False,
) -> str:
    """Generate a secure password that includes every selected character type."""
    if not isinstance(length, int) or isinstance(length, bool):
        raise ValueError("Password length must be a whole number.")
    if not 8 <= length <= 128:
        raise ValueError("Password length must be between 8 and 128 characters.")

    groups = build_character_sets(
        use_uppercase=use_uppercase,
        use_lowercase=use_lowercase,
        use_digits=use_digits,
        use_symbols=use_symbols,
        exclude_ambiguous=exclude_ambiguous,
    )
    if not groups:
        raise ValueError("Select at least one character type.")
    if len(groups) > length:
        raise ValueError("Password length is too short for the selected character types.")

    pool = "".join(groups)
    if no_repeats and length > len(set(pool)):
        raise ValueError(
            f"Only {len(set(pool))} unique characters are available. "
            "Reduce the length or allow repeated characters."
        )

    # First choose one character from each selected group so all selected types
    # are guaranteed to appear at least once.
    chosen = [secrets.choice(group) for group in groups]

    if no_repeats:
        available = [character for character in dict.fromkeys(pool) if character not in chosen]
        chosen.extend(secrets.SystemRandom().sample(available, length - len(chosen)))
    else:
        chosen.extend(secrets.choice(pool) for _ in range(length - len(chosen)))

    secrets.SystemRandom().shuffle(chosen)
    return "".join(chosen)


def generate_passphrase(
    word_count: int = 6,
    *,
    separator: str = "-",
    capitalize_words: bool = False,
    no_repeated_words: bool = True,
) -> str:
    """Generate a memorable passphrase from the built-in offline word list."""
    if not isinstance(word_count, int) or isinstance(word_count, bool):
        raise ValueError("Word count must be a whole number.")
    if not 4 <= word_count <= 12:
        raise ValueError("Choose between 4 and 12 words.")
    if separator not in {"-", "_", ".", " "}:
        raise ValueError("Choose a supported word separator.")
    if no_repeated_words and word_count > len(WORDS):
        raise ValueError("Not enough unique words are available.")

    if no_repeated_words:
        selected = secrets.SystemRandom().sample(WORDS, word_count)
    else:
        selected = [secrets.choice(WORDS) for _ in range(word_count)]

    if capitalize_words:
        selected = [word.capitalize() for word in selected]
    return separator.join(selected)


def estimate_entropy_bits(
    *,
    password_length: int | None = None,
    pool_size: int | None = None,
    word_count: int | None = None,
    word_list_size: int = len(WORDS),
    no_repeats: bool = False,
) -> float:
    """Estimate search-space entropy in bits (not a crack-time guarantee)."""
    if word_count is not None:
        count = word_count
        size = word_list_size
    else:
        count = password_length or 0
        size = pool_size or 0

    if count <= 0 or size <= 1:
        return 0.0

    if no_repeats:
        if count > size:
            return 0.0
        return math.fsum(math.log2(size - index) for index in range(count))
    return count * math.log2(size)


def strength_label(entropy_bits: float) -> tuple[str, str]:
    """Return a simple, approximate strength label and explanation."""
    if entropy_bits < 40:
        return "Needs improvement", "Try a longer password or more character types."
    if entropy_bits < 60:
        return "Fair", "Good start. A longer password or passphrase is better."
    if entropy_bits < 80:
        return "Strong", "A strong generated secret. Keep it private."
    return "Very strong", "Excellent estimated search space. Keep it private."
