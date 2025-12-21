# People Graph MVP (Streamlit + PyVis)

## 실행 방법
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate

pip install -r requirements.txt
streamlit run app.py
```

## 데이터
- `data/graph.json` 에 저장됩니다.
- 샘플 데이터: `data/sample_san-ti.json`

## 기능(v0.1)
- 인물/관계 추가
- 그래프 시각화
- 검색/필터
- 클릭 상세(우측 패널)
