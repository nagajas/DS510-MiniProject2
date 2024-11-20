from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from PIL import Image
from tqdm import tqdm
import cv2
import torch
from transformers import (
    ViTImageProcessor,
    GPT2TokenizerFast,
    VisionEncoderDecoderModel,
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)
from IndicTransToolkit.IndicTransToolkit import IndicProcessor 
from gtts import gTTS
import io

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Load models and tokenizers with error handling
try:
    # Image Captioning Models
    vision_model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning").to(DEVICE)
    vision_tokenizer = GPT2TokenizerFast.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    vision_processor = ViTImageProcessor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
    
    # Indic Translation Models
    ip = IndicProcessor(inference=True)
    indic_tokenizer = AutoTokenizer.from_pretrained(
        "ai4bharat/indictrans2-en-indic-1B",
        trust_remote_code=True
    )
    indic_model = AutoModelForSeq2SeqLM.from_pretrained(
        "ai4bharat/indictrans2-en-indic-1B",
        trust_remote_code=True
    )
    
except Exception as e:
    print(f"Error loading models: {e}")
    raise e 

# Language and Audio Mappings
lang_map = {
    'English': 'eng_Latn',
    'Hindi': 'hin_Deva',
    'Tamil': 'tam_Taml',
    'Telugu': 'tel_Telu',
    'Marathi': 'mar_Maru',
    'Kannada': 'kan_Knda',
}

audio_pairs = {
    'English': 'en',
    'Hindi': 'hi',
    'Tamil': 'ta',
    'Telugu': 'te',
    'Marathi': 'mr',
    'Kannada': 'kn',
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_cap(image_file, model, tokenizer, image_processor):
    """
    Generate caption for the uploaded image using OpenCV.
    """
    try:
        # Load the image with OpenCV
        image = cv2.imread(image_file)
        if image is None:
            raise ValueError("Failed to load image with OpenCV.")

        # Convert BGR to RGB (as OpenCV loads images in BGR format)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Convert the image to a PIL Image format for the model's processor
        image = Image.fromarray(image)

        # Process the image using the model's processor
        image = image_processor(images=image, return_tensors="pt").to(DEVICE)

        # Generate the caption
        predictions = model.generate(**image, max_new_tokens=50)
        caption = tokenizer.batch_decode(predictions, skip_special_tokens=True)[0].strip().capitalize()
        return caption
    except Exception as e:
        print(f"Error generating caption: {e}")
        return None

def generate_translations(src_sentence, src_lang, tgt_lang, model, tokenizer, ip):
    try:
        # Validate source and target languages
        if not src_lang or not tgt_lang:
            raise ValueError("Invalid source or target language code")

        # Preprocess the input sentence
        batch = ip.preprocess_batch([src_sentence], src_lang=src_lang, tgt_lang=tgt_lang)

        batch = tokenizer(
            batch,
            padding="longest",
            truncation=True,
            max_length=256,
            return_tensors="pt"
        ).to(DEVICE)

        model.to(DEVICE)

        with torch.inference_mode():
            outputs = model.generate(**batch, num_beams=5, num_return_sequences=1, max_length=256)

        with tokenizer.as_target_tokenizer():
            outputs = tokenizer.batch_decode(outputs, skip_special_tokens=True, clean_up_tokenization_spaces=True)

        tgt_sentences = ip.postprocess_batch(outputs, lang=tgt_lang)

        return tgt_sentences[0]

    except ValueError as e:
        print(f"ValueError: {e}")
    except Exception as e:
        print(f"Error during translation: {e}")

    return None


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """
    Handle image upload, generate caption, translate it, and create audio narration.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected for uploading'}), 400

    # Fetch target language and validate
    target_lang = request.form.get('language', 'Hindi')
    if target_lang not in lang_map:
        return jsonify({'error': f"Unsupported language: {target_lang}"}), 400

    print(f"Target Language: {target_lang}")

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        try:
            file.save(filepath)
        except Exception as e:
            print(f"Error saving file: {e}")
            return jsonify({'error': 'Failed to save the uploaded file'}), 500

        # Generate caption
        caption = generate_cap(filepath, vision_model, vision_tokenizer, vision_processor)
        if not caption:
            return jsonify({'error': 'Failed to generate caption for the image'}), 500
        print(f"Generated Caption: {caption}")

        # Translate caption
        print(f"Translating caption to {target_lang}")
        translated = generate_translations(
            caption,
            'eng_Latn',
            lang_map[target_lang],
            indic_model,
            indic_tokenizer,
            ip
        )
        if not translated:
            return jsonify({'error': 'Failed to translate the caption'}), 500
        print(f"Translated Caption: {translated}")

        # Generate audio narration
        audio_file = f"{os.path.splitext(filename)[0]}_audio_{target_lang}.mp3"
        audio_path = os.path.join(app.config['UPLOAD_FOLDER'], audio_file)

        tts_text = translated if target_lang != 'English' else caption
        tts = gTTS(text=tts_text, 
                   lang=audio_pairs.get(target_lang,'en'),
                    slow=False)
        audio_data = io.BytesIO()
        tts.write_to_fp(audio_data)
        audio_data.seek(0)

        with open(audio_path, 'wb') as f:
            f.write(audio_data.read())

        # Construct response
        response = {
            'filename': filename,
            'caption': caption,
            'translated': translated if target_lang != 'English' else caption,
            'audio_file': audio_file
        }
        return jsonify(response), 200

    else:
        return jsonify({'error': 'Allowed file types are png, jpg, jpeg'}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)