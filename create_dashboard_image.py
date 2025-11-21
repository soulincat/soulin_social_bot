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
    
    # Center text in container (at top)
    text_x = container_x + (container_size - text_width) // 2
    text_y = container_y + int(container_size * 0.15)  # Position near top
    
    # Draw text (text-primary: #f8fafc)
    text_color = (248, 250, 252, 255)  # #f8fafc
    draw.text((text_x, text_y), text, font=font, fill=text_color)
    
    # Add mini-boxes for "Fans" and "Earn" below the text
    # Mini-box styling: glassmorphism with rgba(255, 255, 255, 0.08), border-radius: 16px
    mini_box_width = int(container_size * 0.42)  # Each box is about 42% of container width
    mini_box_height = 120
    mini_box_spacing = int(container_size * 0.06)  # 6% spacing between boxes
    mini_box_y = text_y + text_height + 40  # Position below text
    
    # Calculate positions for two boxes side by side
    total_boxes_width = (mini_box_width * 2) + mini_box_spacing
    boxes_start_x = container_x + (container_size - total_boxes_width) // 2
    
    # Create mini-boxes
    for i, (label, value, subtitle, trend) in enumerate([
        ("Fans", "$12,450", "Monthly Total", "+18.5% MoM"),
        ("Earn", "$8,920", "Monthly Total", "+22.3% MoM")
    ]):
        box_x = boxes_start_x + i * (mini_box_width + mini_box_spacing)
        box_y = mini_box_y
        
        # Create mini-box with glassmorphism
        mini_box_overlay = Image.new('RGBA', (mini_box_width, mini_box_height), (255, 255, 255, int(255 * 0.08)))
        mini_box_blurred = base.crop((box_x, box_y, box_x + mini_box_width, box_y + mini_box_height))
        mini_box_blurred = mini_box_blurred.filter(ImageFilter.GaussianBlur(radius=6))
        
        # Create mini-box mask with rounded corners (16px radius)
        mini_mask = Image.new('L', (mini_box_width, mini_box_height), 0)
        mini_mask_draw = ImageDraw.Draw(mini_mask)
        mini_mask_draw.rounded_rectangle(
            [(0, 0), (mini_box_width, mini_box_height)],
            radius=16,
            fill=255
        )
        
        # Composite mini-box
        mini_box_composite = Image.new('RGBA', (mini_box_width, mini_box_height), (0, 0, 0, 0))
        mini_box_composite = Image.alpha_composite(mini_box_composite, mini_box_blurred)
        mini_box_composite = Image.alpha_composite(mini_box_composite, mini_box_overlay)
        mini_box_composite.putalpha(mini_mask)
        
        # Paste mini-box
        base.paste(mini_box_composite, (box_x, box_y), mini_box_composite)
        
        # Draw border (rgba(255, 255, 255, 0.15))
        mini_draw = ImageDraw.Draw(base)
        mini_draw.rounded_rectangle(
            [box_x, box_y, box_x + mini_box_width, box_y + mini_box_height],
            radius=16,
            outline=(255, 255, 255, int(255 * 0.15)),
            width=1
        )
        
        # Add text content to mini-box
        # Label (smaller font)
        label_font_size = 14
        try:
            label_font = ImageFont.truetype(inter_path, label_font_size) if os.path.exists(inter_path) else font
        except:
            label_font = ImageFont.load_default()
        
        label_bbox = mini_draw.textbbox((0, 0), label, font=label_font)
        label_text_width = label_bbox[2] - label_bbox[0]
        label_x = box_x + 16  # Padding
        label_y = box_y + 16
        mini_draw.text((label_x, label_y), label, font=label_font, fill=(168, 178, 209, 255))  # #a8b2d1 (text-muted)
        
        # Value (larger, bold)
        value_font_size = 28
        try:
            value_font = ImageFont.truetype(inter_path, value_font_size) if os.path.exists(inter_path) else font
        except:
            value_font = ImageFont.load_default()
        
        value_bbox = mini_draw.textbbox((0, 0), value, font=value_font)
        value_text_width = value_bbox[2] - value_bbox[0]
        value_x = box_x + 16
        value_y = label_y + 24
        mini_draw.text((value_x, value_y), value, font=value_font, fill=text_color)
        
        # Subtitle
        subtitle_font_size = 12
        try:
            subtitle_font = ImageFont.truetype(inter_path, subtitle_font_size) if os.path.exists(inter_path) else font
        except:
            subtitle_font = ImageFont.load_default()
        
        subtitle_x = box_x + 16
        subtitle_y = value_y + 28
        mini_draw.text((subtitle_x, subtitle_y), subtitle, font=subtitle_font, fill=(168, 178, 209, 255))
        
        # Trend (green for up)
        trend_font_size = 12
        try:
            trend_font = ImageFont.truetype(inter_path, trend_font_size) if os.path.exists(inter_path) else font
        except:
            trend_font = ImageFont.load_default()
        
        trend_bbox = mini_draw.textbbox((0, 0), trend, font=trend_font)
        trend_text_width = trend_bbox[2] - trend_bbox[0]
        trend_x = box_x + mini_box_width - trend_text_width - 16
        trend_y = subtitle_y
        mini_draw.text((trend_x, trend_y), trend, font=trend_font, fill=(34, 197, 94, 255))  # #22c55e (success green)
    
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

