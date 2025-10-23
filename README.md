# 📖 PDF to Audiobook Converter

Convert your study materials and scientific papers into high-quality audiobooks that you can listen to for hours!

## ✨ Features

- **Easy to use**: Just drop PDFs in a folder and run
- **High quality**: Uses Kokoro-82M, specifically designed for audiobook narration
- **CPU-only**: No GPU required, runs on any computer
- **Fast**: Direct PDF text extraction (no slow OCR needed for most PDFs)
- **Smart**: Automatically handles scanned PDFs if OCR is installed
- **Natural voice**: Pleasant, clear voice perfect for long listening sessions

## 🚀 Quick Start

### 1. Install Python

Make sure you have Python 3.8 or newer installed:
```bash
python --version
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: If you have scanned/image-based PDFs, also install OCR support:
- Windows: Download Tesseract from [here](https://github.com/UB-Mannheim/tesseract/wiki)
- Mac: `brew install tesseract`
- Linux: `sudo apt-get install tesseract-ocr`

Then uncomment the OCR lines in `requirements.txt` and run `pip install -r requirements.txt` again.

### 3. Add Your PDFs

Put your PDF files in the `input` folder (it will be created automatically).

### 4. Run the Converter

```bash
python pdf_to_audiobook.py
```

### 5. Get Your Audiobooks

Find your MP3 audiobooks in the `output` folder!

## 📁 Folder Structure

```
studytoaudiobook/
├── pdf_to_audiobook.py    # Main script
├── requirements.txt        # Dependencies
├── README.md              # This file
├── input/                 # Put your PDF files here
└── output/                # Your audiobooks will appear here
```

## 🎯 How It Works

1. **Text Extraction**: Reads text directly from PDFs (super fast!)
2. **Text Cleaning**: Prepares text for natural speech
3. **Voice Synthesis**: Converts to speech using Kokoro (audiobook-quality voice)
4. **Audio Export**: Saves as high-quality MP3 files

## 🔧 Advanced Options

### Change Voice Speed

Edit the script and find this line:
```python
audio_data = generate(chunk, voice='af_bella', speed=1.0)
```

Change `speed` to:
- `0.9` for slower (more comprehension time)
- `1.1` for faster (save time)
- `1.0` is natural speed (recommended)

### Different Voice

Kokoro supports multiple voices. Change `voice='af_bella'` to:
- `'af_bella'` - Clear female voice (default, great for audiobooks)
- `'af_sarah'` - Alternative female voice
- `'am_adam'` - Male voice
- `'am_michael'` - Alternative male voice

## ❓ Troubleshooting

### "No PDF files found"
- Make sure your PDF files are in the `input` folder
- Check that files end with `.pdf`

### "Very little text found"
- Your PDF might be scanned/image-based
- Install OCR support (see Quick Start step 2)

### "Out of memory"
- Close other applications
- Process one PDF at a time (remove others from input folder temporarily)

### Audio sounds robotic
- This is normal for very technical text with lots of equations/symbols
- Try cleaning up the PDF text manually for better results

## 💡 Tips

- **Best for**: Scientific papers, textbooks, articles with regular text
- **Quality**: Works best with PDFs that have selectable text (not scanned images)
- **Duration**: A 20-page paper typically produces 15-30 minutes of audio
- **File size**: MP3 files are about 1-2 MB per minute of audio

## 🎓 Perfect For

- Study materials for exams
- Research papers
- Academic articles
- Technical documentation
- Long-form reading materials

## 📝 License

Free to use for personal and educational purposes.

## 🆘 Support

If you encounter issues:
1. Check that all dependencies are installed
2. Make sure your PDF has extractable text
3. Try with a different PDF to isolate the problem

## 🌟 Why This Solution?

- **Kokoro-82M**: Specifically trained for audiobook narration (not just generic TTS)
- **CPU-optimized**: Uses ONNX runtime for fast CPU inference
- **Small model**: Only 82M parameters, downloads quickly, runs anywhere
- **Natural speech**: Proper pacing, intonation, and breathing for long listening
- **No cloud**: Everything runs locally on your computer, completely private

Enjoy your audiobooks! 🎧
