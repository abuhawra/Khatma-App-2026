import streamlit as st
import json
import uuid
import urllib.parse 
import datetime 
import os

# إعدادات الصفحة
st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ==========================================
# CSS الشامل لضبط اتجاه اللغة من اليمين (RTL)
# ==========================================
st.markdown("""
<style>
    /* فرض الاتجاه من اليمين إلى اليسار على كامل التطبيق */
    html, body, [data-testid="stAppViewContainer"] {
        direction: rtl !important;
        text-align: right !important;
    }
    
    /* ضبط التنسيق للعناصر */
    .stApp { direction: rtl !important; }
    
    /* تأمين محاذاة كافة النصوص */
    p, div, h1, h2, h3, h4, h5, h6, span, label, input, textarea, button {
        text-align: right !important;
        direction: rtl !important;
    }
    
    /* ضبط القوائم المنسدلة */
    div[data-baseweb="select"] {
        text-align: right !important;
    }
    
    .dashboard-card { border-radius: 12px; padding: 20px 10px; color: white; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); display: flex; flex-direction: column; align-items: center; justify-content: center; }
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
query_params = st.query_params

# ==========================================
# واجهة التحكم والمنطق
# ==========================================
st.title("⚙️ لوحة التحكم المركزية")

# قراءة كلمة المرور وتأمين اللوحة
admin_login = st.text_input("كلمة المرور:", type="password")

if admin_login == "admin":
    # استخدام مسميات واضحة ومختصرة لضمان التنسيق
    tab1, tab2, tab3, tab4 = st.tabs(["🔗 الروابط", "➕ إضافة مجموعة", "📝 تعديل المجموعة", "📱 المتابعة والتذكير"])
    
    with tab1:
        st.write("### روابط المجموعات:")
        if not db["groups"]:
            st.warning("لا توجد مجموعات حالياً.")
        else:
            for g_id, g_info in db["groups"].items():
                st.write(f"**{g_info['name']}**")
                st.code(f"{BASE_URL}/?group={g_id}")
    
    with tab2:
        g_name = st.text_input("اسم الختمة الجديدة:")
        g_pass = st.text_input("كلمة مرور الختمة:")
        if st.button("إنشاء الختمة"):
            if g_name and g_pass:
                g_id = "group_" + str(uuid.uuid4())[:8]
                db["groups"][g_id] = {
                    "name": g_name, 
                    "password": g_pass, 
                    "khatma_count": 0, 
                    "parts": ["لم تبدأ"] * 30, 
                    "readers": [f"قارئ {i+1}" for i in range(30)],
                    "last_updates": {}
                }
                save_data(db)
                st.success(f"تم إنشاء {g_name} بنجاح!")
                st.rerun()

    with tab3:
        if not db["groups"]:
            st.info("لا توجد مجموعات.")
        else:
            # هنا التعديلات التي طلبتها
            e_id = st.selectbox("اختر المجموعة:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
            g_info = db["groups"][e_id]
            
            new_name = st.text_input("اسم الختمة:", value=g_info["name"])
            new_count = st.number_input("الختمات المنجزة:", value=g_info.get("khatma_count", 0))
            e_text = st.text_area("تعديل أسماء القراء (30 اسماً):", value="\n".join(g_info["readers"]), height=300)
            
            if st.button("حفظ التعديلات"):
                readers = e_text.splitlines()
                if len(readers) == 30:
                    g_info.update({"name": new_name, "khatma_count": new_count, "readers": readers})
                    save_data(db)
                    st.success("تم التحديث!")
                    st.rerun()
                else: st.error("يجب أن يكون العدد 30.")

    with tab4:
        st.write("قسم المتابعة والتذكير...")

elif admin_login != "":
    st.error("كلمة المرور خاطئة!")
