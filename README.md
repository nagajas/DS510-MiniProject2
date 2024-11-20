# DS510 : Artificial Intelligence and Machine Learning Lab
## Mini Project - 02

This project is a Flask-based web application that allows users to upload images, generate captions for those images, translate the captions into various languages, and create audio narrations of the translated captions.

The application uses a pre-trained VisionEncoderDecoderModel to generate captions for uploaded images and the IndicTrans2 model to translate the captions into multiple languages. The audio narrations are generated using Google Text-to-Speech (gTTS).

![Web UI](assets/website.png)

## Features

- **Image Upload**: Users can upload images in `png`, `jpg`, or `jpeg` formats.
- **Caption Generation**: Automatically generate captions for uploaded images using a pre-trained VisionEncoderDecoderModel.
- **Translation**: Translate the generated captions into multiple languages using the IndicTrans2 model.
- **Audio Narration**: Generate audio narrations of the translated captions using Google Text-to-Speech (gTTS).

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/nagajas/DS510-MiniProject2.git
    cd DS510-MiniProject2
    ```

2. Create and activate a virtual environment:
    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Clone the IndicTransToolkit for Machine Translation
    ```sh
    git clone https://github.com/VarunGumma/IndicTransToolkit
    ```

4. Install the required dependencies:
    - When using python version >= 3.9 (recommended):
    ```sh
    pip install -r requirements_py3.9+.txt
    ```
    - When using python < 3.9:
    ```sh
    pip install -r requirements.txt
    ```

## Usage

1. Start the Flask application:
    ```sh
    python app.py
    ```

2. Open your web browser and navigate to `http://localhost:3000` to run the website locally.

3. Use the web UI to upload an image, select a target language, and generate the caption, translation, and audio narration.

## Configuration

- **UPLOAD_FOLDER**: Directory where uploaded files are stored. Default is `static/uploads`.
- **MAX_CONTENT_LENGTH**: Maximum allowed size for uploaded files. Default is `16MB`.

## Supported Languages

The application supports the following languages for translation and audio narration:

- English
- Hindi
- Tamil
- Telugu
- Marathi
- Kannada

![Language Selection](assets/langs.png)

You can select the target language from the dropdown menu on the web UI.

## File Structure

```
DS510-MiniProject2/
├── app.py
├── frontend/
|   ├── App.js
|   └── App.css
├── requirements.txt
├── static/
│   └── uploads/
└── README.md
```

## Dependencies

- Flask
- Flask-Cors
- OpenCV
- Torch
- Transformers
- gTTS
- PIL
- TQDM

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Hugging Face](https://huggingface.co/) for the pre-trained models.
- [Google Text-to-Speech](https://pypi.org/project/gTTS/) for audio narration.
- [OpenCV](https://opencv.org/) for image processing.
