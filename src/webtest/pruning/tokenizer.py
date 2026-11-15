"""Tokenizer: Calculates token count for DOM serialization."""

import re


class DOMTokenizer:
    """Calculates token counts for serialized DOM strings deterministically."""

    # Regex matching word tokens, numbers, punctuation, and whitespace chunks
    TOKEN_PATTERN = re.compile(r"\w+|[^\w\s]|\s+", re.UNICODE)

    @classmethod
    def count_tokens(cls, text: str) -> int:
        """Count tokens in text using subword/word pattern."""
        if not text:
            return 0
        matches = cls.TOKEN_PATTERN.findall(text)
        count = 0
        for token in matches:
            if token.isspace():
                # Sequential whitespaces collapse into 1 token per 4 spaces or newline
                count += max(1, len(token) // 4)
            elif len(token) > 8:
                # Long words / tokens take multiple subwords
                count += (len(token) + 3) // 4
            else:
                count += 1
        return count

