# main.py
import os
import random
import time
import requests
import google.generativeai as genai
from dotenv import load_dotenv
import schedule
from requests_oauthlib import OAuth1Session

def generate_twitter_ai_content(topic):
    """
    Generates engaging social media post content for Twitter using the Gemini AI model.
    The prompt is designed to create concise, engaging, and hashtag-rich tweets (max 280 characters).
    """
    if not model:
        return f"AI model not configured. Placeholder tweet for {topic}."

    prompt = f"""
You are a creative social media marketing assistant for a landscaping and outdoor design company.
Your goal is to generate ONE concise, engaging, and lead-generating social media post for Twitter (max 280 characters).
The post should:
- Be interesting and encourage potential customers to inquire about services.
- Use relevant emojis and trending hashtags to make it appealing.
- Only output a single message/no multiple options.
- Do NOT include call to action to visit website or chat on whatsapp.

Topic: "{topic}"
"""
    try:
        response = model.generate_content(prompt)
        print("Twitter API Response:", response)
        if response.candidates and response.candidates[0].content.parts:
            single_tweet = response.candidates[0].content.parts[0].text.strip()
            if not single_tweet:
                single_tweet = "Contact us for expert landscaping and outdoor services!"
            return single_tweet
        else:
            print(f"Error: Gemini API response structure unexpected or empty content for topic '{topic}'.")
            return f"Failed to generate AI content for {topic}."
    except Exception as e:
        print(f"Error generating AI content for topic '{topic}': {e}")
        return f"Failed to generate AI content for {topic}."



# --- Configuration ---
# Gemini API Key: Get this from Google AI Studio or Google Cloud Console.
# It's crucial to keep this secure and not hardcode it in public repositories.
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Social Media API Credentials (PLACEHOLDERS - DO NOT USE IN PRODUCTION AS IS)
# For Facebook:
# You need a Facebook Page ID and a Long-Lived Page Access Token.
# Obtaining this token involves creating a Facebook Developer App, getting user
# authentication with specific permissions (e.g., 'pages_manage_posts'),
# and then exchanging a short-lived user token for a long-lived page token.
# This process is complex and typically handled by a secure backend server.
FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "YOUR_FACEBOOK_PAGE_ID")
FACEBOOK_ACCESS_TOKEN = os.getenv("FACEBOOK_ACCESS_TOKEN", "YOUR_FACEBOOK_ACCESS_TOKEN")

# For Twitter (X):
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY", "YOUR_TWITTER_API_KEY")
TWITTER_API_SECRET = os.getenv("TWITTER_API_SECRET", "YOUR_TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN = os.getenv("TWITTER_ACCESS_TOKEN", "YOUR_TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET = os.getenv("TWITTER_ACCESS_TOKEN_SECRET", "YOUR_TWITTER_ACCESS_TOKEN_SECRET")


# Predefined topics for social media post generation
TOPICS = [
    "Expert Landscaping and Design",
    "Dedicated Garden Maintenance",
    "Professional Tree Care & Maintenance",
    "Durable Walkway & Road Construction",
    "Precise Excavation & Cabro Laying",
    "Stunning Water Features & Pools"
]

# Initialize Gemini API
# This checks if the API key is available before configuring the model.
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.0-flash') # Using the specified Gemini model
else:
    print("Warning: GEMINI_API_KEY not found in .env. AI content generation will not work.")
    model = None

# --- Helper Functions ---

def generate_facebook_ai_content(topic):
    """
    Generates engaging social media post content using the Gemini AI model.
    The prompt is designed to create lead-generating and engaging messages.
    """
    if not model:
        return f"AI model not configured. Placeholder post for {topic}."

    prompt = f"""
You are a creative social media marketing assistant for a landscaping and outdoor design company.
Your goal is to generate ONE concise, engaging, and lead-generating social media post for Facebook (max 500 characters).
The post should:
- Be interesting and encourage potential customers to inquire about services.
- Use relevant emojis to make it appealing.
- Only output a single message/no multiple options.
- include  trending hashtags.
- no call to action to visit website or chat on whatsapp.don't include call to action to visit website or chat on whatsapp.


Topic: "{topic}"
"""
    try:
        # Make the API call to Gemini
        response = model.generate_content(prompt)
        print("API Response:", response)  # Debugging line to see the full response structure
        # Extract the text from the API response
        if response.candidates and response.candidates[0].content.parts:
            single_post = response.candidates[0].content.parts[0].text.strip()
            # Final fallback: ensure non-empty message
            if not single_post:
                single_post = "Contact us for expert landscaping and outdoor services! [visit our website](https://ecogreencontractors.solutions/) or [chat with us on whatsapp](https://wa.me/254746887291?text=Hello%21%20I%27m%20interested%20in%20landscaping%20and%20outdoor%20services)"
            return single_post
        else:
            print(f"Error: Gemini API response structure unexpected or empty content for topic '{topic}'.")
            return f"Failed to generate AI content for {topic}."
    except Exception as e:
        # Catch any exceptions during the API call or response parsing
        print(f"Error generating AI content for topic '{topic}': {e}")
        return f"Failed to generate AI content for {topic}."

def post_to_facebook(message):
    """
    Posts a message to a Facebook Page using the Graph API.
    
    Requirements:
    - The FACEBOOK_ACCESS_TOKEN must be a Page Access Token (not a User Access Token).
    - The token must have both 'pages_read_engagement' and 'pages_manage_posts' permissions.
    - The user who generated the token must be an admin of the page.
    
    How to obtain the correct token:
    1. Go to Facebook Developer Portal > My Apps > [Your App].
    2. Request 'pages_read_engagement' and 'pages_manage_posts' permissions.
    3. Use Graph API Explorer to generate a User Access Token with these permissions.
    4. Exchange for a long-lived token (optional).
    5. Use /me/accounts to get the Page Access Token for your page.
    6. Update your .env with this token.
    """
    print(f"Attempting to post to Facebook: {message[:70]}...")
    # Validate credentials and token format
    if not FACEBOOK_PAGE_ID or not FACEBOOK_ACCESS_TOKEN or FACEBOOK_ACCESS_TOKEN == "YOUR_FACEBOOK_ACCESS_TOKEN" or FACEBOOK_PAGE_ID == "YOUR_FACEBOOK_PAGE_ID":
        print("Facebook API credentials not properly configured. Skipping Facebook post.")
        print("Make sure you have a valid Page Access Token with 'pages_read_engagement' and 'pages_manage_posts' permissions.")
        return False
 
    url = f"https://graph.facebook.com/{FACEBOOK_PAGE_ID}/feed"
    payload = {
        "message": message,
        "access_token": FACEBOOK_ACCESS_TOKEN
    }
    try:
        response = requests.post(url, data=payload, timeout=10)
        if response.status_code == 200:
            response_json = response.json()
            post_id = response_json.get("id")
            if post_id:
                print(f"Successfully posted to Facebook! Post ID: {post_id}")
                return True
            else:
                print(f"Facebook API response did not contain post ID: {response_json}")
                return False
        elif response.status_code == 400 and "(#200)" in response.text:
            print("Facebook API error (#200): Insufficient permissions or wrong token type.")
            print("Make sure your token is a Page Access Token with the required permissions and you are an admin of the page.")
            print("See the function docstring for step-by-step instructions.")
            return False
        else:
            print(f"Facebook post failed. Status: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("Facebook post request timed out.")
        return False
    except requests.exceptions.RequestException as e:
        print(f"Error posting to Facebook: {e}")
        return False

def post_to_twitter(message):
    """
    Posts a message to Twitter using the Twitter API v2 and OAuth1Session.
    """
    print(f"Attempting to post to Twitter (X): {message[:70]}...")
    url = "https://api.twitter.com/2/tweets"
    payload = {"text": message}
    try:
        oauth = OAuth1Session(
            TWITTER_API_KEY,
            client_secret=TWITTER_API_SECRET,
            resource_owner_key=TWITTER_ACCESS_TOKEN,
            resource_owner_secret=TWITTER_ACCESS_TOKEN_SECRET,
        )
        response = oauth.post(url, json=payload, timeout=10)
        print("Status code:", response.status_code)
        print("Response:", response.text)
        if response.status_code == 201 or response.status_code == 200:
            try:
                response_json = response.json()
                tweet_id = response_json.get("data", {}).get("id")
                if tweet_id:
                    print(f"Successfully posted to Twitter! Tweet ID: {tweet_id}")
                else:
                    print(f"Successfully posted to Twitter! Response: {response_json}")
            except Exception:
                print(f"Successfully posted to Twitter! Response: {response.text}")
            return True
        else:
            print(f"Twitter post failed. Status: {response.status_code}, Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error posting to Twitter: {e}")
        return False

def send_social_media_post():
    """
    Main function to orchestrate the social media post generation and sending process.
    This function is called by the scheduler.
    """
    print(f"\n--- Starting new social media post cycle at {time.ctime()} ---")
    
    # 1. Randomly select a topic
    selected_facebook_topic = random.choice(TOPICS)
    print(f"Selected topic: {selected_facebook_topic}")

    # 2. Generate AI content for the post
    post_content = generate_facebook_ai_content(selected_facebook_topic)
    print(f"Generated Post Content:\n{post_content}")

    # 3. Send the post to Facebook
    facebook_success = post_to_facebook(post_content)
    print(f"Facebook post success: {facebook_success}")

    # Twitter posting functionality has been removed.
    # Log only Facebook outcome
    if facebook_success:
        print("Post successfully sent to Facebook!")
    else:
        print("Failed to send post to Facebook.")
    selected_twitter_topic = random.choice(TOPICS)
    print(f"Selected topic for Twitter: {selected_twitter_topic}")
    twitter_post_content = generate_twitter_ai_content(selected_twitter_topic)
    print(f"Generated Twitter Post Content:\n{twitter_post_content}")
    twitter_success = post_to_twitter(twitter_post_content)
    if twitter_success:
        print("Post successfully sent to Twitter!")
    else:
        print("Failed to send post to Twitter.")
    print("--- End of post cycle ---")

# --- Scheduling ---

def schedule_posts():
    """
    Schedules the social media posts to run 5 times per day.
    This uses the 'schedule' library for demonstration purposes.
    For a production environment, a more robust solution like:
    - Linux Cron jobs
    - AWS Lambda with EventBridge
    - Google Cloud Scheduler with Cloud Functions/Run
    - A dedicated task queue (e.g., Celery with Redis/RabbitMQ)
    would be recommended, as this script needs to run continuously.
    """
    print("Scheduling social media posts to run 5 times per day...")
    
    # To run 5 times per day, each run should be approximately every 4.8 hours (24 / 5).
    # We'll set specific times for clarity and consistency.
    schedule.every().day.at("06:56").do(send_social_media_post)
    schedule.every().day.at("12:00").do(send_social_media_post)
    schedule.every().day.at("16:00").do(send_social_media_post)
    schedule.every().day.at("09:56").do(send_social_media_post)
    schedule.every().day.at("00:00").do(send_social_media_post) # Next day's first post

    print("Scheduler started. The script will run continuously and execute tasks at scheduled times.")
    print("Press Ctrl+C to stop the scheduler.")
    while True:
        schedule.run_pending()
        time.sleep(1) # Wait one second before checking for pending jobs again

# --- Main Execution Block ---
if __name__ == "__main__":
    # You can uncomment the line below to run a single post immediately for testing purposes.
    # This is useful to quickly check if AI generation and API calls (even simulated ones) work.
    # send_social_media_post()

    # To start the automated daily posting, uncomment the line below.
    # Remember that this script needs to be running continuously in the background
    # for the scheduler to work.
    schedule_posts()