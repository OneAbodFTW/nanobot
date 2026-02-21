#!/usr/bin/env python3
import os
import sys
import argparse
import re
import json
import requests
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound


def get_video_id(url):
    """Extracts the video ID from a YouTube URL."""
    pattern = r"(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    else:
        raise ValueError("Invalid YouTube URL")


def get_transcript(video_id):
    """Fetches the transcript for a given video ID."""
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)
        # Combine text parts into a single string
        full_text = " ".join([item["text"] for item in transcript_list])
        return full_text
    except TranscriptsDisabled:
        print("Error: Transcripts are disabled for this video.", file=sys.stderr)
        sys.exit(1)
    except NoTranscriptFound:
        print("Error: No transcript found for this video.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error fetching transcript: {e}", file=sys.stderr)
        sys.exit(1)


def summarize_text(text, api_key):
    """Summarizes the text using the OpenRouter API."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        # Optional: Include site URL and name for OpenRouter rankings
        "HTTP-Referer": "https://nanobot.dev",
        "X-Title": "Nanobot YouTube Summarizer",
    }

    # Prompt engineering for a good summary
    prompt = (
        "Please provide a comprehensive and structured summary of the following video transcript. "
        "Use markdown formatting with headers and bullet points. "
        "Focus on the main ideas, key arguments, and any actionable takeaways.\n\n"
        f"Transcript:\n{text}"
    )

    data = {
        "model": "moonshotai/kimi-k2.5",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful assistant that summarizes video transcripts.",
            },
            {"role": "user", "content": prompt},
        ],
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        result = response.json()
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            print("Error: API returned an empty response.", file=sys.stderr)
            sys.exit(1)
    except requests.exceptions.RequestException as e:
        print(f"Error communicating with OpenRouter API: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Summarize YouTube videos using OpenRouter API.")
    parser.add_argument("url", help="The YouTube video URL to summarize")
    args = parser.parse_args()

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("Error: OPENROUTER_API_KEY environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    try:
        video_id = get_video_id(args.url)
        print(f"Fetching transcript for video ID: {video_id}...", file=sys.stderr)
        transcript_text = get_transcript(video_id)

        print("Generating summary...", file=sys.stderr)
        summary = summarize_text(transcript_text, api_key)

        print("\n" + "=" * 40 + "\n")
        print(summary)
        print("\n" + "=" * 40 + "\n")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
