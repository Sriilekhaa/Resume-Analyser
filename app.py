from flask import Flask, render_template, request, redirect, url_for
import os
from analyzer import extract_text_from_file, analyze_resume_with_meta_ai

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'resume' not in request.files:
        return redirect(request.url)

    file = request.files['resume']
    if file.filename == '':
        return redirect(request.url)

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(file_path)

    resume_text = extract_text_from_file(file_path)
    result_json = analyze_resume_with_meta_ai(resume_text)

    import json
    analysis = json.loads(result_json)

    # return render_template('result.html', analysis=analysis)
    return analysis

if __name__ == '__main__':
    app.run(debug=True)
