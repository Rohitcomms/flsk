from flask import Flask, request, jsonify
from pytube import YouTube
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

app = Flask(__name__)

LANGUAGE = "english"
SENTENCES_COUNT = 5

def summarize_text(text, sentence_count):
    parser = PlaintextParser.from_string(text, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)
    summarizer = LsaSummarizer(stemmer)
    summarizer.stop_words = get_stop_words(LANGUAGE)
    summary = summarizer(parser.document, sentence_count)
    return " ".join(str(sentence) for sentence in summary)

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    if not data or 'youtube_url' not in data:
        return jsonify({'error': 'Please provide a YouTube URL in the request body.'}), 400
    
    youtube_url = data['youtube_url']
    
    try:
        yt = YouTube(youtube_url)
        captions = yt.captions.get_by_language_code('en')
        
        if not captions:
            return jsonify({'error': 'No English captions available for this video.'}), 400
        
        transcript = captions.generate_srt_captions()
        summarized_text = summarize_text(transcript, SENTENCES_COUNT)
        
        return jsonify({
            'video_title': yt.title,
            'summary': summarized_text
        })
    except Exception as e:
        return jsonify({'error': 'Failed to process the YouTube URL. Please ensure it is correct.', 'details': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
