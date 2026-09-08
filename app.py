import os

import streamlit as st

from dotenv import load_dotenv
from google import genai
from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs


# ---------------- LOAD API KEY ----------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


# ---------------- ASK GEMINI ----------------

def ask_llm(prompt):

    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=prompt
    )

    # Debug information
    print("\n========== GEMINI RESPONSE ==========")
    print(response)

    print("\n========== RESPONSE TEXT ==========")
    print(response.text)

    print("\n========== CANDIDATES ==========")
    print(response.candidates)

    if response.text:
        return response.text
    else:
        return "Gemini did not return any text."


# ---------------- GET VIDEO ID ----------------

def get_video_id(url):

    parsed_url = urlparse(url)

    # Normal YouTube URL
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:

        video_id = parse_qs(parsed_url.query).get("v")

        if video_id:
            return video_id[0]

    # Short YouTube URL
    if parsed_url.hostname == "youtu.be":

        return parsed_url.path.strip("/")

    return None


# ---------------- GET TRANSCRIPT ----------------

def get_transcript(video_id):

    api = YouTubeTranscriptApi()

    transcript = api.fetch(
        video_id,
        languages=["hi", "en"]
    )

    text = " ".join(
        item.text for item in transcript
    )

    return text


# ---------------- STREAMLIT UI ----------------

st.title("🎥 YouTube Video Summarizer")

st.write(
    "Enter a YouTube URL and get an AI-generated summary."
)


youtube_url = st.text_input(
    "Enter YouTube URL"
)


# ---------------- SUMMARIZE BUTTON ----------------

if st.button("Summarize"):

    if youtube_url:

        try:

            # Get video ID
            video_id = get_video_id(youtube_url)

            if video_id is None:

                st.error("Invalid YouTube URL")

            else:

                st.write("Video ID:", video_id)


                # Get transcript
                with st.spinner("Getting transcript..."):

                    transcript = get_transcript(video_id)


                # Show transcript length
                st.write(
                    "Transcript length:",
                    len(transcript)
                )


                # Create prompt
                prompt = f"""
Summarize the following YouTube video transcript.

Give me:

1. A short summary
2. The main key points
3. The conclusion

Transcript:

{transcript}
"""


                # Ask Gemini
                with st.spinner("Generating summary..."):

                    summary = ask_llm(prompt)


                # Display result
                st.subheader("📄 Summary")

                st.write(summary)


        except Exception as e:

            st.error(
                f"Something went wrong: {e}"
            )

    else:

        st.warning(
            "Please enter a YouTube URL."
        )