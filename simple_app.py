#!/usr/bin/env python3
"""
Simple AI Fashion Stylist - No external dependencies version
This version works with just Python standard library
"""

import os
import json
import http.server
import socketserver
import urllib.parse
import shutil
from datetime import datetime
import base64
import email
from email.message import EmailMessage

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
        else:
            self.send_error(404)
    
    def handle_upload(self):
        """Handle file upload"""
        try:
            # Parse multipart form data
            content_type = self.headers['Content-Type']
            if not content_type.startswith('multipart/form-data'):
                self.send_error(400, "Invalid content type")
                return
            
            # Create uploads directory if it doesn't exist
            os.makedirs('uploads', exist_ok=True)
            
            # Parse form data using email parser
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Simple multipart parsing
            boundary = content_type.split('boundary=')[1]
            parts = post_data.split(f'--{boundary}'.encode())
            
            form = {}
            for part in parts:
                if b'Content-Disposition: form-data' in part:
                    lines = part.split(b'\r\n')
                    for i, line in enumerate(lines):
                        if b'Content-Disposition: form-data' in line:
                            # Extract field name
                            if b'name="file"' in line:
                                # This is the file field
                                file_start = part.find(b'\r\n\r\n') + 4
                                file_data = part[file_start:]
                                # Remove trailing boundary markers
                                if file_data.endswith(b'\r\n'):
                                    file_data = file_data[:-2]
                                form['file'] = type('FileItem', (), {
                                    'filename': 'uploaded_file.jpg',
                                    'file': type('FileObj', (), {'read': lambda: file_data})()
                                })()
                            elif b'name=' in line:
                                # Extract field name and value
                                name_start = line.find(b'name="') + 6
                                name_end = line.find(b'"', name_start)
                                field_name = line[name_start:name_end].decode()
                                
                                # Find the value
                                value_start = part.find(b'\r\n\r\n') + 4
                                value_data = part[value_start:]
                                if value_data.endswith(b'\r\n'):
                                    value_data = value_data[:-2]
                                form[field_name] = value_data.decode()
            
            # Get file
            file_item = form['file']
            if not file_item.filename:
                self.send_error(400, "No file uploaded")
                return
            
            # Get form data
            item_type = form.getvalue('item_type', 'unknown')
            color = form.getvalue('color', 'unknown')
            style = form.getvalue('style', 'unknown')
            
            # Save file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file_item.filename}"
            filepath = os.path.join('uploads', filename)
            
            with open(filepath, 'wb') as f:
                shutil.copyfileobj(file_item.file, f)
            
            # Add to wardrobe
            wardrobe = self.load_wardrobe()
            item = {
                'id': len(wardrobe['items']) + 1,
                'filename': filename,
                'filepath': filepath,
                'item_type': item_type,
                'color': color,
                'style': style,
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
    
    def get_index_html(self):
        """Return the main HTML page"""
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
                        <input type="file" id="file" name="file" accept="image/*" required>
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

        <!-- Wardrobe Display -->
        <div class="card">
            <h2>👔 My Wardrobe</h2>
            <div id="wardrobeGrid" class="wardrobe-grid">
                <!-- Wardrobe items will be displayed here -->
            </div>
        </div>
    </div>

    <script>
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
                    loadWardrobe();
                } else {
                    messageDiv.innerHTML = `<div class="error">❌ ${result.error || 'Upload failed'}</div>`;
                }
            } catch (error) {
                messageDiv.innerHTML = '<div class="error">❌ Upload failed. Please try again.</div>';
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
    PORT = 8000
    
    # Create necessary directories
    os.makedirs('uploads', exist_ok=True)
    
    print("👗 AI Fashion Stylist - Simple Version")
    print("=" * 50)
    print(f"🚀 Starting server on http://localhost:{PORT}")
    print("📁 Upload your clothing items and get outfit suggestions!")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 50)
    
    with socketserver.TCPServer(("", PORT), FashionStylistHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋 Server stopped. Thanks for using AI Fashion Stylist!")

if __name__ == "__main__":
    main()
