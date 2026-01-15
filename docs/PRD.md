# 인맥도(인물-관계 그래프) MVP PRD v0.1

## 1. 목표
책/드라마/프로젝트 등에서 **인물(노드)** 과 **관계(엣지)** 를 입력·관리하고, 웹브라우저에서 **인터랙티브 그래프**로 탐색합니다.  
Obsidian 그래프뷰처럼 “링크”가 아니라, **관계 자체(유형/근거/메모)** 를 1급 데이터로 다룹니다.

## 2. 사용자 시나리오 (삼체 예시)
- 사용자는 인물 A(왕먀오)와 인물 B(스창)의 관계를 `협력` 으로 기록하고, 근거를 `1권 3장 p.57`로 남긴다.
- 그래프에서 왕먀오를 클릭하면 연결된 관계 목록이 오른쪽 패널에 뜬다.
- 관계 유형(협력/적대/가족/소속 등)으로 필터링해 “ETO 소속” 관계만 본다.

## 3. 범위(스코프)
### 포함 (v0.1)
1) 인물 CRUD
- 이름, 별명, 태그, 설명(노트)
2) 관계 CRUD
- source, target, 관계유형(type), 방향성(directional), 가중치(weight), 근거(evidence), 메모(note)
3) 시각화/탐색
- 검색(이름/별명)
- 필터(관계유형, 태그)
- 노드 클릭 시 상세 정보 패널(인물 정보 + 연결 관계 리스트)
4) 저장
- 로컬 `data/graph.json` 파일에 저장/불러오기

### 제외 (나중)
- 로그인/동기화, 협업, 권한
- 추천/자동 추출(NLP)
- 타임라인 애니메이션
- Obsidian Vault 자동 연동(단, v0.3 목표로 확장 설계 반영)

## 4. 데이터 모델
### Node (인물/조직/장소로 확장 가능)
- id: uuid
- name: str
- aliases: list[str]
- type: "person" | "org" | "place" | "concept"
- tags: list[str]
- notes: str

### Edge (관계)
- id: uuid
- source_id: uuid
- target_id: uuid
- relation_type: str (예: friend, enemy, family, member_of, cooperates_with)
- directional: bool
- weight: float | null
- evidence: str (예: “1권 3장 p.57”, 링크 등)
- note: str

## 5. 화면/UX (v0.1)
- 좌측: 데이터 입력 탭
  - [인물 추가/수정]
  - [관계 추가/수정]
- 중앙: 그래프(드래그, 확대/축소)
- 우측: 선택 항목 상세
  - 인물: 속성 + 연결 관계 리스트
  - 관계: 관계 속성

## 6. 기술 스택(권장)
- Python 3.11+
- Streamlit (UI/서빙)
- networkx (그래프 관리)
- pyvis (vis.js 기반 HTML 그래프 렌더)
- JSON 파일 저장 (v0.1), v1.0에서 SQLite로 전환 권장

## 7. 수용 기준(Definition of Done)
- 인물 10명, 관계 20개를 입력 후 재실행해도 데이터가 유지된다.
- 그래프에서 노드 클릭 시 상세가 표시된다.
- 관계유형 필터가 동작한다.
- 검색으로 노드를 하이라이트할 수 있다.

## 8. 다음 버전 로드맵(요약)
- v0.2: CSV/JSON import/export, 관계유형 컬러, 최단경로 탐색
- v0.3: Obsidian YAML 읽기(인물 노트), 관계 노트 지원, Obsidian URI 열기
- v1.0: SQLite, 프로젝트(작품) 단위 분리, 백업/버전
