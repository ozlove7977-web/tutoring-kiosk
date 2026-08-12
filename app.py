import base64
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(
    page_title="Private Tutoring",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

KST = ZoneInfo("Asia/Seoul")

ADMIN_PASSWORD = str(st.secrets["ADMIN_PASSWORD"])

AUTO_RETURN_SECONDS = 17

SETTINGS_FILE = Path("settings.json")


# ============================================================
# 사운드 파일
# ============================================================

TEN_MINUTES_SOUND = "sounds/ten_minutes.mp3"
SCHOOL_BELL_SOUND = "sounds/school_bell.mp3"
FINISHED_SOUND = "sounds/class_finished.mp3"


# ============================================================
# 기본 관리자 설정
# ============================================================

DEFAULT_SETTINGS = {
    "cello_minutes": 60,
    "english_minutes": 90,
    "volume": 80,
}


# ============================================================
# 설정 불러오기
# ============================================================

def load_settings():

    if not SETTINGS_FILE.exists():
        return DEFAULT_SETTINGS.copy()

    try:

        with open(
            SETTINGS_FILE,
            "r",
            encoding="utf-8",
        ) as f:

            saved = json.load(f)

        settings = DEFAULT_SETTINGS.copy()
        settings.update(saved)

        return settings

    except Exception:

        return DEFAULT_SETTINGS.copy()


# ============================================================
# 설정 저장하기
# ============================================================

def save_settings(settings):

    with open(
        SETTINGS_FILE,
        "w",
        encoding="utf-8",
    ) as f:

        json.dump(
            settings,
            f,
            ensure_ascii=False,
            indent=2,
        )


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "startup_authenticated": False,
    "admin_authenticated": False,

    "page": "welcome",

    "lesson": None,

    "start_time": None,
    "end_time": None,

    "warning_played": False,

    "finish_sound_needed": False,
    "complete_started_at": None,

    "settings": load_settings(),
}


for key, value in DEFAULTS.items():

    if key not in st.session_state:
        st.session_state[key] = value


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Streamlit 기본 UI 숨기기 */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        visibility: hidden;
    }

    [data-testid="stHeader"] {
        display: none !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    [data-testid="stSidebar"] {
        display: none !important;
    }


    /* ========================================================
       전체 배경
       ======================================================== */

    .stApp {

        background:
            radial-gradient(
                circle at 15% 20%,
                rgba(72, 92, 190, 0.13),
                transparent 32%
            ),
            radial-gradient(
                circle at 85% 80%,
                rgba(130, 70, 180, 0.10),
                transparent 32%
            ),
            linear-gradient(
                135deg,
                #080a0f 0%,
                #10131b 50%,
                #07090d 100%
            );

        color: white;
    }


    .block-container {

        max-width: 1200px;

        padding-top: 4vh;
        padding-bottom: 4vh;
    }


    /* ========================================================
       공통
       ======================================================== */

    .brand {

        color: #768096;

        font-size: 11px;

        font-weight: 700;

        letter-spacing: 0.32em;
    }


    /* ========================================================
       최초 로그인 / 관리자
       ======================================================== */

    .admin-screen {

        min-height: 55vh;

        display: flex;

        flex-direction: column;

        justify-content: flex-end;

        align-items: center;

        text-align: center;
    }


    .admin-title {

        margin-top: 22px;

        font-size:
            clamp(42px, 5vw, 68px);

        font-weight: 800;

        letter-spacing: -0.05em;
    }


    .admin-subtitle {

        margin-top: 12px;

        margin-bottom: 28px;

        color: #8e96a7;

        font-size: 15px;
    }


    .setting-label {

        color: #a1a8b7;

        font-size: 13px;

        font-weight: 700;

        letter-spacing: 0.08em;

        margin-top: 24px;

        margin-bottom: 10px;
    }


    /* ========================================================
       WELCOME
       ======================================================== */

    .welcome {

        min-height: 63vh;

        display: flex;

        flex-direction: column;

        justify-content: center;
    }


    .system-ready {

        display: inline-block;

        margin-top: 18px;

        padding: 9px 14px;

        border-radius: 100px;

        border:
            1px solid rgba(255,255,255,0.08);

        background:
            rgba(255,255,255,0.03);

        color: #929bad;

        font-size: 11px;

        font-weight: 700;

        letter-spacing: 0.15em;
    }


    .green-dot {

        color: #61e69d;

        margin-right: 8px;
    }


    .welcome-title {

        margin-top: 25px;

        font-size:
            clamp(58px, 8vw, 105px);

        line-height: 0.95;

        font-weight: 800;

        letter-spacing: -0.06em;
    }


    .welcome-subtitle {

        margin-top: 22px;

        color: #8c94a5;

        font-size: 17px;
    }


    /* ========================================================
       수업 선택
       ======================================================== */

    .select-title {

        margin-top: 30px;

        font-size:
            clamp(44px, 5vw, 68px);

        font-weight: 800;

        letter-spacing: -0.05em;
    }


    .select-subtitle {

        margin-top: 10px;

        margin-bottom: 28px;

        color: #8992a3;

        font-size: 15px;
    }


    .lesson-card {

        min-height: 160px;

        padding: 25px;

        border-radius: 22px;

        border:
            1px solid rgba(255,255,255,0.08);

        background:
            linear-gradient(
                145deg,
                rgba(255,255,255,0.07),
                rgba(255,255,255,0.025)
            );

        box-shadow:
            0 18px 45px rgba(0,0,0,0.16);

        margin-bottom: 8px;
    }


    .lesson-en {

        color: #70798b;

        font-size: 10px;

        font-weight: 700;

        letter-spacing: 0.22em;
    }


    .lesson-name {

        margin-top: 10px;

        font-size: 30px;

        font-weight: 800;

        letter-spacing: -0.04em;
    }


    .lesson-time {

        margin-top: 23px;

        color: #9aa2b1;

        font-size: 16px;
    }


    /* ========================================================
       TIMER
       ======================================================== */

    .timer-area {

        min-height: 58vh;

        display: flex;

        flex-direction: column;

        justify-content: center;

        align-items: center;

        text-align: center;
    }


    .live {

        color: #6ee8a5;

        font-size: 11px;

        font-weight: 700;

        letter-spacing: 0.20em;
    }


    .subject {

        margin-top: 27px;

        color: #a0a7b5;

        font-size: 19px;
    }


    .timer-number {

        margin-top: 9px;

        font-size:
            clamp(76px, 12vw, 165px);

        line-height: 0.95;

        font-weight: 800;

        letter-spacing: -0.065em;

        font-variant-numeric: tabular-nums;
    }


    .remaining {

        margin-top: 17px;

        color: #747c8d;

        font-size: 10px;

        font-weight: 700;

        letter-spacing: 0.30em;
    }


    .timer-meta {

        margin-top: 26px;

        color: #798191;

        font-size: 13px;
    }


    .warning {

        margin-top: 20px;

        padding: 9px 15px;

        border-radius: 999px;

        border:
            1px solid rgba(255,204,92,0.17);

        background:
            rgba(255,204,92,0.07);

        color: #ffd166;

        font-size: 11px;

        font-weight: 700;

        letter-spacing: 0.12em;
    }


    /* ========================================================
       COMPLETE
       ======================================================== */

    .complete {

        min-height: 61vh;

        display: flex;

        flex-direction: column;

        justify-content: center;

        align-items: center;

        text-align: center;
    }


    .complete-label {

        color: #747d90;

        font-size: 11px;

        font-weight: 700;

        letter-spacing: 0.25em;
    }


    .complete-title {

        margin-top: 18px;

        font-size:
            clamp(55px, 8vw, 100px);

        line-height: 0.93;

        font-weight: 800;

        letter-spacing: -0.06em;
    }


    .complete-subtitle {

        margin-top: 22px;

        color: #929aaa;

        font-size: 17px;
    }


    /* ========================================================
       버튼
       ======================================================== */

    .stButton > button {

        width: 100%;

        min-height: 58px;

        border-radius: 17px;

        border:
            1px solid rgba(255,255,255,0.12);

        background:
            linear-gradient(
                180deg,
                rgba(255,255,255,0.10),
                rgba(255,255,255,0.045)
            );

        color: white !important;

        font-size: 15px;

        font-weight: 700;

        transition: 0.18s ease;

        box-shadow:
            0 15px 40px rgba(0,0,0,0.18);
    }


    .stButton > button:hover {

        transform: translateY(-2px);

        border-color:
            rgba(255,255,255,0.28);

        background:
            linear-gradient(
                180deg,
                rgba(255,255,255,0.15),
                rgba(255,255,255,0.07)
            );
    }


    /* ========================================================
       PASSWORD INPUT
       ======================================================== */

    div[data-testid="stTextInput"]
    div[data-baseweb="input"] {

        background:
            #f3f4f6 !important;

        border-radius:
            14px !important;
    }


    div[data-testid="stTextInput"]
    input {

        min-height:
            54px !important;

        background:
            #f3f4f6 !important;

        color:
            #111827 !important;

        -webkit-text-fill-color:
            #111827 !important;

        caret-color:
            #111827 !important;

        text-align:
            center !important;

        font-size:
            20px !important;

        font-weight:
            800 !important;
    }


    div[data-testid="stTextInput"]
    input::placeholder {

        color:
            #7a8190 !important;

        -webkit-text-fill-color:
            #7a8190 !important;

        opacity: 1 !important;
    }


    /* ========================================================
       NUMBER INPUT
       ======================================================== */

    div[data-testid="stNumberInput"]
    div[data-baseweb="input"] {

        background:
            #f3f4f6 !important;

        border-radius:
            14px !important;
    }


    div[data-testid="stNumberInput"]
    input {

        min-height:
            52px !important;

        background:
            #f3f4f6 !important;

        color:
            #111827 !important;

        -webkit-text-fill-color:
            #111827 !important;

        caret-color:
            #111827 !important;

        text-align:
            center !important;

        font-size:
            20px !important;

        font-weight:
            800 !important;
    }


    div[data-testid="stNumberInput"]
    button {

        color:
            #111827 !important;

        background:
            #f3f4f6 !important;
    }


    div[data-testid="stNumberInput"]
    button svg {

        color:
            #111827 !important;

        fill:
            #111827 !important;
    }


    /* slider */

    div[data-testid="stSlider"] {

        color: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HTML
# ============================================================

def show_html(code):

    st.html(code)


# ============================================================
# AUDIO 파일 → BASE64
# ============================================================

def encode_audio(file_path):

    path = Path(file_path)

    if not path.exists():
        return None

    data = path.read_bytes()

    return base64.b64encode(
        data
    ).decode("utf-8")


# ============================================================
# 일반 사운드 재생
# ============================================================

def play_sound(file_path):

    audio = encode_audio(file_path)

    if audio is None:
        return

    volume = (
        st.session_state.settings["volume"]
        / 100
    )

    components.html(
        f"""
        <audio
            id="single_audio"
            autoplay
            preload="auto"
        >
            <source
                src="data:audio/mpeg;base64,{audio}"
                type="audio/mpeg"
            >
        </audio>

        <script>

            const audio =
                document.getElementById("single_audio");

            audio.volume = {volume};

            audio.play().catch(
                function(error) {{
                    console.log("Audio error:", error);
                }}
            );

        </script>
        """,
        height=1,
    )


# ============================================================
# 종료 사운드
# 종소리 + 종료 안내 동시 시작
# 종료 안내는 종소리가 끝날 때까지 반복
# ============================================================

def play_finish_sequence():

    bell = encode_audio(
        SCHOOL_BELL_SOUND
    )

    voice = encode_audio(
        FINISHED_SOUND
    )

    if bell is None or voice is None:
        return

    volume = (
        st.session_state.settings["volume"]
        / 100
    )

    components.html(
        f"""
        <audio
            id="bell"
            preload="auto"
        >
            <source
                src="data:audio/mpeg;base64,{bell}"
                type="audio/mpeg"
            >
        </audio>


        <audio
            id="voice"
            preload="auto"
            loop
        >
            <source
                src="data:audio/mpeg;base64,{voice}"
                type="audio/mpeg"
            >
        </audio>


        <script>

            const bell =
                document.getElementById("bell");

            const voice =
                document.getElementById("voice");


            bell.volume = {volume};
            voice.volume = {volume};


            Promise.all([
                bell.play(),
                voice.play()
            ]).catch(
                function(error) {{
                    console.log("Audio error:", error);
                }}
            );


            bell.addEventListener(
                "ended",
                function() {{

                    voice.pause();
                    voice.currentTime = 0;

                }}
            );

        </script>
        """,
        height=1,
    )


# ============================================================
# 남은 시간 표시
# ============================================================

def format_time(seconds):

    seconds = max(
        0,
        int(seconds)
    )

    hours = seconds // 3600

    minutes = (
        seconds % 3600
    ) // 60

    secs = seconds % 60

    return (
        f"{hours:02d}:"
        f"{minutes:02d}:"
        f"{secs:02d}"
    )


# ============================================================
# 수업 시작
# ============================================================

def start_lesson(name, minutes):

    now = datetime.now(KST)

    st.session_state.lesson = {
        "name": name,
        "minutes": int(minutes),
    }

    st.session_state.start_time = now

    st.session_state.end_time = (
        now
        + timedelta(
            minutes=int(minutes)
        )
    )

    st.session_state.warning_played = False

    st.session_state.finish_sound_needed = False

    st.session_state.complete_started_at = None

    st.session_state.page = "timer"

    st.rerun()


# ============================================================
# 처음 화면으로
# ============================================================

def return_home():

    st.session_state.page = "welcome"

    st.session_state.lesson = None

    st.session_state.start_time = None

    st.session_state.end_time = None

    st.session_state.warning_played = False

    st.session_state.finish_sound_needed = False

    st.session_state.complete_started_at = None

    # 관리자 설정 인증만 해제
    st.session_state.admin_authenticated = False

    # startup_authenticated는 건드리지 않음
    # 그래서 수업 끝날 때마다 비밀번호를 다시 묻지 않음

    st.rerun()


# ============================================================
# 최초 접속 비밀번호
# ============================================================

if not st.session_state.startup_authenticated:

    show_html(
        """
        <div class="admin-screen">

            <div class="brand">
                PRIVATE TUTORING SYSTEM
            </div>

            <div class="admin-title">
                ADMIN ACCESS
            </div>

            <div class="admin-subtitle">
                키오스크를 시작하려면 관리자 비밀번호를 입력해 주세요.
            </div>

        </div>
        """
    )

    left, middle, right = st.columns(
        [1.2, 1, 1.2]
    )

    with middle:

        startup_password = st.text_input(
            "시작 비밀번호",
            type="password",
            placeholder="PASSWORD",
            label_visibility="collapsed",
            key="startup_password",
        )

        if st.button(
            "ENTER  →",
            use_container_width=True,
            key="startup_login_button",
        ):

            if startup_password == ADMIN_PASSWORD:

                st.session_state.startup_authenticated = True

                st.session_state.page = "welcome"

                st.rerun()

            else:

                st.error(
                    "비밀번호가 올바르지 않습니다."
                )

    st.stop()


# ============================================================
# WELCOME
# ============================================================

if st.session_state.page == "welcome":

    show_html(
        """
        <div class="welcome">

            <div class="brand">
                PRIVATE TUTORING
            </div>

            <div>
                <span class="system-ready">

                    <span class="green-dot">
                        ●
                    </span>

                    SYSTEM READY

                </span>
            </div>

            <div class="welcome-title">
                어서오세요.
            </div>

            <div class="welcome-subtitle">
                오늘의 수업을 시작해 주세요.
            </div>

        </div>
        """
    )

    left, middle, right = st.columns(
        [1, 1.2, 1]
    )

    with middle:

        if st.button(
            "과외 시작하기  →",
            use_container_width=True,
        ):

            st.session_state.page = "select"

            st.rerun()


# ============================================================
# SELECT
# ============================================================

elif st.session_state.page == "select":

    settings = st.session_state.settings

    show_html(
        """
        <div class="brand">
            PRIVATE TUTORING
        </div>

        <div class="select-title">
            수업을 선택하세요.
        </div>

        <div class="select-subtitle">
            시작할 수업을 선택해 주세요.
        </div>
        """
    )

    c1, c2, c3 = st.columns(3)


    # ========================================================
    # 첼로
    # ========================================================

    with c1:

        show_html(
            f"""
            <div class="lesson-card">

                <div class="lesson-en">
                    CELLO
                </div>

                <div class="lesson-name">
                    첼로 과외
                </div>

                <div class="lesson-time">
                    {settings["cello_minutes"]} MIN
                </div>

            </div>
            """
        )

        if st.button(
            "첼로 과외 시작  →",
            use_container_width=True,
            key="start_cello",
        ):

            start_lesson(
                "첼로 과외",
                settings["cello_minutes"],
            )


    # ========================================================
    # 영어
    # ========================================================

    with c2:

        show_html(
            f"""
            <div class="lesson-card">

                <div class="lesson-en">
                    ENGLISH
                </div>

                <div class="lesson-name">
                    영어 과외
                </div>

                <div class="lesson-time">
                    {settings["english_minutes"]} MIN
                </div>

            </div>
            """
        )

        if st.button(
            "영어 과외 시작  →",
            use_container_width=True,
            key="start_english",
        ):

            start_lesson(
                "영어 과외",
                settings["english_minutes"],
            )


    # ========================================================
    # 수학
    # ========================================================

    with c3:

        show_html(
            """
            <div class="lesson-card">

                <div class="lesson-en">
                    MATHEMATICS
                </div>

                <div class="lesson-name">
                    수학 과외
                </div>

                <div class="lesson-time">
                    시간 직접 설정
                </div>

            </div>
            """
        )

        math_minutes = st.number_input(
            "수학 수업 시간",
            min_value=1,
            max_value=300,
            value=90,
            step=10,
            key="math_minutes",
            label_visibility="collapsed",
        )

        if st.button(
            "수학 과외 시작  →",
            use_container_width=True,
            key="start_math",
        ):

            start_lesson(
                "수학 과외",
                int(math_minutes),
            )


    st.write("")
    st.write("")

    blank, admin_col, home_col = st.columns(
        [2, 1, 1]
    )

    with admin_col:

        if st.button(
            "⚙ 관리자 설정",
            use_container_width=True,
            key="open_admin",
        ):

            # 들어갈 때마다 인증 초기화
            st.session_state.admin_authenticated = False

            st.session_state.page = "admin_login"

            st.rerun()


    with home_col:

        if st.button(
            "← 처음으로",
            use_container_width=True,
            key="select_home",
        ):

            return_home()


# ============================================================
# ADMIN LOGIN
# ============================================================

elif st.session_state.page == "admin_login":

    show_html(
        """
        <div class="admin-screen">

            <div class="brand">
                PRIVATE TUTORING SYSTEM
            </div>

            <div class="admin-title">
                ADMIN SETTINGS
            </div>

            <div class="admin-subtitle">
                설정을 변경하려면 관리자 비밀번호를 입력해 주세요.
            </div>

        </div>
        """
    )

    left, middle, right = st.columns(
        [1.2, 1, 1.2]
    )

    with middle:

        admin_password = st.text_input(
            "관리자 비밀번호",
            type="password",
            placeholder="PASSWORD",
            label_visibility="collapsed",
            key="admin_password",
        )

        if st.button(
            "ENTER  →",
            use_container_width=True,
            key="admin_login_button",
        ):

            if admin_password == ADMIN_PASSWORD:

                st.session_state.admin_authenticated = True

                st.session_state.page = "admin_settings"

                st.rerun()

            else:

                st.error(
                    "비밀번호가 올바르지 않습니다."
                )


        if st.button(
            "← 과외 선택으로",
            use_container_width=True,
            key="admin_login_back",
        ):

            st.session_state.admin_authenticated = False

            st.session_state.page = "select"

            st.rerun()


# ============================================================
# ADMIN SETTINGS
# ============================================================

elif st.session_state.page == "admin_settings":

    # URL/상태 꼬여서 직접 들어오는 것 방지

    if not st.session_state.admin_authenticated:

        st.session_state.page = "admin_login"

        st.rerun()


    settings = st.session_state.settings


    show_html(
        """
        <div class="brand">
            PRIVATE TUTORING SYSTEM
        </div>

        <div class="admin-title">
            ADMIN SETTINGS
        </div>

        <div class="admin-subtitle">
            과외 시간과 알림 소리 크기를 설정합니다.
        </div>
        """
    )


    left, middle, right = st.columns(
        [1, 1.4, 1]
    )


    with middle:

        # ====================================================
        # 첼로
        # ====================================================

        show_html(
            """
            <div class="setting-label">
                CELLO · 첼로 과외 시간
            </div>
            """
        )

        cello_minutes = st.number_input(
            "첼로 과외 시간",
            min_value=1,
            max_value=300,
            value=int(
                settings["cello_minutes"]
            ),
            step=5,
            key="admin_cello_minutes",
            label_visibility="collapsed",
        )


        # ====================================================
        # 영어
        # ====================================================

        show_html(
            """
            <div class="setting-label">
                ENGLISH · 영어 과외 시간
            </div>
            """
        )

        english_minutes = st.number_input(
            "영어 과외 시간",
            min_value=1,
            max_value=300,
            value=int(
                settings["english_minutes"]
            ),
            step=5,
            key="admin_english_minutes",
            label_visibility="collapsed",
        )


        # ====================================================
        # 볼륨
        # ====================================================

        show_html(
            """
            <div class="setting-label">
                MASTER VOLUME · 알림 소리 크기
            </div>
            """
        )

        volume = st.slider(
            "알림 소리 크기",
            min_value=0,
            max_value=100,
            value=int(
                settings["volume"]
            ),
            step=5,
            key="admin_volume",
            label_visibility="collapsed",
        )

        st.caption(
            f"현재 설정: {volume}%"
        )


        # ====================================================
        # 테스트 사운드
        # ====================================================

        if st.button(
            "🔊 소리 테스트",
            use_container_width=True,
            key="test_sound",
        ):

            # 테스트할 때 현재 슬라이더 값 사용
            old_volume = (
                st.session_state.settings["volume"]
            )

            st.session_state.settings["volume"] = (
                int(volume)
            )

            play_sound(
                TEN_MINUTES_SOUND
            )

            st.session_state.settings["volume"] = (
                old_volume
            )


        st.write("")


        # ====================================================
        # 저장
        # ====================================================

        if st.button(
            "✓ 설정 저장하고 나오기",
            use_container_width=True,
            key="save_admin_settings",
        ):

            new_settings = {
                "cello_minutes":
                    int(cello_minutes),

                "english_minutes":
                    int(english_minutes),

                "volume":
                    int(volume),
            }

            save_settings(
                new_settings
            )

            st.session_state.settings = (
                new_settings
            )

            # 관리자 화면에서 나오는 순간 인증 해제
            st.session_state.admin_authenticated = False

            st.session_state.page = "select"

            st.rerun()


        # ====================================================
        # 취소
        # ====================================================

        if st.button(
            "취소하고 나오기",
            use_container_width=True,
            key="cancel_admin_settings",
        ):

            st.session_state.admin_authenticated = False

            st.session_state.page = "select"

            st.rerun()


# ============================================================
# TIMER
# ============================================================

elif st.session_state.page == "timer":

    lesson = st.session_state.lesson


    @st.fragment(
        run_every="1s"
    )
    def timer_fragment():

        now = datetime.now(KST)

        remaining = (
            st.session_state.end_time
            - now
        ).total_seconds()


        # ====================================================
        # 수업 종료
        # ====================================================

        if remaining <= 0:

            st.session_state.finish_sound_needed = True

            st.session_state.complete_started_at = None

            st.session_state.page = "complete"

            st.rerun(
                scope="app"
            )


        # ====================================================
        # 10분 전 안내
        # ====================================================

        if (
            remaining <= 600
            and remaining > 0
            and not st.session_state.warning_played
        ):

            play_sound(
                TEN_MINUTES_SOUND
            )

            st.session_state.warning_played = True


        # ====================================================
        # 시간 표시
        # ====================================================

        start_text = (
            st.session_state.start_time
            .strftime("%H:%M")
        )

        end_text = (
            st.session_state.end_time
            .strftime("%H:%M")
        )


        warning_html = ""

        if remaining <= 600:

            warning_html = """
            <div class="warning">
                ENDING SOON · 종료까지 10분 이내
            </div>
            """


        show_html(
            f"""
            <div class="timer-area">

                <div class="live">
                    ● LIVE SESSION
                </div>

                <div class="subject">
                    {lesson["name"]}
                </div>

                <div class="timer-number">
                    {format_time(remaining)}
                </div>

                <div class="remaining">
                    REMAINING
                </div>

                {warning_html}

                <div class="timer-meta">

                    START&nbsp;&nbsp;
                    {start_text}

                    &nbsp;&nbsp;·&nbsp;&nbsp;

                    END&nbsp;&nbsp;
                    {end_text}

                </div>

            </div>
            """
        )


        left, add_col, finish_col, right = st.columns(
            [1, 1, 1, 1]
        )


        # ====================================================
        # 10분 추가
        # ====================================================

        with add_col:

            if st.button(
                "+ 10 MIN",
                use_container_width=True,
                key="add_10_minutes",
            ):

                st.session_state.end_time += (
                    timedelta(
                        minutes=10
                    )
                )

                st.rerun(
                    scope="fragment"
                )


        # ====================================================
        # 강제 종료
        # ====================================================

        with finish_col:

            if st.button(
                "수업 종료",
                use_container_width=True,
                key="finish_lesson",
            ):

                st.session_state.finish_sound_needed = True

                st.session_state.complete_started_at = None

                st.session_state.page = "complete"

                st.rerun(
                    scope="app"
                )


    timer_fragment()


# ============================================================
# COMPLETE
# ============================================================

elif st.session_state.page == "complete":

    # 완료 화면 최초 진입 시간

    if st.session_state.complete_started_at is None:

        st.session_state.complete_started_at = (
            time.time()
        )


    # 종료 사운드 최초 1회 시작

    if st.session_state.finish_sound_needed:

        play_finish_sequence()

        st.session_state.finish_sound_needed = False


    show_html(
        """
        <div class="complete">

            <div class="complete-label">
                PRIVATE TUTORING
            </div>

            <div class="complete-title">
                SESSION<br>
                COMPLETE
            </div>

            <div class="complete-subtitle">
                수업이 종료되었습니다.
            </div>

        </div>
        """
    )


    left, middle, right = st.columns(
        [1.2, 1, 1.2]
    )


    # ========================================================
    # 직접 처음 화면으로
    # ========================================================

    with middle:

        if st.button(
            "처음 화면으로",
            use_container_width=True,
            key="complete_home",
        ):

            return_home()


    # ========================================================
    # 자동 처음 화면 복귀
    # ========================================================

    @st.fragment(
        run_every="1s"
    )
    def auto_return():

        elapsed = (
            time.time()
            - st.session_state.complete_started_at
        )

        seconds_left = max(
            0,
            AUTO_RETURN_SECONDS - elapsed
        )

        st.markdown(
            f"""
            <div style="
                text-align:center;
                color:#747d90;
                font-size:12px;
                margin-top:18px;
                letter-spacing:.05em;
            ">
                {max(0, int(seconds_left) + 1)}초 후
                자동으로 처음 화면으로 돌아갑니다.
            </div>
            """,
            unsafe_allow_html=True,
        )


        if elapsed >= AUTO_RETURN_SECONDS:

            st.session_state.page = "welcome"

            st.session_state.lesson = None

            st.session_state.start_time = None

            st.session_state.end_time = None

            st.session_state.warning_played = False

            st.session_state.finish_sound_needed = False

            st.session_state.complete_started_at = None

            st.session_state.admin_authenticated = False

            # startup_authenticated는 True 유지
            # 따라서 수업 끝난 뒤에는 로그인 화면으로 가지 않음

            st.rerun(
                scope="app"
            )


    auto_return()