"""Basic automated checks for the password engine. Run: python -m unittest"""

import unittest

from password_engine import (
    AMBIGUOUS,
    WORDS,
    build_character_sets,
    generate_password,
    generate_passphrase,
    estimate_entropy_bits,
)


class PasswordEngineTests(unittest.TestCase):
    def test_password_length_and_character_types(self):
        password = generate_password(24)
        self.assertEqual(len(password), 24)
        self.assertTrue(any(ch.isupper() for ch in password))
        self.assertTrue(any(ch.islower() for ch in password))
        self.assertTrue(any(ch.isdigit() for ch in password))
        self.assertTrue(any(ch in "!@#$%^&*()-_=+[]{};:,.?" for ch in password))

    def test_exclude_ambiguous(self):
        password = generate_password(64, exclude_ambiguous=True)
        self.assertTrue(set(password).isdisjoint(AMBIGUOUS))

    def test_no_repeats(self):
        password = generate_password(30, no_repeats=True)
        self.assertEqual(len(password), len(set(password)))

    def test_no_repeats_capacity_error(self):
        with self.assertRaises(ValueError):
            generate_password(100, use_uppercase=False, use_lowercase=False,
                              use_digits=True, use_symbols=False, no_repeats=True)

    def test_require_at_least_one_type(self):
        with self.assertRaises(ValueError):
            generate_password(16, use_uppercase=False, use_lowercase=False,
                              use_digits=False, use_symbols=False)

    def test_passphrase_word_count_and_no_duplicates(self):
        phrase = generate_passphrase(6, no_repeated_words=True)
        words = phrase.split("-")
        self.assertEqual(len(words), 6)
        self.assertEqual(len(words), len(set(words)))
        self.assertTrue(set(words).issubset(set(WORDS)))

    def test_entropy_is_positive(self):
        self.assertGreater(estimate_entropy_bits(password_length=20, pool_size=90), 0)
        self.assertGreater(estimate_entropy_bits(word_count=6), 0)


if __name__ == "__main__":
    unittest.main()
