#!/bin/bash
# convert_images.sh
# Requires 'webp' package (sudo apt install webp)

FRONTEND_PUBLIC_DIR="/home/meto/Desktop/Projects/TechEventRadarAdmin/frontend/public"

echo "Converting images in $FRONTEND_PUBLIC_DIR to WebP..."

cd "$FRONTEND_PUBLIC_DIR" || exit

# Convert PNG to WebP
for f in *.png; do
    if [ -f "$f" ]; then
        echo "Converting $f to ${f%.png}.webp"
        cwebp -q 80 "$f" -o "${f%.png}.webp"
    fi
done

# Convert JPEG/JPG to WebP
for f in *.jpeg *.jpg; do
    if [ -f "$f" ]; then
        echo "Converting $f to ${f%.*}.webp"
        cwebp -q 80 "$f" -o "${f%.*}.webp"
    fi
done

# Convert SVG to WebP (Optional, but user requested)
# Note: cwebp doesn't handle SVG. Using 'magick' if available, otherwise skip.
if command -v magick &> /dev/null; then
    for f in *.svg; do
        if [ -f "$f" ]; then
            echo "Converting $f to ${f%.svg}.webp"
            magick "$f" "${f%.svg}.webp"
        fi
    done
else
    echo "ImageMagick not found, skipping SVG to WebP conversion."
fi

echo "Done!"
