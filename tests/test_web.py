import pytest
from selfbot.errors import ValidationError
from selfbot.web import _validate_url
def test_web_blocks_non_https_and_private():
    with pytest.raises(ValidationError): _validate_url("http://example.com")
    with pytest.raises(ValidationError): _validate_url("https://127.0.0.1")
