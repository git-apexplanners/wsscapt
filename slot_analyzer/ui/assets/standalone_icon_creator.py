"""Standalone script to create a simple hacker-style icon for the application."""

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise

import os
from pathlib import Path

def create_icon():
    """Create a simple hacker-style icon."""
    # Create a new image with a black background
    img_size = 256
    img = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw a dark background with a green border
    border_width = 4
    draw.rectangle(
        [(border_width, border_width), (img_size - border_width, img_size - border_width)],
        fill=(10, 10, 10, 255),
        outline=(0, 255, 65, 255),
        width=border_width
    )
    
    # Draw a simple slot machine symbol
    try:
        # Try to use a default font
        font = ImageFont.load_default()
        
        # Draw text
        text = "S"
        text_width, text_height = draw.textbbox((0, 0), text, font=font)[2:4]
        position = ((img_size - text_width) // 2, (img_size - text_height) // 2 - 10)
        draw.text(position, text, fill=(0, 255, 65, 255), font=font)
        
        # Draw binary-like pattern at the bottom
        binary = "10101010"
        binary_width, binary_height = draw.textbbox((0, 0), binary, font=font)[2:4]
        binary_position = ((img_size - binary_width) // 2, img_size - binary_height - 20)
        draw.text(binary_position, binary, fill=(0, 255, 65, 255), font=font)
        
    except Exception as e:
        # Draw a simple symbol if text fails
        center = img_size // 2
        radius = img_size // 4
        draw.ellipse(
            [(center - radius, center - radius), (center + radius, center + radius)],
            outline=(0, 255, 65, 255),
            width=4
        )
    
    # Save the image as PNG
    assets_dir = Path(__file__).parent
    img.save(assets_dir / "icon.png")
    
    # Try to save as ICO
    try:
        img.save(assets_dir / "icon.ico", format="ICO", sizes=[(32, 32), (64, 64), (128, 128), (256, 256)])
    except Exception as e:
        pass
if __name__ == "__main__":
    create_icon()
