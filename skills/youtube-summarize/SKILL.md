# YouTube Summarize Skill

This nanobot skill provides a command-line utility to fetch transcripts from YouTube videos and summarize them using an OpenRouter-powered LLM (Kimi-k2.5).

## Prerequisites

- **Python 3**: This skill requires Python 3 to be installed.
- **OpenRouter API Key**: You need an API key from [OpenRouter](https://openrouter.ai/).

## Installation

1.  **Install Python Dependencies:**

    This skill depends on the `youtube-transcript-api` and `requests` libraries. Install them using pip:

    ```bash
    pip install youtube-transcript-api requests
    ```

2.  **Make Scripts Executable:**

    Ensure the bash wrapper script is executable:

    ```bash
    chmod +x skills/youtube-summarize/summarize-yt
    ```

3.  **Install to /usr/local/bin (Optional):**

    To use the command globally, you can symlink the wrapper script to `/usr/local/bin` (assuming you have sudo privileges):

    ```bash
    ln -s $(pwd)/skills/youtube-summarize/summarize-yt /usr/local/bin/summarize-yt
    ```

    Alternatively, you can copy the entire folder contents to a directory in your PATH.

## Usage

1.  **Set Environment Variable:**

    Set your OpenRouter API key in your shell environment:

    ```bash
    export OPENROUTER_API_KEY="your_api_key_here"
    ```

    You can add this line to your `~/.bashrc` or `~/.zshrc` file to make it permanent.

2.  **Run the Summarizer:**

    Pass a YouTube video URL to the script:

    ```bash
    ./skills/youtube-summarize/summarize-yt https://www.youtube.com/watch?v=VIDEO_ID
    ```

    Or if installed globally:

    ```bash
    summarize-yt https://www.youtube.com/watch?v=VIDEO_ID
    ```

## How It Works

1.  The `summarize-yt` bash script validates the environment and locates the python script.
2.  The `summarize_yt.py` script:
    -   Extracts the video ID from the provided URL.
    -   Fetches the video transcript using `youtube-transcript-api`.
    -   Sends the transcript to the OpenRouter API using the `moonshotai/kimi-k2.5` model.
    -   Receives and prints a structured markdown summary.

## Troubleshooting

-   **Transcripts Disabled**: If a video does not have captions/transcripts enabled, the tool will fail with an error message.
-   **API Errors**: Ensure your API key is correct and valid. Check your internet connection.
