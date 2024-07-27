#!/bin/bash

# Determine the operating system
OS="$(uname -s)"

echo "Detected operating system: $OS"

install_tesseract_macos() {
    echo "Installing Tesseract OCR on macOS..."
    brew update
    brew install tesseract
}

install_tesseract_ubuntu() {
    echo "Installing Tesseract OCR on Ubuntu..."
    sudo apt-get update
    sudo apt-get install -y tesseract-ocr
}

install_tesseract_windows() {
    echo "Please install Tesseract OCR manually on Windows:"
    echo "1. Download the installer from https://github.com/UB-Mannheim/tesseract/wiki"
    echo "2. Follow the installation instructions"
    echo "3. Add the Tesseract installation path to your system PATH"
}

install_dependencies() {
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
}

case "$OS" in
    Darwin)
        install_tesseract_macos
        ;;
    Linux)
        install_tesseract_ubuntu
        ;;
    CYGWIN*|MINGW32*|MSYS*|MINGW*)
        install_tesseract_windows
        ;;
    *)
        echo "Unsupported operating system: $OS"
        exit 1
        ;;
esac

install_dependencies

echo "Setup completed."
