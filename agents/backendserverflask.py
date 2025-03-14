from flask import Flask, request, jsonify
from transformers import pipeline

app = Flask(__name__)

# Load Hugging Face summarization model
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def trim_middle_text(text, trim_ratio=0.5):
    """
    Trims the middle portion of the text based on the given ratio.
    Returns the trimmed version only.
    """
    words = text.split()
    total_words = len(words)
    
    if total_words <= 150:  
        return text  # No need to trim if it's already short
    
    # Calculate trimming size
    trim_size = int(total_words * trim_ratio)
    start_trim = (total_words - trim_size) // 2
    end_trim = start_trim + trim_size

    return " ".join(words[start_trim:end_trim])  # Return only trimmed text

@app.route('/validate_audio', methods=['POST'])
def process_text():
    """
    API Endpoint: Accepts JSON input with 'text' and 'length'.
    Trims & summarizes only if the estimated length exceeds 60 seconds.
    """
    data = request.get_json()
    text = data.get("text", "")
    estimated_length = data.get("length", 0)

    if not text:
        return jsonify({"error": "Text field is required"}), 400

    # If length is within limit, return original text
    if estimated_length <= 60:
        return jsonify({"message": text})

    # Otherwise, trim and summarize
    trimmed_text = trim_middle_text(text)
    summarized_text = summarizer(trimmed_text, max_length=100, min_length=50, do_sample=False)[0]['summary_text']

    return jsonify({"message": summarized_text})

if __name__ == '__main__':
    app.run(debug=True)
