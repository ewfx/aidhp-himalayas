# Test Suite for `main.py`

This test suite is designed to validate the functionality of the `main.py` script in the `aidhp-himalayas` project. It uses the `unittest` framework and mocks external dependencies to ensure isolated and reliable tests.

## **Test Cases**

### 1. **Flask Application Tests**
- **`test_index_get`**:
  - Tests the `GET` request to the Flask application.
  - Verifies that the response status code is `200`.
  - Checks if the response contains the text `Hyper Personalized Recommendation Generator`.

- **`test_index_post`**:
  - Tests the `POST` request to the Flask application.
  - Mocks the `generate_recommendations` and `generate_video_with_moviepy` functions.
  - Verifies that the response status code is `200`.
  - Ensures the mocked functions are called.

### 2. **CLI Mode Test**
- **`test_cli_mode`**:
  - Simulates running the script in CLI mode using `sys.argv`.
  - Mocks the `input` function to provide a customer ID.
  - Mocks the `generate_recommendations` and `generate_video_with_moviepy` functions.
  - Verifies that the mocked functions are called.
  - Expects a `SystemExit` due to `sys.exit(1)`.

### 3. **Utility Function Tests**
- **`test_load_data`**:
  - Mocks the decryption and data loading process using `msoffcrypto.OfficeFile` and `pandas.read_excel`.
  - Verifies that the `load_data` function returns non-`None` data.

- **`test_generate_user_prompt`**:
  - Tests the `generate_user_prompt` function with mock data.
  - Verifies that the generated prompt contains expected customer details.

## **How to Run the Tests**

## Run test using this command
python -m unittest discover -s . -p "*.py"