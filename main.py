# app.py
import streamlit as st
from datetime import datetime, timedelta
import random
import textwrap

# -----------------------------
# Page Config & Global Styles
# -----------------------------
st.set_page_config(
    page_title="MBTI 공부법 추천기 🎓",
    page_icon="🧠",
    layout="centered",
)

# Fun gradient title + subtle animations (CSS only)
st.markdown("""
<style>
:root {
  --card-bg: #111418;
  --muted: #9aa4ad;
  --grad1: linear-gradient(90deg,#7c4dff, #00e5ff 30%, #00e676 60%, #ffeb3b 90%);
}
* {scroll-behavior:smooth;}
h1 span.gradient {
  background: var(--grad1);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  animation: hue 8s linear infinite;
}
@keyframes hue { from { filter:hue-rotate(0deg);} to {filter:hue-rotate(360deg);} }

div.stMarkdown p.badge {
  display:inline-block; padding:.25rem .6rem; border-radius:999px; 
  background:#1d232b; color:#cbd5e1; font-size:.8rem; border:1px solid #2b3440;
}
.card {
  background: rgba(255,255,255,0.03); border:1px solid #2b3440;
  padding:1rem; border-radius:1rem; transition: transform .2s ease, box-shadow .2s ease;
}
.card:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,0,0,.2); }
.kicker { color: var(--muted); font-size:.9rem; letter-spacing:.04em; text-transform:uppercase; }
.codeish { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Data
# -----------------------------
MBTIS = [
    "INTJ","INTP","ENTJ","ENTP",
    "INFJ","INFP","ENFJ","ENFP",
    "ISTJ","ISFJ","ESTJ","ESFJ",
    "ISTP","ISFP","ESTP","ESFP"
]

TEMPERAMENT = {
    "Analyst (NT) 🧪": {"members": ["INTJ","INTP","ENTJ","ENTP"], "accent":"🟣"},
    "Diplomat (NF) 🕊️": {"members": ["INFJ","INFP","ENFJ","ENFP"], "accent":"🟢"},
    "Sentinel (SJ) 🧱": {"members": ["ISTJ","ISFJ","ESTJ","ESFJ"], "accent":"🔵"},
    "Explorer (SP) 🧭": {"members": ["ISTP","ISFP","ESTP","ESFP"], "accent":"🟠"},
}

RECOMMENDATIONS = {
    # NT
    "INTJ": {
        "motto":"전략은 간결하게, 실행은 꾸준하게 ♟️",
        "style":"장기 목표에서 역산해 계획 세우는 걸 선호. 깊이 있는 몰입 학습에 강함.",
        "tips":[
            "🎯 역산 계획(Goal → Milestones → Daily 3 Tasks)으로 학습 범위 좁히기",
            "📚 스파이럴 노트(한 주제 3회 반복)로 장기기억 강화",
            "⏱️ 50-10 포모도로(50분 집중/10분 리셋)로 딥워크 시간확보",
            "🧩 어려운 문제는 ‘가설→실험→결론’ 템플릿으로 정리",
        ],
        "avoid":[
            "끝없는 자료 수집만 하다 시작 못하는 것",
            "완벽한 준비가 될 때까지 미루는 것",
        ],
        "tools":["Obsidian", "Notion DB", "Anki Cloze"],
        "sprint":{"focus":50,"break":10,"sets":3}
    },
    "INTP": {
        "motto":"호기심이 커리큘럼이다 🧪",
        "style":"개념 연결과 모델링에 강점. ‘왜?’를 파고들며 이해 중심.",
        "tips":[
            "🗺️ 개념지도로 전후 개념 연결(원인→메커니즘→결과)",
            "🧠 ‘자기 설명(Self-Explain)’로 풀이 과정 말로 풀기",
            "⏱️ 40-10-10(집중-리뷰-산책) 루틴으로 발산/수렴 균형",
            "🧩 오답은 ‘오개념 로그’로 기록(틀린 이유 분류)",
        ],
        "avoid":["완벽한 이론 정리 전 실전 회피", "탭과 참고자료 과다"],
        "tools":["Obsidian Graph","Excalidraw","Anki"],
        "sprint":{"focus":40,"break":10,"sets":4}
    },
    "ENTJ": {
        "motto":"목표는 수치로, 진도는 속도로 📈",
        "style":"성과 지향. 타임박싱과 KPI 기반 관리에 강함.",
        "tips":[
            "🏁 주간 KPI(문제수/챕터수/요약카드 수) 정의",
            "📆 타임블록(아침 전략, 저녁 리뷰) 고정",
            "👥 스터디 리드(서약+리뷰)로 책임감 부여",
            "⚡ ‘1x 속독 → 2x 문제 → 0.5x 정리’ 3회전",
        ],
        "avoid":["과한 욕심으로 번아웃", "휴식 무시"],
        "tools":["Notion Kanban","Toggle Track","Quizlet"],
        "sprint":{"focus":45,"break":10,"sets":4}
    },
    "ENTP": {
        "motto":"아이디어로 시작해 실전으로 증명하라 💡",
        "style":"브레인스토밍과 역발상에 강함. 실전 문제로 배우기 적합.",
        "tips":[
            "🌀 ‘10분 아이디어 덤프’ 후 문제셋으로 검증",
            "🎤 러버덕 설명/튜터 역할로 개념 확정",
            "🔁 변형문제(조건 바꾸기)로 전이학습",
            "⏱️ 35-7-3(집중-짧은휴식-마이크로정리)",
        ],
        "avoid":["주제 과잉 확장", "루틴 불안정"],
        "tools":["Mindmap","StackEdit","Khan Academy"],
        "sprint":{"focus":35,"break":7,"sets":5}
    },
    # NF
    "INFJ": {
        "motto":"의미를 이해로, 이해를 습관으로 🌙",
        "style":"의미와 맥락을 중시. 조용한 몰입 환경에서 강함.",
        "tips":[
            "🕯️ 의도 선언문 작성(Why-What-How) 후 시작",
            "📓 ‘한 문단 요지 1문장’ 습관으로 핵심화",
            "🧘 45-10 포커스 + 2세트 후 감정 체크",
            "💬 스스로에게 가르치듯 노트(Teach-yourself Note)",
        ],
        "avoid":["타인을 지나치게 돕다 자기 시간 소모", "완벽주의"],
        "tools":["Notion Template","Calm","Anki"],
        "sprint":{"focus":45,"break":10,"sets":3}
    },
    "INFP": {
        "motto":"동기 불씨를 목표 엔진으로 🔥",
        "style":"내적 동기로 장거리 학습. 스토리텔링에 강점.",
        "tips":[
            "📚 ‘스토리 노트’: 개념을 작은 이야기로 연결",
            "🎯 ‘오늘의 3가지 착한 목표’(작고 선명)",
            "⏱️ 30-5-10(집중-짧은휴식-리플렉션)",
            "🌱 보상 루틴(작은 간식/산책)으로 지속성 강화",
        ],
        "avoid":["동기 떨어질 때 전면 중단", "목표 추상화 과다"],
        "tools":["Daylio","Forest","GoodNotes"],
        "sprint":{"focus":30,"break":5,"sets":5}
    },
    "ENFJ": {
        "motto":"함께 배우고 서로 성장하기 🤝",
        "style":"협업과 피드백에 강함. 구조화된 계획에 적합.",
        "tips":[
            "👥 페어스터디(서로 가르치기 10분 교대)",
            "🗂️ 체크리스트+리뷰 미팅(주 1회)",
            "📢 발표용 슬라이드로 요약(5장 이내)",
            "⏱️ 40-10 루틴 + 마지막 5분 칭찬 피드백",
        ],
        "avoid":["타인 일정에 끌려 자기 시간 부족", "과도한 약속"],
        "tools":["Google Slides","Notion DB","Pomofocus"],
        "sprint":{"focus":40,"break":10,"sets":4}
    },
    "ENFP": {
        "motto":"재미를 설계하면 집중은 따라온다 🎉",
        "style":"다채로운 자극에서 에너지. 게임화가 잘 맞음.",
        "tips":[
            "🎮 XP 시스템(문제=+10XP, 요약=+20XP)로 gamification",
            "🧩 ‘랜덤 퀘스트’ 15분 미션 뽑기",
            "🔁 25-5 스프린트로 잦은 리셋",
            "📣 친구에게 하루 1가지 배운 점 공유",
        ],
        "avoid":["할 일 분산, 맥락 전환 과다", "야밤 과몰입"],
        "tools":["Habitica","Quizlet","Trello"],
        "sprint":{"focus":25,"break":5,"sets":6}
    },
    # SJ
    "ISTJ": {
        "motto":"정석을 지키면 성적은 오른다 📘",
        "style":"체계적/절차적 학습에 강함. 규칙적인 루틴 선호.",
        "tips":[
            "📅 주간 커리큘럼(장표/페이지/문제수) 수치화",
            "🧱 기본→유형→실전 3단계 체크박스",
            "⏱️ 45-10 포모도로, 마지막 5분 체크리스트",
            "🗄️ 오답은 원인 라벨(개념/실수/시간)로 관리",
        ],
        "avoid":["유연성 부족으로 계획 변경 거부", "완벽히 채워야 시작"],
        "tools":["Excel/Sheets","GoodNotes","Pomodoro"],
        "sprint":{"focus":45,"break":10,"sets":4}
    },
    "ISFJ": {
        "motto":"차분함이 최고의 생산성 🌿",
        "style":"안정적 환경에서 꾸준히. 상세한 기록 선호.",
        "tips":[
            "📓 ‘오늘 배운 5문장’ 일지",
            "🔁 낮은 난도 반복→자신감→상향 난도",
            "⏱️ 35-7 루틴 + 스트레칭",
            "🧺 공부 공간 정돈 의식(시작 신호)",
        ],
        "avoid":["도움요청 망설임", "과한 낮은 난도 고착"],
        "tools":["Notion Template","TickTick","YouTube 1.25x"],
        "sprint":{"focus":35,"break":7,"sets":5}
    },
    "ESTJ": {
        "motto":"계획·실행·통제·개선 ♻️",
        "style":"표준화된 절차와 관리에 강함.",
        "tips":[
            "📊 진도 대시보드(일/주) 운영",
            "🧪 모의고사 주기적 시행→AAR(사후분석)",
            "⏱️ 50-10 집약 루틴",
            "🤝 책임 파트너와 상호 점검",
        ],
        "avoid":["결과만 보고 과정 개선 소홀", "휴식 경시"],
        "tools":["Notion Kanban","Google Forms Quiz","RescueTime"],
        "sprint":{"focus":50,"break":10,"sets":3}
    },
    "ESFJ": {
        "motto":"관계의 힘으로 습관을 만든다 💞",
        "style":"협력/격려 환경에서 꾸준히.",
        "tips":[
            "👭 체크인 버디(아침/저녁 5분)",
            "🎤 스터디 발표(짧고 자주)",
            "⏱️ 30-5 루틴 + 그룹 리뷰",
            "🍵 휴식에 소셜 보상(짧은 통화/메신저)",
        ],
        "avoid":["타인 일정 우선으로 자기 계획 흔들림"],
        "tools":["Google Calendar","Shared Notes","Quizlet Live"],
        "sprint":{"focus":30,"break":5,"sets":6}
    },
    # SP
    "ISTP": {
        "motto":"손으로 배우면 오래간다 🔧",
        "style":"문제 해결형·실습형에 강함.",
        "tips":[
            "🧰 실습/케이스 먼저 → 이론 역추적",
            "⏱️ 30-5 스프린트 + ‘1문제 1원인’ 로그",
            "📷 풀이 사진/클립으로 빠른 회고",
            "🧩 퍼즐형 문제로 난이도 곡선 설계",
        ],
        "avoid":["지루하면 즉시 이탈 → 짧고 자주로 설계"],
        "tools":["Notability","Desmos","LeetCode"],
        "sprint":{"focus":30,"break":5,"sets":6}
    },
    "ISFP": {
        "motto":"감각을 정돈하면 집중이 선명해진다 🎨",
        "style":"미적·감각적 자극에 동기. 조용한 공간 선호.",
        "tips":[
            "🎧 ‘집중 플레이리스트’ 의식화",
            "📝 컬러코딩 요약카드(3색 규칙)",
            "⏱️ 30-5 루틴 + 산책 보상",
            "🌤️ 아침 햇빛/통풍으로 시작 의식",
        ],
        "avoid":["환경 정돈 없을 때 집중 난항"],
        "tools":["GoodNotes","Lo-fi Playlist","Anki Image Occlusion"],
        "sprint":{"focus":30,"break":5,"sets":6}
    },
    "ESTP": {
        "motto":"실전 감각으로 터득하라 🏃",
        "style":"경쟁·속도·체험형. 타이머와 랭킹 효과적.",
        "tips":[
            "⏱️ 타임어택 문제셋(제한시간 기록)",
            "📣 스터디 배틀/퀴즈쇼",
            "🔁 빠른 시도→바로 피드백→재도전 루프",
            "🧠 20-5-5(집중-휴식-리뷰) 고빈도",
        ],
        "avoid":["속도만 강조해 품질 저하"],
        "tools":["Kahoot!","Stopwatch","Anki Speed Drill"],
        "sprint":{"focus":20,"break":5,"sets":7}
    },
    "ESFP": {
        "motto":"즐거움이 최강 연료 🎊",
        "style":"사회적 상호작용/리듬감에 동기.",
        "tips":[
            "🎵 리듬 암기(라임/비트) + 스터디 하이라이트 영상",
            "👯 듀오 학습(서로 촬영·칭찬·교정)",
            "⏱️ 25-5 루틴 + 보상식(스낵/댄스)",
            "🪄 ‘5분만 시작’ 마법으로 진입장벽 제거",
        ],
        "avoid":["잡담/알림 과다 → 방해요소 차단"],
        "tools":["Focus To-Do","WhatsApp Study Group","Quizlet"],
        "sprint":{"focus":25,"break":5,"sets":6}
    },
}

def group_of(mbti:str)->str:
    for k,v in TEMPERAMENT.items():
        if mbti in v["members"]: return f'{k} {v["accent"]}'
    return "MBTI"

def confetti():
    # playful effects (works in Streamlit Cloud)
    try:
        st.balloons()
        # st.snow()  # uncomment if you like snow ❄️
        st.toast("공부 매칭 완료! ✨", icon="🎯")
    except Exception:
        pass

def sprint_plan(mbti:str):
    s = RECOMMENDATIONS[mbti]["sprint"]
    total_min = s["sets"] * (s["focus"] + s["break"])
    return s, total_min

# -----------------------------
# Sidebar (Controls)
# -----------------------------
with st.sidebar:
    st.markdown("### 🎛️ 옵션")
    mbti = st.selectbox("MBTI를 선택하세요", MBTIS, index=MBTIS.index("ENFP") if "ENFP" in MBTIS else 0)
    fun_mode = st.toggle("🎉 파티 모드(애니메이션)", value=True)
    today = st.date_input("시작 날짜", value=datetime.now().date())
    st.markdown("<p class='badge'>Tip: 선택만 해도 추천이 업데이트돼요!</p>", unsafe_allow_html=True)

# Progress shimmer
with st.spinner("당신의 성향에 맞는 학습 레시피를 조합 중…🧪"):
    rec = RECOMMENDATIONS[mbti]
    splan, total_min = sprint_plan(mbti)

if fun_mode:
    confetti()

# -----------------------------
# Header
# -----------------------------
st.markdown("<div class='kicker'>Study Matchmaking</div>", unsafe_allow_html=True)
st.markdown(f"# <span class='gradient'>{mbti}</span>에게 딱 맞는 공부법 🧠✨", unsafe_allow_html=True)
st.caption(f"{group_of(mbti)} · 오늘 {today.strftime('%Y-%m-%d')} 기준 추천")

# -----------------------------
# Summary Row
# -----------------------------
c1, c2 = st.columns(2, vertical_alignment="center")
with c1:
    st.markdown("#### 🧭 학습 모토")
    st.markdown(f"<div class='card'>{rec['motto']}</div>", unsafe_allow_html=True)

with c2:
    st.markdown("#### 🎨 학습 스타일")
    st.markdown(f"<div class='card'>{rec['style']}</div>", unsafe_allow_html=True)

# -----------------------------
# Cards: Tips / Avoid / Tools
# -----------------------------
st.markdown("#### 📚 핵심 루틴 & 팁")
st.markdown("<div class='card'>"+ "<br>".join(f"• {t}" for t in rec["tips"]) + "</div>", unsafe_allow_html=True)

c3, c4 = st.columns([1,1])
with c3:
    st.markdown("#### ⚠️ 이런 점을 주의해요")
    st.markdown("<div class='card'>"+ "<br>".join(f"• {t}" for t in rec["avoid"]) + "</div>", unsafe_allow_html=True)
with c4:
    st.markdown("#### 🛠️ 잘 맞는 도구")
    st.markdown("<div class='card'>"+ " | ".join(f"🔗 {t}" for t in rec["tools"]) + "</div>", unsafe_allow_html=True)

# -----------------------------
# Sprint Generator
# -----------------------------
st.markdown("#### ⏱️ 스터디 스프린트 생성기")
focus = splan["focus"]; br = splan["break"]; sets = splan["sets"]
start_time = datetime.combine(today, datetime.min.time()).replace(hour=9)
blocks = []
t = start_time
for i in range(1, sets+1):
    f_end = t + timedelta(minutes=focus)
    b_end = f_end + timedelta(minutes=br)
    blocks.append((i, t, f_end, "🎯 집중"))
    blocks.append((i, f_end, b_end, "☕ 휴식"))
    t = b_end

st.markdown(
    f"<div class='card'>"
    f"<b>추천 루틴:</b> {focus}분 집중 + {br}분 휴식 × {sets}세트 "
    f"(총 약 <b>{total_min}분</b>)</div>",
    unsafe_allow_html=True
)

# Show as a neat table-like text (keeps dependencies minimal)
for (i, s, e, label) in blocks:
    st.write(f"{i}세트 | {s.strftime('%H:%M')} → {e.strftime('%H:%M')} | {label}")

# -----------------------------
# Downloadable Personalized Plan
# -----------------------------
plan_text = textwrap.dedent(f"""
🎓 MBTI 공부법 추천 요약 — {mbti}

• 모토: {rec['motto']}
• 스타일: {rec['style']}

📚 핵심 팁
{chr(10).join("- " + t for t in rec['tips'])}

⚠️ 주의할 점
{chr(10).join("- " + t for t in rec['avoid'])}

🛠️ 도구
{", ".join(rec['tools'])}

⏱️ 스프린트
- {focus}분 집중 + {br}분 휴식 × {sets}세트 (총 약 {total_min}분)
- 시작: {start_time.strftime('%Y-%m-%d %H:%M')}

Made with ❤️ in Streamlit
""").strip()

st.download_button(
    "📄 내 맞춤 학습 플랜 저장하기",
    data=plan_text.encode("utf-8"),
    file_name=f"Study_Plan_{mbti}.txt",
    mime="text/plain",
)

# -----------------------------
# Tiny FAQ / Science Behind
# -----------------------------
with st.expander("🔬 왜 이런 추천이 나왔나요? (열어서 보기)"):
    st.markdown("""
- 개인 성향(MBTI)의 일반적 학습 선호를 바탕으로 **루틴·도구·주의점**을 매칭했습니다.  
- 핵심 원리: **반복노출(Spaced Repetition)**, **회상 연습(Retrieval Practice)**, **오류기록(Error Log)**, **메타인지 리뷰(Metacognition)**.  
- 사람마다 차이가 크니, 1~2주간 써보고 **수치(문제수/시간/정답률)**로 조정하세요.  
""")

st.markdown("---")
st.caption("💡 팁: 사이드바에서 MBTI를 바꾸면 즉시 새로운 추천이 적용돼요!")
