Below is a sample `README.md` that describes how to use the provided Python script for downloading YouTube comments into a CSV file. This script utilizes the `tkinter` library for a graphical user interface (GUI) and requires a valid YouTube API key to fetch comments.

---

# YouTube Comments Downloader

This Python script provides a GUI for downloading comments from a YouTube video into a CSV file. It uses the YouTube Data API v3 and `tkinter` for the interface.

## Features

- GUI for easy use
- Downloads comments from a specified YouTube video URL
- Saves comments in a CSV file with details such as commenter name, comment date, content, and like count

## Prerequisites

Before running this script, ensure you have:

- Python installed on your machine
- `tkinter` library installed (comes pre-installed with Python)
- `requests` library installed (can be installed via pip)
- A valid YouTube API Key

## Installation

1. Ensure you have Python and pip installed.
2. Install the required `requests` package using pip if you haven't already:
   ```
   pip install requests
   ```

## Usage

1. Replace the placeholder YouTube API key in the script with your own key:
   ```python
   YOUTUBE_API_KEY = "YOUR_API_KEY_HERE"
   ```
2. Run the script:
   ```
   python youtube_comments_downloader.py
   ```
3. The GUI window will open. Paste the URL of the YouTube video you want to download comments from in the text box.
4. Click the "Get comments" button.
5. A file dialog will prompt you to choose the location and name of the CSV file where the comments will be saved.
6. The script will start downloading the comments and will show a message once done.

## Output Format

The CSV file will contain the following columns:

- Name (`姓名`)
- Comment Time (`回覆時間`)
- Comment Content (`回覆內容`)
- Like Count (`按讚數量`)

## Note

This script uses the YouTube Data API v3, which has a quota limit. Be mindful of the number of requests you make to avoid exceeding your quota.

## Disclaimer

This script is for educational purposes only. Ensure you comply with YouTube's API terms and conditions.