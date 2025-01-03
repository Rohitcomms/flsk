import yt_dlp
import requests
from flask import Flask, request, jsonify
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

def get_transcript(video_url):
    ydl_opts = {
        'writesubtitles': True,  # Download subtitles
        'subtitleslangs': ['en'],  # Download English subtitles
        'quiet': True,  # Suppress output
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        result = ydl.extract_info(video_url, download=False)
        if 'requested_subtitles' in result:
            subtitle_info = result['requested_subtitles']
            if 'en' in subtitle_info:
                subtitle_url = subtitle_info['en']['url']
                return subtitle_url
            else:
                raise Exception("English subtitles not found.")
        else:
            raise Exception("No subtitles found for this video.")

def download_subtitles(subtitle_url):
    response = requests.get(subtitle_url)
    if response.status_code == 200:
        return response.text
    else:
        raise Exception("Failed to download subtitles.")

@app.route('/')
def home():
    return "Server is running!"

@app.route('/summarize', methods=['POST'])
def summarize_video():
    try:
        # Get JSON data from the request
        data = request.get_json()
        youtube_url = data.get("url")
        if not youtube_url:
            return jsonify({"error": "No YouTube URL provided"}), 400

        # Extract transcript URL using yt-dlp
        try:
            transcript_url = get_transcript(youtube_url)
            subtitle_text = download_subtitles(transcript_url)
        except Exception as e:
            return jsonify({"error": str(e)}), 400

        # Prepare the transcript text for summarization
        transcript_text = subtitle_text.replace("\n", " ")

        # Summarize the transcript using LSA summarizer
        parser = PlaintextParser.from_string(transcript_text, PlaintextParser.URN_MODE)
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, 3)  # Summarize into 3 sentences

        # Prepare the summary text
        summary_text = " ".join(str(sentence) for sentence in summary)

        # Return the summary as JSON response
        return jsonify({"summary": summary_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
