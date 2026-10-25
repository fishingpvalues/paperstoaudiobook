# paperstoaudiobook

Converts PDFs and images in the `input/` folder to MP3 files in `output/`, using
Kokoro (82M parameter TTS model) for the voice. Runs on CPU.

Text is taken directly from the PDF with PyPDF2. If a PDF has no extractable text, or
the input is an image (`.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`, `.tif`), the script
falls back to OCR with PaddleOCR (English). The text is cleaned, split into chunks,
synthesised with the voice `af_bella` at speed 1.0, and exported as MP3 with pydub.

## Install

Python 3.8 or newer. pydub needs `ffmpeg` on the PATH, and pdf2image needs
`poppler` for the OCR fallback on PDFs.

```bash
pip install -r requirements.txt
```

The Kokoro voice files are downloaded on first run.

## Run

```bash
python pdf_to_audiobook.py
```

Put files in `input/` first. `input/` and `output/` are created if missing, and are
ignored by git.

## Options

Voice and speed are hard-coded in `text_to_speech()` in `pdf_to_audiobook.py`:

```python
self.pipeline(chunk, voice='af_bella', speed=1.0)
```

Other Kokoro voices such as `af_sarah`, `am_adam` and `am_michael` can be substituted.

## Layout

```
paperstoaudiobook/
├── pdf_to_audiobook.py
├── requirements.txt
├── input/                 # PDFs and images to convert
├── output/                # generated MP3 files
├── HOW_TO_USE.txt         # step-by-step guide for non-programmers
├── QUICK_START.txt
├── START_HERE.md
└── TECHNICAL_DECISIONS.md # why Kokoro and PaddleOCR
```

## Limitations

- English only (voice and OCR model).
- Equations and symbols are read out poorly.
- Quality depends on the text layer of the PDF.

## License

MIT, see `LICENSE`.
