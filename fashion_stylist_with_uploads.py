#!/usr/bin/env python3
"""
AI Fashion Stylist with Image Uploads - No deprecated modules
This version includes image uploads without using the deprecated cgi module
"""

import os
import json
import http.server
import socketserver
import urllib.parse
import shutil
from datetime import datetime
import re

class FashionStylistHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_index_html().encode())
        elif self.path == '/wardrobe':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            wardrobe = self.load_wardrobe()
            self.wfile.write(json.dumps(wardrobe).encode())
        elif self.path.startswith('/uploads/'):
            filename = self.path[9:]  # Remove '/uploads/'
            self.serve_uploaded_file(filename)
        else:
            super().do_GET()
    
    def do_POST(self):
        if self.path == '/upload':
            self.handle_upload()
        elif self.path == '/generate-outfit':
            self.handle_generate_outfit()
        elif self.path == '/rate-outfit':
            self.handle_rate_outfit()
        else:
            self.send_error(404)
    
    def handle_upload(self):
        """Handle file upload with custom multipart parsing"""
        try:
            # Create uploads directory if it doesn't exist
            os.makedirs('uploads', exist_ok=True)
            
            # Get content type and length
            content_type = self.headers['Content-Type']
            content_length = int(self.headers['Content-Length'])
            
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Invalid content type")
                return
            
            # Read the raw POST data
            post_data = self.rfile.read(content_length)
            
            # Parse multipart data
            boundary = content_type.split('boundary=')[1]
            parts = self.parse_multipart_data(post_data, boundary)
            
            # Extract form data
            file_data = None
            form_data = {}
            
            for part in parts:
                if 'filename=' in part['headers']:
                    # This is a file
                    file_data = part
                else:
                    # This is form data
                    field_name = self.extract_field_name(part['headers'])
                    if field_name:
                        form_data[field_name] = part['data'].decode('utf-8')
            
            if not file_data:
                self.send_error(400, "No file uploaded")
                return
            
            # Save file
            filename = self.extract_filename(file_data['headers'])
            if not filename:
                filename = 'uploaded_file.jpg'
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"{timestamp}_{filename}"
            filepath = os.path.join('uploads', safe_filename)
            
            with open(filepath, 'wb') as f:
                f.write(file_data['data'])
            
            # Add to wardrobe
            wardrobe = self.load_wardrobe()
            item = {
                'id': len(wardrobe['items']) + 1,
                'filename': safe_filename,
                'filepath': filepath,
                'item_type': form_data.get('item_type', 'unknown'),
                'color': form_data.get('color', 'unknown'),
                'style': form_data.get('style', 'unknown'),
                'uploaded_at': datetime.now().isoformat()
            }
            wardrobe['items'].append(item)
            self.save_wardrobe(wardrobe)
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'message': 'File uploaded successfully',
                'item': item
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Upload failed: {str(e)}")
    
    def parse_multipart_data(self, data, boundary):
        """Parse multipart form data"""
        parts = []
        boundary_bytes = f'--{boundary}'.encode()
        
        # Split by boundary
        sections = data.split(boundary_bytes)
        
        for section in sections:
            if not section.strip():
                continue
                
            # Find the header/data separator
            header_end = section.find(b'\r\n\r\n')
            if header_end == -1:
                continue
                
            headers = section[:header_end].decode('utf-8')
            data_part = section[header_end + 4:]
            
            # Remove trailing boundary markers
            if data_part.endswith(b'\r\n'):
                data_part = data_part[:-2]
            
            parts.append({
                'headers': headers,
                'data': data_part
            })
        
        return parts
    
    def extract_field_name(self, headers):
        """Extract field name from headers"""
        match = re.search(r'name="([^"]+)"', headers)
        return match.group(1) if match else None
    
    def extract_filename(self, headers):
        """Extract filename from headers"""
        match = re.search(r'filename="([^"]+)"', headers)
        return match.group(1) if match else None
    
    def handle_generate_outfit(self):
        """Handle outfit generation"""
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            mood = data.get('mood', 'casual')
            occasion = data.get('occasion', 'daily')
            
            wardrobe = self.load_wardrobe()
            
            if not wardrobe['items']:
                self.send_error(400, "No items in wardrobe")
                return
            
            # Generate outfit
            outfit = self.generate_outfit(wardrobe['items'], mood, occasion)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            response = {
                'outfit': outfit,
                'mood': mood,
                'occasion': occasion
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Generation failed: {str(e)}")
    
    def handle_rate_outfit(self):
        """Handle outfit rating"""
        try:
            # Create uploads directory if it doesn't exist
            os.makedirs('uploads', exist_ok=True)
            
            # Get content type and length
            content_type = self.headers['Content-Type']
            content_length = int(self.headers['Content-Length'])
            
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Invalid content type")
                return
            
            # Read the raw POST data
            post_data = self.rfile.read(content_length)
            
            # Parse multipart data
            boundary = content_type.split('boundary=')[1]
            parts = self.parse_multipart_data(post_data, boundary)
            
            # Extract form data
            file_data = None
            form_data = {}
            
            for part in parts:
                if 'filename=' in part['headers']:
                    # This is a file
                    file_data = part
                else:
                    # This is form data
                    field_name = self.extract_field_name(part['headers'])
                    if field_name:
                        form_data[field_name] = part['data'].decode('utf-8')
            
            if not file_data:
                self.send_error(400, "No outfit photo uploaded")
                return
            
            # Save outfit photo
            filename = self.extract_filename(file_data['headers'])
            if not filename:
                filename = 'outfit_photo.jpg'
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_filename = f"outfit_{timestamp}_{filename}"
            filepath = os.path.join('uploads', safe_filename)
            
            with open(filepath, 'wb') as f:
                f.write(file_data['data'])
            
            # Get rating parameters
            theme = form_data.get('theme', 'casual')
            occasion = form_data.get('occasion', 'daily')
            description = form_data.get('description', '')
            
            # Generate outfit rating
            rating = self.rate_outfit(theme, occasion, description, safe_filename)
            
            # Save rating to history
            self.save_rating({
                'filename': safe_filename,
                'theme': theme,
                'occasion': occasion,
                'description': description,
                'rating': rating,
                'rated_at': datetime.now().isoformat()
            })
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'message': 'Outfit rated successfully',
                'rating': rating,
                'filename': safe_filename
            }
            self.wfile.write(json.dumps(response).encode())
            
        except Exception as e:
            self.send_error(500, f"Rating failed: {str(e)}")
    
    def serve_uploaded_file(self, filename):
        """Serve uploaded files"""
        filepath = os.path.join('uploads', filename)
        if os.path.exists(filepath):
            self.send_response(200)
            # Determine content type based on file extension
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                self.send_header('Content-type', 'image/jpeg')
            else:
                self.send_header('Content-type', 'application/octet-stream')
            self.end_headers()
            with open(filepath, 'rb') as f:
                shutil.copyfileobj(f, self.wfile)
        else:
            self.send_error(404)
    
    def load_wardrobe(self):
        """Load wardrobe data"""
        try:
            with open('wardrobe.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"items": []}
    
    def save_wardrobe(self, wardrobe):
        """Save wardrobe data"""
        with open('wardrobe.json', 'w') as f:
            json.dump(wardrobe, f, indent=2)
    
    def generate_outfit(self, items, mood, occasion):
        """Generate outfit based on items, mood, and occasion"""
        # Simple rule-based outfit generation
        outfit = {
            "top": "Choose a comfortable top",
            "bottom": "Select appropriate bottoms", 
            "shoes": "Pick suitable shoes",
            "accessories": "Add finishing touches"
        }
        
        # Find items by type
        tops = [item for item in items if item['item_type'] in ['top', 'dress']]
        bottoms = [item for item in items if item['item_type'] == 'bottom']
        shoes = [item for item in items if item['item_type'] == 'shoes']
        accessories = [item for item in items if item['item_type'] == 'accessories']
        
        # Select items based on mood and occasion
        if tops:
            if mood == "formal":
                formal_tops = [t for t in tops if t['style'] == 'formal']
                if formal_tops:
                    outfit["top"] = f"{formal_tops[0]['color']} {formal_tops[0]['item_type']} ({formal_tops[0]['style']})"
                else:
                    outfit["top"] = f"{tops[0]['color']} {tops[0]['item_type']} - dress it up with accessories"
            else:
                outfit["top"] = f"{tops[0]['color']} {tops[0]['item_type']} ({tops[0]['style']})"
        
        if bottoms:
            outfit["bottom"] = f"{bottoms[0]['color']} {bottoms[0]['item_type']} ({bottoms[0]['style']})"
        
        if shoes:
            outfit["shoes"] = f"{shoes[0]['color']} {shoes[0]['item_type']} ({shoes[0]['style']})"
        
        if accessories:
            outfit["accessories"] = f"{accessories[0]['color']} {accessories[0]['item_type']} ({accessories[0]['style']})"
        
        # Add styling tips based on mood
        if mood == "formal":
            outfit["styling_tips"] = "Opt for classic pieces in neutral colors. Ensure everything is well-fitted and polished. Add a blazer or structured jacket for extra sophistication."
        elif mood == "casual":
            outfit["styling_tips"] = "Keep it relaxed and comfortable. Mix textures and add personal touches. Don't be afraid to layer pieces for a more interesting look."
        elif mood == "party":
            outfit["styling_tips"] = "Go bold with colors and statement pieces. Don't forget to accessorize! Add some sparkle or metallic accents to make it party-ready."
        elif mood == "romantic":
            outfit["styling_tips"] = "Choose soft, flowing fabrics and romantic colors. Add delicate accessories and consider layering for a dreamy look."
        elif mood == "edgy":
            outfit["styling_tips"] = "Mix textures and add bold accessories. Don't be afraid to break fashion rules and make a statement."
        else:
            outfit["styling_tips"] = "Choose pieces that make you feel confident and comfortable. Trust your instincts and add your personal touch."
        
        outfit["reasoning"] = f"This outfit is designed for a {mood} mood and {occasion} occasion. The selected pieces work together to create a cohesive look that matches your desired style."
        
        return outfit
    
    def rate_outfit(self, theme, occasion, description, filename):
        """Rate an outfit based on theme and occasion"""
        # Generate a comprehensive outfit rating
        rating = {
            "overall_score": 0,
            "theme_appropriateness": 0,
            "occasion_suitability": 0,
            "style_cohesion": 0,
            "color_coordination": 0,
            "accessories": 0,
            "feedback": "",
            "strengths": [],
            "improvements": [],
            "star_rating": 0
        }
        
        # Calculate scores based on theme and occasion
        if theme == "formal":
            if occasion in ["work", "office", "business"]:
                rating["overall_score"] = 85
                rating["theme_appropriateness"] = 90
                rating["occasion_suitability"] = 95
                rating["style_cohesion"] = 80
                rating["color_coordination"] = 85
                rating["accessories"] = 75
                rating["feedback"] = "Excellent formal look! This outfit is perfectly suited for a professional setting. The formal theme aligns beautifully with the work occasion."
                rating["strengths"] = ["Professional appearance", "Appropriate for business setting", "Clean and polished look"]
                rating["improvements"] = ["Consider adding a statement accessory", "Ensure proper fit and tailoring"]
            else:
                rating["overall_score"] = 70
                rating["theme_appropriateness"] = 90
                rating["occasion_suitability"] = 60
                rating["feedback"] = "Great formal styling, but might be too formal for this occasion. Consider adapting the formality level."
                rating["strengths"] = ["Well-executed formal look", "Good color coordination"]
                rating["improvements"] = ["Adjust formality to match occasion", "Consider more casual accessories"]
        
        elif theme == "casual":
            if occasion in ["daily", "travel", "sports"]:
                rating["overall_score"] = 88
                rating["theme_appropriateness"] = 95
                rating["occasion_suitability"] = 90
                rating["style_cohesion"] = 85
                rating["color_coordination"] = 80
                rating["accessories"] = 75
                rating["feedback"] = "Perfect casual outfit! This look is ideal for everyday wear and matches the occasion beautifully."
                rating["strengths"] = ["Comfortable and practical", "Great for daily activities", "Relaxed yet put-together"]
                rating["improvements"] = ["Add a pop of color or pattern", "Consider layering for versatility"]
            else:
                rating["overall_score"] = 75
                rating["theme_appropriateness"] = 90
                rating["occasion_suitability"] = 70
                rating["feedback"] = "Nice casual look, but you might want to elevate it slightly for this occasion."
                rating["strengths"] = ["Comfortable and stylish", "Good casual execution"]
                rating["improvements"] = ["Add more sophisticated elements", "Consider dressier accessories"]
        
        elif theme == "party":
            if occasion in ["party", "event", "date"]:
                rating["overall_score"] = 90
                rating["theme_appropriateness"] = 95
                rating["occasion_suitability"] = 92
                rating["style_cohesion"] = 88
                rating["color_coordination"] = 85
                rating["accessories"] = 90
                rating["feedback"] = "Fabulous party look! This outfit is perfect for a fun event and really captures the party vibe."
                rating["strengths"] = ["Eye-catching and fun", "Perfect for social events", "Great use of accessories"]
                rating["improvements"] = ["Ensure comfort for dancing", "Consider the venue's dress code"]
            else:
                rating["overall_score"] = 65
                rating["theme_appropriateness"] = 90
                rating["occasion_suitability"] = 50
                rating["feedback"] = "Great party styling, but might be too flashy for this occasion. Consider toning it down."
                rating["strengths"] = ["Bold and confident", "Great party elements"]
                rating["improvements"] = ["Adapt to occasion appropriateness", "Consider more subtle styling"]
        
        elif theme == "romantic":
            if occasion in ["date", "romantic dinner", "special occasion"]:
                rating["overall_score"] = 92
                rating["theme_appropriateness"] = 95
                rating["occasion_suitability"] = 90
                rating["style_cohesion"] = 90
                rating["color_coordination"] = 88
                rating["accessories"] = 85
                rating["feedback"] = "Absolutely romantic and elegant! This outfit is perfect for a special date or romantic occasion."
                rating["strengths"] = ["Elegant and romantic", "Perfect for special moments", "Beautiful color choices"]
                rating["improvements"] = ["Consider adding delicate jewelry", "Ensure the outfit is comfortable for the evening"]
            else:
                rating["overall_score"] = 70
                rating["theme_appropriateness"] = 90
                rating["occasion_suitability"] = 60
                rating["feedback"] = "Beautiful romantic styling, but might be too dressy for this occasion."
                rating["strengths"] = ["Elegant and feminine", "Great romantic elements"]
                rating["improvements"] = ["Adjust formality level", "Consider more practical elements"]
        
        else:  # Default rating
            rating["overall_score"] = 75
            rating["theme_appropriateness"] = 80
            rating["occasion_suitability"] = 75
            rating["style_cohesion"] = 70
            rating["color_coordination"] = 75
            rating["accessories"] = 70
            rating["feedback"] = "Nice outfit! It shows good style sense and works well for the intended occasion."
            rating["strengths"] = ["Good overall styling", "Appropriate for the occasion"]
            rating["improvements"] = ["Consider adding more personality", "Experiment with accessories"]
        
        # Calculate star rating (1-5 stars)
        rating["star_rating"] = max(1, min(5, round(rating["overall_score"] / 20)))
        
        # Add personalized feedback based on description
        if description:
            rating["feedback"] += f" Based on your description '{description}', this outfit shows great attention to detail."
        
        return rating
    
    def save_rating(self, rating_data):
        """Save rating to history"""
        try:
            with open('ratings.json', 'r') as f:
                ratings = json.load(f)
        except FileNotFoundError:
            ratings = {"ratings": []}
        
        ratings["ratings"].append(rating_data)
        
        with open('ratings.json', 'w') as f:
            json.dump(ratings, f, indent=2)
    
    def get_index_html(self):
        """Return the main HTML page with image upload functionality"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Fashion Stylist</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            color: white;
        }

        .header h1 {
            font-size: 3rem;
            margin-bottom: 10px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .header p {
            font-size: 1.2rem;
            opacity: 0.9;
        }

        .main-content {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            margin-bottom: 40px;
        }

        .rating-section {
            grid-column: 1 / -1;
            margin-top: 20px;
        }

        .card {
            background: white;
            border-radius: 15px;
            padding: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            transition: transform 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
        }

        .card h2 {
            color: #667eea;
            margin-bottom: 20px;
            font-size: 1.8rem;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
            color: #555;
        }

        .form-group input,
        .form-group select {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 16px;
            transition: border-color 0.3s ease;
        }

        .form-group input:focus,
        .form-group select:focus {
            outline: none;
            border-color: #667eea;
        }

        .file-input-wrapper {
            position: relative;
            display: inline-block;
            width: 100%;
        }

        .file-input {
            position: absolute;
            opacity: 0;
            width: 100%;
            height: 100%;
            cursor: pointer;
        }

        .file-input-label {
            display: block;
            padding: 12px;
            background: #f8f9fa;
            border: 2px dashed #667eea;
            border-radius: 8px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .file-input-label:hover {
            background: #e3f2fd;
            border-color: #5a6fd8;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 24px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            width: 100%;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        .wardrobe-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }

        .wardrobe-item {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }

        .wardrobe-item:hover {
            border-color: #667eea;
            transform: scale(1.05);
        }

        .wardrobe-item img {
            width: 100%;
            height: 120px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 10px;
        }

        .wardrobe-item h4 {
            font-size: 14px;
            margin-bottom: 5px;
            color: #333;
        }

        .wardrobe-item p {
            font-size: 12px;
            color: #666;
        }

        .outfit-display {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }

        .outfit-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }

        .outfit-item h4 {
            color: #667eea;
            margin-bottom: 5px;
        }

        .styling-tips {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #2196f3;
        }

        .success {
            background: #e8f5e8;
            color: #2e7d32;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #4caf50;
        }

        .error {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
            border-left: 4px solid #f44336;
        }

        .rating-display {
            background: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }

        .score-item {
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .score-bar {
            width: 200px;
            height: 20px;
            background: #e1e5e9;
            border-radius: 10px;
            overflow: hidden;
        }

        .score-fill {
            height: 100%;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }

        .stars {
            color: #ffd700;
            font-size: 24px;
            margin: 10px 0;
        }

        .strengths, .improvements {
            background: white;
            padding: 15px;
            margin: 10px 0;
            border-radius: 8px;
        }

        .strengths {
            border-left: 4px solid #4caf50;
        }

        .improvements {
            border-left: 4px solid #ff9800;
        }

        .strengths h4, .improvements h4 {
            margin-bottom: 10px;
        }

        .strengths ul, .improvements ul {
            margin: 0;
            padding-left: 20px;
        }

        @media (max-width: 768px) {
            .main-content {
                grid-template-columns: 1fr;
            }
            
            .header h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👗 AI Fashion Stylist</h1>
            <p>Upload your wardrobe and get personalized outfit suggestions!</p>
        </div>

        <div class="main-content">
            <!-- Upload Section -->
            <div class="card">
                <h2>📸 Add to Wardrobe</h2>
                <form id="uploadForm" enctype="multipart/form-data">
                    <div class="form-group">
                        <label for="file">Upload Clothing Item</label>
                        <div class="file-input-wrapper">
                            <input type="file" id="file" name="file" class="file-input" accept="image/*" required>
                            <label for="file" class="file-input-label">
                                📁 Click to upload image
                            </label>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="item_type">Item Type</label>
                        <select id="item_type" name="item_type" required>
                            <option value="">Select type...</option>
                            <option value="top">Top/Shirt</option>
                            <option value="bottom">Bottom/Pants</option>
                            <option value="dress">Dress</option>
                            <option value="shoes">Shoes</option>
                            <option value="accessories">Accessories</option>
                            <option value="outerwear">Outerwear</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="color">Color</label>
                        <select id="color" name="color" required>
                            <option value="">Select color...</option>
                            <option value="black">Black</option>
                            <option value="white">White</option>
                            <option value="red">Red</option>
                            <option value="blue">Blue</option>
                            <option value="green">Green</option>
                            <option value="yellow">Yellow</option>
                            <option value="pink">Pink</option>
                            <option value="purple">Purple</option>
                            <option value="brown">Brown</option>
                            <option value="gray">Gray</option>
                            <option value="navy">Navy</option>
                            <option value="beige">Beige</option>
                            <option value="multicolor">Multicolor</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="style">Style</label>
                        <select id="style" name="style" required>
                            <option value="">Select style...</option>
                            <option value="casual">Casual</option>
                            <option value="formal">Formal</option>
                            <option value="sporty">Sporty</option>
                            <option value="vintage">Vintage</option>
                            <option value="bohemian">Bohemian</option>
                            <option value="minimalist">Minimalist</option>
                            <option value="trendy">Trendy</option>
                        </select>
                    </div>
                    
                    <button type="submit" class="btn">Add to Wardrobe</button>
                </form>
                
                <div id="uploadMessage"></div>
            </div>

            <!-- Outfit Generation Section -->
            <div class="card">
                <h2>✨ Generate Outfit</h2>
                
                <div class="form-group">
                    <label for="mood">Mood</label>
                    <select id="mood" name="mood">
                        <option value="casual">Casual & Comfortable</option>
                        <option value="formal">Formal & Professional</option>
                        <option value="party">Party & Fun</option>
                        <option value="romantic">Romantic & Elegant</option>
                        <option value="edgy">Edgy & Bold</option>
                        <option value="minimalist">Minimalist & Clean</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="occasion">Occasion</label>
                    <select id="occasion" name="occasion">
                        <option value="daily">Daily Wear</option>
                        <option value="work">Work/Office</option>
                        <option value="date">Date Night</option>
                        <option value="party">Party/Event</option>
                        <option value="travel">Travel</option>
                        <option value="sports">Sports/Active</option>
                    </select>
                </div>
                
                <button id="generateBtn" class="btn">Generate My Outfit</button>
                
                <div id="outfitResult"></div>
            </div>
        </div>

        <!-- Outfit Rating Section -->
        <div class="card rating-section">
            <h2>⭐ Rate Your Outfit</h2>
            <p style="margin-bottom: 20px; color: #666;">Upload a photo of your outfit and get AI-powered feedback based on your theme and occasion!</p>
            
            <form id="rateOutfitForm" enctype="multipart/form-data">
                <div class="form-group">
                    <label for="outfit_photo">Upload Your Outfit Photo</label>
                    <div class="file-input-wrapper">
                        <input type="file" id="outfit_photo" name="outfit_photo" class="file-input" accept="image/*" required>
                        <label for="outfit_photo" class="file-input-label">
                            📸 Click to upload your outfit photo
                        </label>
                    </div>
                </div>
                
                <div class="form-group">
                    <label for="outfit_theme">Outfit Theme</label>
                    <select id="outfit_theme" name="outfit_theme" required>
                        <option value="">Select theme...</option>
                        <option value="casual">Casual & Comfortable</option>
                        <option value="formal">Formal & Professional</option>
                        <option value="party">Party & Fun</option>
                        <option value="romantic">Romantic & Elegant</option>
                        <option value="edgy">Edgy & Bold</option>
                        <option value="minimalist">Minimalist & Clean</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="outfit_occasion">Occasion</label>
                    <select id="outfit_occasion" name="outfit_occasion" required>
                        <option value="">Select occasion...</option>
                        <option value="daily">Daily Wear</option>
                        <option value="work">Work/Office</option>
                        <option value="date">Date Night</option>
                        <option value="party">Party/Event</option>
                        <option value="travel">Travel</option>
                        <option value="sports">Sports/Active</option>
                        <option value="business">Business Meeting</option>
                        <option value="romantic dinner">Romantic Dinner</option>
                        <option value="special occasion">Special Occasion</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label for="outfit_description">Description (Optional)</label>
                    <textarea id="outfit_description" name="outfit_description" rows="3" placeholder="Tell us about your outfit - colors, style, what you were going for..."></textarea>
                </div>
                
                <button type="submit" class="btn">Rate My Outfit</button>
            </form>
            
            <div id="ratingResult"></div>
        </div>

        <!-- Wardrobe Display -->
        <div class="card">
            <h2>👔 My Wardrobe</h2>
            <div id="wardrobeGrid" class="wardrobe-grid">
                <!-- Wardrobe items will be displayed here -->
            </div>
        </div>
    </div>

    <script>
        // File input handling
        document.getElementById('file').addEventListener('change', function(e) {
            const label = document.querySelector('.file-input-label');
            if (e.target.files.length > 0) {
                label.textContent = `📷 ${e.target.files[0].name}`;
            } else {
                label.textContent = '📁 Click to upload image';
            }
        });

        // Outfit photo input handling
        document.getElementById('outfit_photo').addEventListener('change', function(e) {
            const label = document.querySelector('label[for="outfit_photo"]');
            if (e.target.files.length > 0) {
                label.textContent = `📸 ${e.target.files[0].name}`;
            } else {
                label.textContent = '📸 Click to upload your outfit photo';
            }
        });

        // Upload form handling
        document.getElementById('uploadForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const messageDiv = document.getElementById('uploadMessage');
            
            try {
                messageDiv.innerHTML = '<div style="text-align: center; padding: 20px; color: #667eea;">Uploading...</div>';
                
                const response = await fetch('/upload', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    messageDiv.innerHTML = '<div class="success">✅ Item added to wardrobe successfully!</div>';
                    this.reset();
                    document.querySelector('.file-input-label').textContent = '📁 Click to upload image';
                    loadWardrobe();
                } else {
                    messageDiv.innerHTML = `<div class="error">❌ ${result.error || 'Upload failed'}</div>`;
                }
            } catch (error) {
                messageDiv.innerHTML = '<div class="error">❌ Upload failed. Please try again.</div>';
            }
        });

        // Rate outfit form handling
        document.getElementById('rateOutfitForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const resultDiv = document.getElementById('ratingResult');
            
            try {
                resultDiv.innerHTML = '<div style="text-align: center; padding: 20px; color: #667eea;">Rating your outfit...</div>';
                
                const response = await fetch('/rate-outfit', {
                    method: 'POST',
                    body: formData
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    displayRating(result);
                    this.reset();
                    document.querySelector('label[for="outfit_photo"]').textContent = '📸 Click to upload your outfit photo';
                } else {
                    resultDiv.innerHTML = `<div class="error">❌ ${result.error || 'Rating failed'}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = '<div class="error">❌ Failed to rate outfit. Please try again.</div>';
            }
        });

        // Generate outfit
        document.getElementById('generateBtn').addEventListener('click', async function() {
            const mood = document.getElementById('mood').value;
            const occasion = document.getElementById('occasion').value;
            const resultDiv = document.getElementById('outfitResult');
            
            try {
                resultDiv.innerHTML = '<div style="text-align: center; padding: 20px; color: #667eea;">Generating your outfit...</div>';
                
                const response = await fetch('/generate-outfit', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ mood, occasion })
                });
                
                const result = await response.json();
                
                if (response.ok) {
                    displayOutfit(result);
                } else {
                    resultDiv.innerHTML = `<div class="error">❌ ${result.error || 'Failed to generate outfit'}</div>`;
                }
            } catch (error) {
                resultDiv.innerHTML = '<div class="error">❌ Failed to generate outfit. Please try again.</div>';
            }
        });

        function displayOutfit(data) {
            const resultDiv = document.getElementById('outfitResult');
            
            let html = `
                <div class="outfit-display">
                    <h3>🎯 Your ${data.mood} Outfit for ${data.occasion}</h3>
                    
                    <div class="outfit-item">
                        <h4>👕 Top</h4>
                        <p>${data.outfit.top}</p>
                    </div>
                    
                    <div class="outfit-item">
                        <h4>👖 Bottom</h4>
                        <p>${data.outfit.bottom}</p>
                    </div>
                    
                    <div class="outfit-item">
                        <h4>👟 Shoes</h4>
                        <p>${data.outfit.shoes}</p>
                    </div>
                    
                    <div class="outfit-item">
                        <h4>💍 Accessories</h4>
                        <p>${data.outfit.accessories}</p>
                    </div>
                    
                    <div class="styling-tips">
                        <h4>💡 Styling Tips</h4>
                        <p>${data.outfit.styling_tips}</p>
                    </div>
                    
                    <div class="styling-tips">
                        <h4>🤔 Why This Works</h4>
                        <p>${data.outfit.reasoning}</p>
                    </div>
                </div>
            `;
            
            resultDiv.innerHTML = html;
        }

        function displayRating(data) {
            const resultDiv = document.getElementById('ratingResult');
            const rating = data.rating;
            
            let html = `
                <div class="rating-display">
                    <h3>⭐ Your Outfit Rating</h3>
                    
                    <div style="text-align: center; margin: 20px 0;">
                        <div class="stars">
                            ${'★'.repeat(rating.star_rating)}${'☆'.repeat(5 - rating.star_rating)}
                        </div>
                        <h2 style="color: #667eea; margin: 10px 0;">${rating.overall_score}/100</h2>
                    </div>
                    
                    <div class="score-item">
                        <span><strong>Overall Score</strong></span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${rating.overall_score}%"></div>
                        </div>
                        <span>${rating.overall_score}/100</span>
                    </div>
                    
                    <div class="score-item">
                        <span><strong>Theme Appropriateness</strong></span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${rating.theme_appropriateness}%"></div>
                        </div>
                        <span>${rating.theme_appropriateness}/100</span>
                    </div>
                    
                    <div class="score-item">
                        <span><strong>Occasion Suitability</strong></span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${rating.occasion_suitability}%"></div>
                        </div>
                        <span>${rating.occasion_suitability}/100</span>
                    </div>
                    
                    <div class="score-item">
                        <span><strong>Style Cohesion</strong></span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${rating.style_cohesion}%"></div>
                        </div>
                        <span>${rating.style_cohesion}/100</span>
                    </div>
                    
                    <div class="score-item">
                        <span><strong>Color Coordination</strong></span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${rating.color_coordination}%"></div>
                        </div>
                        <span>${rating.color_coordination}/100</span>
                    </div>
                    
                    <div class="score-item">
                        <span><strong>Accessories</strong></span>
                        <div class="score-bar">
                            <div class="score-fill" style="width: ${rating.accessories}%"></div>
                        </div>
                        <span>${rating.accessories}/100</span>
                    </div>
                    
                    <div class="styling-tips">
                        <h4>💬 AI Feedback</h4>
                        <p>${rating.feedback}</p>
                    </div>
                    
                    <div class="strengths">
                        <h4>✅ Strengths</h4>
                        <ul>
                            ${rating.strengths.map(strength => `<li>${strength}</li>`).join('')}
                        </ul>
                    </div>
                    
                    <div class="improvements">
                        <h4>💡 Areas for Improvement</h4>
                        <ul>
                            ${rating.improvements.map(improvement => `<li>${improvement}</li>`).join('')}
                        </ul>
                    </div>
                </div>
            `;
            
            resultDiv.innerHTML = html;
        }

        // Load wardrobe
        async function loadWardrobe() {
            try {
                const response = await fetch('/wardrobe');
                const wardrobe = await response.json();
                
                const grid = document.getElementById('wardrobeGrid');
                
                if (wardrobe.items.length === 0) {
                    grid.innerHTML = '<p style="text-align: center; color: #666; grid-column: 1/-1;">No items in wardrobe yet. Upload some clothing items to get started!</p>';
                    return;
                }
                
                grid.innerHTML = wardrobe.items.map(item => `
                    <div class="wardrobe-item">
                        <img src="/uploads/${item.filename}" alt="${item.item_type}" onerror="this.style.display='none'">
                        <h4>${item.item_type.charAt(0).toUpperCase() + item.item_type.slice(1)}</h4>
                        <p>${item.color} • ${item.style}</p>
                    </div>
                `).join('');
            } catch (error) {
                console.error('Error loading wardrobe:', error);
            }
        }

        // Load wardrobe on page load
        loadWardrobe();
    </script>
</body>
</html>
        """

def main():
    """Main function to run the server"""
    PORT = 8002
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    
    print("👗 AI Fashion Stylist - With Image Uploads")
    print("=" * 50)
    print(f"🚀 Starting server on http://localhost:{PORT}")
    print("📸 Upload your clothing photos and get outfit suggestions!")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    with socketserver.TCPServer(("", PORT), FashionStylistHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped. Thanks for using AI Fashion Stylist!")

if __name__ == "__main__":
    main()
