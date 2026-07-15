import streamlit as st
import json
import uuid
import datetime
import os

# إعدادات الصفحة
st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ==========================================
# CSS - التنسيق الجمالي والاتجاه RTL
# ==========================================
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
    .stApp { direction: rtl !important; }
    p, div, h1, h2, h3, h4, h5, h6, span, label, input, textarea, button { text-align: right !important; }
    div[data-testid="stMarkdownContainer"] { text-align: right !important; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# إدارة البيانات (بمسارات مطلقة لضمان العمل)
# ==========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

def load_data():
    if not os.path.exists(DATA_FILE):
        initial = {"groups": {}, "base_url": ""}
        with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(initial, f)
        return initial
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except:
        return {"groups": {}, "base_url": ""}

def save_data(data):
    with open(DATA_FILE, 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()
query_params = st.query_params
current_group_id = query_params.get("group")

# ==========================================
# 1. واجهة المجموعة
# ==========================================
if current_group_id and current_group_id in db["groups"]:
    group_data = db["groups"][current_group_id]
    st.title(f"📖 {group_data['name']}")
    
    def update_status(i, key):
        new_status = st.session_state[key]
        group_data['parts'][i] = new_status
        save_data(db)
        # مزامنة الأزرار
        other_key = f"late_s_{i}" if key.startswith("s_") else f"s_{i}"
        if other_key in st.session_state: st.session_state[other_key] = new_status

    tab1, tab2 = st.tabs(["📊 الجدول", "✅ متابعة القراء"])
    
    with tab1:
        for i in range(30):
            cols = st.columns([1, 2, 7])
            cols[0].write(f"**الجزء {i+1}**")
            cols[1].write(group_data['readers'][i])
            cols[2].radio("الحالة", ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"],
                          index=["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"].index(group_data['parts'][i]),
                          key=f"s_{i}", horizontal=True, label_visibility="collapsed",
                          on_change=update_status, args=(i, f"s_{i}"))

    with tab2:
        for i in range(30):
            if group_data['parts'][i] != "تمت التلاوة":
                st.radio(f"{group_data['readers'][i]} (الجزء {i+1})", ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"],
                         index=["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"].index(group_data['parts'][i]),
                         key=f"late_s_{i}", horizontal=True, on_change=update_status, args=(i, f"late_s_{i}"))

# ==========================================
# 2. لوحة التحكم
# ==========================================
else:
    st.title("⚙️ لوحة التحكم المركزية")
    if st.text_input("كلمة المرور:", type="password") == "admin":
        tab1, tab2, tab3 = st.tabs(["🔗 الروابط", "➕ إضافة مجموعة", "📝 تعديل المجموعة"])
        
        with tab1:
            for g_id, g_info in db["groups"].items():
                st.write(f"**{g_info['name']}**")
                link = f"{st.query_params.get('url', '')}/?group={g_id}"
                st.markdown(f"[{link}]({link})")
        
        with tab2:
            name = st.text_input("اسم الختمة:")
            if st.button("إنشاء"):
                g_id = "group_" + str(uuid.uuid4())[:8]
                db["groups"][g_id] = {"name": name, "parts": ["لم تبدأ"]*30, "readers": [f"قارئ {i+1}" for i in range(30)], "khatma_count": 0}
                save_data(db); st.rerun()

        with tab3:
            e_id = st.selectbox("اختر المجموعة:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
            g_info = db["groups"][e_id]
            g_info["name"] = st.text_input("الاسم:", value=g_info["name"])
            g_info["khatma_count"] = st.number_input("الختمات المنجزة:", value=g_info.get("khatma_count", 0))
            e_text = st.text_area("الأسماء:", value="\n".join(g_info["readers"]), height=300)
            if st.button("حفظ"):
                g_info["readers"] = e_text.splitlines()
                save_data(db); st.rerun()
