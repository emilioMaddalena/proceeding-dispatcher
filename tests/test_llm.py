import pytest
import requests

from src.llm import Llm


@pytest.fixture(scope="module")
def llm_instance():  # noqa: D103
    return Llm("llama2-uncensored:latest")


def mock_get_success(_):
    """Mock a successful GET request."""

    class MockResponse:
        status_code = 200

    return MockResponse()


def mock_get_failure(_):
    """Mock a failed GET request."""
    raise requests.exceptions.ConnectionError


def test_is_ollama_running_success(monkeypatch, llm_instance):
    """Test if the OLLAMA server is running."""
    monkeypatch.setattr(requests, "get", mock_get_success)
    assert llm_instance._is_ollama_running() is True


def test_is_ollama_running_failure(monkeypatch, llm_instance):
    """Test if the OLLAMA server is not running."""
    monkeypatch.setattr(requests, "get", mock_get_failure)
    assert llm_instance._is_ollama_running() is False


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


# def test_keep_alive(interface):  # noqa: D103
#     result = interface.keep_alive()
#     assert result is not None

# def test_append_context(interface):  # noqa: D10
#     interface.append_context("Test context")
#     assert "Test context" in interface.context

# def test_submit_query(interface):  # noqa: D103
#     response = interface.submit_query("Hello")
#     assert isinstance(response, str)
