"""
app.py — 9K Warehouse (OPTIMIZED)
"""

import streamlit as st
import pandas as pd
import os
import base64
import streamlit.components.v1 as components

st.set_page_config(
    page_title="9K Warehouse",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ══════════════════════════════════════════
# helpers — كل شيء مع cache
# ══════════════════════════════════════════
@st.cache_data(show_spinner=False)
def _load_emp(mtime: float):
    return pd.read_excel("employees.xlsx")

def load_employees():
    mtime = os.path.getmtime("employees.xlsx") if os.path.exists("employees.xlsx") else 0
    return _load_emp(mtime)

@st.cache_data(show_spinner=False, max_entries=200)
def get_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

@st.cache_data(show_spinner=False, max_entries=200)
def get_mime(path: str) -> str:
    ext = path.rsplit(".", 1)[-1].lower()
    return "image/png" if ext == "png" else "image/jpeg"

def img_html(path: str, alt: str = "", style: str = "") -> str:
    if not os.path.exists(path):
        return '<div style="width:100%;height:100%;display:grid;place-items:center;opacity:.08;font-size:48px;">📦</div>'
    s = f' style="{style}"' if style else ""
    return f'<img src="data:{get_mime(path)};base64,{get_b64(path)}" alt="{alt}"{s}>'

@st.cache_data(show_spinner=False, max_entries=50)
def list_dir_imgs(folder: str):
    if not os.path.exists(folder): return []
    return sorted([f for f in os.listdir(folder) if f.lower().endswith((".jpg",".jpeg",".png"))])

@st.cache_data(show_spinner=False, max_entries=50)
def list_dir_vids(folder: str):
    if not os.path.exists(folder): return []
    return sorted([f for f in os.listdir(folder) if f.lower().endswith((".mp4",".mov",".avi",".webm"))])

@st.cache_data(show_spinner=False, max_entries=20)
def get_cv_path(cv_val: str) -> str | None:
    if not cv_val or cv_val in ("", "nan", "None", "NaN"):
        return None
    cv_val = cv_val.strip()
    cv_dir = "assets/P9k"
    if os.path.exists(cv_val): return cv_val
    full = os.path.join(cv_dir, cv_val)
    if os.path.exists(full): return full
    if os.path.exists(cv_dir):
        for fname in os.listdir(cv_dir):
            if fname.lower() == cv_val.lower():
                return os.path.join(cv_dir, fname)
    return None

# تحميل كل صور الموظفين مسبقاً في الذاكرة
@st.cache_data(show_spinner=False)
def preload_employee_images(emp_df):
    result = {}
    for _, row in emp_df.iterrows():
        path = f"assets/employees/{row['Image']}"
        if os.path.exists(path):
            result[row['Name']] = (get_b64(path), get_mime(path))
    return result

employees   = load_employees()
emp_images  = preload_employee_images(employees)

for k, v in [("view","home"), ("employee",None), ("cv_open",False)]:
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════
# CSS — مرة واحدة فقط
# ══════════════════════════════════════════
@st.cache_data(show_spinner=False)
def get_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Inter:wght@300;400;500;600;700;800&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
:root{--gold:#c9a84c;--bg:#060a12;--card:#0c1020;--border:rgba(201,168,76,.15);--text:#e8e6df;--muted:#4a4940;}
html,body,.stApp{background:var(--bg)!important;font-family:'Inter',sans-serif;color:var(--text);}
#MainMenu,footer,header,.stDeployButton,[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"],[data-testid="collapsedControl"],
section[data-testid="stSidebar"],.stSidebar{display:none!important;visibility:hidden!important;}
.block-container{padding:0!important;max-width:100%!important;}
/* HOME */
.hero-wrap{position:relative;width:100%;min-height:100svh;overflow:hidden;display:flex;flex-direction:column;}
.hero-img{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:center top;filter:brightness(.55) saturate(.85);}
.hero-overlay{position:absolute;inset:0;background:linear-gradient(160deg,rgba(6,10,18,.25) 0%,rgba(6,10,18,.15) 35%,rgba(6,10,18,.7) 75%,rgba(6,10,18,.95) 100%);}
.hero-content{position:relative;z-index:10;flex:1;display:flex;flex-direction:column;justify-content:flex-end;padding:2rem 1.6rem 1.5rem;gap:.9rem;}
.hero-eyebrow{display:flex;align-items:center;gap:8px;font-size:10px;font-weight:700;letter-spacing:3.5px;text-transform:uppercase;color:var(--gold);}
.hero-eyebrow::before{content:'';width:20px;height:1.5px;background:var(--gold);display:block;}
.hero-title{font-family:'Bebas Neue',sans-serif;font-size:clamp(44px,11vw,100px);color:#fff;line-height:1;letter-spacing:4px;text-transform:uppercase;text-shadow:0 0 60px rgba(201,168,76,.18);white-space:nowrap;}
.hero-title span{color:var(--gold);}
.hero-sub{font-size:11px;color:rgba(232,230,223,.65);letter-spacing:3.5px;text-transform:uppercase;}
.stats-row{display:grid;grid-template-columns:repeat(3,1fr);gap:1px;background:var(--border);border-top:1px solid var(--border);border-bottom:1px solid var(--border);}
.stat-card{background:var(--bg);padding:1.6rem 1rem;text-align:center;transition:background .2s;}
.stat-card:hover{background:#0d1525;}
.stat-num{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;color:var(--gold);line-height:1;text-shadow:0 0 20px rgba(201,168,76,.3);}
.stat-label{font-size:10px;color:#c8c5bc;letter-spacing:2px;text-transform:uppercase;margin-top:5px;font-weight:700;}
.body-wrap{padding:2rem 1.6rem 1rem;}
.about-grid{display:grid;gap:1rem;margin-bottom:2rem;}
.about-card{background:linear-gradient(135deg,#0d1828,#0a1220);border:1px solid var(--border);border-radius:12px;padding:1.8rem 1.6rem;position:relative;overflow:hidden;}
.about-card::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,var(--gold),transparent);}
.about-label{font-size:13px;font-weight:800;letter-spacing:2px;text-transform:uppercase;color:var(--gold);margin-bottom:1rem;text-shadow:0 0 20px rgba(201,168,76,.35);}
.about-text{font-size:14px;color:rgba(232,230,223,.78);line-height:1.85;font-weight:300;}
/* TEAM */
.pw2{padding:0 1.6rem;}
.emp-card2{background:#060a12;border:1px solid rgba(201,168,76,.15);border-radius:10px;overflow:hidden;margin-bottom:4px;cursor:pointer;transition:background .2s;}
.emp-card2:hover{background:#0e1525;}
.emp-card2:hover .cimg2 img{transform:scale(1.04);filter:brightness(1);}
.emp-card2:hover .carrow2{opacity:1;transform:translate(0,0);}
.cimg2{position:relative;overflow:hidden;aspect-ratio:3/4;background:#08101a;}
.cimg2 img{width:100%;height:100%;object-fit:cover;object-position:center top;display:block;transition:transform .5s,filter .4s;filter:grayscale(15%) brightness(.88);}
.cimg2::after{content:'';position:absolute;inset:0;background:linear-gradient(to top,rgba(6,10,18,.95) 0%,rgba(6,10,18,.2) 45%,transparent 100%);}
.cnum2{position:absolute;top:12px;left:12px;z-index:2;font-size:9px;letter-spacing:2px;color:rgba(201,168,76,.5);font-weight:600;}
.carrow2{position:absolute;top:12px;right:12px;z-index:2;width:28px;height:28px;border:1px solid #c9a84c;border-radius:50%;display:grid;place-items:center;color:#c9a84c;font-size:12px;opacity:0;transform:translate(4px,-4px);transition:all .3s;}
.cbody2{padding:12px 14px 14px;border-top:1px solid rgba(201,168,76,.15);background:rgba(6,10,18,.98);}
.cname2{font-size:14px;font-weight:700;color:#fff;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.crole2{font-size:10px;color:#c9a84c;font-weight:600;letter-spacing:1.5px;text-transform:uppercase;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
/* PROFILE */
.profile-hero{display:grid;grid-template-columns:1fr;border-radius:16px;overflow:hidden;border:1px solid rgba(201,168,76,.2);box-shadow:0 0 60px rgba(201,168,76,.06),0 20px 60px rgba(0,0,0,.5);margin-bottom:1.5rem;min-height:340px;}
.profile-left{background:linear-gradient(135deg,#0b1628,#07101e 60%,#050d18);padding:2.5rem 2rem;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;gap:1.1rem;position:relative;}
.profile-left::before{content:'';position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#c9a84c,rgba(201,168,76,.1),transparent);}
.profile-tag{font-size:10px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#c9a84c;display:flex;align-items:center;gap:8px;opacity:.85;}
.profile-tag::before{content:'';width:18px;height:2px;background:#c9a84c;display:block;}
.profile-name{font-family:'Bebas Neue',sans-serif;font-size:clamp(42px,9vw,72px);color:#fff;line-height:.92;text-transform:uppercase;letter-spacing:2px;text-shadow:0 0 50px rgba(201,168,76,.25),0 4px 20px rgba(0,0,0,.6);}
.profile-role{display:inline-flex;align-items:center;gap:8px;font-size:11px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#c9a84c;padding:9px 18px;border:1px solid rgba(201,168,76,.4);border-radius:6px;background:rgba(201,168,76,.08);width:fit-content;}
.profile-role::before{content:'◆';font-size:6px;opacity:.6;}
.profile-right{overflow:hidden;min-height:320px;position:relative;background:linear-gradient(135deg,#06090f,#0a1220);}
.profile-right::before{content:'';position:absolute;inset:0;z-index:1;background:linear-gradient(to right,rgba(7,16,30,.4) 0%,transparent 25%);}
.profile-right img{width:100%;height:100%;object-fit:cover;object-position:center top;display:block;filter:brightness(.93) contrast(1.04);transition:transform .6s ease;}
.profile-right:hover img{transform:scale(1.03);}
.info-row{display:grid;grid-template-columns:1fr 1fr;gap:1rem;margin-bottom:1rem;}
.info-card{background:linear-gradient(135deg,#0d1828,#0a1220);border:1px solid rgba(201,168,76,.15);border-radius:10px;padding:1.2rem 1.4rem;position:relative;overflow:hidden;}
.info-card::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%;background:#c9a84c;opacity:.5;}
.bio-block{background:linear-gradient(135deg,#0d1828,#0a1220);border:1px solid rgba(201,168,76,.12);border-left:3px solid #c9a84c;border-radius:10px;padding:1.6rem 1.8rem;margin-bottom:1.5rem;}
.sh2{display:flex;align-items:center;gap:12px;margin:2rem 0 1rem;}
.st2{font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:2px;color:#e8e6df;text-transform:uppercase;white-space:nowrap;}
.sl2{flex:1;height:1px;background:rgba(255,255,255,.06);}
.sc2{font-size:10px;color:#4a4940;white-space:nowrap;letter-spacing:1px;}
.eb2{padding:2.5rem;border:1px dashed rgba(255,255,255,.06);border-radius:10px;text-align:center;background:#0c1020;font-size:12px;color:#4a4940;letter-spacing:1px;margin-bottom:1rem;}
/* WAREHOUSE */
.pw{padding:0 1.6rem;}
.wh-stats{display:grid;grid-template-columns:repeat(2,1fr);gap:1px;background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.06);border-radius:12px;overflow:hidden;margin-bottom:2rem;}
.wh-stat{background:#0c1020;padding:1.4rem;text-align:center;}
.wh-stat-num{font-family:'Bebas Neue',sans-serif;font-size:2.5rem;color:#c9a84c;line-height:1;margin-bottom:4px;}
.wh-stat-label{font-size:9px;color:#4a4940;letter-spacing:2px;text-transform:uppercase;font-weight:600;}
.ba-pair{display:grid;grid-template-columns:1fr 1fr;gap:3px;border-radius:12px;overflow:hidden;border:1px solid rgba(255,255,255,.06);margin-bottom:1rem;}
.ba-panel{position:relative;aspect-ratio:4/3;overflow:hidden;background:#0c1020;}
.ba-panel img{width:100%;height:100%;object-fit:cover;display:block;filter:brightness(.9);transition:transform .4s;}
.ba-panel:hover img{transform:scale(1.04);}
.ba-badge{position:absolute;top:10px;left:10px;z-index:2;font-size:9px;font-weight:800;letter-spacing:2px;text-transform:uppercase;padding:4px 10px;border-radius:3px;}
.ba-badge.b{background:rgba(239,68,68,.85);color:#fff;}.ba-badge.a{background:rgba(34,197,94,.85);color:#fff;}
.ba-cap{position:absolute;bottom:0;left:0;right:0;padding:1rem 1rem .8rem;background:linear-gradient(to top,rgba(6,10,18,.9),transparent);font-size:12px;font-weight:600;color:rgba(236,234,227,.85);}
.ba-empty{aspect-ratio:4/3;background:#0c1020;display:flex;align-items:center;justify-content:center;flex-direction:column;gap:8px;font-size:10px;color:#4a4940;letter-spacing:1px;text-align:center;padding:1rem;}
.wh-gal{position:relative;aspect-ratio:4/3;overflow:hidden;border-radius:4px;background:#0c1020;}
.wh-gal img{width:100%;height:100%;object-fit:cover;display:block;filter:brightness(.88);transition:transform .5s,filter .3s;}
.wh-gal:hover img{transform:scale(1.06);filter:brightness(1);}
.shdr{display:flex;align-items:center;gap:12px;margin:2rem 0 1rem;}
.stl{font-family:'Bebas Neue',sans-serif;font-size:22px;letter-spacing:2px;color:#e8e6df;text-transform:uppercase;white-space:nowrap;}
.sln{flex:1;height:1px;background:rgba(255,255,255,.06);}
.scnt{font-size:10px;color:#4a4940;white-space:nowrap;letter-spacing:1px;}
.ebox{padding:2.5rem;border:1px dashed rgba(255,255,255,.06);border-radius:10px;text-align:center;background:#0c1020;font-size:12px;color:#4a4940;letter-spacing:1px;}
/* BUTTONS */
.stButton button{background:rgba(201,168,76,.07)!important;color:rgba(201,168,76,.95)!important;border:1px solid rgba(201,168,76,.3)!important;border-radius:8px!important;font-family:'Inter',sans-serif!important;font-size:11px!important;font-weight:700!important;letter-spacing:2px!important;text-transform:uppercase!important;padding:12px 18px!important;width:100%!important;transition:all .2s!important;}
.stButton button:hover{background:rgba(201,168,76,.14)!important;border-color:var(--gold)!important;color:var(--gold)!important;}
.footer{border-top:1px solid var(--border);margin-top:1.5rem;padding:1.5rem 1.6rem;text-align:center;font-size:11px;color:#a09d96;letter-spacing:2px;text-transform:uppercase;font-weight:500;}
@media(min-width:768px){
    .hero-content{padding:2rem 4rem 2rem;}.body-wrap{padding:3rem 4rem 1rem;}
    .about-grid{grid-template-columns:1fr 1fr;}.hero-title{font-size:clamp(72px,8vw,120px);}
    .pw2{padding:0 3.5rem;}.pw{padding:0 3.5rem;}
    .wh-stats{grid-template-columns:repeat(4,1fr);}
    .profile-hero{grid-template-columns:1fr 420px;min-height:480px;}
    .profile-left{padding:3.5rem 3rem;}.profile-right{min-height:480px;}
}
::-webkit-scrollbar{width:4px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:rgba(201,168,76,.2);border-radius:10px;}
</style>"""

st.markdown(get_css(), unsafe_allow_html=True)

# ══════════════════════════════════════════
# NAV
# ══════════════════════════════════════════
def render_nav():
    col_logo, col_btns = st.columns([1, 2])
    with col_logo:
        st.markdown("""<div style="display:flex;align-items:center;gap:10px;padding:.5rem 0;">
            <div style="width:36px;height:36px;border:1.5px solid #c9a84c;border-radius:8px;display:grid;place-items:center;font-family:'Bebas Neue',sans-serif;font-size:13px;color:#c9a84c;">9K</div>
            <div><div style="font-family:'Bebas Neue',sans-serif;font-size:14px;letter-spacing:2px;color:#e8e6df;text-transform:uppercase;">9K Warehouse</div>
            <div style="font-size:9px;color:#4a4940;letter-spacing:2px;text-transform:uppercase;">Gaza · Est. 2026</div></div>
        </div>""", unsafe_allow_html=True)
    with col_btns:
        c1,c2,c3 = st.columns(3)
        with c1:
            if st.button("🏠 Home",      key="nav_home"): st.session_state.view="home";      st.rerun()
        with c2:
            if st.button("👥 Team",      key="nav_team"): st.session_state.view="team";      st.rerun()
        with c3:
            if st.button("🏭 Warehouse", key="nav_wh"):   st.session_state.view="warehouse"; st.rerun()
    st.markdown("<div style='height:1px;background:rgba(255,255,255,.06);margin:0 0 1.5rem;'></div>", unsafe_allow_html=True)

# ══════════════════════════════════════════
# 🏠 HOME
# ══════════════════════════════════════════
if st.session_state.view == "home":
    hp = "assets/9K_Image.png"
    if not os.path.exists(hp): hp = "assets/9kwh.png"
    img_src = f"data:image/png;base64,{get_b64(hp)}" if os.path.exists(hp) \
              else "https://images.unsplash.com/photo-1553413077-190dd305871c?w=1600&q=80"

    st.markdown(f"""
    <div class="hero-wrap">
        <img class="hero-img" src="{img_src}" alt="9K Warehouse">
        <div class="hero-overlay"></div>
        <div class="hero-content">
            <div class="hero-eyebrow">Professional Warehouse Team · Gaza</div>
            <div class="hero-title">9K <span>WAREHOUSE</span></div>
            <div class="hero-sub">Operations Division · Est. 2026</div>
        </div>
    </div>
    <div class="stats-row">
        <div class="stat-card"><div class="stat-num">9K</div><div class="stat-label">Items Managed</div></div>
        <div class="stat-card"><div class="stat-num">24/7</div><div class="stat-label">Operations</div></div>
        <div class="stat-card"><div class="stat-num">100%</div><div class="stat-label">Accuracy</div></div>
    </div>
    <div class="body-wrap"><div class="about-grid">
        <div class="about-card"><div class="about-label">Who We Are</div><div class="about-text">9K Warehouse is a professional logistics and warehouse management team based in Gaza, committed to delivering excellence in every operation.</div></div>
        <div class="about-card"><div class="about-label">Our Mission</div><div class="about-text">Reliable, accurate, and efficient warehouse operations supporting humanitarian and commercial needs — with integrity and precision.</div></div>
    </div></div>""", unsafe_allow_html=True)

    col1,col2 = st.columns(2)
    with col1:
        if st.button("👥  Meet The Team →", key="h_team"): st.session_state.view="team"; st.rerun()
    with col2:
        if st.button("🏭  View Warehouse →", key="h_wh"): st.session_state.view="warehouse"; st.rerun()
    st.markdown('<div class="footer">© 2026 9K Warehouse &nbsp;•&nbsp; Gaza &nbsp;•&nbsp; All Rights Reserved</div>', unsafe_allow_html=True)
    st.stop()

render_nav()

# ══════════════════════════════════════════
# 🏭 WAREHOUSE
# ══════════════════════════════════════════
if st.session_state.view == "warehouse":
    ba_folder  = "assets/warehouse/before_after"
    gal_folder = "assets/warehouse/gallery"

    # تحميل كل الصور مرة واحدة
    @st.cache_data(show_spinner=False)
    def load_wh_data(ba_f, gal_f):
        exts = (".jpg",".jpeg",".png")
        befores = sorted([f for f in os.listdir(ba_f) if "before" in f.lower() and f.lower().endswith(exts)]) if os.path.exists(ba_f) else []
        afters  = sorted([f for f in os.listdir(ba_f) if "after"  in f.lower() and f.lower().endswith(exts)]) if os.path.exists(ba_f) else []
        pairs   = [(os.path.join(ba_f,b), os.path.join(ba_f,a),
                    b.replace("before_","").rsplit(".",1)[0].replace("_"," ").title())
                   for b,a in zip(befores,afters)]
        gals    = sorted([f for f in os.listdir(gal_f) if f.lower().endswith(exts)]) if os.path.exists(gal_f) else []
        return pairs, gals

    pairs, gal_imgs = load_wh_data(ba_folder, gal_folder)

    st.markdown(f"""
    <div class="pw" style="margin-bottom:2.5rem;">
        <div style="display:flex;align-items:center;gap:8px;font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#c9a84c;margin-bottom:.8rem;"><span style="width:20px;height:1px;background:#c9a84c;display:block;"></span>Our Facility</div>
        <div style="font-family:'Bebas Neue',sans-serif;font-size:clamp(40px,8vw,70px);color:#e8e6df;line-height:.95;letter-spacing:2px;text-transform:uppercase;margin-bottom:1rem;">9K <span style="color:#c9a84c;">Warehouse</span><br>Operations Center</div>
        <div style="font-size:13px;color:#4a4940;max-width:400px;line-height:1.8;">A full look at how we organize, manage, and transform our warehouse into a fully operational facility.</div>
    </div>
    <div class="pw"><div class="wh-stats">
        <div class="wh-stat"><div class="wh-stat-num">12</div><div class="wh-stat-label">Team Members</div></div>
        <div class="wh-stat"><div class="wh-stat-num">24/7</div><div class="wh-stat-label">Operations</div></div>
        <div class="wh-stat"><div class="wh-stat-num">100%</div><div class="wh-stat-label">Organized</div></div>
        <div class="wh-stat"><div class="wh-stat-num">9K</div><div class="wh-stat-label">Warehouse</div></div>
    </div></div>
    <div class="pw"><div class="shdr"><div class="stl">Before &amp; After</div><div class="sln"></div></div></div>
    """, unsafe_allow_html=True)

    if pairs:
        for bp,ap,cap in pairs:
            st.markdown(f'<div class="pw" style="margin-bottom:.5rem;"><div class="ba-pair"><div class="ba-panel">{img_html(bp,"Before")}<div class="ba-badge b">Before</div><div class="ba-cap">{cap} — Before</div></div><div class="ba-panel">{img_html(ap,"After")}<div class="ba-badge a">After</div><div class="ba-cap">{cap} — After</div></div></div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="pw"><div class="ba-pair"><div class="ba-empty">📦<br>Add before_1.jpg<br><small style="color:#c9a84c">assets/warehouse/before_after/</small></div><div class="ba-empty">🏭<br>Add after_1.jpg<br><small style="color:#c9a84c">assets/warehouse/before_after/</small></div></div></div>', unsafe_allow_html=True)

    st.markdown(f'<div class="pw"><div class="shdr" style="margin-top:2rem;"><div class="stl">Warehouse Photos</div><div class="sln"></div><div class="scnt">{len(gal_imgs)} photos</div></div></div>', unsafe_allow_html=True)
    if gal_imgs:
        gcols = st.columns(3)
        for idx,gf in enumerate(gal_imgs):
            with gcols[idx%3]:
                st.markdown(f'<div class="wh-gal" style="margin:0 0 8px;">{img_html(os.path.join(gal_folder,gf),f"photo {idx+1}")}</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="pw"><div class="ebox">Add photos to <span style="color:#c9a84c">assets/warehouse/gallery/</span></div></div>', unsafe_allow_html=True)

    st.markdown('<div class="footer">© 2026 9K Warehouse • Gaza</div>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════
# 👤 PROFILE
# ══════════════════════════════════════════
if st.session_state.view == "profile":

    if st.button("← Back to Team", key="back"):
        st.session_state.view = "team"
        st.session_state.cv_open = False
        st.rerun()

    name    = st.session_state.employee
    emp_row = employees[employees["Name"] == name].iloc[0] if name in employees["Name"].values else None

    position    = emp_row["Position"] if emp_row is not None else "Team Member"
    emp_img     = f"assets/employees/{emp_row['Image']}" if emp_row is not None else ""

    folder_name = name  # default
    if emp_row is not None:
        for col in ("Folder", "FolderName"):
            if col in emp_row.index:
                v = str(emp_row[col]).strip()
                if v not in ("","nan","None"):
                    folder_name = v
                    break

    default_bio = "Dedicated team member at 9K Warehouse — contributing expertise and commitment to every operation."
    bio = default_bio
    if emp_row is not None and "Bio" in emp_row.index:
        v = str(emp_row["Bio"]).strip()
        if v not in ("","nan","None"):
            bio = v

    # صورة الموظف — من الـ cache
    if name in emp_images:
        b64_e, mime_e = emp_images[name]
        ph = f'<img src="data:{mime_e};base64,{b64_e}" alt="{name}" style="width:100%;height:100%;object-fit:cover;object-position:center top;display:block;background:#06090f;">'
    else:
        ph = '<div style="width:100%;height:100%;display:grid;place-items:center;background:#06090f;font-size:64px;opacity:.08;">👤</div>'

    # CV
    cv_val  = ""
    if emp_row is not None:
        for col in emp_row.index:
            if str(col).strip().lower() in ("cv","resume"):
                v = str(emp_row[col]).strip()
                if v not in ("","nan","None","NaN"):
                    cv_val = v
                    break
    cv_path = get_cv_path(cv_val)

    st.markdown(f"""
    <div style="padding:0 1.6rem;">
    <div class="profile-hero">
        <div class="profile-left">
            <div class="profile-tag">Employee Profile</div>
            <div class="profile-name">{name}</div>
            <div class="profile-role">{position}</div>
        </div>
        <div class="profile-right">{ph}</div>
    </div>
    <div class="info-row">
        <div class="info-card">
            <div style="font-size:12px;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:#c9a84c;margin-bottom:8px;">Full Name</div>
            <div style="font-size:17px;font-weight:600;color:#fff;">{name}</div>
        </div>
        <div class="info-card">
            <div style="font-size:12px;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:#c9a84c;margin-bottom:8px;">Position</div>
            <div style="font-size:17px;font-weight:600;color:#fff;">{position}</div>
        </div>
    </div>
    <div class="bio-block">
        <div style="font-size:12px;font-weight:800;letter-spacing:3px;text-transform:uppercase;color:#c9a84c;margin-bottom:10px;">About</div>
        <div style="font-size:15px;color:rgba(232,230,223,.85);line-height:1.9;font-weight:300;">{bio}</div>
    </div>
    </div>""", unsafe_allow_html=True)

    # ── CV ──
    st.markdown('<div style="padding:0 1.6rem;"><div class="sh2"><div class="st2">📄 Curriculum Vitae</div><div class="sl2"></div></div></div>', unsafe_allow_html=True)

    if cv_path:
        col1, col2 = st.columns(2)
        with col1:
            if st.button("👁  View CV", key="cv_toggle", use_container_width=True):
                st.session_state.cv_open = not st.session_state.cv_open
                st.rerun()
        with col2:
            with open(cv_path, "rb") as f:
                st.download_button("⬇  Download CV", f, file_name=os.path.basename(cv_path), use_container_width=True)

        if st.session_state.cv_open:
            pdf_b64 = get_b64(cv_path)
            st.markdown(f"""
            <div style="padding:10px 1.6rem 0;">
            <div style="border:1px solid rgba(201,168,76,.2);border-radius:14px;overflow:hidden;box-shadow:0 0 40px rgba(0,0,0,.7);background:#0d1117;">
                <iframe src="data:application/pdf;base64,{pdf_b64}" width="100%" height="900px" style="border:none;"></iframe>
            </div></div>""", unsafe_allow_html=True)
    else:
        st.markdown('<div style="padding:0 1.6rem;"><div class="eb2">📂 No CV uploaded yet</div></div>', unsafe_allow_html=True)

    # ── Gallery ──
    img_folder = f"data/{folder_name}/images"
    if not os.path.exists(img_folder): img_folder = f"data/{folder_name}"
    imgs = list_dir_imgs(img_folder)

    st.markdown(f'<div style="padding:0 1.6rem;"><div class="sh2"><div class="st2">Work Gallery</div><div class="sl2"></div><div class="sc2">{len(imgs)} photos</div></div></div>', unsafe_allow_html=True)

    if imgs:
        @st.cache_data(show_spinner=False)
        def build_gallery_html(folder, file_list):
            imgs_b64 = []
            for im in file_list:
                fp = f"{folder}/{im}"
                if os.path.exists(fp):
                    ext2  = fp.rsplit(".",1)[-1].lower()
                    mime2 = "image/png" if ext2=="png" else "image/jpeg"
                    imgs_b64.append(f"data:{mime2};base64,{get_b64(fp)}")
            thumbs = "".join([f'<div class="gl-item" onclick="lbOpen({i})"><img src="{s}" alt="photo {i+1}" loading="lazy"><div class="gl-overlay"><div class="gl-icon">&#8599;</div><div class="gl-num">#{str(i+1).zfill(2)}</div></div></div>' for i,s in enumerate(imgs_b64)])
            imgs_js = ",".join([f'"{s}"' for s in imgs_b64])
            h = ((len(imgs_b64)+3)//4)*200+80
            return thumbs, imgs_js, h

        thumbs_html, imgs_js, height = build_gallery_html(img_folder, tuple(imgs))
        components.html(f"""<!DOCTYPE html><html><head>
        <style>*{{box-sizing:border-box;margin:0;padding:0;}}body{{background:transparent;}}
        .gl-grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;}}
        @media(max-width:600px){{.gl-grid{{grid-template-columns:repeat(2,1fr);}}}}
        .gl-item{{position:relative;aspect-ratio:1/1;overflow:hidden;border-radius:10px;border:1px solid rgba(201,168,76,.15);cursor:pointer;background:#06090f;}}
        .gl-item img{{width:100%;height:100%;object-fit:cover;display:block;transition:transform .5s,filter .3s;filter:brightness(.85);}}
        .gl-item:hover img{{transform:scale(1.07);filter:brightness(1);}}
        .gl-overlay{{position:absolute;inset:0;background:linear-gradient(to top,rgba(6,10,18,.8) 0%,transparent 55%);opacity:0;transition:opacity .3s;display:flex;flex-direction:column;justify-content:space-between;align-items:flex-end;padding:10px;}}
        .gl-item:hover .gl-overlay{{opacity:1;}}
        .gl-icon{{width:30px;height:30px;border:1px solid #c9a84c;border-radius:50%;display:grid;place-items:center;color:#c9a84c;font-size:15px;background:rgba(6,10,18,.6);transform:translate(4px,-4px);transition:transform .3s;}}
        .gl-item:hover .gl-icon{{transform:translate(0,0);}}
        .gl-num{{font-size:10px;font-weight:700;letter-spacing:2px;color:rgba(201,168,76,.7);align-self:flex-start;}}
        #lb{{display:none;position:fixed;inset:0;z-index:9999;background:rgba(4,7,14,.97);backdrop-filter:blur(16px);align-items:center;justify-content:center;}}
        #lb.open{{display:flex;}}
        #lb-img{{max-width:88vw;max-height:88vh;object-fit:contain;border-radius:8px;box-shadow:0 0 80px rgba(201,168,76,.15);transition:opacity .22s;}}
        .lb-nav{{position:fixed;top:50%;transform:translateY(-50%);width:50px;height:50px;border:1px solid rgba(201,168,76,.4);border-radius:50%;background:rgba(6,10,18,.8);color:#c9a84c;font-size:24px;display:grid;place-items:center;cursor:pointer;z-index:10001;user-select:none;}}
        #lb-prev{{left:16px;}}#lb-next{{right:16px;}}
        #lb-close{{position:fixed;top:18px;right:18px;width:44px;height:44px;border:1px solid rgba(201,168,76,.4);border-radius:50%;background:rgba(201,168,76,.08);color:#c9a84c;font-size:18px;display:grid;place-items:center;cursor:pointer;z-index:10001;}}
        #lb-counter{{position:fixed;bottom:22px;left:50%;transform:translateX(-50%);font-size:11px;font-weight:700;letter-spacing:4px;color:rgba(201,168,76,.65);z-index:10001;}}
        #lb-dots{{position:fixed;bottom:50px;left:50%;transform:translateX(-50%);display:flex;gap:6px;z-index:10001;}}
        .dot{{width:6px;height:6px;border-radius:50%;background:rgba(201,168,76,.3);transition:all .2s;cursor:pointer;}}
        .dot.active{{background:#c9a84c;width:18px;border-radius:3px;}}</style></head><body>
        <div class="gl-grid">{thumbs_html}</div>
        <div id="lb" onclick="lbBg(event)">
            <div id="lb-close" onclick="lbClose()">✕</div>
            <img id="lb-img" src="" alt="">
            <div class="lb-nav" id="lb-prev" onclick="lbMove(-1)">&#8249;</div>
            <div class="lb-nav" id="lb-next" onclick="lbMove(1)">&#8250;</div>
            <div id="lb-dots"></div><div id="lb-counter"></div>
        </div>
        <script>
        const imgs=[{imgs_js}];let cur=0;
        function buildDots(){{const c=document.getElementById('lb-dots');c.innerHTML=imgs.map((_,i)=>`<div class="dot ${{i===cur?'active':''}}" onclick="lbGo(${{i}})"></div>`).join('');}}
        function lbOpen(i){{cur=i;lbUpdate();document.getElementById('lb').classList.add('open');document.addEventListener('keydown',lbKey);}}
        function lbClose(){{document.getElementById('lb').classList.remove('open');document.removeEventListener('keydown',lbKey);}}
        function lbBg(e){{if(e.target.id==='lb')lbClose();}}
        function lbMove(d){{cur=(cur+d+imgs.length)%imgs.length;lbUpdate();}}
        function lbGo(i){{cur=i;lbUpdate();}}
        function lbUpdate(){{const img=document.getElementById('lb-img');img.style.opacity=0;setTimeout(()=>{{img.src=imgs[cur];img.style.opacity=1;}},180);document.getElementById('lb-counter').textContent=String(cur+1).padStart(2,'0')+' / '+String(imgs.length).padStart(2,'0');buildDots();}}
        function lbKey(e){{if(e.key==='ArrowRight')lbMove(1);else if(e.key==='ArrowLeft')lbMove(-1);else if(e.key==='Escape')lbClose();}}
        </script></body></html>""", height=height, scrolling=False)
    else:
        st.markdown('<div style="padding:0 1.6rem;"><div class="eb2">📷 No work images yet</div></div>', unsafe_allow_html=True)

    # ── Videos ──
    vid_folder = f"data/{folder_name}/videos"
    vids = list_dir_vids(vid_folder)

    st.markdown(f'<div style="padding:0 1.6rem;"><div class="sh2" style="margin-top:1.5rem;"><div class="st2">Work Videos</div><div class="sl2"></div><div class="sc2">{len(vids)} videos</div></div></div>', unsafe_allow_html=True)

    if vids:
        @st.cache_data(show_spinner=False)
        def build_video_html(folder, file_list):
            mime_map = {"mp4":"video/mp4","mov":"video/mp4","avi":"video/x-msvideo","webm":"video/webm"}
            vids_data = []
            for vd in file_list:
                vp = f"{folder}/{vd}"
                if os.path.exists(vp):
                    ext3 = vd.rsplit(".",1)[-1].lower()
                    vids_data.append({"src":f"data:{mime_map.get(ext3,'video/mp4')};base64,{get_b64(vp)}","mime":mime_map.get(ext3,"video/mp4")})
            thumbs = "".join([f'<div class="vt-item" onclick="vpOpen({i})"><video src="{v["src"]}" muted preload="metadata" class="vt-preview" onmouseenter="this.play()" onmouseleave="this.pause();this.currentTime=0;"></video><div class="vt-overlay"><div class="vt-play">&#9654;</div></div><div class="vt-num">#{str(i+1).zfill(2)}</div></div>' for i,v in enumerate(vids_data)])
            srcs  = ",".join([f'"{v["src"]}"'  for v in vids_data])
            mimes = ",".join([f'"{v["mime"]}"' for v in vids_data])
            h = ((len(vids_data)+1)//2)*220+200
            return thumbs, srcs, mimes, h

        vid_thumbs, vids_js_src, vids_js_mime, vid_height = build_video_html(vid_folder, tuple(vids))
        components.html(f"""<!DOCTYPE html><html><head>
        <style>*{{box-sizing:border-box;margin:0;padding:0;}}body{{background:transparent;}}
        .vt-grid{{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;}}
        @media(min-width:700px){{.vt-grid{{grid-template-columns:repeat(3,1fr);}}}}
        .vt-item{{position:relative;aspect-ratio:16/9;overflow:hidden;border-radius:10px;border:1px solid rgba(201,168,76,.15);cursor:pointer;background:#06090f;}}
        .vt-preview{{width:100%;height:100%;object-fit:cover;display:block;filter:brightness(.75);transition:transform .5s,filter .3s;}}
        .vt-item:hover .vt-preview{{transform:scale(1.04);filter:brightness(.9);}}
        .vt-overlay{{position:absolute;inset:0;background:rgba(6,10,18,.3);display:flex;align-items:center;justify-content:center;}}
        .vt-play{{width:52px;height:52px;border:2px solid #c9a84c;border-radius:50%;display:grid;place-items:center;color:#c9a84c;font-size:20px;background:rgba(6,10,18,.7);padding-left:4px;transition:all .25s;}}
        .vt-item:hover .vt-play{{background:rgba(201,168,76,.15);transform:scale(1.1);}}
        .vt-num{{position:absolute;top:10px;left:12px;font-size:10px;font-weight:700;letter-spacing:2px;color:rgba(201,168,76,.6);}}
        #vp{{display:none;position:fixed;inset:0;z-index:9999;background:rgba(4,7,14,.97);backdrop-filter:blur(16px);align-items:center;justify-content:center;flex-direction:column;gap:16px;}}
        #vp.open{{display:flex;}}
        #vp-video{{max-width:90vw;max-height:75vh;border-radius:10px;background:#000;}}
        .vp-nav{{position:fixed;top:50%;transform:translateY(-50%);width:50px;height:50px;border:1px solid rgba(201,168,76,.4);border-radius:50%;background:rgba(6,10,18,.8);color:#c9a84c;font-size:24px;display:grid;place-items:center;cursor:pointer;z-index:10001;user-select:none;}}
        #vp-prev{{left:16px;}}#vp-next{{right:16px;}}
        #vp-close{{position:fixed;top:18px;right:18px;width:44px;height:44px;border:1px solid rgba(201,168,76,.4);border-radius:50%;background:rgba(201,168,76,.08);color:#c9a84c;font-size:18px;display:grid;place-items:center;cursor:pointer;z-index:10001;}}
        #vp-counter{{font-size:11px;font-weight:700;letter-spacing:4px;color:rgba(201,168,76,.65);}}</style></head><body>
        <div class="vt-grid">{vid_thumbs}</div>
        <div id="vp" onclick="vpBg(event)">
            <div id="vp-close" onclick="vpClose()">✕</div>
            <video id="vp-video" controls autoplay></video>
            <div class="vp-nav" id="vp-prev" onclick="vpMove(-1)">&#8249;</div>
            <div class="vp-nav" id="vp-next" onclick="vpMove(1)">&#8250;</div>
            <div id="vp-counter"></div>
        </div>
        <script>
        const srcs=[{vids_js_src}];const mimes=[{vids_js_mime}];let vcur=0;
        function vpOpen(i){{vcur=i;vpUpdate();document.getElementById('vp').classList.add('open');document.addEventListener('keydown',vpKey);}}
        function vpClose(){{const v=document.getElementById('vp-video');v.pause();v.src='';document.getElementById('vp').classList.remove('open');document.removeEventListener('keydown',vpKey);}}
        function vpBg(e){{if(e.target.id==='vp')vpClose();}}
        function vpMove(d){{vcur=(vcur+d+srcs.length)%srcs.length;vpUpdate();}}
        function vpUpdate(){{const v=document.getElementById('vp-video');v.pause();v.src=srcs[vcur];v.type=mimes[vcur];v.load();v.play();document.getElementById('vp-counter').textContent=String(vcur+1).padStart(2,'0')+' / '+String(srcs.length).padStart(2,'0');}}
        function vpKey(e){{if(e.key==='ArrowRight')vpMove(1);else if(e.key==='ArrowLeft')vpMove(-1);else if(e.key==='Escape')vpClose();}}
        </script></body></html>""", height=vid_height, scrolling=False)
    else:
        st.markdown('<div style="padding:0 1.6rem;"><div class="eb2">🎬 No work videos yet</div></div>', unsafe_allow_html=True)

    st.markdown('<div style="border-top:1px solid rgba(201,168,76,.15);padding:1.5rem;text-align:center;font-size:11px;color:#a09d96;letter-spacing:2px;text-transform:uppercase;">© 2026 9K Warehouse • Gaza</div>', unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════
# 👥 TEAM
# ══════════════════════════════════════════
st.markdown("""
<div class="pw2"><div style="margin-bottom:2.5rem;">
    <div style="display:flex;align-items:center;gap:8px;font-size:10px;font-weight:700;letter-spacing:3px;text-transform:uppercase;color:#c9a84c;margin-bottom:.8rem;">
        <span style="width:20px;height:1px;background:#c9a84c;display:block;"></span>Our People
    </div>
    <div style="font-family:'Bebas Neue',sans-serif;font-size:clamp(40px,8vw,70px);color:#e8e6df;line-height:.95;letter-spacing:2px;text-transform:uppercase;margin-bottom:1rem;">
        Meet the<br><span style="color:#c9a84c;">Warehouse Team</span>
    </div>
    <div style="font-size:13px;color:#4a4940;max-width:400px;line-height:1.8;">The professionals behind every operation — dedicated, skilled, and driven to excellence.</div>
</div></div>""", unsafe_allow_html=True)

cols = st.columns(4)
for i, row in employees.iterrows():
    with cols[i % 4]:
        num = str(i+1).zfill(2)
        if row['Name'] in emp_images:
            b64_t, mime_t = emp_images[row['Name']]
            itag = f'<img src="data:{mime_t};base64,{b64_t}" alt="{row["Name"]}">'
        else:
            itag = '<img src="https://cdn-icons-png.flaticon.com/512/149/149071.png" style="padding:40px;opacity:.15;">'

        st.markdown(f"""
        <div class="emp-card2">
            <div class="cimg2">{itag}
                <div class="cnum2">{num}</div>
                <div class="carrow2">↗</div>
            </div>
            <div class="cbody2">
                <div class="cname2">{row['Name']}</div>
                <div class="crole2">{row['Position']}</div>
            </div>
        </div>""", unsafe_allow_html=True)

        if st.button("View Profile", key=f"btn_{i}"):
            st.session_state.view     = "profile"
            st.session_state.employee = row["Name"]
            st.session_state.cv_open  = False
            st.rerun()
