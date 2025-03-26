# Hyper Personalized Recommendation Generator

This project is a Flask-based application that generates hyper-personalized financial product recommendations for customers. It uses OpenAI's GPT model, customer data, and Twitter sentiment analysis to create text and video-based recommendations.

---

## **Features**
- **Flask Web Interface**: A user-friendly web interface to input customer details and generate recommendations.
- **Command-Line Interface (CLI)**: A CLI mode for generating recommendations directly from the terminal.
- **OpenAI Integration**: Uses OpenAI's GPT model to generate personalized recommendations.
- **Video Generation**: Creates video recommendations using MoviePy and text-to-speech (TTS) technology.
- **Data Security**: Ensures customer data is processed securely with consent verification.
- **Real-Time Logging**: Displays logs and progress updates in real-time using Flask-SocketIO.

---

## **Setup Instructions**

### **1. Prerequisites**
- Python 3.8 or higher
- Required libraries (see below)
- ImageMagick installed on your system ([Download ImageMagick](https://imagemagick.org/script/download.php))

### **2. Install Dependencies**
Install the required Python libraries using `pip`:
pandas, openai, moviepy, pyttsx3, pytubefix, openpyxl, msoffcrypto-tool, flask, flask-socketio, python-dotenv

3. Environment Variables
Create a .env file in the root directory and add the following:

4. Set ImageMagick Path
Update the IMAGEMAGICK_BINARY_PATH variable in main.py with the path to your ImageMagick installation:

Usage
1. Run the Flask Application
Start the Flask server:

The application will open in your default web browser at http://127.0.0.1:5000.

2. Run in CLI Mode
To run the script in CLI mode:

You will be prompted to enter a customer ID.

File Structure

f:\code\aidhp-himalayas
│
├── code
│   ├── src
│   │   ├── main.py                # Main application script
│   │   └── ...
│   ├── test
│       ├── unittest.py            # Unit tests for the application
│       └── ...
├── data                           # Input data files
│   ├── customer_transactions.xlsx
│   ├── customer_profile.xlsx
│   ├── twitter_data.xlsx
│   └── background_music.mp3
├── artifacts                      # Output files
│   ├── output
│   │   ├── recommendations.txt
│   │   ├── recommendations_video.mp4
│   └── temp
│       ├── temp_audio.mp3
│       ├── temp_background_video.mp4
│       └── ...
├── .env                           # Environment variables
├            
└── [README.md]



Testing

Run Unit Tests
Navigate to the test directory and run the tests:
python -m unittest discover -s . -p "*.py"


Test Cases
Flask Application:
   Test GET and POST requests to the web interface.
CLI Mode:
   Test recommendation generation in CLI mode.
Utility Functions:
   Test data loading, user prompt generation, and OpenAI API calls.

Key Components
1. Flask Application
Routes:
   /: Main route for generating recommendations via the web interface.
Static Files:
   Serves generated video files from the artifacts/output directory.

2. Recommendation Generation
Data Loading:
   Loads and decrypts customer data from Excel files.
OpenAI Integration:
   Generates recommendations using OpenAI's GPT model.
Video Generation:
   Creates video recommendations with text overlays and background music.
3. Logging
   Real-time logs are displayed in the web interface using Flask-SocketIO.
Dependencies
   The project uses the following Python libraries:

Flask
Flask-SocketIO
pandas
openai
pyttsx3
moviepy
msoffcrypto
openpyxl
python-dotenv
Install all dependencies using:

Troubleshooting
1. OpenAI API Key Not Set
   Ensure the OPENAI_API_KEY is set in the .env file.

2. ImageMagick Not Found
   Verify the IMAGEMAGICK_BINARY_PATH is correct and points to the installed ImageMagick binary.

3. Missing Data Files
   Ensure the required Excel files are present in the data directory:

customer_transactions.xlsx
customer_profile.xlsx
twitter_data.xlsx

4. Permission Errors
Run the script with appropriate permissions to access files and directories.



