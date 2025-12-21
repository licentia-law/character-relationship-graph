# -*- coding: utf-8 -*-
"""
인맥도(인물-관계 그래프) MVP v0.1
- Streamlit + NetworkX + PyVis 기반
- 인물(Node)과 관계(Edge)를 입력하고 그래프로 시각화
"""

import json
import os
import uuid
from typing import Dict, List, Any, Optional

import streamlit as st
import networkx as nx
from pyvis.network import Network

# =========================
# 기본 설정
# =========================

# 데이터 저장 경로
DATA_PATH = os.path.join("data", "graph.json")

# =========================
# 데이터 입출력 관련 함수
# =========================

def load_data(path: str) -> Dict[str, Any]:
    """
    graph.json 파일을 로드
    파일이 없으면 기본 구조 반환
    """
    if not os.path.exists(path):
        return {"meta": {"project": "Untitled"}, "nodes": [], "edges": []}

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(path: str, data: Dict[str, Any]) -> None:
    """
    현재 그래프 데이터를 JSON 파일로 저장
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def new_id(prefix: str) -> str:
    """
    노드(n_), 엣지(e_)용 간단한 UUID 생성
    """
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


# =========================
# 그래프 구성 관련 함수
# =========================

def build_graph(data: Dict[str, Any]) -> nx.MultiDiGraph:
    """
    JSON 데이터를 NetworkX MultiDiGraph로 변환
    - 방향성 관계 지원
    - 무방향 관계는 역방향 edge를 하나 더 생성
    """
    G = nx.MultiDiGraph()

    # 노드 추가
    for n in data.get("nodes", []):
        G.add_node(n["id"], **n)

    # 엣지 추가
    for e in data.get("edges", []):
        G.add_edge(
            e["source_id"],
            e["target_id"],
            key=e["id"],
            **e
        )

        # 무방향 관계라면 반대 방향 edge도 추가
        if not e.get("directional", True):
            G.add_edge(
                e["target_id"],
                e["source_id"],
                key=e["id"] + "_rev",
                **{**e, "id": e["id"], "is_reverse": True}
            )

    return G


def pyvis_html(
    G: nx.MultiDiGraph,
    highlight_node_id: Optional[str],
    allowed_relation_types: Optional[set]
) -> str:
    """
    NetworkX 그래프를 PyVis HTML로 변환
    - 선택된 노드 하이라이트
    - 관계 유형 필터 적용
    """
    net = Network(
        height="650px",
        width="100%",
        bgcolor="#ffffff",
        font_color="#222222",
        directed=True
    )

    net.barnes_hut()

    # =========================
    # 노드 렌더링
    # =========================
    for nid, attrs in G.nodes(data=True):
        title = (
            f"<b>{attrs.get('name','')}</b><br/>"
            f"type: {attrs.get('type','person')}<br/>"
            f"aliases: {', '.join(attrs.get('aliases', []) or [])}<br/>"
            f"tags: {', '.join(attrs.get('tags', []) or [])}<br/>"
            f"notes: {attrs.get('notes','')}"
        )

        net.add_node(
            nid,
            label=attrs.get("name", nid),
            title=title,
            value=10,
            borderWidth=3 if highlight_node_id == nid else 1
        )

    # =========================
    # 엣지 렌더링
    # =========================
    for u, v, k, attrs in G.edges(keys=True, data=True):

        # 내부 처리용 reverse edge는 화면에 표시하지 않음
        if attrs.get("is_reverse"):
            continue

        relation_type = attrs.get("relation_type", "관련")

        # 관계유형 필터 적용
        if allowed_relation_types and relation_type not in allowed_relation_types:
            continue

        title = (
            f"type: {relation_type}<br/>"
            f"evidence: {attrs.get('evidence','')}<br/>"
            f"note: {attrs.get('note','')}"
        )

        net.add_edge(
            u,
            v,
            label=relation_type,
            title=title,
            arrows="to" if attrs.get("directional", True) else ""
        )

    # 물리 엔진 옵션 (배치 안정화)
    net.set_options("""
    var options = {
      "physics": {
        "barnesHut": {
          "gravitationalConstant": -8000,
          "springLength": 180
        },
        "minVelocity": 0.75
      },
      "interaction": {
        "hover": true,
        "tooltipDelay": 120
      }
    }
    """)

    return net.generate_html()


# =========================
# 검색 / 유틸 함수
# =========================

def find_node_by_name(data: Dict[str, Any], q: str) -> Optional[Dict[str, Any]]:
    """
    이름 또는 별명으로 인물 검색
    """
    q = (q or "").strip().lower()
    if not q:
        return None

    for n in data.get("nodes", []):
        if q in n.get("name", "").lower():
            return n

        aliases = [a.lower() for a in (n.get("aliases") or [])]
        if any(q in a for a in aliases):
            return n

    return None


def get_node(data: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
    """
    node_id로 인물 조회
    """
    for n in data.get("nodes", []):
        if n["id"] == node_id:
            return n
    return None


def edges_for_node(
    data: Dict[str, Any],
    node_id: str,
    allowed_relation_types: Optional[set]
) -> List[Dict[str, Any]]:
    """
    특정 인물과 연결된 관계 목록 반환
    """
    result = []

    for e in data.get("edges", []):
        if allowed_relation_types and e.get("relation_type") not in allowed_relation_types:
            continue

        if e["source_id"] == node_id or e["target_id"] == node_id:
            result.append(e)

    return result


# =========================
# Streamlit UI 시작
# =========================

st.set_page_config(
    page_title="People Graph MVP",
    layout="wide"
)

st.title("인맥도(인물-관계 그래프) MVP v0.1")

# 데이터 로드
data = load_data(DATA_PATH)

# =========================
# 사이드바: 프로젝트 / 가져오기 / 내보내기
# =========================

with st.sidebar:
    st.subheader("프로젝트")

    project = st.text_input(
        "프로젝트명",
        value=data.get("meta", {}).get("project", "Untitled")
    )
    data.setdefault("meta", {})["project"] = project

    st.divider()
    st.subheader("가져오기 / 내보내기")

    # JSON 가져오기
    uploaded = st.file_uploader("JSON 가져오기", type=["json"])
    if uploaded:
        imported = json.loads(uploaded.read().decode("utf-8"))
        if "nodes" in imported and "edges" in imported:
            data = imported
            save_data(DATA_PATH, data)
            st.success("가져오기 완료")
        else:
            st.error("올바르지 않은 형식")

    # JSON 내보내기
    st.download_button(
        "현재 데이터 다운로드",
        data=json.dumps(data, ensure_ascii=False, indent=2),
        file_name="graph.json",
        mime="application/json"
    )

# =========================
# 메인 레이아웃
# =========================

left, mid, right = st.columns([1.1, 2.2, 1.2], gap="large")

# =========================
# 좌측: 입력 영역 (인물 / 관계)
# =========================

with left:
    st.subheader("입력")
    tab1, tab2 = st.tabs(["인물", "관계"])

    # -------- 인물 --------
    with tab1:
        st.caption("인물 추가 / 수정")

        mode = st.radio("모드", ["추가", "수정"], horizontal=True)

        if mode == "수정" and data["nodes"]:
            options = {f"{n['name']} ({n['id']})": n["id"] for n in data["nodes"]}
            selected = st.selectbox("수정할 인물", list(options.keys()))
            edit_id = options[selected]
            current = get_node(data, edit_id)
        else:
            edit_id = None
            current = {}

        name = st.text_input("이름", value=current.get("name", ""))
        aliases = st.text_input("별명(쉼표)", value=", ".join(current.get("aliases", [])))
        ntype = st.selectbox("type", ["person", "org", "place", "concept"])
        tags = st.text_input("태그(쉼표)", value=", ".join(current.get("tags", [])))
        notes = st.text_area("설명", value=current.get("notes", ""), height=100)

        if st.button("저장", use_container_width=True):
            if not name.strip():
                st.warning("이름은 필수입니다.")
            else:
                node = {
                    "id": edit_id or new_id("n"),
                    "name": name.strip(),
                    "aliases": [a.strip() for a in aliases.split(",") if a.strip()],
                    "type": ntype,
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    "notes": notes.strip(),
                }

                if edit_id:
                    data["nodes"] = [node if n["id"] == edit_id else n for n in data["nodes"]]
                    st.success("인물 수정 완료")
                else:
                    data["nodes"].append(node)
                    st.success("인물 추가 완료")

                save_data(DATA_PATH, data)

    # -------- 관계 --------
    with tab2:
        st.caption("관계 추가")

        if len(data["nodes"]) < 2:
            st.info("인물을 2명 이상 추가하세요.")
        else:
            id_to_name = {n["id"]: n["name"] for n in data["nodes"]}

            source = st.selectbox("Source", list(id_to_name.keys()),
                                  format_func=lambda x: id_to_name[x])
            target = st.selectbox("Target", list(id_to_name.keys()),
                                  format_func=lambda x: id_to_name[x])

            relation_type = st.text_input("관계유형", value="관련")
            directional = st.checkbox("방향성", value=True)
            weight = st.slider("가중치", 0.0, 1.0, 0.5)
            evidence = st.text_input("근거(권/챕터/페이지)")
            note = st.text_area("메모", height=80)

            if st.button("관계 저장", use_container_width=True):
                if source == target:
                    st.warning("같은 인물끼리는 연결할 수 없습니다.")
                else:
                    data["edges"].append({
                        "id": new_id("e"),
                        "source_id": source,
                        "target_id": target,
                        "relation_type": relation_type,
                        "directional": directional,
                        "weight": weight,
                        "evidence": evidence,
                        "note": note,
                    })
                    save_data(DATA_PATH, data)
                    st.success("관계 추가 완료")

# =========================
# 중앙: 그래프
# =========================

with mid:
    st.subheader("그래프")

    all_types = sorted({e["relation_type"] for e in data["edges"]})
    selected_types = st.multiselect("관계유형 필터", all_types, default=all_types)
    allowed_types = set(selected_types) if selected_types else None

    q = st.text_input("검색(이름/별명)")
    hit = find_node_by_name(data, q)
    highlight = hit["id"] if hit else None

    G = build_graph(data)
    html = pyvis_html(G, highlight, allowed_types)
    st.components.v1.html(html, height=680, scrolling=True)

# =========================
# 우측: 상세 정보
# =========================

with right:
    st.subheader("상세")

    if hit:
        st.markdown(f"### {hit['name']}")
        st.write("type:", hit["type"])
        st.write("aliases:", ", ".join(hit["aliases"]))
        st.write("tags:", ", ".join(hit["tags"]))
        st.write(hit["notes"])

        st.divider()
        st.markdown("#### 연결 관계")

        for e in edges_for_node(data, hit["id"], allowed_types):
            st.markdown(
                f"- **{e['relation_type']}** : "
                f"{e['source_id']} → {e['target_id']}"
            )
            if e["evidence"]:
                st.caption(f"근거: {e['evidence']}")
            if e["note"]:
                st.caption(f"메모: {e['note']}")
    else:
        st.caption("검색으로 인물을 선택하세요.")
