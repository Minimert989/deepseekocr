# 🚀 Quick Reference Guide

**Math Exam OCR Web Application**  
**Repository**: https://github.com/Minimert989/deepseekocr

---

## 📦 What's in This Repository?

```
deepseekocr/
├── 📄 Core Application
│   ├── app.py                      # Flask backend server (327 lines)
│   ├── requirements.txt            # Python dependencies
│   └── .gitignore                  # Git ignore rules
│
├── 🌐 Web Interface
│   └── templates/
│       ├── index.html              # Main user interface (682 lines)
│       └── test.html               # Debug test page (287 lines)
│
├── 📁 Directory Structure
│   ├── uploads/.gitkeep            # PDF upload directory
│   ├── results/.gitkeep            # Processing results directory
│   └── static/.gitkeep             # Static assets directory
│
└── 📚 Documentation
    ├── README.md                   # Quick start & API docs (7.6 KB)
    ├── PROJECT_SUMMARY.md          # Complete project history (26.6 KB)
    ├── README_MATH_OCR.md         # Feature descriptions (7.0 KB)
    ├── DEPLOYMENT_INFO.md         # Setup instructions (8.5 KB)
    ├── UPDATE_REALTIME_LOGS.md    # SSE implementation (8.4 KB)
    └── QUICK_REFERENCE.md         # This file
```

---

## ⚡ Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/Minimert989/deepseekocr.git
cd deepseekocr
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Server
```bash
python3 app.py
```

### 4. Open Browser
Navigate to: http://localhost:5001

---

## 🎯 Key Features

| Feature | Description | Status |
|---------|-------------|--------|
| 📤 File Upload | Drag & drop PDF upload | ✅ Working |
| 🤖 Multi-Model AI | 4 vision models with fallback | ✅ Working |
| ⚡ Real-time Logs | SSE-based live progress | ✅ Working |
| 🔤 Text Extraction | High-quality OCR | ✅ Working |
| 📐 LaTeX Support | Math formula extraction | ✅ Working |
| 🖼️ Image Extraction | Extract embedded images | ✅ Working |
| 🎨 Syntax Highlighting | Color-coded results | ✅ Working |
| 💾 Download Results | Export as text files | ✅ Working |

---

## 🔧 API Endpoints

### Upload PDF
```http
POST /upload
Content-Type: multipart/form-data

file: <PDF file>
```

**Response:**
```json
{
  "filename": "uploaded_file.pdf"
}
```

### Start Processing
```http
POST /process
Content-Type: application/json

{
  "filename": "uploaded_file.pdf",
  "hf_token": "hf_xxxxx"
}
```

**Response:**
```json
{
  "session_id": "uuid-string"
}
```

### Stream Logs (SSE)
```http
GET /stream/<session_id>
```

**Event Types:**
- `log` - Progress message
- `complete` - Processing finished with results
- `ping` - Keep-alive heartbeat

---

## 🤖 AI Models Used

The application tries these models in order:

1. **deepseek-ai/deepseek-vl-7b-chat** (Primary)
   - Best for mathematical content
   - High accuracy for formulas

2. **microsoft/Florence-2-large** (Fallback 1)
   - General purpose vision model
   - Good for text extraction

3. **Qwen/Qwen2-VL-7B-Instruct** (Fallback 2)
   - Multilingual support
   - Handles various layouts

4. **meta-llama/Llama-3.2-11B-Vision-Instruct** (Fallback 3)
   - Latest generation model
   - Strong reasoning capabilities

---

## 📊 Processing Flow

```
┌─────────────────┐
│  Upload PDF     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Validate File  │
└────────┬────────┘
         │
         ▼
┌─────────────────────┐
│  Convert to Images  │
│  (300 DPI)          │
└──────────┬──────────┘
           │
           ▼
┌──────────────────────┐
│  Process Each Page   │◄─── Retry with
│  with AI Model       │     next model
└──────────┬───────────┘     on failure
           │
           ▼
┌──────────────────────┐
│  Extract LaTeX       │
│  Extract Images      │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  Generate Results    │
│  Stream to Client    │
└──────────────────────┘
```

---

## 💡 Usage Tips

### Getting Hugging Face Token
1. Go to https://huggingface.co/settings/tokens
2. Create a new access token
3. Copy and use in the application

### Best Practices
- **PDF Quality**: Use high-quality scans for better results
- **Page Count**: Smaller PDFs process faster
- **Token Security**: Don't share your HF token publicly
- **Browser**: Use modern browsers for best SSE support

### Troubleshooting

#### Server Not Starting
```bash
# Check if port 5001 is available
netstat -tulpn | grep 5001

# Kill existing process
pkill -f "python3 app.py"

# Restart server
python3 app.py
```

#### SSE Connection Issues
- Check browser console for errors
- Verify server is running
- Test with `/test` debug page

#### Processing Hangs
- Check server logs
- Verify HF token is valid
- Try with smaller PDF first

---

## 📖 Documentation Guide

### For Quick Start
→ **[README.md](README.md)** - Installation and basic usage

### For Features
→ **[README_MATH_OCR.md](README_MATH_OCR.md)** - Detailed feature list

### For Deployment
→ **[DEPLOYMENT_INFO.md](DEPLOYMENT_INFO.md)** - Production setup

### For Technical Details
→ **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete architecture

### For SSE Implementation
→ **[UPDATE_REALTIME_LOGS.md](UPDATE_REALTIME_LOGS.md)** - Real-time logs

---

## 🔗 External Links

- **GitHub Repository**: https://github.com/Minimert989/deepseekocr
- **Hugging Face**: https://huggingface.co
- **Flask Documentation**: https://flask.palletsprojects.com/
- **PyMuPDF**: https://pymupdf.readthedocs.io/

---

## 📝 Development History

### Phase 1: PDF Processing (Nov 9, 2025)
- ✅ Processed 53-page Japanese textbook
- ✅ Tested multiple OCR approaches
- ✅ Created initial backup archive

### Phase 2: Web Application (Nov 10, 2025)
- ✅ Built Flask backend
- ✅ Created responsive UI
- ✅ Implemented SSE logging
- ✅ Added multi-model fallback
- ✅ Deployed to GitHub

**Total Development Time**: ~12 hours

---

## 🎓 Key Takeaways

1. **Always have fallback strategies** for external APIs
2. **Real-time feedback** is crucial for user experience
3. **Comprehensive logging** saves debugging time
4. **Isolated testing** helps identify issues quickly
5. **Progressive documentation** tracks project evolution

---

## 🚨 Known Issues

### Server Stability (⚠️ In Progress)
- Intermittent connection drops on port 5001
- Needs process manager for production
- Consider using Gunicorn or uWSGI

### AI Model Availability (⚠️ External)
- Hugging Face API rate limits
- Model endpoint deprecation risk
- Depends on external service

### Processing Time (📌 Future Enhancement)
- No progress percentage (only page count)
- Cannot pause/cancel processing
- Large PDFs take significant time

---

## 🔮 Future Enhancements

### High Priority
- [ ] Production WSGI server setup
- [ ] Process manager (supervisor/pm2)
- [ ] Progress percentage indicator
- [ ] Cancel processing button

### Medium Priority
- [ ] Batch PDF processing
- [ ] Result export formats (JSON, CSV, MD)
- [ ] OCR history tracking
- [ ] User authentication

### Low Priority
- [ ] Equation solver integration
- [ ] Multiple language UI
- [ ] Custom model fine-tuning
- [ ] Cloud deployment (AWS, GCP)

---

## 📞 Support

### Issues
Report bugs or feature requests at:  
https://github.com/Minimert989/deepseekocr/issues

### Questions
For questions about the implementation:
- Check the documentation files
- Review the code comments
- Use the `/test` debug page

---

## 📜 License

This project is provided as-is for educational purposes.  
See repository for license information.

---

**Last Updated**: 2025-11-10  
**Version**: 1.0.0  
**Status**: ✅ Production Ready (with known issues)

---

## 🎉 Quick Commands Cheat Sheet

```bash
# Setup
git clone https://github.com/Minimert989/deepseekocr.git
cd deepseekocr
pip install -r requirements.txt

# Run
python3 app.py

# Test
curl http://localhost:5001/

# Debug
curl http://localhost:5001/test

# Check processes
ps aux | grep python3

# View logs
tail -f flask_server.log

# Stop server
pkill -f "python3 app.py"
```

---

**🔗 Repository**: https://github.com/Minimert989/deepseekocr  
**📦 Latest Commit**: 2ee4d60
