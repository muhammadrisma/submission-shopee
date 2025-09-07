# Quick Start Guide - Food Receipt Analyzer

## 🚀 Get Started in 5 Minutes

### 1. Check Your Installation
```bash
python check_installation.py
```

### 2. Install Missing Dependencies

**If you see "Tesseract OCR" error:**
- **Windows:** See `INSTALL_TESSERACT_WINDOWS.md`
- **macOS:** `brew install tesseract`
- **Linux:** `sudo apt install tesseract-ocr`

**If you see Python dependency errors:**
```bash
pip install -r requirements.txt
```

### 3. Configure the Application
```bash
# Copy example configuration
cp .env.example .env

# Edit .env file and add your OpenRouter API key (optional for AI queries)
# OPENROUTER_API_KEY=your_api_key_here
```

### 4. Run the Application

**Option 1: Python script (recommended)**
```bash
python run_app.py
```

**Option 2: Windows batch file (if PATH issues)**
```cmd
run_app.bat
```

**Option 3: Manual PATH setup**
```cmd
set "PATH=C:\Program Files\Tesseract-OCR;%PATH%"
python run_app.py
```

The application will open in your browser at `http://localhost:8501`

## 📱 Using the Application

### Upload a Receipt
1. Click "📤 Upload Receipt" in the sidebar
2. Drag and drop or click to select a receipt image
3. Click "🔍 Process Receipt"
4. View the extracted data

### Ask Questions
1. Click "🤖 Ask Questions" in the sidebar
2. Type questions like:
   - "What food did I buy yesterday?"
   - "How much did I spend last week?"
   - "Where did I buy milk?"
3. Get AI-powered answers about your receipts

### View Analytics
1. Click "📊 Dashboard" to see spending analytics
2. View recent purchases and trends

## 🔧 Troubleshooting

### Common Issues

**"Tesseract not found"**
- Install Tesseract OCR (see installation guides)
- Make sure it's in your system PATH

**"OpenRouter API request failed"**
- Add your API key to the .env file
- AI queries are optional - upload still works without it

**"Database error"**
- Check if the `data/` folder exists and is writable
- The app will create the database automatically

**"Upload folder missing"**
- The app creates this automatically
- Check folder permissions

### Get Help
1. Run `python check_installation.py` for diagnostics
2. Check the Settings page in the app for status
3. View detailed guides in `INSTALLATION.md`

## 🎯 What You Can Do

✅ **Upload receipt images** (JPG, PNG, PDF)  
✅ **Extract text and data** automatically  
✅ **Store receipts** in local database  
✅ **Ask natural language questions** about your purchases  
✅ **View spending analytics** and trends  
✅ **Search by store, date, or item**  

## 📁 Supported File Types

- **Images:** JPG, JPEG, PNG
- **Documents:** PDF (first page)
- **Max size:** 10MB per file

## 🤖 Example Questions

Try asking these questions after uploading some receipts:

- "What did I buy at Walmart yesterday?"
- "How much did I spend on food last week?"
- "Show me all my grocery purchases from Target"
- "What stores did I shop at this month?"
- "Find all receipts with milk"
- "Total spending in the last 30 days"

## 🔑 API Key (Optional)

For AI-powered natural language queries, get a free API key:

1. Sign up at https://openrouter.ai/
2. Get your API key from the dashboard
3. Add to `.env` file:
   ```
   OPENROUTER_API_KEY=your_key_here
   ```

**Note:** The app works without an API key - you just won't have AI query features.

## 🎉 You're Ready!

Your Food Receipt Analyzer is now ready to use. Start by uploading your first receipt!