import streamlit as st
import json
import uuid
import urllib.parse 
import datetime 
import os

# إعدادات الصفحة
st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ==========================================
# CSS الشامل لضبط الاتجاه RTL
# ==========================================
st.markdown("""
<style>
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }
    .stApp { direction: rtl !important; }
    p, div, h1, h2, h3, h4, h5, h6, span, label, input, textarea, button {
        text-align: right !important;
    }
    div[data-testid="stMarkdownContainer"] { text-align: right !important; }
    div[role="radiogroup"] { gap: 10px; }
    .gray-bg { background-color: rgba(130, 130, 130, 0.08); padding: 5px 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# دوال إدارة البيانات
# ==========================================
def load_data():
    file_path = 'data.json'
    if not os.path.exists(file_path):
        initial = {"groups": {}, "base_url": ""}
        with open(file_path, 'w', encoding='utf-8') as f: json.dump(initial, f)
        return initial
    try:
        with open(file_path, 'r', encoding='utf-8') as f: return json.load(f)
    except:
        return {"groups": {}, "base_url": ""}

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f: json.dump(data, f, ensure_ascii=False, indent=4)

db = load_data()
BASE_URL = db.get("base_url", "")

# ==========================================
# التعامل مع الرابط (التوجيه للمجموعة)
# ==========================================
query_params = st.query_params
current_group_id = query_params.get("group")

# ==========================================
# واجهة المستخدم
# ==========================================
if current_group_id and current_group_id in db["groups"]:
    group_data = db["groups"][current_group_id]
    st.title(f"📖 {group_data['name']}")
    
    # دالة التحديث للربط بين التبويبات
    def update_status(i, key):
        new_status = st.session_state[key]
        now = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
        if "last_updates" not in group_data: group_data["last_updates"] = {}
        group_data["last_updates"][str(i)] = {"time": now, "timestamp": datetime.datetime.now().timestamp()}
        group_data['parts'][i] = new_status
        save_data(db)
        # مزامنة الأزرار
        other_key = f"late_s_{i}" if key.startswith("s_") else f"s_{i}"
        if other_key in st.session_state: st.session_state[other_key] = new_status

    tab1, tab2, tab3 = st.tabs(["📊 الجدول", "✅ تأكيد التلاوة", "📖 تفاصيل"])
    
    with tab1:
        for i in range(30):
            cols = st.columns([1, 2, 7])
            cols[0].write(f"**الجزء {i+1}**")
            cols[1].write(group_data['readers'][i])
            cols[2].radio("الحالة", ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"], 
                          index=["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"].index(group_data['parts'][i]),
                          key=f"s_{i}", horizontal=True, label_visibility="collapsed",
                          on_change=update_status, args=(i, f"s_{i}"))

    with tab2: # المتأخرون
        for i in range(30):
            if group_data['parts'][i] != "تمت التلاوة":
                st.radio(f"{group_data['readers'][i]} (الجزء {i+1})", ["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"],
                         index=["لم تبدأ", "نص جزء", "حزب", "حزب ونص", "تمت التلاوة"].index(group_data['parts'][i]),
                         key=f"late_s_{i}", horizontal=True, on_change=update_status, args=(i, f"late_s_{i}"))
    
    with tab3: # التفاصيل
        st.write("### أحدث 5 تحديثات للمتأخرين:")
        updates = group_data.get("last_updates", {})
        sorted_upd = sorted(updates.items(), key=lambda x: x[1]['timestamp'], reverse=True)[:5]
        for idx, (part_idx, data) in enumerate(sorted_upd):
            st.write(f"{idx+1}. {group_data['readers'][int(part_idx)]} - الجزء {int(part_idx)+1} - {data['time']}")

else:
    # لوحة التحكم المركزية
    st.title("⚙️ لوحة التحكم المركزية")
    if st.text_input("كلمة المرور:", type="password") == "admin":
        tab1, tab2, tab3 = st.tabs(["🔗 الروابط", "➕ إضافة مجموعة", "📝 تعديل المجموعة"])
        
        with tab1:
            for g_id, g_info in db["groups"].items():
                st.write(f"**{g_info['name']}**")
                # رابط مباشر للمجموعة
                link = f"{BASE_URL}/?group={g_id}"
                st.markdown(f"[{link}]({link})")
        
        with tab2:
            name = st.text_input("اسم الختمة:")
            pw = st.text_input("كلمة مرور الختمة:")
            if st.button("إنشاء"):
                g_id = "group_" + str(uuid.uuid4())[:8]
                db["groups"][g_id] = {"name": name, "password": pw, "parts": ["لم تبدأ"]*30, "readers": [f"قارئ {i+1}" for i in range(30)], "last_updates": {}}
                save_data(db); st.rerun()

        with tab3:
            e_id = st.selectbox("اختر المجموعة:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
            g_info = db["groups"][e_id]
            g_info["name"] = st.text_input("اسم الختمة:", value=g_info["name"])
            e_text = st.text_area("الأسماء:", value="\n".join(g_info["readers"]), height=300)
            if st.button("حفظ"):
                g_info["readers"] = e_text.splitlines()
                save_data(db); st.rerun()
