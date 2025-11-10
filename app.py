#!/usr/bin/env python3
"""
수학 모의고사 OCR 처리 웹 애플리케이션
DeepSeek OCR을 사용하여 문제를 글자+LaTeX+그림으로 추출
"""

from flask import Flask, render_template, request, jsonify, send_file, send_from_directory, Response, stream_with_context
from flask_cors import CORS
import fitz  # PyMuPDF
import os
import json
import base64
import requests
from io import BytesIO
from PIL import Image
import time
from werkzeug.utils import secure_filename
import re
import queue
import threading

app = Flask(__name__)
CORS(app)

# 로그 큐 저장소 (세션별)
log_queues = {}

# 설정
UPLOAD_FOLDER = 'uploads'
RESULT_FOLDER = 'results'
ALLOWED_EXTENSIONS = {'pdf'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def pdf_to_images(pdf_path, dpi=300):
    """PDF를 고해상도 이미지로 변환"""
    doc = fitz.open(pdf_path)
    images = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append({
            'page_num': page_num + 1,
            'image': img,
            'width': pix.width,
            'height': pix.height
        })
    
    doc.close()
    return images

def image_to_base64(image):
    """PIL Image를 base64로 인코딩"""
    buffered = BytesIO()
    image.save(buffered, format="PNG", optimize=True, quality=95)
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

def call_deepseek_ocr(image, hf_token, page_num, session_id=None):
    """DeepSeek VL 또는 다른 Vision 모델을 사용한 수학 문제 OCR"""
    
    # 이미지를 바이트로 변환
    buffered = BytesIO()
    image.save(buffered, format="PNG", optimize=True, quality=95)
    img_bytes = buffered.getvalue()
    
    # Hugging Face Inference API 엔드포인트들 시도
    models = [
        "deepseek-ai/deepseek-vl-7b-chat",
        "microsoft/Florence-2-large",
        "Qwen/Qwen2-VL-7B-Instruct",
        "meta-llama/Llama-3.2-11B-Vision-Instruct"
    ]
    
    # 수학 문제 인식에 최적화된 프롬프트
    prompt = """이 이미지는 수학 모의고사 문제입니다. 다음 형식으로 정확하게 추출해주세요:

1. 모든 텍스트를 정확히 인식
2. 수학 수식은 LaTeX 형식으로 변환 (예: $x^2 + 2x + 1 = 0$, \\frac{1}{2}, \\sqrt{2})
3. 그림이나 도표가 있으면 [IMAGE: 그림 설명] 형식으로 표시
4. 문제 번호, 선택지, 조건 등 모든 내용 포함
5. 한국어와 수식을 정확히 구분

출력 형식:
문제 번호. [문제 내용 + LaTeX 수식]
[IMAGE: 그림이 있다면 설명]
선택지나 조건이 있다면 포함

정확하고 완전하게 추출해주세요."""
    
    for model in models:
        try:
            if session_id:
                log_to_client(session_id, f"   시도: {model}")
            
            api_url = f"https://api-inference.huggingface.co/models/{model}"
            
            headers = {
                "Authorization": f"Bearer {hf_token}"
            }
            
            # 이미지를 직접 전송
            response = requests.post(
                api_url,
                headers=headers,
                data=img_bytes,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # 결과 파싱
                generated_text = ""
                if isinstance(result, list) and len(result) > 0:
                    if 'generated_text' in result[0]:
                        generated_text = result[0]['generated_text']
                    elif 'text' in result[0]:
                        generated_text = result[0]['text']
                elif isinstance(result, dict):
                    generated_text = result.get('generated_text', result.get('text', ''))
                
                if generated_text:
                    if session_id:
                        log_to_client(session_id, f"   ✓ 성공: {model}")
                    return {
                        "success": True,
                        "text": f"{prompt}\n\n{generated_text}",
                        "model": model,
                        "page": page_num
                    }
            
            if session_id:
                log_to_client(session_id, f"   ✗ 실패: {model} (코드: {response.status_code})")
            
            # 모델이 로딩 중이거나 실패한 경우 다음 모델 시도
            continue
            
        except Exception as e:
            if session_id:
                log_to_client(session_id, f"   ✗ 오류: {model} - {str(e)}")
            continue
    
    # 모든 모델 실패 시 PyMuPDF로 텍스트 추출
    return {
        "success": False,
        "error": "모든 Vision 모델 실패. PyMuPDF 텍스트 추출로 대체됩니다.",
        "page": page_num
    }

def extract_math_content(ocr_text):
    """OCR 결과에서 수학 내용 추출 및 구조화"""
    
    # LaTeX 수식 패턴 찾기
    latex_patterns = re.findall(r'\$[^$]+\$|\\\[[^\]]+\\\]|\\\([^\)]+\\\)', ocr_text)
    
    # 이미지 설명 찾기
    image_descriptions = re.findall(r'\[IMAGE:[^\]]+\]', ocr_text)
    
    return {
        "raw_text": ocr_text,
        "latex_expressions": latex_patterns,
        "images": image_descriptions,
        "has_math": len(latex_patterns) > 0,
        "has_image": len(image_descriptions) > 0
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test')
def test_page():
    return render_template('test.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """PDF 파일 업로드 및 처리"""
    
    if 'pdf' not in request.files:
        return jsonify({"error": "PDF 파일이 없습니다"}), 400
    
    if 'hf_token' not in request.form:
        return jsonify({"error": "Hugging Face 토큰이 필요합니다"}), 400
    
    file = request.files['pdf']
    hf_token = request.form['hf_token']
    
    if file.filename == '':
        return jsonify({"error": "파일이 선택되지 않았습니다"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "PDF 파일만 업로드 가능합니다"}), 400
    
    # 파일 저장
    filename = secure_filename(file.filename)
    timestamp = int(time.time())
    safe_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_filename)
    file.save(filepath)
    
    try:
        # PDF를 이미지로 변환
        images = pdf_to_images(filepath, dpi=300)
        total_pages = len(images)
        
        return jsonify({
            "success": True,
            "filename": safe_filename,
            "total_pages": total_pages,
            "message": f"{total_pages}페이지 PDF 업로드 완료"
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def extract_text_with_pymupdf(filepath, page_num):
    """PyMuPDF로 텍스트 직접 추출 (대체 방법)"""
    try:
        doc = fitz.open(filepath)
        page = doc[page_num - 1]
        text = page.get_text()
        doc.close()
        
        return {
            "success": True,
            "text": text,
            "method": "PyMuPDF",
            "page": page_num
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "page": page_num
        }

def log_to_client(session_id, message):
    """클라이언트에 로그 메시지 전송"""
    if session_id in log_queues:
        log_queues[session_id].put(message)

def process_pdf_background(filename, hf_token, session_id):
    """백그라운드에서 PDF 처리"""
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    try:
        log_to_client(session_id, f"📄 PDF 파일 로드 중: {filename}")
        
        # PDF를 이미지로 변환
        log_to_client(session_id, "🖼️ PDF를 이미지로 변환 중...")
        images = pdf_to_images(filepath, dpi=300)
        total_pages = len(images)
        
        log_to_client(session_id, f"✅ 총 {total_pages}페이지 감지됨")
        log_to_client(session_id, "")
        
        results = []
        
        # 각 페이지 처리
        for idx, img_data in enumerate(images):
            page_num = img_data['page_num']
            image = img_data['image']
            
            log_to_client(session_id, f"{'='*50}")
            log_to_client(session_id, f"📖 페이지 {page_num}/{total_pages} 처리 시작")
            log_to_client(session_id, f"   이미지 크기: {img_data['width']}x{img_data['height']} 픽셀")
            
            # 먼저 DeepSeek OCR 시도
            log_to_client(session_id, "🤖 AI Vision 모델로 OCR 시도 중...")
            ocr_result = call_deepseek_ocr(image, hf_token, page_num, session_id)
            
            # 실패하면 PyMuPDF로 대체
            if not ocr_result.get('success'):
                log_to_client(session_id, "⚠️ Vision 모델 실패, PyMuPDF 대체 방법 사용")
                ocr_result = extract_text_with_pymupdf(filepath, page_num)
                log_to_client(session_id, f"✅ PyMuPDF로 텍스트 추출 완료")
            else:
                model_name = ocr_result.get('method', ocr_result.get('model', 'Unknown'))
                log_to_client(session_id, f"✅ OCR 성공 (모델: {model_name})")
            
            if ocr_result.get('success'):
                # 수학 내용 추출
                log_to_client(session_id, "📐 수학 내용 분석 중...")
                math_content = extract_math_content(ocr_result.get('text', ''))
                
                latex_count = len(math_content.get('latex_expressions', []))
                image_count = len(math_content.get('images', []))
                
                if latex_count > 0:
                    log_to_client(session_id, f"   ✓ LaTeX 수식 {latex_count}개 발견")
                if image_count > 0:
                    log_to_client(session_id, f"   ✓ 그림 {image_count}개 발견")
                
                # 이미지 저장
                log_to_client(session_id, "💾 고해상도 이미지 저장 중...")
                img_filename = f"{filename.rsplit('.', 1)[0]}_page_{page_num:03d}.png"
                img_path = os.path.join(app.config['RESULT_FOLDER'], img_filename)
                image.save(img_path, "PNG", optimize=True, quality=95)
                log_to_client(session_id, f"   ✓ 저장 완료: {img_filename}")
                
                result_data = {
                    "page": page_num,
                    "image_path": img_filename,
                    "ocr_result": ocr_result,
                    "math_content": math_content,
                    "width": img_data['width'],
                    "height": img_data['height'],
                    "method": ocr_result.get('method', ocr_result.get('model', 'Unknown'))
                }
            else:
                log_to_client(session_id, "❌ 텍스트 추출 실패")
                # 이미지만 저장
                img_filename = f"{filename.rsplit('.', 1)[0]}_page_{page_num:03d}.png"
                img_path = os.path.join(app.config['RESULT_FOLDER'], img_filename)
                image.save(img_path, "PNG", optimize=True, quality=95)
                
                result_data = {
                    "page": page_num,
                    "image_path": img_filename,
                    "error": ocr_result.get('error', 'Unknown error'),
                    "width": img_data['width'],
                    "height": img_data['height']
                }
            
            results.append(result_data)
            
            progress = int((page_num / total_pages) * 100)
            log_to_client(session_id, f"✅ 페이지 {page_num} 완료 (진행률: {progress}%)")
            log_to_client(session_id, "")
        
        # 결과 저장
        log_to_client(session_id, "💾 최종 결과 저장 중...")
        result_filename = f"{filename.rsplit('.', 1)[0]}_result.json"
        result_path = os.path.join(app.config['RESULT_FOLDER'], result_filename)
        
        with open(result_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        log_to_client(session_id, f"✅ 결과 저장 완료: {result_filename}")
        log_to_client(session_id, "")
        log_to_client(session_id, f"{'='*50}")
        log_to_client(session_id, f"🎉 모든 처리 완료! 총 {total_pages}페이지")
        log_to_client(session_id, "")
        
        # 완료 신호
        log_to_client(session_id, "__COMPLETE__" + json.dumps({
            "success": True,
            "total_pages": total_pages,
            "results": results,
            "result_file": result_filename
        }))
    
    except Exception as e:
        log_to_client(session_id, f"❌ 오류 발생: {str(e)}")
        log_to_client(session_id, "__ERROR__" + str(e))

@app.route('/process', methods=['POST'])
def process_pdf():
    """PDF OCR 처리 시작 (비동기)"""
    
    data = request.json
    filename = data.get('filename')
    hf_token = data.get('hf_token')
    
    if not filename or not hf_token:
        return jsonify({"error": "필수 매개변수가 누락되었습니다"}), 400
    
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({"error": "파일을 찾을 수 없습니다"}), 404
    
    # 세션 ID 생성
    session_id = f"{filename}_{int(time.time())}"
    
    # 로그 큐 생성
    log_queues[session_id] = queue.Queue()
    
    # 백그라운드에서 처리 시작
    thread = threading.Thread(target=process_pdf_background, args=(filename, hf_token, session_id))
    thread.daemon = True
    thread.start()
    
    return jsonify({
        "success": True,
        "session_id": session_id,
        "message": "처리가 시작되었습니다. /stream/<session_id>로 로그를 받으세요."
    })

@app.route('/stream/<session_id>')
def stream_logs(session_id):
    """실시간 로그 스트리밍 (SSE)"""
    
    def generate():
        if session_id not in log_queues:
            yield f"data: {json.dumps({'error': '세션을 찾을 수 없습니다'})}\n\n"
            return
        
        log_queue = log_queues[session_id]
        
        while True:
            try:
                message = log_queue.get(timeout=30)
                
                if message.startswith("__COMPLETE__"):
                    result_json = message.replace("__COMPLETE__", "")
                    yield f"data: {json.dumps({'type': 'complete', 'data': json.loads(result_json)})}\n\n"
                    break
                elif message.startswith("__ERROR__"):
                    error_msg = message.replace("__ERROR__", "")
                    yield f"data: {json.dumps({'type': 'error', 'message': error_msg})}\n\n"
                    break
                else:
                    yield f"data: {json.dumps({'type': 'log', 'message': message})}\n\n"
            
            except queue.Empty:
                # 타임아웃 시 연결 유지용 ping
                yield f"data: {json.dumps({'type': 'ping'})}\n\n"
        
        # 정리
        if session_id in log_queues:
            del log_queues[session_id]
    
    return Response(stream_with_context(generate()), mimetype='text/event-stream')

@app.route('/results/<filename>')
def get_result(filename):
    """결과 파일 다운로드"""
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

@app.route('/images/<filename>')
def get_image(filename):
    """이미지 파일 가져오기"""
    return send_from_directory(app.config['RESULT_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
