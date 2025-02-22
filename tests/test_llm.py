from unittest.mock import patch

import pytest
import requests

from src.llm import Llm


@pytest.fixture(scope="module")
def mock_llm_instance():  # noqa: D103
    """Return an LLM instance with no underlying connection to the server."""

    def mocked_init(self, model_name, system_message):
        """Similar to Llm.__init__, but without the server connection."""
        self.model_name = model_name
        self.system_message = system_message

    with patch("src.llm.Llm.__init__", new=mocked_init):
        return Llm("dummy_name", system_message=None)


def mock_get_success(_):
    """Mock a successful GET request."""

    class MockResponse:
        status_code = 200

    return MockResponse()


def mock_get_failure(_):
    """Mock a failed GET request."""
    raise requests.exceptions.ConnectionError


def test_is_ollama_running_success(monkeypatch, mock_llm_instance):
    """Test if the OLLAMA server is running."""
    monkeypatch.setattr(requests, "get", mock_get_success)
    assert mock_llm_instance._is_ollama_running()


def test_is_ollama_running_failure(monkeypatch, mock_llm_instance):
    """Test if the OLLAMA server is not running."""
    monkeypatch.setattr(requests, "get", mock_get_failure)
    assert not mock_llm_instance._is_ollama_running()


def test_validate_history_valid():
    """Test _validate_history with valid history."""
    valid_history = ["user message", "assistant message", "user message", "assistant message"]
    try:
        Llm._validate_history(valid_history)
    # fail the test if an error is raised (the history is valid)
    except ValueError:
        pytest.fail("_validate_history raised ValueError unexpectedly!")


def test_validate_history_invalid_type():
    """Test _validate_history with invalid history type."""
    invalid_history = "this is not a list"
    with pytest.raises(ValueError, match="History must be a list of strings."):
        Llm._validate_history(invalid_history)  # type: ignore


def test_validate_history_invalid_elements():
    """Test _validate_history with invalid history elements."""
    invalid_history = ["user message", 123, "user message", "assistant message"]
    with pytest.raises(ValueError, match="History must be a list of strings."):
        Llm._validate_history(invalid_history)


def test_validate_history_odd_length():
    """Test _validate_history with odd number of history elements."""
    invalid_history = ["user message", "assistant message", "user message"]
    with pytest.raises(ValueError, match="History must contain an even number of elements."):
        Llm._validate_history(invalid_history)


@pytest.mark.parametrize("system_message", ["be gentle", "", "answer as if you were a robot"])
def test_prepend_system_message(system_message):
    """Test _prepend_system_message."""
    message = [{"role": "user", "content": "What is the meaning of life?"}]
    output_message = Llm._prepend_system_message(system_message, message)
    # Make sure it's a list of dicts
    assert isinstance(output_message, list) and all(isinstance(msg, dict) for msg in output_message)
    # Make sure the first dict contains an actual system message
    assert output_message[0]["role"] == "system" and output_message[0]["content"] == system_message
