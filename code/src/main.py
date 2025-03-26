import pandas as pd
import openai
import os
import sys
import webbrowser
from pathlib import Path
import logging
import pyttsx3
from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, VideoFileClip, concatenate_videoclips, CompositeAudioClip
from moviepy.config import change_settings
import textwrap
from pytubefix import YouTube
from dotenv import load_dotenv
import openpyxl
from io import BytesIO
import msoffcrypto
import time
from flask import Flask, request, render_template_string
from flask_socketio import SocketIO, emit

# Initialize Flask app and SocketIO
app = Flask(__name__)
socketio = SocketIO(app)

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

class SocketIOHandler(logging.Handler):
    def emit(self, record):
        if record.levelno == logging.INFO or record.levelno >= logging.ERROR:
            log_message = self.format(record).split(' - ')[-1]
            socketio.emit('log', {'message': log_message})

socketio_handler = SocketIOHandler()
logger.addHandler(socketio_handler)

# Load environment variables
load_dotenv()
openai_key = os.getenv('OPENAI_API_KEY')
excel_password = os.getenv('EXCEL_PASSWORD')
logger.info(f"Current working directory: {os.getcwd()}")
logger.info(f"Loaded OPENAI_API_KEY: {'Set' if openai_key else 'Not Set'}")
logger.info(f"Loaded EXCEL_PASSWORD: {'Set' if excel_password else 'Not Set'}")

# Securely load API keys and password
openai.api_key = os.getenv('OPENAI_API_KEY', openai_key)
EXCEL_PASSWORD = os.getenv('EXCEL_PASSWORD', excel_password)
logger.info(f"Final openai.api_key: {'Set' if openai.api_key else 'Not Set'}")
logger.info(f"Final EXCEL_PASSWORD: {'Set' if EXCEL_PASSWORD else 'Not Set'}")

# Set ImageMagick path
IMAGEMAGICK_BINARY_PATH = r"C:\Program Files\ImageMagick-7.1.1-Q16-HDRI\magick.exe"
change_settings({"IMAGEMAGICK_BINARY": IMAGEMAGICK_BINARY_PATH})

# Define base directory (assuming script is in code\src)
BASE_DIR = Path(__file__).resolve().parent.parent  # Moves up from code\src to code

# File paths relative to BASE_DIR
INPUT_FILE_TRANSACTIONS = BASE_DIR / 'data' / 'customer_transactions.xlsx'
INPUT_FILE_PROFILE = BASE_DIR / 'data' / 'customer_profile.xlsx'
INPUT_FILE_TWITTER = BASE_DIR / 'data' / 'twitter_data.xlsx'
OUTPUT_FILE = BASE_DIR / 'artifacts' / 'output' / 'recommendations.txt'
VIDEO_OUTPUT_FILE = BASE_DIR / 'artifacts' / 'output' / 'recommendations_video.mp4'
TEMP_AUDIO_FILE = BASE_DIR / 'artifacts' / 'temp' / 'temp_audio.mp3'
TEMP_VIDEO_FILE = BASE_DIR / 'artifacts' / 'temp' / 'temp_background_video.mp4'
YOUTUBE_URL = "https://www.youtube.com/watch?v=PuR_hbA38oI"
BACKGROUND_MUSIC_FILE = BASE_DIR / 'data' / 'background_music.mp3'

# Ensure output and temp directories exist
os.makedirs(OUTPUT_FILE.parent, exist_ok=True)
os.makedirs(TEMP_AUDIO_FILE.parent, exist_ok=True)

# Default system prompt (moved to global scope for consistency)
DEFAULT_SYSTEM_PROMPT = """You are a Wells Fargo bank financial advisor for the customers. Design the top three dynamic banking products and services recommendations specific to "check_box_selection" category based on customer demographic data, transaction categories, profile, income, expenditure, loan values, profession, and other provided values, along with Twitter sentiment from the provided data. Generate the recommendation as if you are speaking directly to the customer in a powerful, engaging speech to make them interested in buying the products. Follow this exact format:

Start with: Hello [Customer Name], This message is from your Investment Advisor [Investment Advisor]
Wellsfargo would like to recommend you few products
Then list exactly three product recommendations.

Use complete product names as offered on www.wellsfargo.com. Do not include the customer ID or transaction amounts in the recommendation. Ensure each recommendation is concise and complete, fitting all three within a total of 220 words maximum. Do not truncate the third recommendation; adjust brevity earlier if needed. Do not use any special characters like # or * in the output."""

# HTML Template (unchanged)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hyper Personalized Recommendation Generator</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.5.1/socket.io.js"></script>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #fff;
            color: #333;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 30px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            min-height: 80vh;
            display: flex;
            flex-direction: column;
        }
        header {
            text-align: center;
            margin-bottom: 30px;
            background-color: #B5121B;
            color: white;
            padding: 20px;
            border-radius: 8px 8px 0 0;
        }
        h1 {
            margin: 0;
            font-size: 32px;
        }
        h2 {
            font-size: 18px;
            font-weight: normal;
            margin: 10px 0 0;
        }
        .form-section {
            width: 80%;
            margin: 0 auto 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            font-weight: bold;
            color: #B5121B;
        }
        textarea {
            width: 100%;
            height: 200px;
            padding: 12px;
            border: 1px solid #B5121B;
            border-radius: 4px;
            resize: vertical;
            box-sizing: border-box;
            font-size: 14px;
        }
        .input-group {
            display: flex;
            gap: 20px;
            align-items: flex-start;
        }
        .customer-id-section {
            flex: 1;
        }
        input[type="text"] {
            width: 100%;
            padding: 12px;
            border: 1px solid #B5121B;
            border-radius: 4px;
            box-sizing: border-box;
            font-size: 14px;
        }
        .checkbox-section {
            margin: 20px auto;
            width: 80%;
            display: flex;
            flex-direction: column;
            gap: 12px;
        }
        .checkbox-item {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .checkbox-item input[type="checkbox"] {
            margin: 0;
            accent-color: #B5121B;
        }
        .checkbox-item label {
            margin: 0;
            font-weight: normal;
            color: #333;
        }
        .button-section {
            text-align: center;
            margin: 20px 0;
        }
        button {
            background-color: #B5121B;
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #9B0F15;
        }
        .status {
            text-align: center;
            margin: 20px 0;
        }
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #B5121B;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            animation: spin 1s linear infinite;
            display: inline-block;
            margin-right: 10px;
            vertical-align: middle;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .hidden {
            display: none;
        }
        .status-text {
            vertical-align: middle;
            color: #B5121B;
        }
        .result, .video-link {
            width: 80%;
            margin: 20px auto;
            padding: 15px;
            border: 1px solid #B5121B;
            border-radius: 4px;
            background-color: #fff;
            box-shadow: 0 1px 5px rgba(0,0,0,0.05);
        }
        .result h2 {
            color: #B5121B;
            margin-top: 0;
        }
        .result p {
            margin: 10px 0;
            white-space: pre-wrap;
            line-height: 1.6;
        }
        .video-link h2 {
            color: #B5121B;
        }
        .video-link a {
            color: #B5121B;
            text-decoration: none;
        }
        .video-link a:hover {
            text-decoration: underline;
        }
        .log-output {
            width: 80%;
            margin: 20px auto 0;
            padding: 15px;
            border: 1px solid #B5121B;
            border-radius: 4px;
            background-color: #fff;
            font-size: 14px;
            flex-grow: 1;
            color: #333;
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', () => {
            const socket = io.connect('http://' + document.domain + ':' + location.port);
            socket.on('log', (data) => { document.getElementById('log-output').innerText = data.message; });
            socket.on('recommendation', (data) => {
                const resultDiv = document.getElementById('result');
                if (!resultDiv.innerHTML) { resultDiv.innerHTML = '<h2>Recommendations:</h2>'; }
                resultDiv.innerHTML += '<p>' + data.content + '</p>';
            });
            socket.on('recommendations_complete', (data) => {
                document.getElementById('recommendation-spinner').classList.add('hidden');
                document.getElementById('recommendation-text').classList.add('hidden');
                document.getElementById('video-spinner').classList.remove('hidden');
                document.getElementById('video-text').classList.remove('hidden');
                const recommendations = data.content.split('\\n\\n');
                let formattedContent = '<h2>Recommendations:</h2>';
                recommendations.forEach(rec => {
                    if (rec.trim()) { formattedContent += '<p>' + rec.trim() + '</p>'; }
                });
                document.getElementById('result').innerHTML = formattedContent;
            });
            socket.on('video_link', (data) => {
                document.getElementById('video-spinner').classList.add('hidden');
                document.getElementById('video-text').classList.add('hidden');
                if (data.link) {
                    document.getElementById('video-link').innerHTML = '<h2>Video Recommendation:</h2><a href="' + data.link + '" target="_blank">Watch the Recommendation Video</a>';
                } else {
                    document.getElementById('video-link').innerHTML = 'No video generated.';
                }
            });
            function clearAndGenerate() {
                document.getElementById('result').innerHTML = '';
                document.getElementById('video-link').innerHTML = '';
                document.getElementById('log-output').innerText = '';
                document.getElementById('recommendation-spinner').classList.remove('hidden');
                document.getElementById('recommendation-text').classList.remove('hidden');
                document.getElementById('video-spinner').classList.add('hidden');
                document.getElementById('video-text').classList.add('hidden');
                fetch('/', {
                    method: 'POST',
                    body: new FormData(document.getElementById('recommendation-form')),
                    headers: { 'Accept': 'application/json' }
                }).catch(error => {
                    console.error('Error:', error);
                    document.getElementById('recommendation-spinner').classList.add('hidden');
                    document.getElementById('recommendation-text').classList.add('hidden');
                    document.getElementById('video-spinner').classList.add('hidden');
                    document.getElementById('video-text').classList.add('hidden');
                    document.getElementById('result').innerHTML = '<h2>Recommendations:</h2><p>Error generating recommendations.</p>';
                });
                return false;
            }
            document.getElementById('recommendation-form').onsubmit = clearAndGenerate;
        });
    </script>
</head>
<body>
    <div class="container">
        <header>
            <h1>Hyper Personalized Recommendation Generator</h1>
            <h2>Wells Fargo offers a wide range of product categories to cater to its customers' financial needs. Please enter Customer ID, select Product categories below, and review prompt box and Generate Recommendation for Text and Video baed Recommendations.</h2>
        </header>
        <form id="recommendation-form">
            <div class="form-section">
                <div class="input-group">
                    <div style="flex: 2;">
                        <label for="prompt">Open AI System Prompt:</label>
                        <textarea id="prompt" name="prompt">{{ prompt }}</textarea>
                    </div>
                    <div class="customer-id-section">
                        <label for="customer_id">Customer ID:</label>
                        <input type="text" id="customer_id" name="customer_id" placeholder="Enter Customer ID" required>
                    </div>
                </div>
            </div>
            <div class="checkbox-section">
                <div class="checkbox-item">
                    <input type="checkbox" id="consumerSmallBusiness" name="categories" value="Consumer and Small Business Banking">
                    <label for="consumerSmallBusiness">Consumer and Small Business Banking</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="consumerLending" name="categories" value="Consumer Lending">
                    <label for="consumerLending">Consumer Lending</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="corporateInvestment" name="categories" value="Corporate and Investment Banking">
                    <label for="corporateInvestment">Corporate and Investment Banking</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="wealthManagement" name="categories" value="Wealth and Investment Management">
                    <label for="wealthManagement">Wealth and Investment Management</label>
                </div>
                <div class="checkbox-item">
                    <input type="checkbox" id="commercialBanking" name="categories" value="Commercial Banking">
                    <label for="commercialBanking">Commercial Banking</label>
                </div>
            </div>
            <div class="button-section">
                <button type="submit">Generate</button>
            </div>
        </form>
        <div class="status">
            <div id="recommendation-spinner" class="spinner hidden"></div>
            <span id="recommendation-text" class="status-text hidden">Generating Personalized Recommendations</span>
            <div id="video-spinner" class="spinner hidden"></div>
            <span id="video-text" class="status-text hidden">Generating Recommendations Video</span>
        </div>
        <div id="result" class="result">
            {% if result %}
            <h2>Recommendations:</h2>
            {% for line in result.split('\n\n') if line.strip() %}
            <p>{{ line.strip() }}</p>
            {% endfor %}
            {% endif %}
        </div>
        <div id="video-link" class="video-link">
            {% if video_link %}
            <h2>Video Recommendation:</h2>
            <a href="{{ video_link }}" target="_blank">Watch the Recommendation Video</a>
            {% endif %}
        </div>
        <div class="log-output" id="log-output"></div>
    </div>
</body>
</html>
"""

# Flask Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_prompt = request.form.get('prompt', DEFAULT_SYSTEM_PROMPT)
        customer_id = request.form.get('customer_id').strip()
        selected_categories = request.form.getlist('categories')
        
        if not selected_categories:
            logger.info("No categories selected, defaulting to 'Consumer and Small Business Banking'")
            categories_str = "Consumer and Small Business Banking"
            socketio.emit('log', {'message': "No categories selected, proceeding with default 'Consumer and Small Business Banking'"})
        else:
            categories_str = ", ".join(selected_categories)
        
        system_prompt = user_prompt.replace("check_box_selection", categories_str)
        logger.info(f"System prompt used: {system_prompt}")
        logger.info(f"Generating for Customer ID: {customer_id}")
        
        # Generate recommendations and video sequentially
        recommendations = generate_recommendations(system_prompt, customer_id)
        if recommendations and "Error" not in recommendations[0]:
            generate_video_with_moviepy(recommendations[0])
        return render_template_string(HTML_TEMPLATE, prompt=system_prompt, result=None, video_link=None)
    
    return render_template_string(HTML_TEMPLATE, prompt=DEFAULT_SYSTEM_PROMPT, result=None, video_link=None)

# Serve static files (adjusted to artifacts/output for video serving)
app.static_folder = str(BASE_DIR / 'artifacts' / 'output')  # Convert Path to string
app.static_url_path = '/static'

def check_prerequisites():
    logger.info("Checking prerequisites...")
    for module, name in [(openai, "OpenAI"), (pyttsx3, "pyttsx3"), (TextClip, "MoviePy"), (YouTube, "pytubefix"), (openpyxl, "openpyxl"), (msoffcrypto, "msoffcrypto")]:
        if not module:
            logger.error(f"{name} library is not installed.")
            raise ImportError(f"{name} library is not installed.")
    if not openai.api_key or not EXCEL_PASSWORD:
        logger.error("API key or Excel password are not set.")
        raise ValueError("API key or Excel password are not set.")
    if not os.path.exists(IMAGEMAGICK_BINARY_PATH):
        logger.error(f"ImageMagick binary not found at {IMAGEMAGICK_BINARY_PATH}.")
        raise FileNotFoundError("ImageMagick binary not found.")
    if not os.path.exists(str(BACKGROUND_MUSIC_FILE)):  # Convert Path to string
        logger.error(f"Background music file not found at {BACKGROUND_MUSIC_FILE}.")
        raise FileNotFoundError("Background music file not found.")
    logger.info("All prerequisites are met.")

def load_data(transactions_file_path, profile_file_path, twitter_file_path, customer_id):
    transactions_file_path = str(transactions_file_path)  # Convert Path to string
    profile_file_path = str(profile_file_path)  # Convert Path to string
    twitter_file_path = str(twitter_file_path)  # Convert Path to string
    
    logger.info(f"Loading data from {transactions_file_path} for Customer ID: {customer_id}...")
    if not Path(transactions_file_path).is_file():
        logger.error(f"Input file {transactions_file_path} not found!")
        raise FileNotFoundError(f"Input file {transactions_file_path} not found!")
    
    try:
        with open(transactions_file_path, 'rb') as f:
            encrypted_file = msoffcrypto.OfficeFile(f)
            encrypted_file.load_key(password=EXCEL_PASSWORD)
            decrypted_stream = BytesIO()
            encrypted_file.decrypt(decrypted_stream)
            decrypted_stream.seek(0)
        
        transactions_data = pd.read_excel(decrypted_stream)
        transactions_data.columns = transactions_data.columns.str.strip().str.lower()
        logger.info(f"Transactions data columns: {transactions_data.columns.tolist()}")
        logger.info(f"Unique Customer IDs in transactions: {transactions_data['customer id'].unique().tolist()}")
        
        if 'customer id' not in transactions_data.columns or transactions_data['customer id'].isnull().any():
            logger.error("Transactions file must contain non-null 'Customer ID' column.")
            raise ValueError("Invalid 'Customer ID' data in transactions file.")
        
        transactions_data['customer id'] = transactions_data['customer id'].astype(str).str.strip()
        transactions_data = transactions_data[transactions_data['customer id'] == customer_id]
        if transactions_data.empty:
            logger.warning(f"No transactions found for Customer ID {customer_id}")
        
        if 'consent' not in transactions_data.columns or (not transactions_data.empty and (transactions_data['consent'].isnull().any() or not transactions_data['consent'].all())):
            logger.error("All customers in transactions file must have provided explicit consent.")
            raise ValueError("Missing or invalid consent in transactions file.")
        
        if 'consent_social_media' not in transactions_data.columns:
            transactions_data['consent_social_media'] = False
        
        logger.info("Transactions data loaded successfully.")
    
    except Exception as e:
        logger.error(f"Failed to read transactions Excel file: {e}")
        raise
    
    logger.info(f"Loading data from {profile_file_path} for Customer ID: {customer_id}...")
    if not Path(profile_file_path).is_file():
        logger.error(f"Input file {profile_file_path} not found!")
        raise FileNotFoundError(f"Input file {profile_file_path} not found!")
    
    try:
        with open(profile_file_path, 'rb') as f:
            encrypted_file = msoffcrypto.OfficeFile(f)
            encrypted_file.load_key(password=EXCEL_PASSWORD)
            decrypted_stream = BytesIO()
            encrypted_file.decrypt(decrypted_stream)
            decrypted_stream.seek(0)
        
        profile_data = pd.read_excel(decrypted_stream)
        profile_data.columns = profile_data.columns.str.strip().str.lower()
        logger.info(f"Profile data columns: {profile_data.columns.tolist()}")
        logger.info(f"Unique Customer IDs in profile: {profile_data['customer id'].unique().tolist()}")
        
        if 'customer id' not in profile_data.columns:
            logger.error("Profile file must contain 'Customer ID' column.")
            raise ValueError("Profile file must contain 'Customer ID' column.")
        
        profile_data['customer id'] = profile_data['customer id'].astype(str).str.strip()
        profile_data = profile_data[profile_data['customer id'] == customer_id]
        logger.info("Profile data loaded successfully.")
    
    except Exception as e:
        logger.error(f"Failed to read profile Excel file: {e}")
        raise
    
    logger.info(f"Loading data from {twitter_file_path} for Customer ID: {customer_id}...")
    if not Path(twitter_file_path).is_file():
        logger.error(f"Input file {twitter_file_path} not found!")
        raise FileNotFoundError(f"Input file {twitter_file_path} not found!")
    
    try:
        with open(twitter_file_path, 'rb') as f:
            encrypted_file = msoffcrypto.OfficeFile(f)
            encrypted_file.load_key(password=EXCEL_PASSWORD)
            decrypted_stream = BytesIO()
            encrypted_file.decrypt(decrypted_stream)
            decrypted_stream.seek(0)
        
        twitter_data = pd.read_excel(decrypted_stream)
        twitter_data.columns = twitter_data.columns.str.strip().str.lower()
        logger.info(f"Twitter data columns: {twitter_data.columns.tolist()}")
        logger.info(f"Unique Customer IDs in twitter: {twitter_data['customer id'].unique().tolist()}")
        
        if 'customer id' not in twitter_data.columns:
            logger.error("Twitter file must contain 'Customer ID' column.")
            raise ValueError("Twitter file must contain 'Customer ID' column.")
        
        twitter_data['customer id'] = twitter_data['customer id'].astype(str).str.strip()
        twitter_data = twitter_data[twitter_data['customer id'] == customer_id]
        logger.info("Twitter data loaded successfully.")
    
    except Exception as e:
        logger.error(f"Failed to read twitter Excel file: {e}")
        raise
    
    combined_data = pd.merge(transactions_data, profile_data, on='customer id', how='left', suffixes=('_trans', '_profile'))
    combined_data = pd.merge(combined_data, twitter_data, on='customer id', how='left')
    logger.info(f"Combined data columns after merge: {combined_data.columns.tolist()}")
    if not combined_data.empty:
        logger.info(f"Data for Customer ID {customer_id} after merge: {combined_data.to_dict(orient='records')}")
    else:
        logger.info(f"No combined data for Customer ID {customer_id}")
    
    return combined_data

def generate_user_prompt(customer_id, data):
    customer_data = data[data['customer id'] == customer_id]
    if customer_data.empty:
        logger.info(f"No data found for Customer ID {customer_id}")
        return f"No data found for Customer ID {customer_id}"
    if not customer_data['consent'].iloc[0]:
        logger.info(f"Skipping {customer_id} due to lack of consent.")
        return f"Skipping {customer_id} due to lack of consent."
    
    first_name = None
    possible_first_name_columns = ['first name_trans', 'first name_profile', 'first name']
    
    for col in possible_first_name_columns:
        if col in customer_data.columns:
            first_name_value = customer_data[col].iloc[0]
            if pd.notna(first_name_value) and str(first_name_value).strip():
                first_name = first_name_value
                logger.info(f"Customer ID {customer_id}: Using '{col}' = {first_name}")
                break
    
    if first_name is None:
        logger.warning(f"Customer ID {customer_id}: No 'first name' found, using 'Customer'.")
        first_name = "Customer"
    
    transaction_summary = ', '.join(f"{row['category']}" for _, row in customer_data[['category']].tail(5).iterrows()) or "no recent transactions"
    sentiment_summary = "Twitter sentiment: " + (f"{customer_data['sentiment'].iloc[0]} based on tweet: {customer_data['tweet'].iloc[0]}" if pd.notna(customer_data['sentiment'].iloc[0]) and customer_data['consent_social_media'].iloc[0] else "not available or not consented")
    
    customer_info = customer_data.to_dict(orient='records')[0]
    customer_info_str = ", ".join(f"{key}: {value}" for key, value in customer_info.items() if key not in ['customer id', 'transaction amount'])
    
    prompt = (
        f"Generate a recommendation for {first_name} based on the following consented data:\n"
        f"Recent transaction categories: {transaction_summary}. {sentiment_summary}\n"
        f"Customer details: {customer_info_str}"
    )
    logger.info(f"Generated user prompt for {customer_id}: {prompt}")
    return prompt

def get_recommendation(system_prompt, user_prompt):
    if "Skipping" in user_prompt or "No data found" in user_prompt:
        return user_prompt
    logger.info("Calling OpenAI API with consented data...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=250,
            temperature=0.7
        )
        recommendation = response.choices[0].message.content.strip()
        word_count = len(recommendation.split())
        logger.info(f"Recommendation generated successfully with {word_count} words: {recommendation}")
        socketio.emit('recommendation', {'content': recommendation})
        return recommendation
    except Exception as e:
        logger.error(f"Error calling OpenAI API: {e}")
        socketio.emit('recommendation', {'content': "Unable to generate recommendation due to an API error. Visit wellsfargo.com."})
        return "Unable to generate recommendation due to an API error. Visit wellsfargo.com."

def download_youtube_video(youtube_url, output_path):
    output_path = Path(output_path)  # Ensure it's a Path object
    output_dir = output_path.parent  # Directory: artifacts/temp
    filename = output_path.name  # Filename: temp_background_video.mp4
    full_path = str(output_path)  # Full path: F:\code\aidhp-himalayas\artifacts\temp\temp_background_video.mp4
    
    logger.info(f"Downloading YouTube video from {youtube_url} to {full_path}...")
    original_dir = os.getcwd()  # Save current working directory
    
    try:
        # Ensure the directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Change to the target directory
        os.chdir(str(output_dir))
        logger.info(f"Changed working directory to: {os.getcwd()}")
        
        yt = YouTube(youtube_url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        if not stream:
            raise Exception("No suitable video stream found.")
        
        # Download to the current directory (artifacts/temp)
        stream.download(filename=filename)
        
        # Verify the file exists
        if not os.path.exists(full_path):
            # Check if it was downloaded to the base directory
            base_file = str(BASE_DIR / filename)
            if os.path.exists(base_file):
                logger.warning(f"File was downloaded to base directory: {base_file}. Moving to {full_path}")
                os.rename(base_file, full_path)
            else:
                raise FileNotFoundError(f"File was not downloaded to {full_path} or base directory")
        
        file_size = os.path.getsize(full_path)
        if file_size < 1024:
            logger.warning(f"Downloaded file {full_path} is unusually small ({file_size} bytes), may be incomplete.")
        logger.info(f"Video downloaded to {full_path}, size: {file_size} bytes")
    
    except Exception as e:
        logger.error(f"Error downloading YouTube video: {e}")
        raise
    finally:
        # Restore original working directory
        os.chdir(original_dir)
        logger.info(f"Restored working directory to: {os.getcwd()}")

def generate_video_with_moviepy(recommendation_text):
    logger.info("Generating video with recommendation text...")
    check_prerequisites()
    
    # Use the provided recommendation text directly
    recommendations_text = recommendation_text.strip()
    logger.info(f"Video content to be narrated: {recommendations_text}")
    
    # Generate audio
    engine = pyttsx3.init()
    engine.setProperty('rate', 140)
    engine.save_to_file(recommendations_text, str(TEMP_AUDIO_FILE))  # Convert Path to string
    engine.runAndWait()
    
    narration_audio = AudioFileClip(str(TEMP_AUDIO_FILE))  # Convert Path to string
    audio_duration = narration_audio.duration
    logger.info(f"Audio duration: {audio_duration} seconds")
    
    # Generate text clips
    sentences = recommendations_text.split('. ')
    text_clips = []
    current_time = 0
    for sentence in sentences:
        wrapped_lines = textwrap.wrap(sentence, width=50)
        for i in range(0, len(wrapped_lines), 2):
            two_lines = "\n".join(wrapped_lines[i:i+2])
            chunk_duration = audio_duration / len(recommendations_text.split()) * len(two_lines.split())
            text_clip = TextClip(two_lines, fontsize=30, color='red', font='Arial-Bold', size=(1280, 70), method='caption', align='center').set_position(('center', 360)).set_duration(chunk_duration).set_start(current_time)
            text_clips.append(text_clip)
            current_time += chunk_duration
    
    watermark = TextClip(
        "This video uses only consented customer data",
        fontsize=20,
        color='white',
        font='Arial',
        bg_color='black',
        size=(1280, 50),
        method='caption',
        align='center'
    ).set_position(('center', 670)).set_duration(audio_duration)
    
    # Download and prepare background video
    download_youtube_video(YOUTUBE_URL, TEMP_VIDEO_FILE)
    background_base = VideoFileClip(str(TEMP_VIDEO_FILE)).without_audio().resize((1280, 720))  # Convert Path to string
    background = concatenate_videoclips([background_base] * (int(audio_duration // background_base.duration) + 1)).subclip(0, audio_duration)
    
    # Add background music
    background_music = AudioFileClip(str(BACKGROUND_MUSIC_FILE)).subclip(0, audio_duration).volumex(0.15)  # Convert Path to string
    final_audio = CompositeAudioClip([narration_audio, background_music])
    
    # Create and save video
    video = CompositeVideoClip([background] + text_clips + [watermark], size=(1280, 720)).set_duration(audio_duration).set_audio(final_audio)
    video.write_videofile(str(VIDEO_OUTPUT_FILE), fps=24, codec='libx264', audio_codec='aac')  # Convert Path to string
    
    # Clean up resources
    narration_audio.close()
    background_base.close()
    background.close()
    background_music.close()
    video.close()
    for clip in text_clips:
        clip.close()
    watermark.close()
    
    # Extended cleanup to handle misplaced file
    temp_files = [TEMP_AUDIO_FILE, TEMP_VIDEO_FILE, BASE_DIR / 'temp_background_video.mp4']
    for temp_file in temp_files:
        temp_file_str = str(temp_file)
        retries = 5
        while retries > 0:
            try:
                if os.path.exists(temp_file_str):
                    os.remove(temp_file_str)
                    logger.info(f"Deleted temporary file: {temp_file_str}")
                break
            except PermissionError as e:
                logger.warning(f"Failed to delete {temp_file_str}: {e}. Retrying in 1 second...")
                time.sleep(1)
                retries -= 1
            except Exception as e:
                logger.error(f"Error deleting {temp_file_str}: {e}")
                raise
        if retries == 0:
            logger.warning(f"Could not delete {temp_file_str} after retries. File may still be in use.")
    
    logger.info(f"Video generated and saved as {VIDEO_OUTPUT_FILE}")
    socketio.emit('video_link', {'link': f"/static/recommendations_video.mp4" if os.path.exists(str(VIDEO_OUTPUT_FILE)) else None})  # Convert Path to string

def generate_recommendations(system_prompt, customer_id):
    logger.info(f"Starting recommendation generation for Customer ID: {customer_id}...")
    try:
        check_prerequisites()
        data = load_data(INPUT_FILE_TRANSACTIONS, INPUT_FILE_PROFILE, INPUT_FILE_TWITTER, customer_id)
        data['consent_social_media'] = data['consent_social_media'].astype(bool).fillna(False)
        
        recommendations = []
        logger.info(f"Processing Customer ID: {customer_id}")
        user_prompt = generate_user_prompt(customer_id, data)
        recommendation = get_recommendation(system_prompt, user_prompt)
        recommendations.append(recommendation.strip())
        
        # Write to file for consistency and debugging
        with open(str(OUTPUT_FILE), 'w') as f:  # Convert Path to string
            f.write(recommendation)
        logger.info(f"Written to {OUTPUT_FILE}: {recommendation}")
        
        socketio.emit('recommendations_complete', {'content': recommendation})
        return recommendations
    except Exception as e:
        logger.error(f"Recommendation generation failed: {e}")
        socketio.emit('recommendations_complete', {'content': f"Error: {str(e)}"})
        return [f"Error: {str(e)}"]

def generate_all_recommendations_and_video():
    logger.info("Starting process in CLI mode...")
    customer_id = input("Please enter Customer ID: ").strip()
    if not customer_id:
        logger.error("Customer ID is required in CLI mode.")
        sys.exit(1)
    
    system_prompt = DEFAULT_SYSTEM_PROMPT.replace("check_box_selection", "Consumer and Small Business Banking")
    logger.info(f"CLI mode system prompt: {system_prompt}")
    
    try:
        recommendations = generate_recommendations(system_prompt, customer_id)
        if recommendations and "Error" not in recommendations[0]:
            generate_video_with_moviepy(recommendations[0])
        logger.info("Process completed successfully.")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--cli":
        logger.info("Script started in command-line mode.")
        generate_all_recommendations_and_video()
    else:
        logger.info("Starting Flask-SocketIO server...")
        url = "http://127.0.0.1:5000"
        webbrowser.open(url)
        socketio.run(app, host='0.0.0.0', port=5000, debug=True)