import streamlit as st
import json
import uuid
import datetime
import os

st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ================= CSS =================
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
    .stApp { direction: rtl !important; }
    .dashboard-card { border-radius: 12px; padding: 15px; color: white; margin-bottom: 10px; text-align: center; }
    .card-green { background-color: #277953; }
    .card-yellow { background-color: #d4a32a; }
</style>
""", unsafe_allow_html=True)

# ================= دوال البيانات =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

def load_data():
    if not os.path.exists(DATA_FILE): return {"groups": {}, "base_url": ""}
    with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()
query_params = st.query_params
current_group_id = query_params.get("group")

# ================= المنطق =================
if current_group_id and current_group_id in db["groups"]:
    group_data = db["groups"][current_group_id]
    st.title(f"📖 {group_data['name']}")

    # الإحصائيات
    completed = sum(1 for p in group_data['parts'] if p == "تمت التلاوة")
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='dashboard-card card-green'><h2>{completed}</h2><p>الأجزاء المكتملة</p></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='dashboard-card card-yellow'><h2>{30 - completed}</h2><p>الأجزاء المتبقية</p></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='dashboard-card card-green'><h2>{group_data.get('khatma_count', 0)}</h2><p>الختمات المنجزة</p></div>", unsafe_allow_html=True)
    st.progress(completed / 30)

    def update_status(i, key):
        group_data['parts'][i] = st.session_state[key]
        save_data(db)
        other_key = f"late_s_{i}" if key.startswith("s_") else f"s_{i}"
        if other_key in st.session_state: st.session_state[other_key] = st.session_state[key]

    tab1, tab2 = st.tabs(["📊 الجدول", "✅ تأكيد التلاوة"])
    with tab1:
        for i in range(30):
            cols = st.columns([1, 2, 7])
            cols[0].write(f"**الجزء {i+1}**")
            cols[1].write(group_data['readers'][i])
            cols[2].radio("الحالة", ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"],
                          index=["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"].index(group_data['parts'][i]),
                          key=f"s_{i}", horizontal=True, label_visibility="collapsed", on_change=update_status, args=(i, f"s_{i}"))

    with tab2:
        for i in range(30):
            if group_data['parts'][i] != "تمت التلاوة":
                st.radio(f"{group_data['readers'][i]} (الجزء {i+1})", ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"],
                         index=["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"].index(group_data['parts'][i]),
                         key=f"late_s_{i}", horizontal=True, on_change=update_status, args=(i, f"late_s_{i}"))

else:
    # لوحة التحكم
    st.title("⚙️ لوحة التحكم المركزية")
    if st.text_input("كلمة المرور:", type="password") == "admin":
        tab1, tab2, tab3 = st.tabs(["🔗 الروابط", "➕ إضافة مجموعة", "📝 تعديل المجموعة"])
        with tab1:
            for g_id, g_info in db["groups"].items():
                st.write(f"**{g_info['name']}**"); st.code(f"{BASE_URL}/?group={g_id}")
        with tab2:
            name = st.text_input("اسم الختمة:")
            if st.button("إنشاء"):
                g_id = "group_" + str(uuid.uuid4())[:8]
                db["groups"][g_id] = {"name": name, "parts": ["لم تبدأ"]*30, "readers": [f"قارئ {i+1}" for i in range(30)], "khatma_count": 0}
                save_data(db); st.rerun()
        with tab3:
            e_id = st.selectbox("المجموعة:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
            g_info = db["groups"][e_id]
            g_info["name"] = st.text_input("الاسم:", value=g_info["name"])
            g_info["khatma_count"] = st.number_input("الختمات المنجزة:", value=g_info.get("khatma_count", 0))
            e_text = st.text_area("الأسماء:", value="\n".join(g_info["readers"]), height=300)
            if st.button("حفظ"):
                g_info["readers"] = e_text.splitlines(); save_data(db); st.rerun()
