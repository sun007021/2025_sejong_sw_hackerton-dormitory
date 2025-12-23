"""Matching-related exceptions."""


class MatchingException(Exception):
    """Base exception for matching-related errors."""
    pass


class InsufficientStudentsException(MatchingException):
    """Raised when there are not enough students to perform matching."""
    pass


class MatchingAlreadyExistsException(MatchingException):
    """Raised when attempting to match students that are already matched."""
    pass


class NoUnmatchedStudentsException(MatchingException):
    """Raised when there are no unmatched students available for matching."""
    pass