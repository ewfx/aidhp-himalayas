import unittest
from unittest.mock import patch, MagicMock, mock_open
import sys
from code.src.main import app, generate_user_prompt, load_data
from code.src.main import generate_all_recommendations_and_video

# filepath: f:\code\aidhp-himalayas\code\src\test_main.py

class TestMain(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("code.src.main.generate_recommendations")
    @patch("code.src.main.generate_video_with_moviepy")
    def test_index_get(self, mock_generate_video, mock_generate_recommendations):
        response = self.app.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hyper Personalized Recommendation Generator", response.data)

    @patch("code.src.main.generate_recommendations")
    @patch("code.src.main.generate_video_with_moviepy")
    def test_index_post(self, mock_generate_video, mock_generate_recommendations):
        mock_generate_recommendations.return_value = ["Test Recommendation"]
        response = self.app.post("/", data={
            "prompt": "Test Prompt",
            "customer_id": "12345",
            "categories": ["Consumer and Small Business Banking"]
        })
        self.assertEqual(response.status_code, 200)
        mock_generate_recommendations.assert_called_once()
        mock_generate_video.assert_called_once()

    @patch("code.src.main.generate_recommendations")
    @patch("code.src.main.generate_video_with_moviepy")
    @patch("builtins.input", return_value="12345")
    @patch("sys.argv", ["main.py", "--cli"])
    def test_cli_mode(self, mock_argv, mock_input, mock_generate_video, mock_generate_recommendations):
        mock_generate_recommendations.return_value = ["Test Recommendation"]
        with self.assertRaises(SystemExit):  # Expecting sys.exit(1)
            generate_all_recommendations_and_video()
        mock_generate_recommendations.assert_called_once()
        mock_generate_video.assert_called_once()

    @patch("code.src.main.pd.read_excel")
    @patch("code.src.main.msoffcrypto.OfficeFile")
    def test_load_data(self, mock_office_file, mock_read_excel):
        mock_office_file.return_value.decrypt = MagicMock()
        mock_read_excel.return_value = MagicMock()
        data = load_data("transactions.xlsx", "profile.xlsx", "twitter.xlsx", "12345")
        self.assertIsNotNone(data)

    def test_generate_user_prompt(self):
        mock_data = {
            "customer id": ["12345"],
            "consent": [True],
            "first name": ["John"],
            "category": ["Shopping"],
            "sentiment": ["Positive"],
            "tweet": ["Great service!"]
        }
        prompt = generate_user_prompt("12345", mock_data)
        self.assertIn("John", prompt)
        self.assertIn("Shopping", prompt)

if __name__ == "__main__":
    unittest.main()