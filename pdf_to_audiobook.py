#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF to Audiobook Converter
Converts PDF study materials to high-quality MP3 audiobooks using CPU-only inference.
Perfect for scientific papers and long-form listening.
"""

import os
import sys
from pathlib import Path
import PyPDF2
from pydub import AudioSegment
from kokoro import KPipeline
import numpy as np
from tqdm import tqdm
import time
import warnings
warnings.filterwarnings('ignore')

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Try to import OCR libraries
try:
    from paddleocr import PaddleOCR
    from pdf2image import convert_from_path
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    print("Note: OCR not available. Install paddleocr for image/scanned PDF support.")


class PDFToAudiobook:
    def __init__(self, input_dir="input", output_dir="output"):
        """
        Initialize converter with input/output directories.

        Args:
            input_dir: Folder containing PDF files
            output_dir: Folder where MP3 files will be saved
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)

        # Create directories if they don't exist
        self.input_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)

        print(f"✓ Input folder: {self.input_dir.absolute()}")
        print(f"✓ Output folder: {self.output_dir.absolute()}")

        # Initialize Kokoro TTS pipeline (CPU-only)
        print(f"\n⏳ Setting up text-to-speech engine...")
        print(f"   (First time? This downloads voice files - only happens once!)")
        self.pipeline = KPipeline(lang_code='a', device='cpu')

        # Initialize PaddleOCR for image/scanned document support (CPU-only)
        if OCR_AVAILABLE:
            print(f"\n⏳ Setting up image reader (for photos and scans)...")
            print(f"   (First time? Downloading reading models - only happens once!)")
            # PaddleOCR defaults to CPU mode, just specify language
            self.ocr = PaddleOCR(lang='en')
            print(f"✓ Image reader ready!")
        else:
            self.ocr = None

        print(f"\n✓ All set! Ready to convert your documents to audiobooks!")

    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from PDF using direct parsing (fast, CPU-only).
        Falls back to OCR if no text is found.

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text as string
        """
        print(f"\n📄 Processing: {pdf_path.name}")
        text = ""

        try:
            # Try direct text extraction first (works for 95% of PDFs)
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                print(f"   Total pages: {total_pages}")

                # Progress bar for extracting text
                print(f"   Extracting text from PDF...")
                with tqdm(total=total_pages, desc="   Reading pages",
                         bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} pages',
                         ncols=80) as pbar:
                    for page in pdf_reader.pages:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text += f"\n\n{page_text}"
                        pbar.update(1)

                print(f"   ✓ Finished reading PDF!")

        except Exception as e:
            print(f"   ⚠ Error during text extraction: {e}")
            return None

        # Check if we got meaningful text
        if len(text.strip()) < 100:
            print(f"   ⚠ Very little text found ({len(text)} chars)")

            if OCR_AVAILABLE:
                print(f"   🔍 Attempting OCR (this may take a while)...")
                text = self._ocr_fallback(pdf_path)
            else:
                print(f"   ⚠ OCR not available. Install pytesseract for scanned PDFs.")
                return None

        return text

    def _ocr_fallback(self, pdf_path):
        """
        Fallback OCR method for scanned PDFs (CPU-only using PaddleOCR).

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text as string
        """
        if not self.ocr:
            print(f"   ⚠️  OCR not available. Install paddleocr to read scanned documents.")
            return ""

        try:
            print(f"   Converting PDF pages to images...")
            images = convert_from_path(pdf_path)
            text = ""

            print(f"   Reading scanned pages (this takes longer)...")
            with tqdm(total=len(images), desc="   Scanning pages",
                     bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} pages',
                     ncols=80) as pbar:
                for i, image in enumerate(images):
                    # Save temp image for PaddleOCR
                    temp_path = f"temp_page_{i}.png"
                    image.save(temp_path)

                    try:
                        result = self.ocr.predict(temp_path)

                        # Extract text from OCR result (new PaddleOCR API format)
                        if result and 'text_recognition' in result:
                            texts = result['text_recognition'].get('text', [])
                            if texts:
                                page_text = '\n'.join(texts)
                                text += f"\n\n{page_text}"
                    finally:
                        # Clean up temp file
                        if os.path.exists(temp_path):
                            os.remove(temp_path)

                    pbar.update(1)

            print(f"   ✓ Scanned document processed!")
            return text

        except Exception as e:
            print(f"   ⚠️  Error reading scanned pages: {e}")
            return ""

    def extract_text_from_image(self, image_path):
        """
        Extract text from image files (JPEG, PNG, etc.) using PaddleOCR.

        Args:
            image_path: Path to image file

        Returns:
            Extracted text as string
        """
        if not self.ocr:
            print(f"   ⚠️  Image reading not available. Install paddleocr to read images.")
            return None

        print(f"\n📷 Processing image: {image_path.name}")
        text = ""

        try:
            print(f"   Reading text from image...")
            # PaddleOCR can work with file path directly
            result = self.ocr.predict(str(image_path))

            # Extract text from OCR result (new PaddleOCR API format)
            if result and 'text_recognition' in result:
                texts = result['text_recognition'].get('text', [])
                if texts:
                    text = '\n'.join(texts)
                    print(f"   ✓ Text extracted from image!")
                else:
                    print(f"   ⚠️  No text found in this image")
                    return None
            else:
                print(f"   ⚠️  No text found in this image")
                return None

        except Exception as e:
            print(f"   ⚠️  Error reading image: {e}")
            return None

        return text

    def clean_text_for_speech(self, text):
        """
        Clean and prepare text for natural speech synthesis.

        Args:
            text: Raw extracted text

        Returns:
            Cleaned text suitable for TTS
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())

        # Split into sentences for better pacing
        # This helps with natural pauses and breathing
        sentences = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                sentences.append(line)

        return '\n'.join(sentences)

    def text_to_speech(self, text, output_path):
        """
        Convert text to speech using Kokoro-82M (CPU-optimized audiobook model).

        Args:
            text: Text to convert
            output_path: Path to save MP3 file
        """
        print(f"\n🎙️  Converting text to audio...")

        # Split text into manageable chunks (Kokoro handles ~1000 chars well)
        chunk_size = 1000
        chunks = []

        # Split by sentences to avoid cutting mid-sentence
        sentences = text.split('\n')
        current_chunk = ""

        for sentence in sentences:
            if len(current_chunk) + len(sentence) < chunk_size:
                current_chunk += sentence + "\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                current_chunk = sentence + "\n"

        if current_chunk:
            chunks.append(current_chunk)

        print(f"   Preparing {len(chunks)} audio segments...")

        # Estimate time (very rough - about 1-3 seconds per chunk on CPU)
        estimated_minutes = (len(chunks) * 2) / 60
        if estimated_minutes > 1:
            print(f"   ⏱️  This might take around {estimated_minutes:.0f} minutes (grab a coffee!)")

        # Generate audio for each chunk
        audio_segments = []

        # Nice progress bar for audio generation
        with tqdm(total=len(chunks), desc="   Creating audio",
                 bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} segments',
                 ncols=80) as pbar:
            for chunk in chunks:
                try:
                    # Generate audio using Kokoro KPipeline
                    # Using voice 'af_bella' - clear, pleasant female voice great for audiobooks
                    results = list(self.pipeline(chunk, voice='af_bella', speed=1.0))

                    # Combine all audio outputs from the generator
                    for result in results:
                        if result.output and result.output.audio is not None:
                            # Get the audio tensor
                            audio_tensor = result.output.audio

                            # Convert tensor to numpy array and then to int16
                            audio_np = audio_tensor.cpu().numpy()
                            audio_int16 = (audio_np * 32767).astype(np.int16)

                            # Convert to AudioSegment
                            # Kokoro outputs 24kHz 16-bit audio
                            audio_seg = AudioSegment(
                                audio_int16.tobytes(),
                                frame_rate=24000,
                                sample_width=2,
                                channels=1
                            )

                            audio_segments.append(audio_seg)

                    # Add a brief pause between segments for natural flow
                    silence = AudioSegment.silent(duration=400)  # 400ms pause
                    audio_segments.append(silence)

                    pbar.update(1)

                except Exception as e:
                    print(f"\n   ⚠ Error generating audio for chunk: {e}")
                    pbar.update(1)
                    continue

        print(f"   ✓ Audio generation complete!")

        # Combine all segments
        print(f"   📝 Stitching all audio together...")
        final_audio = sum(audio_segments)

        # Export as MP3
        print(f"   💾 Saving your audiobook (high quality MP3)...")
        final_audio.export(
            output_path,
            format="mp3",
            bitrate="128k",
            parameters=["-q:a", "2"]  # High quality
        )

        # Calculate duration
        duration_minutes = len(final_audio) / 1000 / 60
        duration_hours = duration_minutes / 60
        file_size_mb = output_path.stat().st_size / 1024 / 1024

        print(f"\n   ✅ SUCCESS! Your audiobook is ready!")
        print(f"   📁 File: {output_path.name}")
        if duration_hours >= 1:
            print(f"   ⏱️  Length: {duration_hours:.1f} hours ({duration_minutes:.0f} minutes)")
        else:
            print(f"   ⏱️  Length: {duration_minutes:.1f} minutes")
        print(f"   📊 Size: {file_size_mb:.1f} MB")

    def convert_pdf(self, pdf_path):
        """
        Convert a single PDF to audiobook MP3.

        Args:
            pdf_path: Path to PDF file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract text
            text = self.extract_text_from_pdf(pdf_path)

            if not text or len(text.strip()) < 50:
                print(f"   ⚠️  Not enough text found in this PDF to make an audiobook")
                return False

            # Clean text
            print(f"   📝 Preparing text for natural speech...")
            text = self.clean_text_for_speech(text)

            # Generate output filename
            output_filename = pdf_path.stem + ".mp3"
            output_path = self.output_dir / output_filename

            # Convert to speech
            self.text_to_speech(text, output_path)

            return True

        except Exception as e:
            print(f"\n   ❌ Error: {e}")
            print(f"   Could not convert {pdf_path.name}")
            return False

    def convert_image(self, image_path):
        """
        Convert a single image to audiobook MP3.

        Args:
            image_path: Path to image file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Extract text from image
            text = self.extract_text_from_image(image_path)

            if not text or len(text.strip()) < 50:
                print(f"   ⚠️  Not enough text found in this image to make an audiobook")
                return False

            # Clean text
            print(f"   📝 Preparing text for natural speech...")
            text = self.clean_text_for_speech(text)

            # Generate output filename
            output_filename = image_path.stem + ".mp3"
            output_path = self.output_dir / output_filename

            # Convert to speech
            self.text_to_speech(text, output_path)

            return True

        except Exception as e:
            print(f"\n   ❌ Error: {e}")
            print(f"   Could not convert {image_path.name}")
            return False

    def process_all(self):
        """
        Process all PDF and image files in the input directory.
        """
        # Find all supported files
        pdf_files = list(self.input_dir.glob("*.pdf"))
        image_files = []

        # Only look for images if OCR is available
        if OCR_AVAILABLE:
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.bmp', '*.tiff', '*.tif']:
                image_files.extend(self.input_dir.glob(ext))

        all_files = pdf_files + image_files

        if not all_files:
            print(f"\n⚠️  No files found!")
            print(f"   📂 Looking in: {self.input_dir.absolute()}")
            print(f"\n   💡 How to use:")
            print(f"      1. Put your PDF files or images in the 'input' folder")
            if OCR_AVAILABLE:
                print(f"         Supported: PDF, JPG, JPEG, PNG, BMP, TIFF")
            else:
                print(f"         Supported: PDF only (install paddleocr for image support)")
            print(f"      2. Run this program again")
            print(f"      3. Find your audiobooks in the 'output' folder")
            return

        file_summary = []
        if pdf_files:
            file_summary.append(f"{len(pdf_files)} PDF file(s)")
        if image_files:
            file_summary.append(f"{len(image_files)} image file(s)")

        print(f"\n📚 Found {' and '.join(file_summary)} to convert")
        print("=" * 70)

        successful = 0
        failed = 0

        for i, file_path in enumerate(all_files, 1):
            print(f"\n{'='*70}")
            print(f"📄 File {i} of {len(all_files)}: {file_path.name}")
            print(f"{'='*70}")

            # Determine file type and process accordingly
            if file_path.suffix.lower() == '.pdf':
                success = self.convert_pdf(file_path)
            else:
                # It's an image file
                success = self.convert_image(file_path)

            if success:
                successful += 1
            else:
                failed += 1

        # Summary
        print("\n" + "=" * 70)
        print(f"🎉 ALL DONE!")
        print(f"=" * 70)
        print(f"   ✅ Successfully converted: {successful} audiobook(s)")
        if failed > 0:
            print(f"   ❌ Failed: {failed} file(s)")
        print(f"\n   📂 Your audiobooks are here:")
        print(f"      {self.output_dir.absolute()}")
        print(f"\n   🎧 Enjoy listening!")


def main():
    """Main entry point for the script."""
    print("=" * 70)
    print("🎧 PDF TO AUDIOBOOK CONVERTER")
    print("=" * 70)
    print("   Turn any PDF into a high-quality audiobook!")
    print("   Just sit back and let your computer do the work...")
    print("=" * 70)

    # Create converter
    converter = PDFToAudiobook(input_dir="input", output_dir="output")

    # Process all PDFs
    converter.process_all()


if __name__ == "__main__":
    main()
