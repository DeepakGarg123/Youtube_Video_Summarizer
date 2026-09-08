import os

from dotenv import load_dotenv
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def ask_llm(prompt):

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    return response.text

def get_video_id(url):

    parsed_url = urlparse(url)

    
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        video_id = parse_qs(parsed_url.query).get("v")

        if video_id:
            return video_id[0]

    if parsed_url.hostname == "youtu.be":
        return parsed_url.path.strip("/")

    return None


def get_transcript(video_id):

    api = YouTubeTranscriptApi()

    transcript = api.fetch(
        video_id,
        languages=["hi"]
    )

    text = " ".join(
        item.text for item in transcript
    )

    return text

youtube_url = input("Enter YouTube URL: ")

video_id = get_video_id(youtube_url)

print("Video ID:", video_id)

transcript = get_transcript(video_id)
prompt = f"""
Summarize the following YouTube video transcript.

Give me:
1. A short summary
2. The main key points
3. The conclusion

Transcript:
{transcript}
"""
summary = ask_llm(prompt)
print(summary)
