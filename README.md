# Hyper Personalized Recommendation Generator

**Overview**
Hyper-personalization is key strategy for businesses to enhance customer experience, increase engagement. Businesses can create unique and engaging experiences for the customers, driving loyalty and growth.
To recommend the personalization choices to customer:

1.	Reading Customer data, along with consent of the customer.
2.	If consent is provided by customer, 
  •	Uses customer tweets from file generated using Twitter API, conduct sentiment analysis with help of TextBlob. 
  •	Construct personalized prompts using transaction history and sentiment data. 
  •	Utilizes OpenAI API to generate recommendations. 
  •	Converts the generated recommendations into Audio with pyttsx3, to incorporate subtitles, background music, and a watermark. Finalizes the video composition using Moviepy Python library.

**Data flow**
Input (UI/CLI + Excel Files) → Data Merge (Pandas) → Prompt (Customer Data) → OpenAI (Text) → MoviePy (Video) → Output (Text File + Video File + UI)
![image](https://github.com/user-attachments/assets/00c9e973-3552-483b-bcac-a2808c5ce68c)



    **Input Collection**
    •	Web Mode: User submits a form via Flask (customer_id, optional prompt, and categories) through the HTML UI.
    
    •	CLI Mode: User enters customer_id via command-line input; default category is "Consumer and Small Business Banking".
    
    •	Environment variables (OPENAI_API_KEY, EXCEL_PASSWORD) are loaded using dotenv.
    
    
    **Data Loading**
    •	Source Files: Three encrypted Excel files (customer_transactions.xlsx, customer_profile.xlsx, twitter_data.xlsx) are decrypted using msoffcrypto with EXCEL_PASSWORD.
    
    •	Processing: pandas reads and merges the files into a single DataFrame based on customer_id, including transaction, profile, and Twitter data. Consent fields (consent, consent_social_media) are validated.
    
    **Prompt Generation**
    •	User Prompt: Customer data (e.g., name, transactions, sentiment) is extracted and formatted into a string for OpenAI. If no data or consent is missing, an error message is returned.
    
    •	System Prompt: Default or user-provided prompt is adjusted with selected categories (e.g., "Consumer Lending").
    
      **Recommendation Generation**
    •	OpenAI API: The combined prompt is sent to gpt-4o-mini, generating a recommendation text (max 250 tokens). Results are logged and emitted via SocketIO.
    
    •	Output Storage: Text is written to recommendations.txt in artifacts/output.
    
     **Video Creation**
    •	Narration: pyttsx3 converts the recommendation text to audio, saved as temp_audio.mp3.
    
    •	Background: pytubefix downloads a YouTube video to temp_background_video.mp4.
    
    •	Assembly: MoviePy combines:
    
      o	Background video (resized, looped to match audio duration).
      
      o	Text overlays (recommendation split into chunks).
      
      o	Audio (narration + background music from background_music.mp3).
      
      
    •	Output: Final video is saved as recommendations_video.mp4 in artifacts/output.
    
    **Delivery**
    
      •	Web Mode: Flask serves the recommendation text and video link via SocketIO events, updating the UI in real-time.
      
      •	CLI Mode: Results are logged to the console; video is saved locally.
      
      •	Temporary files (temp_audio.mp3, temp_background_video.mp4) are cleaned up.
    

**Approach**
Approach to Designing the application

1.	Modular Design
  o	Goal: Break functionality into reusable, independent components.
  o	Implementation: Separate functions for data loading (load_data), prompt generation (generate_user_prompt), recommendation generation (get_recommendation), and video creation (generate_video_with_moviepy). This enhances maintainability and testing.

3.	User-Centric Workflow
  o	Goal: Cater to both technical (CLI) and non-technical (web) users.
  o	Implementation: Dual execution modes: CLI for quick runs with minimal input, and a Flask-based web app with an intuitive UI for interactive use. Real-time feedback via SocketIO keeps users informed.

5.	Data-Driven Personalization
  o	Goal: Leverage customer data for tailored banking recommendations.
  o	Implementation: Use pandas to merge transaction, profile, and Twitter data, feeding it into OpenAI’s gpt-4o-mini with a structured prompt. Consent checks ensure ethical data use.

7.	Multimedia Engagement
  o	Goal: Enhance recommendations with visual and audio appeal.
  o	Implementation: Combine pyttsx3 for narration, pytubefix for background video, and MoviePy to overlay text and mix audio, creating a polished video output.

9.	Security and Robustness
  o	Goal: Protect sensitive data and ensure reliable execution.
  o	Implementation: Encrypt Excel files with msoffcrypto, validate prerequisites (check_prerequisites), and implement logging for debugging. Temporary file cleanup prevents resource leaks.

11.	Iterative Development
  o	Goal: Build a flexible, extensible prototype.
  o	Implementation: Use Python for rapid prototyping, hardcode initial settings (e.g., YouTube URL), and leave room for future enhancements (e.g., configurable parameters).
________________________________________


**Core Philosophy**
•	Start Simple: Focus on core functionality (data to recommendation to video).
•	Integrate Gradually: Layer in web UI, real-time updates, and multimedia.
•	Prioritize User Experience: Ensure outputs are engaging and accessible.


**Key-Technical considerations**
Key technical considerations and the high-level technology choices 

**1.	Data Handling and Security**
      o	Encrypted Excel Files: The script uses msoffcrypto to decrypt Excel files (customer_transactions.xlsx, customer_profile.xlsx, twitter_data.xlsx) with a password stored in an environment variable (EXCEL_PASSWORD). This ensures sensitive customer data is protected at rest.
      o	Consent Checks: The script enforces consent (consent and consent_social_media) before processing data, aligning with privacy regulations like GDPR or CCPA. Missing or invalid consent halts processing for a customer.
      o	Pandas for Data Processing: pandas is used to load, merge, and filter data based on customer_id. Merging transaction, profile, and Twitter data into a single DataFrame enables comprehensive customer analysis but assumes consistent column naming and data integrity across files.
    
  **2.	API Integration**
  o	OpenAI API: The script leverages OpenAI’s gpt-4o-mini model to generate personalized banking product recommendations. The system prompt is dynamically adjusted with user-selected categories, and the user prompt includes customer data, ensuring context-aware outputs. Error handling for API calls is present but could be more robust (e.g., retry logic for transient failures).
  o	Token and Temperature Settings: max_tokens=250 limits output length to fit the 220-word constraint, and temperature=0.7 balances creativity and coherence in recommendations.
  
  **3.	Web Application**
    o	Flask and SocketIO: The script uses Flask as a lightweight web framework and SocketIO for real-time communication. This enables live updates (logs, recommendations, video links) to the frontend, enhancing user experience.
    o	HTML/CSS/JavaScript: The frontend is a single-page app with a form for input (customer ID, categories, prompt) and dynamic sections for results. JavaScript handles form submission and SocketIO events, while CSS provides a polished UI. However, the template is embedded as a string, which could complicate maintenance for larger UIs.
  
  **4.	Video Generation**
  
    o	MoviePy: Used to create a video with text overlays (recommendations), background video, narration, and music. Text is split into chunks for readability, synced with audio duration, and styled with ImageMagick for rendering.
    o	pyttsx3: Generates text-to-speech narration saved as a temporary MP3. The speech rate (140) is hardcoded, which might not suit all content lengths or user preferences.
    o	YouTube Video Download: pytubefix downloads a background video from a hardcoded URL. Directory management and cleanup are handled, but the process is brittle (e.g., relies on YouTube availability and specific stream formats).
    o	Resource Management: Temporary files are cleaned up with retry logic for PermissionError, but lingering files could still occur if exceptions are unhandled elsewhere.
  
  **5.	Logging and Debugging**
    o	Custom Logging: The script uses Python’s logging with a custom SocketIOHandler to stream logs to the frontend. This is great for real-time feedback but lacks persistent storage (e.g., file logging) for post-mortem analysis.
    o	Prerequisite Checks: The check_prerequisites function validates dependencies, API keys, and file paths, ensuring the script fails fast if setup is incomplete.
  
  **6.	File System Management**
    o	Pathlib: The script uses Path for cross-platform path handling, defining relative paths from the script’s location (BASE_DIR). This is robust but assumes a specific directory structure (data, artifacts/output, artifacts/temp).
    o	Static File Serving: Flask serves the generated video from artifacts/output, requiring correct static folder configuration.
  
  **7.	Execution Modes**
    o	CLI vs. Web: The script supports both command-line (--cli) and web modes. CLI mode prompts for a customer ID and uses a default category, while web mode offers a UI with category selection. This dual-mode design adds flexibility but increases complexity.


**High-Level Technology Choices and Rationale**
  1.	Python
    o	Why: A versatile, high-level language with strong libraries for data processing (pandas), AI (openai), web development (Flask), and multimedia (MoviePy, pyttsx3). Ideal for rapid prototyping and integrating diverse functionalities.
    o	Trade-off: Slower execution compared to compiled languages, but team is expert in Python and performance isn’t critical for this use case.

  3.	Pandas
    o	Why: Efficiently handles tabular data (Excel files) with powerful merging and filtering capabilities, essential for combining customer datasets.
    o	Trade-off: Memory-intensive for large datasets; alternatives like polars could offer better performance for big data.

  5.	OpenAI API
    o	Why: Provides state-of-the-art natural language generation for personalized recommendations, leveraging customer data and sentiment analysis. The gpt-4o-mini model balances cost and quality.
    o	Trade-off: Dependency on external API introduces latency, cost, and potential downtime risks. Local models (e.g., via Hugging Face) could reduce this but require more setup.

  6.	Flask and SocketIO
  
    o	Why: Flask is lightweight and sufficient for a simple web app, while SocketIO enables real-time updates, critical for a responsive UI during recommendation and video generation.
    o	Trade-off: Flask isn’t ideal for large-scale apps; a framework like Django might be overkill here but offers more built-in features

  7.	MoviePy and pyttsx3
  
    o	Why: MoviePy simplifies video editing (text overlays, audio mixing), and pyttsx3 provides offline text-to-speech, avoiding additional API costs. Together, they create engaging video outputs.
    o	Trade-off: MoviePy relies on ImageMagick, adding an external dependency, and pyttsx3’s voice quality is basic compared to cloud-based TTS (e.g., Google Text-to-Speech).

  8.	pytubefix
  
    o	Why: Enables downloading YouTube videos for background content, keeping the script self-contained without hosting large video files.
    o	Trade-off: Relies on YouTube’s API stability and terms of service; a local video library would be more reliable but less dynamic.

  9.	msoffcrypto
  
    o	Why: Decrypts password-protected Excel files, ensuring data security aligns with banking standards.
    o	Trade-off: Adds complexity; unencrypted files or a database might simplify but compromise security.

This script is a solid proof-of-concept for personalized banking recommendations with multimedia output, leveraging Python’s ecosystem effectively. With refinements, it could scale to production use.




**Business recommendations based on AI-Driven findings**

Here is one of Business recommendations provided using the created model:

  Hello John, I am your Investment Advisor Jeremy Porter. Wells Fargo would like to recommend you a few products that can enhance your banking experience and support your financial goals.
  
  	First, I recommend the Wells Fargo Home Mortgage. Understanding your recent concerns regarding the home loan application process, this mortgage offers tailored solutions that can ease your path to homeownership with competitive rates and flexible terms designed for your unique situation.
  
  	Second, consider the Wells Fargo Personal Loan. With your strong income and positive banking history, this personal loan can provide you with the funds you need for any significant purchases or debt consolidation, all while enjoying fixed monthly payments and no prepayment penalties.
  
  	Finally, I suggest the Wells Fargo Cash Back Rewards Card. This credit card allows you to earn cash back on your everyday purchases, including clothing, which has been a recent focus for you. With no annual fee and the ability to earn rewards, it will complement your spending habits while providing you with financial flexibility.
  
  	These products not only align with your current needs but also set you on the path to achieving your financial aspirations. Let’s take the next steps together.
  Visit wellsfargo.com for more details.

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

**Conclusion**
Summary: This script delivers hyper-personalized banking recommendations by integrating customer data, AI, and multimedia output, enhancing customer engagement for Wells Fargo.

Strengths: 
1.	Secure data handling with encryption and consent checks.
2.	Real-time web interface via Flask and SocketIO.
3.	Dynamic text and video generation using OpenAI and MoviePy.

Value: Combines advanced analytics, natural language processing, and visual storytelling to drive product adoption.

Future Potential: 
1.	Scale with async processing for multiple customers.
2.	Enhance with configurable settings and robust error handling.
3.	Explore local AI models for cost efficiency.

Takeaway: A powerful proof-of-concept showcasing Python’s versatility in financial services innovation.


