import base64
import time
from pathlib import Path
from datetime import datetime, timedelta

import streamlit as st
import streamlit.components.v1 as components


# ============================================================
# 기본 설정
# ============================================================

st.set_page_config(
    page_title="Private Tutoring",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Streamlit Secrets를 쓰고 있다면 이 방식 사용
ADMIN_PASSWORD = st.secrets.get("ADMIN_PASSWORD", "1234")

# 종소리가 16초이므로 1초 여유 후 첫 화면으로 복귀
AUTO_RETURN_SECONDS = 17


# ============================================================
# 과외 설정
# ★ 여기서 이름/시간만 바꾸면 됨
# ============================================================

LESSONS = [
    {
        "name": "수학 과외",
        "english": "SESSION 01",
        "minutes": 90,   # 테스트 후 실제 시간으로 변경
    },
    {
        "name": "영어 과외",
        "english": "SESSION 02",
        "minutes": 90,
    },
    {
        "name": "첼로 과외",
        "english": "SESSION 03",
        "minutes": 50,
    },
]


# ============================================================
# MP3 파일
# ============================================================

TEN_MINUTES_SOUND = "sounds/ten_minutes.mp3"
SCHOOL_BELL_SOUND = "sounds/school_bell.mp3"
FINISHED_SOUND = "sounds/class_finished.mp3"


# ============================================================
# 세션 상태
# ============================================================

DEFAULTS = {
    "authenticated": False,
    "page": "welcome",
    "lesson": None,
    "start_time": None,
    "end_time": None,
    "warning_played": False,
    "finish_sound_needed": False,
    "complete_started_at": None,
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
        padding-top: 3vh;
        padding-bottom: 3vh;
    }

    .brand {
        color: #768096;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.32em;
    }

    .online {
        display: inline-flex;
        align-items: center;
        gap: 9px;

        padding: 9px 14px;

        border-radius: 999px;
        border: 1px solid rgba(255,255,255,0.08);

        background: rgba(255,255,255,0.03);

        color: #939bac;

        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.16em;
    }

    .online-dot {
        width: 7px;
        height: 7px;

        display: inline-block;

        border-radius: 50%;

        background: #63e9a2;

        box-shadow:
            0 0 12px rgba(99,233,162,0.75);
    }


    /* 관리자 */

    .admin-screen {
        min-height: 55vh;

        display: flex;
        flex-direction: column;

        justify-content: flex-end;
        align-items: center;

        text-align: center;
    }

    .admin-title {
        margin-top: 14px;

        font-size: clamp(38px, 5vw, 62px);

        font-weight: 800;
        letter-spacing: -0.045em;
    }

    .admin-subtitle {
        margin-top: 12px;

        color: #8e96a7;

        font-size: 15px;
    }


    /* Welcome */

    .welcome {
        min-height: 63vh;

        display: flex;
        flex-direction: column;

        justify-content: center;
    }

    .welcome-title {
        margin-top: 24px;

        font-size: clamp(58px, 8vw, 105px);

        line-height: 0.95;

        font-weight: 800;

        letter-spacing: -0.06em;
    }

    .welcome-subtitle {
        margin-top: 22px;

        color: #8c94a5;

        font-size: 17px;
    }


    /* 선택 화면 */

    .select-title {
        margin-top: 35px;

        font-size: clamp(44px, 5vw, 68px);

        font-weight: 800;

        letter-spacing: -0.05em;
    }

    .select-subtitle {
        margin-top: 9px;
        margin-bottom: 28px;

        color: #8992a3;

        font-size: 15px;
    }

    .lesson-card {
        min-height: 165px;

        padding: 25px;

        border: 1px solid rgba(255,255,255,0.08);

        border-radius: 22px;

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


    /* 타이머 */

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

        font-size: clamp(76px, 12vw, 165px);

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

        border: 1px solid rgba(255,204,92,0.17);

        background: rgba(255,204,92,0.07);

        color: #ffd166;

        font-size: 11px;

        font-weight: 700;

        letter-spacing: 0.12em;
    }


    /* 완료 */

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

        font-size: clamp(55px, 8vw, 100px);

        line-height: 0.93;

        font-weight: 800;

        letter-spacing: -0.06em;
    }

    .complete-subtitle {
        margin-top: 22px;

        color: #929aaa;

        font-size: 17px;
    }


    /* 버튼 */

    .stButton > button {
        width: 100%;

        min-height: 62px;

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


    /* 비밀번호 */

    div[data-baseweb="input"] {
        background: #171a22 !important;

        border-radius: 16px !important;
    }

    div[data-baseweb="input"] input {
        min-height: 60px !important;

        background: #171a22 !important;

        color: white !important;

        -webkit-text-fill-color: white !important;

        caret-color: white !important;

        text-align: center !important;

        font-size: 22px !important;

        font-weight: 700 !important;

        letter-spacing: 0.18em !important;

        border-radius: 16px !important;
    }

    div[data-baseweb="input"] input::placeholder {
        color: #6f788a !important;

        -webkit-text-fill-color: #6f788a !important;

        opacity: 1 !important;
    }

    div[data-baseweb="input"] svg {
        color: white !important;

        fill: white !important;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# HTML 표시
# ============================================================

def show_html(code):
    st.html(code)


# ============================================================
# 오디오 인코딩
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
# 10분 전 안내음
# ============================================================

def play_one_sound(file_path):

    audio = encode_audio(file_path)

    if audio is None:
        return

    components.html(
        f"""
        <audio id="single_sound" autoplay>
            <source
                src="data:audio/mpeg;base64,{audio}"
                type="audio/mpeg"
            >
        </audio>

        <script>

            const audio =
                document.getElementById("single_sound");

            audio.volume = 1.0;

            audio.play().catch(
                function(error) {{
                    console.log(
                        "Audio error:",
                        error
                    );
                }}
            );

        </script>
        """,
        height=1,
    )


# ============================================================
# 종료음
#
# 학교 종소리 + 안내방송 동시 시작
# 안내방송은 종소리가 끝날 때까지 반복
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


            bell.volume = 1.0;

            voice.volume = 1.0;


            Promise.all([
                bell.play(),
                voice.play()
            ]).catch(
                function(error) {{
                    console.log(
                        "Audio error:",
                        error
                    );
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
# 시간 표시
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

def start_lesson(lesson):

    now = datetime.now()

    st.session_state.lesson = lesson

    st.session_state.start_time = now

    st.session_state.end_time = (
        now
        + timedelta(
            minutes=lesson["minutes"]
        )
    )

    st.session_state.warning_played = False

    st.session_state.finish_sound_needed = False

    st.session_state.complete_started_at = None

    st.session_state.page = "timer"

    st.rerun()


# ============================================================
# 처음 화면 복귀
# ============================================================

def return_home():

    st.session_state.page = "welcome"

    st.session_state.lesson = None

    st.session_state.start_time = None

    st.session_state.end_time = None

    st.session_state.warning_played = False

    st.session_state.finish_sound_needed = False

    st.session_state.complete_started_at = None

    st.rerun()


# ============================================================
# 관리자 로그인
# ============================================================

if not st.session_state.authenticated:

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
                관리자 비밀번호를 입력해 주세요.
            </div>

        </div>
        """
    )


    left, middle, right = st.columns(
        [1.25, 1, 1.25]
    )


    with middle:

        password = st.text_input(
            "Password",
            type="password",
            placeholder="PASSWORD",
            label_visibility="collapsed",
        )


        if st.button(
            "ENTER  →",
            use_container_width=True,
        ):

            if (
                password
                == ADMIN_PASSWORD
            ):

                st.session_state.authenticated = True

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

            <div style="margin-top:18px;">

                <span class="online">

                    <span class="online-dot">
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
            "과외 시작하기   →",
            use_container_width=True,
        ):

            st.session_state.page = "select"

            st.rerun()


# ============================================================
# 수업 선택
# ============================================================

elif st.session_state.page == "select":

    show_html(
        """
        <div class="brand">
            PRIVATE TUTORING
        </div>

        <div class="select-title">
            수업을 선택하세요.
        </div>

        <div class="select-subtitle">
            시작할 수업을 터치해 주세요.
        </div>
        """
    )


    columns = st.columns(3)


    for index, lesson in enumerate(
        LESSONS
    ):

        with columns[index]:

            show_html(
                f"""
                <div class="lesson-card">

                    <div class="lesson-en">
                        {lesson["english"]}
                    </div>

                    <div class="lesson-name">
                        {lesson["name"]}
                    </div>

                    <div class="lesson-time">
                        {lesson["minutes"]} MIN
                    </div>

                </div>
                """
            )


            if st.button(
                f"{lesson['name']} 시작   →",
                key=f"lesson_{index}",
                use_container_width=True,
            ):

                start_lesson(
                    lesson
                )


    st.write("")


    left, middle, right = st.columns(
        [1.25, 0.7, 1.25]
    )


    with middle:

        if st.button(
            "← 처음으로",
            use_container_width=True,
        ):

            st.session_state.page = "welcome"

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

        now = datetime.now()


        remaining = (
            st.session_state.end_time
            - now
        ).total_seconds()


        # ----------------------------------------------------
        # 시간 종료
        # ----------------------------------------------------

        if remaining <= 0:

            st.session_state.finish_sound_needed = True

            st.session_state.complete_started_at = None

            st.session_state.page = "complete"

            st.rerun(
                scope="app"
            )


        # ----------------------------------------------------
        # 10분 전 알림
        # ----------------------------------------------------

        if (
            remaining <= 600
            and remaining > 0
            and not st.session_state.warning_played
        ):

            play_one_sound(
                TEN_MINUTES_SOUND
            )

            st.session_state.warning_played = True


        # ----------------------------------------------------
        # 화면
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # 조작 버튼
        # ----------------------------------------------------

        space1, plus, finish, space2 = st.columns(
            [1, 1, 1, 1]
        )


        with plus:

            if st.button(
                "+ 10 MIN",
                use_container_width=True,
            ):

                st.session_state.end_time += (
                    timedelta(
                        minutes=10
                    )
                )

                st.rerun(
                    scope="fragment"
                )


        with finish:

            if st.button(
                "수업 종료",
                use_container_width=True,
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


    # 완료 화면에 들어온 최초 시점
    if (
        st.session_state.complete_started_at
        is None
    ):

        st.session_state.complete_started_at = (
            time.time()
        )


    # 종소리 + 반복 안내방송
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


    # --------------------------------------------------------
    # 직접 복귀 버튼
    # --------------------------------------------------------

    left, middle, right = st.columns(
        [1.2, 1, 1.2]
    )


    with middle:

        if st.button(
            "처음 화면으로",
            use_container_width=True,
        ):

            return_home()


    # --------------------------------------------------------
    # 자동 복귀
    # --------------------------------------------------------

    @st.fragment(
        run_every="1s"
    )
    def complete_auto_return():

        elapsed = (
            time.time()
            - st.session_state.complete_started_at
        )


        seconds_left = max(
            0,
            AUTO_RETURN_SECONDS
            - elapsed
        )


        st.markdown(
            f"""
            <div style="
                text-align:center;
                margin-top:18px;
                color:#747d90;
                font-size:12px;
                letter-spacing:.08em;
            ">
                {max(
                    0,
                    int(seconds_left) + 1
                )}초 후 자동으로 처음 화면으로 돌아갑니다.
            </div>
            """,
            unsafe_allow_html=True,
        )


        if (
            elapsed
            >= AUTO_RETURN_SECONDS
        ):

            st.session_state.page = "welcome"

            st.session_state.lesson = None

            st.session_state.start_time = None

            st.session_state.end_time = None

            st.session_state.warning_played = False

            st.session_state.finish_sound_needed = False

            st.session_state.complete_started_at = None

            st.rerun(
                scope="app"
            )


    complete_auto_return()
