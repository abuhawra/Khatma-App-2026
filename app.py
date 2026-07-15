import streamlit as st
import json
import uuid
import urllib.parse 
import datetime 
import os

# إعدادات الصفحة
st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ==========================================
# CSS - التنسيق الجمالي
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700&display=swap');
    html, body, [class*="st-"] { font-family: 'Tajawal', sans-serif !important; }
    .stApp { direction: rtl; }
    p, div, h1, h2, h3, h4, h5, h6, span, label, input, textarea { text-align: right !important; }
    .dashboard-card { border-radius: 12px; padding: 20px 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; }
    .gray-bg { background-color: rgba(130, 130, 130, 0.08); padding: 5px 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

MASTER_PASSWORD = "admin" 
STATUS_OPTIONS = ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"]

# ==========================================
# دوال البيانات
# ==========================================
def load_data():
    file_path = 'data.json'
    if not os.path.exists(file_path):
        initial = {"groups": {}, "base_url": ""}
        with open(file_path, 'w', encoding='utf-8') as f: json.dump(initial, f)
        return initial
    with open(file_path, 'r', encoding='utf-8') as f: return json.load(f)

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()
BASE_URL = db.get("base_url", "")
query_params = st.query_params

# ==========================================
# دالة تحديث الحالة (تستخدم للربط بين التبويبات)
# ==========================================
def update_part_status(part_index, group_id, source_key):
    new_status = st.session_state[source_key]
    group_data = db["groups"][group_id]
    
    if "last_updates" not in group_data: group_data["last_updates"] = {}
    
    now_dt = datetime.datetime.now()
    group_data["last_updates"][str(part_index)] = {
        "time": now_dt.strftime("%Y-%m-%d  %I:%M %p"),
        "timestamp": now_dt.timestamp()
    }

    group_data['parts'][part_index] = new_status
    save_data(db)
    
    # مزامنة الأزرار
    other_key = f"late_s_{part_index}" if source_key.startswith("s_") else f"s_{part_index}"
    if other_key in st.session_state: st.session_state[other_key] = new_status

# ==========================================
# المنطق البرمجي (التبويبات، الواجهات، واللوحة)
# ==========================================
if "group" in query_params and query_params["group"] in db["groups"]:
    group_id = query_params["group"]
    group_data = db["groups"][group_id]
    
    st.title(f"📖 {group_data['name']}")
    tab1, tab2, tab3, tab4 = st.tabs(["📊 الجدول", "✅ تأكيد التلاوة", "📖 تفاصيل", "📅 الخطة"])
    
    with tab1:
        for i in range(30):
            col1, col2, col3 = st.columns([1, 2, 7])
            current = group_data['parts'][i]
            with col1: st.write(f"**الجزء {i+1}**")
            with col2: st.write(group_data['readers'][i])
            with col3:
                st.radio(f"s_{i}", STATUS_OPTIONS, index=STATUS_OPTIONS.index(current), 
                         key=f"s_{i}", horizontal=True, label_visibility="collapsed",
                         on_change=update_part_status, args=(i, group_id, f"s_{i}"))

    with tab2: # قسم تأكيد التلاوة للمتأخرين
        st.write("### ⏳ القراء الذين لم ينهوا التلاوة")
        for i in range(30):
            if group_data['parts'][i] != "تمت التلاوة":
                st.radio(f"{group_data['readers'][i]} (الجزء {i+1})", STATUS_OPTIONS, 
                         index=STATUS_OPTIONS.index(group_data['parts'][i]),
                         key=f"late_s_{i}", horizontal=True,
                         on_change=update_part_status, args=(i, group_id, f"late_s_{i}"))

    with tab3: # قسم التفاصيل التاريخية
        st.write("### 🏆 أحدث التحديثات")
        # منطق عرض آخر 5 محدثين...

else:
    st.title("⚙️ لوحة التحكم المركزية")
    if st.text_input("كلمة المرور:", type="password") == MASTER_PASSWORD:
        tab1, tab2, tab3, tab4 = st.tabs(["🔗 الروابط", "➕ إضافة مجموعة", "📝 تعديل المجموعة", "📱 المتابعة والتذكير"])
        with tab3:
            # كود تعديل اسم المجموعة والختمات المنجزة والأسماء
            if db["groups"]:
                e_id = st.selectbox("اختر المجموعة:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
                g_info = db["groups"][e_id]
                new_name = st.text_input("اسم الختمة:", value=g_info["name"])
                new_count = st.number_input("الختمات المنجزة:", value=g_info.get("khatma_count", 0))
                e_text = st.text_area("الأسماء:", value="\n".join(g_info["readers"]), height=300)
                if st.button("حفظ التعديلات"):
                    g_info.update({"name": new_name, "khatma_count": new_count, "readers": e_text.splitlines()})
                    save_data(db)
                    st.success("تم التحديث!")
