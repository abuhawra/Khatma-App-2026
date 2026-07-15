import streamlit as st
import json
import uuid
import os

st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ================= CSS المعدل =================
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] { direction: rtl !important; text-align: right !important; }
    .stApp { direction: rtl !important; }
    .highlight-text { font-weight: bold; color: #D32F2F; }
    /* تنسيق الصفوف - الخلفية الخضراء تغطي الصف بالكامل */
    .row-style { padding: 10px; border-bottom: 1px solid #dcdcdc; border-radius: 4px; transition: background-color 0.3s; }
    .row-completed { background-color: #d4edda !important; } 
    .status-box { display: inline-block; width: 15px; height: 15px; margin-left: 3px; border-radius: 2px; }
    .s-green { background-color: #277953; }
    .s-gray { background-color: #e0e0e0; }
    .dashboard-card { border-radius: 12px; padding: 15px; color: white; margin-bottom: 10px; text-align: center; }
    .card-green { background-color: #277953; }
    .card-yellow { background-color: #d4a32a; }
</style>
""", unsafe_allow_html=True)

# ================= البيانات =================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, 'data.json')

def load_data():
    if not os.path.exists(DATA_FILE): return {"groups": {}, "base_url": ""}
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f: return json.load(f)
    except: return {"groups": {}, "base_url": ""}

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
    completed = sum(1 for p in group_data.get('parts', []) if p == "تمت التلاوة")
    khatma_val = group_data.get('khatma_count', 0)
    c1, c2, c3 = st.columns(3)
    c1.markdown(f"<div class='dashboard-card card-green'><h2>{completed}</h2><p>الأجزاء المكتملة</p></div>", unsafe_allow_html=True)
    c2.markdown(f"<div class='dashboard-card card-yellow'><h2>{30 - completed}</h2><p>الأجزاء المتبقية</p></div>", unsafe_allow_html=True)
    c3.markdown(f"<div class='dashboard-card card-green'><h2>{khatma_val}</h2><p>الختمات المنجزة</p></div>", unsafe_allow_html=True)

    def update_status(i, key):
        group_data['parts'][i] = st.session_state[key]
        save_data(db)

    tab1, tab2, tab3 = st.tabs(["📊 الجدول", "✅ تأكيد التلاوة", "📖 تفاصيل"])
    
    with tab1:
        for i in range(30):
            status = group_data['parts'][i]
            row_class = "row-style row-completed" if status == "تمت التلاوة" else "row-style"
            
            st.markdown(f'<div class="{row_class}">', unsafe_allow_html=True)
            cols = st.columns([2, 3, 5])
            
            level = {"لم تبدأ": 0, "نص جزء": 1, "حزب": 2, "حزب ونص": 3, "تمت التلاوة": 4}.get(status, 0)
            squares_html = "".join([f'<div class="status-box {"s-green" if j < level else "s-gray"}"></div>' for j in range(4)])
            
            cols[0].markdown(f"<span class='highlight-text'>الجزء {i+1}</span>", unsafe_allow_html=True)
            cols[1].markdown(f"<span class='highlight-text'>{group_data['readers'][i]}</span><br>{squares_html}", unsafe_allow_html=True)
            
            cols[2].radio("الحالة", ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"],
                          index=["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"].index(status),
                          key=f"s_{i}", horizontal=True, label_visibility="collapsed", on_change=update_status, args=(i, f"s_{i}"))
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        for i in range(30):
            if group_data['parts'][i] != "تمت التلاوة":
                st.radio(f"{group_data['readers'][i]} (الجزء {i+1})", ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"],
                         index=["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"].index(group_data['parts'][i]),
                         key=f"late_s_{i}", horizontal=True, on_change=update_status, args=(i, f"late_s_{i}"))
    with tab3:
        st.write(f"إجمالي الختمات المنجزة: {khatma_val}")

else:
    st.title("⚙️ لوحة التحكم المركزية")
    if st.text_input("كلمة المرور:", type="password") == "admin":
        # ... (باقي كود لوحة التحكم)
        tab1, tab2, tab3 = st.tabs(["🔗 الروابط", "➕ إضافة مجموعة", "📝 تعديل المجموعة"])
        with tab1:
            base_url = st.text_input("رابط الموقع الأساسي", db.get("base_url", ""))
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
            g_info["name"] = st.text_input("الاسم:", value=g_info["name"])
            g_info["khatma_count"] = st.number_input("الختمات:", value=int(g_info.get("khatma_count", 0)))
            e_text = st.text_area("الأسماء:", value="\n".join(g_info["readers"]), height=300)
            if st.button("حفظ"):
                g_info["readers"] = e_text.splitlines(); save_data(db); st.rerun()
