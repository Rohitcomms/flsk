from flask import Flask, request, jsonify
from pytube import YouTube
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

        video = YouTube(youtube_url)
        transcript = video.captions.get_by_language_code('en').generate_srt_captions()
 
        parser = PlaintextParser.from_string(transcript, PlaintextParser.URN_MODE)
        summarizer = LsaSummarizer()
        summary = summarizer(parser.document, 3)

        summary_text = " ".join(str(sentence) for sentence in summary)
        return jsonify({"summary": summary_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=10000)
