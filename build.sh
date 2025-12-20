#!/bin/bash
# Build script for Quarto website with performance optimizations

set -e

echo "Building Quarto website..."
quarto render

echo "Optimizing HTML files for performance..."
python3 optimize_html.py

echo "Build complete! Optimized files are in the docs/ directory."




