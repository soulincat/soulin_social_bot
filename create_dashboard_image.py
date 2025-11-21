"""
Create a 4:5 image from gradient.JPG with glassmorphism container matching dashboard CSS
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
import requests
from io import BytesIO

def download_font(url, font_path):
    """Download font if not exists"""
    if not os.path.exists(font_path):
        try:
            response = requests.get(url)
            with open(font_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded font: {font_path}")
        except Exception as e:
            print(f"Could not download font: {e}")
            return False
    return True

def create_dashboard_image():
    # Load the gradient image
    gradient_path = 'web/assets/gradient.JPG'
    if not os.path.exists(gradient_path):
        print(f"Error: {gradient_path} not found")
        return
    
    # Open the gradient image
    gradient = Image.open(gradient_path).convert('RGBA')
    original_width, original_height = gradient.size
    
    # Calculate 4:5 aspect ratio dimensions
    target_width = 1200
    target_height = 1500  # 4:5 ratio
    
    # Resize the gradient to fit 4:5, focusing on black area
    # For black area focus, we'll crop from top-left or center-top to get more dark area
    gradient_ratio = original_width / original_height
    target_ratio = target_width / target_height
    
    if gradient_ratio > target_ratio:
        # Gradient is wider, crop width - focus on left side (black area)
        new_width = int(original_height * target_ratio)
        # Crop from left to focus on black area
        left = 0
        gradient = gradient.crop((left, 0, left + new_width, original_height))
    else:
        # Gradient is taller, crop height - focus on top (black area)
        new_height = int(original_width / target_ratio)
        # Crop from top to focus on black area
        top = 0
        gradient = gradient.crop((0, top, original_width, top + new_height))
    
    # Resize to target dimensions
    gradient = gradient.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Create base image
    base = Image.new('RGBA', (target_width, target_height), (0, 0, 0, 0))
    base.paste(gradient, (0, 0))
    
    # Calculate square container size (about 60% of width)
    container_size = int(target_width * 0.6)
    container_x = (target_width - container_size) // 2
    container_y = (target_height - container_size) // 2
    border_radius = 24  # Matching CSS border-radius: 24px
    
    # Create glassmorphism container
    # Glass color: rgba(255, 255, 255, 0.12)
    glass_color = (255, 255, 255, int(255 * 0.12))
    
    # Create rounded rectangle mask
    mask = Image.new('L', (container_size, container_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle(
        [(0, 0), (container_size, container_size)],
        radius=border_radius,
        fill=255
    )
    
    # Create glass overlay with blur effect
    glass_overlay = Image.new('RGBA', (container_size, container_size), glass_color)
    
    # Apply blur to simulate backdrop-filter: blur(24px)
    # Note: PIL blur is different from CSS backdrop-filter, but we'll approximate
    blurred_bg = base.crop((container_x, container_y, container_x + container_size, container_y + container_size))
    blurred_bg = blurred_bg.filter(ImageFilter.GaussianBlur(radius=8))
    
    # Composite: blurred background + glass overlay
    glass_container = Image.new('RGBA', (container_size, container_size), (0, 0, 0, 0))
    glass_container = Image.alpha_composite(glass_container, blurred_bg)
    glass_container = Image.alpha_composite(glass_container, glass_overlay)
    
    # Add gradient overlay (matching CSS: linear-gradient(120deg, rgba(255, 255, 255, 0.08), transparent 60%))
    gradient_overlay = Image.new('RGBA', (container_size, container_size), (0, 0, 0, 0))
    gradient_draw = ImageDraw.Draw(gradient_overlay)
    # Create gradient effect
    for i in range(container_size):
        alpha = int(255 * 0.08 * (1 - i / (container_size * 0.6)))
        if alpha > 0:
            gradient_draw.line([(i, 0), (i, container_size)], fill=(255, 255, 255, alpha))
    
    glass_container = Image.alpha_composite(glass_container, gradient_overlay)
    
    # Apply rounded corners
    glass_container.putalpha(mask)
    
    # Paste glass container onto base
    base.paste(glass_container, (container_x, container_y), glass_container)
    
    # Draw border (glass-stroke: rgba(255, 255, 255, 0.35))
    draw = ImageDraw.Draw(base)
    stroke_color = (255, 255, 255, int(255 * 0.35))
    
    # Draw rounded rectangle border
    # We'll approximate with multiple lines for rounded effect
    def draw_rounded_rect(draw, xy, radius, fill=None, outline=None, width=1):
        x1, y1, x2, y2 = xy
        # Draw rounded rectangle
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)
    
    draw_rounded_rect(
        draw,
        [container_x, container_y, container_x + container_size, container_y + container_size],
        radius=border_radius,
        outline=stroke_color,
        width=1
    )
    
    # Add box shadow effect (0 4px 12px rgba(0, 0, 0, 0.08))
    shadow = Image.new('RGBA', (container_size + 24, container_size + 24), (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.rounded_rectangle(
        [(12, 16), (container_size + 12, container_size + 16)],
        radius=border_radius,
        fill=(0, 0, 0, int(255 * 0.08))
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=6))
    base.paste(shadow, (container_x - 12, container_y - 12), shadow)
    base.paste(glass_container, (container_x, container_y), glass_container)
    
    # Add text "Social Funnel Dashboard" using Inter or Space Grotesk
    text = "Social Funnel Dashboard"
    font_size = 48
    
    # Try to load Inter or Space Grotesk font
    font = None
    font_paths = [
        # Try system fonts that might be similar
        "/System/Library/Fonts/Supplemental/HelveticaNeue.ttc",
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
    ]
    
    # Try to download Inter from Google Fonts
    inter_url = "https://github.com/rsms/inter/raw/master/docs/font-files/Inter-Regular.ttf"
    inter_path = "/tmp/Inter-Regular.ttf"
    
    try:
        if download_font(inter_url, inter_path):
            font = ImageFont.truetype(inter_path, font_size)
        else:
            raise Exception("Could not download Inter")
    except:
        # Fallback to system fonts
        for path in font_paths:
            try:
                if os.path.exists(path):
                    font = ImageFont.truetype(path, font_size)
                    break
            except:
                continue
    
    if font is None:
        font = ImageFont.load_default()
        print("Warning: Using default font")
    
    # Get text bounding box
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # Center text in container (vertically and horizontally centered)
    text_x = container_x + (container_size - text_width) // 2
    text_y = container_y + (container_size - text_height) // 2  # Vertically centered
    
    # Draw text (text-primary: #f8fafc)
    text_color = (248, 250, 252, 255)  # #f8fafc
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    # Convert back to RGB for JPEG
    final_image = base.convert('RGB')
    
    # Save the image
    output_path = 'web/assets/dashboard_header.jpg'
    final_image.save(output_path, 'JPEG', quality=95)
    print(f"✅ Created dashboard image: {output_path}")
    print(f"   Dimensions: {target_width}x{target_height} (4:5 ratio)")
    print(f"   Glassmorphism: rgba(255, 255, 255, 0.12) with blur")
    print(f"   Font: Inter/Space Grotesk style")
    
    return output_path

if __name__ == '__main__':
    create_dashboard_image()

