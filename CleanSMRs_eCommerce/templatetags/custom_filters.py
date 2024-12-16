"""Definitions for custom filters used in templates on the website."""

import re

from django import template

register = template.Library()


@register.filter
def get_first_sentence(value):
    """Gets the first sentence from a block of text.

    Args:
        value (str): The text to extract the first sentence from.

    Returns:
        str: The first sentence of the text.
    """

    # Use a regular expression to match the first sentence.
    match = re.match(r"([^.]*\.)", value)
    return match.group(0) if match else value
