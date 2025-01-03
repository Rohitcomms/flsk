from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled


from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # Enable CORS for all domains

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

        # Extract video ID from the URL
        if "v=" in youtube_url:
            video_id = youtube_url.split("v=")[-1].split("&")[0]
        elif "youtu.be/" in youtube_url:
            video_id = youtube_url.split("youtu.be/")[-1]
        else:
            return jsonify({"error": "Invalid YouTube URL format"}), 400

        # Fetch the transcript from YouTube
        try:
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        except NoTranscriptFound:
            return jsonify({"error": "No transcript found for this video. Subtitles may not be available in English."}), 400
        except TranscriptsDisabled:
            return jsonify({"error": "Subtitles are disabled for this video."}), 400
        except Exception as e:
            return jsonify({"error": f"Failed to fetch transcript: {str(e)}"}), 500
        # Prepare transcript text for summarization
        transcript_text = " ".join([item['text'] for item in transcript])

        # Summarize the transcript using LSA summarizer
        parser = PlaintextParser.from_string(transcript_text, PlaintextParser.SENTENCE_TOKENIZER)
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
