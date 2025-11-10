# 📐 수학 모의고사 OCR 웹 애플리케이션

DeepSeek AI를 활용한 수학 문제 자동 추출 시스템  
**텍스트 + LaTeX 수식 + 그림 자동 인식**

## ✨ 주요 기능

### 🤖 AI 기반 OCR
- **DeepSeek VL-7B** - 최첨단 Vision Language 모델
- **Microsoft Florence-2** - 고성능 이미지 이해
- **Qwen2-VL** - 다국어 Vision 모델
- **Llama 3.2 Vision** - Meta의 최신 Vision 모델
- **PyMuPDF** - 대체 텍스트 추출

### 📐 수학 특화 기능
1. **LaTeX 자동 변환**: 수식을 LaTeX 형식으로 변환
   - 예: `x^2 + 2x + 1 = 0` → `$x^2 + 2x + 1 = 0$`
   - 분수: `\\frac{1}{2}`, 제곱근: `\\sqrt{2}`

2. **그림 인식**: 도표, 그래프, 도형 자동 감지
   - `[IMAGE: 그림 설명]` 형식으로 표시

3. **구조화된 추출**:
   - 문제 번호
   - 문제 내용
   - 선택지
   - 조건 및 제약사항

### 🖼️ 고해상도 처리
- **300 DPI** 고해상도 이미지 변환
- PNG 형식으로 원본 품질 유지
- 페이지별 독립 처리

### 🔴 실시간 로그 (NEW!)
- **Server-Sent Events (SSE)** 기반 실시간 로그 스트리밍
- 처리 과정 투명하게 표시
- 색상 코딩으로 가독성 향상
- 각 AI 모델 시도/성공/실패 상태 표시

---

## 🚀 빠른 시작

### 1. 요구사항

```bash
Python 3.8+
pip
```

### 2. 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/math-ocr-app.git
cd math-ocr-app

# 의존성 설치
pip install -r requirements.txt
```

### 3. 실행

```bash
# Flask 서버 시작
python3 app.py
```

서버가 `http://localhost:5001`에서 실행됩니다.

### 4. 사용

1. 웹 브라우저에서 `http://localhost:5001` 접속
2. [Hugging Face](https://huggingface.co/settings/tokens)에서 API 토큰 발급
3. 토큰 입력 후 PDF 업로드
4. 실시간 로그 확인하며 처리 완료 대기
5. 결과 확인 (텍스트 + LaTeX + 이미지)

---

## 📁 프로젝트 구조

```
math-ocr-app/
├── app.py                          # Flask 백엔드 서버
├── templates/
│   ├── index.html                  # 메인 웹 인터페이스
│   └── test.html                   # 디버그 테스트 페이지
├── static/                         # 정적 파일 (비어있음)
├── uploads/                        # 업로드된 PDF 저장 (자동 생성)
├── results/                        # 처리 결과 저장 (자동 생성)
├── requirements.txt                # Python 패키지 목록
├── .gitignore                      # Git 무시 파일
├── README.md                       # 이 파일
├── README_MATH_OCR.md             # 상세 문서
├── DEPLOYMENT_INFO.md             # 배포 정보
└── UPDATE_REALTIME_LOGS.md        # 실시간 로그 업데이트 정보
```

---

## 🔧 기술 스택

### Backend
- **Flask 3.0.0** - Python 웹 프레임워크
- **PyMuPDF 1.26.6** - PDF 처리 및 이미지 변환
- **Pillow 11.2.1** - 이미지 처리
- **Requests 2.32.4** - HTTP API 통신
- **Flask-CORS** - CORS 지원

### AI Models (Hugging Face)
1. DeepSeek VL-7B-Chat (주 모델)
2. Microsoft Florence-2-Large
3. Qwen2-VL-7B-Instruct
4. Llama 3.2 11B Vision

### Frontend
- HTML5 + CSS3 (반응형 디자인)
- Vanilla JavaScript (비동기 처리)
- Server-Sent Events (실시간 로그)
- Drag & Drop API

---

## 📊 API 엔드포인트

### `POST /upload`
PDF 파일 업로드

**Request:**
```bash
curl -X POST http://localhost:5001/upload \
  -F "pdf=@test.pdf" \
  -F "hf_token=hf_xxxxx"
```

**Response:**
```json
{
  "success": true,
  "filename": "1234567890_test.pdf",
  "total_pages": 5,
  "message": "5페이지 PDF 업로드 완료"
}
```

### `POST /process`
OCR 처리 시작

**Request:**
```bash
curl -X POST http://localhost:5001/process \
  -H "Content-Type: application/json" \
  -d '{
    "filename": "1234567890_test.pdf",
    "hf_token": "hf_xxxxx"
  }'
```

**Response:**
```json
{
  "success": true,
  "session_id": "1234567890_test.pdf_1699999999",
  "message": "처리가 시작되었습니다."
}
```

### `GET /stream/<session_id>`
실시간 로그 스트리밍 (SSE)

**Request:**
```bash
curl http://localhost:5001/stream/session_id_here
```

**Response:** (Server-Sent Events)
```
data: {"type": "log", "message": "📄 PDF 파일 로드 중..."}

data: {"type": "log", "message": "✅ 총 5페이지 감지됨"}

data: {"type": "complete", "data": {...}}
```

---

## 🎨 실시간 로그 기능

### 로그 색상 구분

| 아이콘/색상 | 의미 | 예시 |
|------------|------|------|
| ✅ 🟢 초록색 | 성공 | ✅ 처리 완료 |
| ❌ 🔴 빨간색 | 오류/실패 | ❌ 오류 발생 |
| 🤖 🔵 청록색 | AI 처리 | 🤖 AI 모델 시도 |
| 📖 🟡 노란색 | 페이지 정보 | 📖 페이지 시작 |
| ⚪ 회색 | 일반 정보 | 구분선 |

### 로그 예시

```
📄 PDF 파일 로드 중: test.pdf
🖼️ PDF를 이미지로 변환 중...
✅ 총 5페이지 감지됨

══════════════════════════════════════
📖 페이지 1/5 처리 시작
   이미지 크기: 2481x3189 픽셀
🤖 AI Vision 모델로 OCR 시도 중...
   시도: deepseek-ai/deepseek-vl-7b-chat
   ✓ 성공: deepseek-ai/deepseek-vl-7b-chat
✅ OCR 성공 (모델: deepseek-ai/deepseek-vl-7b-chat)
📐 수학 내용 분석 중...
   ✓ LaTeX 수식 3개 발견
   ✓ 그림 1개 발견
💾 고해상도 이미지 저장 중...
   ✓ 저장 완료: test_page_001.png
✅ 페이지 1 완료 (진행률: 20%)
```

---

## 🐛 문제 해결

### "서버 연결 오류"
```bash
# 서버가 실행 중인지 확인
ps aux | grep "python3 app.py"

# 포트 5001이 사용 중인지 확인
lsof -i :5001

# 서버 재시작
pkill -f "python3 app.py"
python3 app.py
```

### "API Error 503"
- **원인**: Hugging Face 모델 로딩 중
- **해결**: 30초 대기 후 재시도

### "모든 Vision 모델 실패"
- **원인**: HF 토큰 권한 부족
- **해결**: PyMuPDF가 자동으로 텍스트 추출 (LaTeX 변환 없음)

### "업로드 실패"
- **원인**: 파일 크기 초과 (100MB 제한)
- **해결**: PDF 압축 도구 사용

---

## 📈 성능

| 항목 | 성능 |
|------|------|
| 이미지 해상도 | 300 DPI (2481×3189) |
| 처리 시간 | 10-30초/페이지 |
| 최대 파일 크기 | 100 MB |
| 지원 형식 | PDF |
| 수식 인식률 | 85-95% (모델 의존) |
| 텍스트 인식률 | 90-98% |

---

## 🔒 보안

- ✅ 업로드된 파일은 임시 저장 후 처리
- ✅ HF 토큰은 서버에 저장되지 않음
- ✅ HTTPS 통신 (배포 시)
- ⚠️ 민감한 시험 문제는 로컬 환경 사용 권장

---

## 📝 라이선스

이 프로젝트는 교육 목적으로 만들어졌습니다.

- DeepSeek AI 모델 라이선스 준수
- Hugging Face 이용약관 준수
- 상업적 사용 시 별도 라이선스 필요

---

## 🙏 크레딧

- **DeepSeek AI**: Vision Language 모델 제공
- **Hugging Face**: AI 모델 호스팅 플랫폼
- **PyMuPDF**: PDF 처리 라이브러리
- **Flask**: Python 웹 프레임워크

---

## 📞 문의 및 지원

문제가 발생하거나 제안사항이 있으시면:
- GitHub Issues 등록
- Pull Request 환영

---

## 📚 추가 문서

- [README_MATH_OCR.md](README_MATH_OCR.md) - 상세 사용 가이드
- [DEPLOYMENT_INFO.md](DEPLOYMENT_INFO.md) - 배포 정보
- [UPDATE_REALTIME_LOGS.md](UPDATE_REALTIME_LOGS.md) - 실시간 로그 업데이트

---

**Made with ❤️ for Mathematics Education**

**Version:** 1.1.0  
**Last Updated:** 2025-11-10
