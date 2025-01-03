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
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[-1]
        else:
            return jsonify({"error": "Invalid YouTube URL"}), 400

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

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

