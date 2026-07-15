import streamlit as st
import json
import uuid
import datetime
import os

st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ================= CSS التنسيق المطور =================
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
    .stApp { direction: rtl !important; }
    p, div, h1, h2, h3, h4, h5, h6, span, label, input, textarea, button { text-align: right !important; }
    .highlight-text { font-weight: bold; color: #D32F2F; }
    .row-style { padding: 10px; border-bottom: 1px solid #dcdcdc; }
    /* تنسيق مربعات الحالة */
    .status-box { display: inline-block; width: 15px; height: 15px; margin-left: 3px; border-radius: 2px; }
    .s-green { background-color: #277953; }
    .s-gray { background-color: #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# ================= دوال البيانات =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

def load_data():
    if not os.path.exists(DATA_FILE): return {"groups": {}, "base_url": ""}
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
        for g_id in data.get("groups", {}):
            if "khatma_count" not in data["groups"][g_id]: data["groups"][g_id]["khatma_count"] = 0
        return data

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

# دالة رسم مربعات التقدم
def get_status_squares(status):
    mapping = {"لم تبدأ": 0, "نص جزء": 1, "حزب": 2, "حزب ونص": 3, "تمت التلاوة": 4}
    level = mapping.get(status, 0)
    squares = ""
    for i in range(4):
        color = "s-green" if i < level else "s-gray"
        squares += f'<div class="status-box {color}"></div>'
    return squares

db = load_data()
query_params = st.query_params
current_group_id = query_params.get("group")

# ================= المنطق =================
if current_group_id and current_group_id in db["groups"]:
    group_data = db["groups"][current_group_id]
    st.title(f"📖 {group_data['name']}")

    def update_status(i, key):
        group_data['parts'][i] = st.session_state[key]
        save_data(db)
        other_key = f"late_s_{i}" if key.startswith("s_") else f"s_{i}"
        if other_key in st.session_state: st.session_state[other_key] = st.session_state[key]

    tab1, tab2, tab3 = st.tabs(["📊 الجدول", "✅ تأكيد التلاوة", "📖 تفاصيل"])
    
    with tab1:
        for i in range(30):
            st.markdown(f'<div class="row-style">', unsafe_allow_html=True)
            cols = st.columns([2, 3, 5])
            cols[0].markdown(f"<span class='highlight-text'>الجزء {i+1}</span>", unsafe_allow_html=True)
            cols[1].markdown(f"<span class='highlight-text'>{group_data['readers'][i]}</span><br>{get_status_squares(group_data['parts'][i])}", unsafe_allow_html=True)
            
            cols[2].radio("الحالة", ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"],
                          index=["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"].index(group_data['parts'][i]),
                          key=f"s_{i}", horizontal=True, label_visibility="collapsed", on_change=update_status, args=(i, f"s_{i}"))
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        for i in range(30):
            if group_data['parts'][i] != "تمت التلاوة":
                st.radio(f"{group_data['readers'][i]} (الجزء {i+1})", ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"],
                         index=["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"].index(group_data['parts'][i]),
                         key=f"late_s_{i}", horizontal=True, on_change=update_status, args=(i, f"late_s_{i}"))

    with tab3:
        st.write(f"### تفاصيل المجموعة: {group_data['name']}")
        st.write(f"إجمالي الختمات المنجزة: {group_data.get('khatma_count', 0)}")

else:
    st.title("⚙️ لوحة التحكم المركزية")
    if st.text_input("كلمة المرور:", type="password") == "admin":
        tab1, tab2, tab3 = st.tabs(["🔗 الروابط", "➕ إضافة مجموعة", "📝 تعديل المجموعة"])
        with tab1:
            base_url = st.text_input("ضع رابط التطبيق هنا", db.get("base_url", ""))
            if st.button("حفظ الرابط"): db["base_url"] = base_url; save_data(db)
            for g_id, g_info in db["groups"].items():
                st.write(f"**{g_info['name']}**")
                st.code(f"{base_url}/?group={g_id}")
        with tab2:
            name = st.text_input("اسم الختمة:")
            if st.button("إنشاء"):
                g_id = "group_" + str(uuid.uuid4())[:8]
                db["groups"][g_id] = {"name": name, "parts": ["لم تبدأ"]*30, "readers": [f"قارئ {i+1}" for i in range(30)], "khatma_count": 0}
                save_data(db); st.rerun()
        with tab3:
            e_id = st.selectbox("المجموعة:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
            g_info = db["groups"][e_id]
            g_info["name"] = st.text_input("تعديل اسم الختمة:", value=g_info["name"])
            g_info["khatma_count"] = st.number_input("الختمات المنجزة:", value=int(g_info.get("khatma_count", 0)))
            e_text = st.text_area("تعديل الأسماء:", value="\n".join(g_info["readers"]), height=300)
            if st.button("حفظ التعديلات"):
                g_info["readers"] = e_text.splitlines(); save_data(db); st.rerun()
