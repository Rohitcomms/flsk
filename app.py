from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer

app = Flask(__name__)

@app.route('/')
def home():
    return "Server is running!"

@app.route('/summarize', methods=['POST'])
def summarize_video():
    try:
        data = request.get_json()
        youtube_url = data.get("url")
        if not youtube_url:
            return jsonify({"error": "No YouTube URL provided"}), 400

        # Extract video ID
        video_id = youtube_url.split("v=")[-1]

        # Fetch the transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        transcript_text = " ".join([item['text'] for item in transcript])

        # Summarize the transcript
        parser = PlaintextParser.from_string(transcript_text, PlaintextParser.URN_MODE)
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, 3)

        # Prepare the summary text
        summary_text = " ".join(str(sentence) for sentence in summary)
        return jsonify({"summary": summary_text})

    except 
