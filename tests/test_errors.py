from selfbot.errors import (
    AppError,
    AppTimeoutError,
    DependencyError,
    ValidationError,
    classify_error,
)


def test_known_error_is_preserved():
    error = ValidationError("bad input")

    classified = classify_error(error)

    assert classified is error
    assert classified.code == "validation"
    assert classified.retryable is False


def test_dependency_error_is_retryable():
    error = DependencyError("provider unavailable")

    assert error.code == "dependency_failure"
    assert error.retryable is True


def test_unknown_error_is_safe():
    classified = classify_error(RuntimeError("secret internal detail"))

    assert isinstance(classified, AppError)
    assert classified.code == "internal"
    assert classified.message == "Unexpected internal error"


def test_timeout_is_retryable():
    assert AppTimeoutError().retryable is True
