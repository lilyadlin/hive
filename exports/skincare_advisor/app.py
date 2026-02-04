"""
Skincare Product Advisor — Streamlit Chatbot
"""

import json
import os
from datetime import date
from pathlib import Path

import anthropic
import streamlit as st

# ── Load API key from .env or environment ────────────────────────────────
def _load_api_key() -> str:
    """Load Anthropic API key from .env file or environment."""
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    env_path = Path(__file__).resolve().parents[2] / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line.startswith("ANTHROPIC_API_KEY="):
                return line.split("=", 1)[1].strip().strip("'\"")
    return ""


API_KEY = _load_api_key()

# ── Page config ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="skintea",
    page_icon="",
    layout="centered",
    initial_sidebar_state="expanded",
)

# ── Custom CSS — muted, neutral, minimal ─────────────────────────────────
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:wght@400;500;600&display=swap');

    /* ── base ── */
    .stApp {
        background-color: #F7F5F2;
        font-family: 'Inter', -apple-system, sans-serif;
    }

    /* hide default streamlit branding but keep sidebar toggle */
    #MainMenu, footer {visibility: hidden;}
    header[data-testid="stHeader"] {background: transparent !important; backdrop-filter: none !important;}
    header[data-testid="stHeader"] .stDeployButton {display: none !important;}

    /* ── sidebar ── */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #EDEBE8;
    }
    [data-testid="stSidebar"] .stMarkdown h2 {
        font-family: 'Playfair Display', Georgia, serif;
        font-weight: 500;
        color: #2D2D2D;
        font-size: 1.15rem;
        letter-spacing: -0.01em;
    }
    [data-testid="stSidebar"] label {
        font-size: 0.75rem;
        font-weight: 500;
        color: #8A857E;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }
    [data-testid="stSidebar"] .stTextInput input,
    [data-testid="stSidebar"] .stTextArea textarea,
    [data-testid="stSidebar"] .stSelectbox > div > div {
        border: 1px solid #E5E2DD !important;
        border-radius: 8px !important;
        background: #FAFAF8 !important;
        font-size: 0.85rem !important;
        color: #2D2D2D !important;
    }
    [data-testid="stSidebar"] .stTextInput input:focus,
    [data-testid="stSidebar"] .stTextArea textarea:focus {
        border-color: #B8B2A8 !important;
        box-shadow: none !important;
    }
    [data-testid="stSidebar"] .stMultiSelect > div {
        border-color: #E5E2DD !important;
        border-radius: 8px !important;
        background: #FAFAF8 !important;
    }
    [data-testid="stSidebar"] .stMultiSelect span[data-baseweb="tag"] {
        background: #EDEBE8 !important;
        color: #4A4642 !important;
        border-radius: 4px !important;
        font-size: 0.75rem !important;
    }
    [data-testid="stSidebar"] .stButton button {
        background: #2D2D2D !important;
        color: #F7F5F2 !important;
        border: none !important;
        border-radius: 8px !important;
        font-size: 0.8rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.03em !important;
        padding: 0.55rem 1rem !important;
        transition: opacity 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        opacity: 0.85 !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: #EDEBE8 !important;
        margin: 1rem 0 !important;
    }
    [data-testid="stSidebar"] .stCaption {
        color: #B8B2A8 !important;
        font-size: 0.7rem !important;
    }

    /* ── profile tags ── */
    .tag {
        display: inline-block;
        background: #EDEBE8;
        color: #4A4642;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.02em;
        margin: 0.15rem 0.1rem;
    }

    /* ── header ── */
    .app-header {
        text-align: center;
        padding: 2.5rem 0 1rem 0;
    }
    .app-header h1 {
        font-family: 'Playfair Display', Georgia, serif;
        font-weight: 500;
        color: #2D2D2D;
        font-size: 1.75rem;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .app-header p {
        color: #A09A93;
        font-size: 0.85rem;
        font-weight: 300;
        margin-top: 0.3rem;
    }

    /* ── chat avatars — espresso & pink ── */
    .stChatMessage[data-testid="stChatMessage-assistant"] [data-testid="stChatMessageAvatar"] div {
        background-color: #4A3228 !important;
    }
    .stChatMessage[data-testid="stChatMessage-assistant"] [data-testid="stChatMessageAvatar"] svg {
        color: #F7F5F2 !important;
    }
    .stChatMessage[data-testid="stChatMessage-user"] [data-testid="stChatMessageAvatar"] div {
        background-color: #D4A0A0 !important;
    }
    .stChatMessage[data-testid="stChatMessage-user"] [data-testid="stChatMessageAvatar"] svg {
        color: #FFFFFF !important;
    }

    /* ── chat messages ── */
    .stChatMessage {
        background: transparent !important;
        border: none !important;
        padding: 0.6rem 0 !important;
    }
    [data-testid="stChatMessageContent"] {
        background: #FFFFFF !important;
        border: 1px solid #EDEBE8 !important;
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        font-size: 0.88rem !important;
        line-height: 1.6 !important;
        color: #2D2D2D !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02) !important;
    }
    /* user messages — slightly different */
    .stChatMessage[data-testid="stChatMessage-user"] [data-testid="stChatMessageContent"] {
        background: #2D2D2D !important;
        color: #F7F5F2 !important;
        border: none !important;
    }

    /* markdown inside chat */
    [data-testid="stChatMessageContent"] p {
        color: inherit !important;
        font-size: 0.88rem !important;
    }
    [data-testid="stChatMessageContent"] strong {
        font-weight: 600 !important;
    }
    [data-testid="stChatMessageContent"] table {
        font-size: 0.82rem !important;
        border-collapse: collapse !important;
    }
    [data-testid="stChatMessageContent"] th {
        background: #FAFAF8 !important;
        font-weight: 500 !important;
        font-size: 0.75rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        color: #8A857E !important;
        padding: 0.5rem 0.8rem !important;
        border-bottom: 1px solid #EDEBE8 !important;
    }
    [data-testid="stChatMessageContent"] td {
        padding: 0.5rem 0.8rem !important;
        border-bottom: 1px solid #F2F0ED !important;
        color: #4A4642 !important;
    }
    [data-testid="stChatMessageContent"] h3 {
        font-family: 'Playfair Display', Georgia, serif;
        font-weight: 500;
        font-size: 1rem;
        color: #2D2D2D;
        margin-top: 1.2rem;
    }

    /* chat input */
    .stChatInput {
        border-top: 1px solid #EDEBE8 !important;
    }
    .stChatInput textarea {
        font-family: 'Inter', sans-serif !important;
        font-size: 0.88rem !important;
        color: #2D2D2D !important;
        border: 1px solid #E5E2DD !important;
        border-radius: 10px !important;
        background: #FFFFFF !important;
    }
    .stChatInput textarea:focus {
        border-color: #4A3228 !important;
        box-shadow: 0 0 0 1px #4A3228 !important;
    }
    .stChatInput textarea::placeholder {
        color: #C4BFB8 !important;
    }
    .stChatInput button {
        color: #4A3228 !important;
    }
    .stChatInput button:hover {
        color: #D4A0A0 !important;
    }
    .stChatInput button:focus, .stChatInput button:active {
        color: #4A3228 !important;
    }
    /* override any red/primary accent colors globally */
    :root {
        --primary-color: #4A3228 !important;
    }
    .st-emotion-cache-1gulkj5, .st-emotion-cache-ue6h4q {
        color: #4A3228 !important;
    }
    /* streamlit focus rings & accents */
    *:focus {
        outline-color: #4A3228 !important;
    }
    .st-bc, .st-bd, .st-be {
        border-color: #4A3228 !important;
    }
    /* send button SVG icon */
    .stChatInput button svg {
        fill: #4A3228 !important;
        stroke: #4A3228 !important;
    }

    /* spinner */
    .stSpinner > div {
        border-top-color: #A09A93 !important;
    }

    /* alert / error */
    .stAlert {
        border-radius: 8px !important;
        font-size: 0.82rem !important;
    }

    /* success toast in sidebar */
    .stSuccess {
        background: #F0EFEB !important;
        color: #4A4642 !important;
        border: 1px solid #DFDBD6 !important;
        border-radius: 8px !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ── State defaults ───────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "profile" not in st.session_state:
    st.session_state.profile = {}
if "evaluation_history" not in st.session_state:
    st.session_state.evaluation_history = []

# ── System prompt ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """\
You are a Skincare Product Advisor. You help users evaluate skincare and beauty products based on three pillars.

## Your Capabilities
You evaluate products using THREE PILLARS, each with a score from 0-10:

### Pillar 1 — Ingredient Safety (35% weight)
- Analyze every ingredient for comedogenic potential (0-5 scale)
- Flag irritants, allergens, and sensitizers
- Reference databases like INCIDecoder, CosDNA, EWG Skin Deep
- Rate overall ingredient safety from 0-10

### Pillar 2 — Skin Compatibility (35% weight)
- Assess the product against the user's specific skin type
- Cross-reference with known sensitivities
- Check for interactions with their current routine products (e.g. retinol + AHA, vitamin C + niacinamide)
- Rate personalized compatibility from 0-10

### Pillar 3 — User Reviews (30% weight)
- Summarize what real users say about this product
- Note common praises and complaints
- Highlight skin-type-specific feedback
- Rate review sentiment from 0-10

## Rating Scale
- 9-10: Strongly Recommend — Excellent match
- 7-8.9: Recommend — Good with minor caveats
- 5-6.9: Neutral — Mixed, proceed with caution
- 3-4.9: Caution — Significant concerns
- 0-2.9: Avoid — Poor match

## How to Respond

When the user asks about a product:
1. Acknowledge briefly
2. Provide a structured rating with all three pillars
3. Give a clear recommendation
4. Mention any interaction warnings with their current routine

Structure your product evaluation with this format:

### Overall: X.X / 10 — [Recommendation]

| Pillar | Score | Finding |
|--------|-------|---------|
| Ingredients | X.X | [one-line summary] |
| Compatibility | X.X | [one-line summary] |
| Reviews | X.X | [one-line summary] |

Then provide the detailed breakdown for each pillar under its own ### heading.

## Important Rules
- NEVER provide medical diagnoses. Suggest seeing a dermatologist for persistent issues.
- Be evidence-based — cite ingredient databases and known comedogenic ratings.
- Be transparent about your scoring methodology.
- If you don't have enough info about the user's skin, ASK before evaluating.
- When the user wants to add a product to their routine, confirm and note it.
- When the user reports a reaction, log it and update your understanding of their skin.

## User Profile
{profile_context}

## Tone
Warm but concise. Knowledgeable without being clinical. Think of yourself as a well-read friend who knows skincare science. Keep responses scannable — use short paragraphs, clear structure. No filler.
"""

# ── Custom avatars (espresso brown & pink) ───────────────────────────────
AVATAR_ASSISTANT = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><circle cx='20' cy='20' r='20' fill='%234A3228'/><text x='20' y='25' text-anchor='middle' fill='%23F7F5F2' font-family='Georgia,serif' font-size='16' font-weight='500'>s</text></svg>"
AVATAR_USER = "data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 40 40'><circle cx='20' cy='20' r='20' fill='%23D4A0A0'/><text x='20' y='25' text-anchor='middle' fill='%23FFFFFF' font-family='Georgia,serif' font-size='16' font-weight='500'>y</text></svg>"

PROFILES_DIR = Path("./skincare_profiles")


def _load_profile(user_id: str) -> dict:
    path = PROFILES_DIR / f"{user_id}.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def _save_profile(user_id: str, profile: dict):
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    path = PROFILES_DIR / f"{user_id}.json"
    profile["last_updated"] = str(date.today())
    path.write_text(json.dumps(profile, indent=2))


def _build_profile_context() -> str:
    p = st.session_state.profile
    if not p:
        return "No profile set yet. Ask the user about their skin type and routine before evaluating."

    parts = [f"Name: {p.get('name', 'Unknown')}"]
    if p.get("skin_type"):
        parts.append(f"Skin type: {p['skin_type']}")
    if p.get("concerns"):
        parts.append(f"Concerns: {', '.join(p['concerns'])}")
    if p.get("sensitivities"):
        parts.append(f"Sensitivities: {', '.join(p['sensitivities'])}")
    if p.get("routine"):
        parts.append(f"Current routine: {', '.join(p['routine'])}")
    if st.session_state.evaluation_history:
        recent = st.session_state.evaluation_history[-5:]
        history_lines = [f"  - {e['product']}: {e['rating']}/10 ({e['rec']})" for e in recent]
        parts.append("Recent evaluations:\n" + "\n".join(history_lines))
    return "\n".join(parts)


# ── Sidebar ──────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## your profile")

    name = st.text_input("Name", value=st.session_state.profile.get("name", ""))

    skin_type = st.selectbox(
        "Skin type",
        ["", "Normal", "Oily", "Dry", "Combination", "Sensitive"],
        index=0,
    )

    concerns = st.multiselect(
        "Concerns",
        ["Acne", "Aging", "Hyperpigmentation", "Redness", "Dryness", "Oiliness", "Large pores", "Texture", "Dark circles"],
        default=st.session_state.profile.get("concerns", []),
    )

    sensitivities = st.text_input(
        "Sensitivities",
        value=", ".join(st.session_state.profile.get("sensitivities", [])),
        placeholder="fragrance, retinol, alcohol...",
    )

    routine = st.text_area(
        "Current routine",
        value="\n".join(st.session_state.profile.get("routine", [])),
        placeholder="One product per line",
        height=90,
    )

    if st.button("Save", use_container_width=True):
        profile = {
            "name": name,
            "skin_type": skin_type,
            "concerns": concerns,
            "sensitivities": [s.strip() for s in sensitivities.split(",") if s.strip()],
            "routine": [r.strip() for r in routine.strip().split("\n") if r.strip()],
        }
        st.session_state.profile = profile
        if name:
            _save_profile(name.lower().replace(" ", "_"), profile)
        st.success("Saved")

    if st.session_state.profile.get("skin_type"):
        st.divider()
        p = st.session_state.profile
        tags = [p["skin_type"]] + p.get("concerns", [])
        tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags)
        st.markdown(tags_html, unsafe_allow_html=True)

    st.divider()
    st.caption("All data stored locally.")

# ── Header ───────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="app-header">
    <h1>skintea</h1>
    <p>rate any product for your skin</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Chat history ─────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=AVATAR_USER if msg["role"] == "user" else AVATAR_ASSISTANT):
        st.markdown(msg["content"])

# ── Chat input ───────────────────────────────────────────────────────────
if prompt := st.chat_input("try 'rate the ordinary niacinamide serum'"):
    if not API_KEY:
        st.error("No API key found. Set ANTHROPIC_API_KEY in your .env file.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar=AVATAR_USER):
        st.markdown(prompt)

    system = SYSTEM_PROMPT.format(profile_context=_build_profile_context())
    api_messages = [
        {"role": m["role"], "content": m["content"]}
        for m in st.session_state.messages
    ]

    with st.chat_message("assistant", avatar=AVATAR_ASSISTANT):
        with st.spinner(""):
            try:
                client = anthropic.Anthropic(api_key=API_KEY)
                response = client.messages.create(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=4096,
                    system=system,
                    messages=api_messages,
                )
                reply = response.content[0].text
            except anthropic.AuthenticationError:
                reply = "Your API key appears to be invalid or expired. Check ANTHROPIC_API_KEY in your .env file."
            except anthropic.BadRequestError as e:
                if "credit balance" in str(e).lower():
                    reply = (
                        "Looks like your API credits have run out. "
                        "Top up at [console.anthropic.com/settings/billing]"
                        "(https://console.anthropic.com/settings/billing) and try again."
                    )
                else:
                    reply = f"Request error: {e}"
            except anthropic.RateLimitError:
                reply = "You're sending requests too quickly. Wait a moment and try again."
            except Exception as e:
                error_str = str(e).lower()
                if "credit" in error_str or "balance" in error_str:
                    reply = (
                        "Looks like your API credits have run out. "
                        "Top up at [console.anthropic.com/settings/billing]"
                        "(https://console.anthropic.com/settings/billing) and try again."
                    )
                else:
                    reply = f"Something went wrong — please try again. ({type(e).__name__})"

        st.markdown(reply)

    st.session_state.messages.append({"role": "assistant", "content": reply})
