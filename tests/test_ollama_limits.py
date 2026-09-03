import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from spanish_rewriter.ollama_client import OllamaClient, OllamaError


class OllamaLimitTests(unittest.TestCase):
    def test_oversized_utf8_prompt_is_rejected_before_network_io(self) -> None:
        client = OllamaClient()
        client._request = Mock()
        with self.assertRaises(OllamaError):
            client.generate_json(model="local", prompt="á" * 6001, schema={}, num_predict=2048)
        client._request.assert_not_called()

    def test_length_limited_json_is_rejected(self) -> None:
        client = OllamaClient()
        client._request = Mock(return_value={"response": "{}", "done_reason": "length"})
        with self.assertRaises(OllamaError):
            client.generate_json(model="local", prompt="Texto.", schema={}, num_predict=2048)


if __name__ == "__main__":
    unittest.main()
