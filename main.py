# main.py
import os
import random
import time
import requests
import google.generativeai as genai
from dotenv import load_dotenv
 # schedule module no longer needed
from requests_oauthlib import OAuth1Session
import requests
from bs4 import BeautifulSoup
import time # To add delays and avoid being blocked


def get_kenya_trends():
    url = "https://trends24.in/kenya/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    } # Mimic a web browser

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.text, 'html.parser')

        # --- IMPORTANT: You need to inspect the trends24.in/kenya/ HTML to find the correct selectors ---
        # Look for the HTML structure that contains the trending topics.
        # This is a placeholder example based on common patterns:
        trending_list_container = soup.find('div', class_='list-container') # Or whatever the actual class/id is
        
        if trending_list_container:
            trends = trending_list_container.find_all('li') # Assuming each trend is an <li> item
            
            kenya_trends = []
            for trend_item in trends:
                hashtag_element = trend_item.find('a') # Assuming the hashtag is in an <a> tag

                if hashtag_element:
                    hashtag = hashtag_element.get_text(strip=True)
                    kenya_trends.append(hashtag)
            return kenya_trends[:6]  # Return top 4 trends
        else:
            print("Could not find the trending list container on the page.")
            return []

    except requests.exceptions.RequestException as e:
        print(f"Error fetching page: {e}")
        return []
    except Exception as e:
        print(f"An error occurred during parsing: {e}")
        return []

def append_hashtags_to_message(message, hashtags):
    """
    Appends a list of hashtags to the message, separated by spaces.
    Ensures each hashtag starts with #. If the final message is longer than 278 characters,
    removes hashtags without # one by one until the message is <= 278 chars.
    """
    hashtags_list = []
    if hashtags:
        if isinstance(hashtags, list):
            hashtags_list = [(h if h.strip().startswith('#') else f'#{h.strip()}') for h in hashtags if h.strip()]
        else:
            h = hashtags.strip()
            hashtags_list = [h if h.startswith('#') else f'#{h}']
    final_message = message + " " + " ".join(hashtags_list).strip()
    # If too long, remove hashtags without # one by one
    if len(final_message) > 278:
        # Find indices of hashtags that originally did NOT have #
        original_hashtags = hashtags if isinstance(hashtags, list) else [hashtags]
        indices_to_remove = [i for i, h in enumerate(original_hashtags) if not h.strip().startswith('#')]
        hashtags_copy = hashtags_list.copy()
        for idx in indices_to_remove:
            if idx < len(hashtags_copy):
                hashtags_copy.pop(idx)
                temp_message = message + " " + " ".join(hashtags_copy).strip()
                if len(temp_message) <= 278:
                    final_message = temp_message
                    break
        # If still too long, truncate hashtags until fits
        while len(final_message) > 278 and hashtags_copy:
            hashtags_copy.pop()
            final_message = message + " " + " ".join(hashtags_copy).strip()
    return final_message

def generate_twitter_ai_content(topic):
    """
    Generates engaging social media post content for Twitter using the Gemini AI model.
    The prompt is designed to create concise, engaging, and hashtag-rich tweets (max 180 characters).
    """
    if not model:
        return f"AI model not configured. Placeholder tweet for {topic}."

    prompt = f"""
You are a creative social media marketing assistant for a landscaping and outdoor design company.
Your goal is to generate ONE concise, engaging, and lead-generating social media post for Twitter (max 215 characters).
The post should:
- Be interesting and encourage potential customers to inquire about services.
- Dont include hashtags, we shall add them later.
- Use relevant emojis to make it appealing.
- Only output a single message/no multiple options.
- Format the content well with proper spacing and line breaks.
- add call to action to visit website https://ecogreencontractors.solutions and enquire on whatsapp +254746887291.

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
    "Emphasize the importance of the user liking and following our facebook page https://www.facebook.com/profile.php?id=61578337620398. And following us on Twitter https://x.com/9Ecogreen"
    "Expert Landscaping and Design",
    "Dedicated Garden Maintenance",
    "Professional Tree Care & Maintenance",
    "Durable Walkway & Road Construction",
    "Precise Excavation & Cabro Laying",
    "Stunning Water Features & Pools",
    "Plants & Flowers",
    "Plants that thrive in Kenya's northern eastern region",
    "Indoor plants and Indoor Planting",
    "Eco-Friendly Outdoor Solutions",
    "Custom Outdoor Lighting Solutions",
    "Request to be followed back on social media for more updates and offers",
    "Unveiling Your Vision: The Landscape Design Process Explained",
    "Modern vs. Traditional: Choosing Your Outdoor Aesthetic",
    "The Art of Outdoor Zoning: Creating Functional 'Rooms' in Your Garden",
    "Small Yard, Big Dreams: Maximizing Compact Outdoor Spaces",
    "Designing for Privacy: Hedges, Screens & Walls for Your Sanctuary",
    "Curb Appeal Secrets: Boosting Your Home's First Impression",
    "Patio Perfection: Choosing Materials & Layouts for Outdoor Living",
    "Walkways & Paths: Guiding Guests with Style and Function",
    "Retaining Walls: Blending Functionality with Aesthetic Appeal",
    "Fire Pits & Outdoor Fireplaces: Igniting Cozy Evenings",
    "The Soothing Sounds: Incorporating Water Features into Your Design",
    "Custom Deck Designs: Extending Your Indoor Living Space Outdoors",
    "Drought-Tolerant Landscaping: Beautiful & Water-Wise Solutions for Kenya",
    "Native Plants for Kenya: Attracting Wildlife & Thriving Gardens",
    "Edible Landscapes: Growing Your Own Food in Style",
    "Color Theory in the Garden: Painting with Plants for Visual Impact",
    "Smart Irrigation: Saving Water, Keeping Your Landscape Lush",
    "Choosing the Right Trees: Shade, Privacy & Long-Term Beauty",
    "Flower Power: Creating Continuous Blooms in Your Garden",
    "Vertical Gardens: Green Walls for Urban & Small Spaces",
    "Outdoor Kitchen Essentials: From Grilling Stations to Gourmet Setups",
    "Poolside Paradise: Landscaping to Enhance Your Aquatic Retreat",
    "Backyard Putting Greens: Practice Your Putt at Home",
    "Illuminate Your Landscape: Evening Ambiance & Safety Lighting",
    "Creating an Outdoor Entertainment Hub: Design Tips",
    "Year-Round Garden Care: A Seasonal Guide for Kenya",
    "Solving Drainage Dilemmas: Managing Water in Your Yard",
    "Landscaping on a Budget: Smart Choices for Maximum Impact",
    "The ROI of Landscaping: How Outdoor Upgrades Pay Off",
    "Beyond Aesthetics: The Health & Wellness Benefits of Outdoor Spaces"
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
        Your goal is to generate ONE concise, engaging, and lead-generating social media post for Facebook (max 700 characters).
        The post should:
        - Be interesting and encourage potential customers to inquire about services.
        - Use relevant emojis to make it appealing.
        - The content should be engaging and lead to inquiries.
        - Content length does not matter though it should be concise and clear.
        - Format the content well with proper spacing and line breaks.
        - Only output a single message/no multiple options.
        - include  trending hashtags.
        - add call to action to visit website https://ecogreencontractors.solutions/ and chat on whatsapp to number +254746887291.


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
    print(f"Attempting to post to Twitter (X): {message}")
    print("posting to twitter a message with length", len(message))
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

    # 2. Fetch trending hashtags in Kenya
    trending_hashtags = get_kenya_trends()
    print(f"Trending hashtags in Kenya: {trending_hashtags}")

    # 3. Generate AI content for Facebook
    post_content = generate_facebook_ai_content(selected_facebook_topic)

    # 4. Send the post to Facebook
    facebook_success = post_to_facebook(post_content)
    print(f"Facebook post success: {facebook_success}")

    if facebook_success:
        print("Post successfully sent to Facebook!")
    else:
        print("Failed to send post to Facebook.")

    # 5. Generate AI content for Twitter and append hashtags
    selected_twitter_topic = random.choice(TOPICS)
    print(f"Selected topic for Twitter: {selected_twitter_topic}")
    twitter_post_content = generate_twitter_ai_content(selected_twitter_topic)
    # Append hashtags to the Twitter post content
    twitter_post_content_with_hashtags = append_hashtags_to_message(twitter_post_content, trending_hashtags)
    print(f"Generated Twitter Post Content with hashtags:\n{twitter_post_content_with_hashtags}")
    twitter_success = post_to_twitter(twitter_post_content_with_hashtags)
    if twitter_success:
        print("Post successfully sent to Twitter!")
    else:
        print("Failed to send post to Twitter.")
    print("--- End of post cycle ---")

# --- Main Execution Block ---
if __name__ == "__main__":
    send_social_media_post()