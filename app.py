import streamlit as st
import json
import uuid
import urllib.parse 
import datetime 
import os

# إعدادات الصفحة
st.set_page_config(page_title="متابعة ختمة القرآن", page_icon="📖", layout="wide")

# ==========================================
# دوال البيانات (محدثة لضمان القراءة)
# ==========================================
def load_data():
    file_path = 'data.json'
    # إذا لم يوجد الملف، ننشئ ملفاً فارغاً ببيانات أولية
    if not os.path.exists(file_path):
        initial_data = {"groups": {}, "base_url": ""}
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, ensure_ascii=False, indent=4)
        return initial_data
    
    # محاولة قراءة الملف
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # التأكد من وجود المفاتيح الأساسية
            if "groups" not in data: data["groups"] = {}
            if "base_url" not in data: data["base_url"] = ""
            return data
    except Exception as e:
        st.error(f"خطأ في قراءة ملف البيانات: {e}")
        return {"groups": {}, "base_url": ""}

def save_data(data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# تحميل البيانات في كل مرة يعمل فيها السكربت
db = load_data()
BASE_URL = db.get("base_url", "")
query_params = st.query_params

# ==========================================
# واجهة التحكم (لوحة الإدارة)
# ==========================================
st.title("⚙️ لوحة التحكم المركزية")
admin_login = st.text_input("كلمة المرور:", type="password")

if admin_login == "admin":
    tab1, tab2, tab3, tab4 = st.tabs(["🔗 الروابط", "➕ إضافة مجموعة", "📝 تعديل المجموعة", "📱 المتابعة والتذكير"])
    
    with tab1:
        st.write("### روابط المجموعات:")
        if not db["groups"]:
            st.warning("لا توجد مجموعات حالياً. أضف مجموعة من تبويب 'إضافة مجموعة'.")
        else:
            for g_id, g_info in db["groups"].items():
                st.write(f"**{g_info['name']}**")
                link = f"{BASE_URL}/?group={g_id}"
                st.code(link)
    
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
                st.success(f"تم إنشاء مجموعة {g_name} بنجاح!")
                st.rerun()

    with tab3:
        if not db["groups"]:
            st.info("لا توجد مجموعات لتعديلها.")
        else:
            e_id = st.selectbox("اختر المجموعة للتعديل:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
            g_info = db["groups"][e_id]
            new_name = st.text_input("تعديل اسم الختمة:", value=g_info["name"])
            new_count = st.number_input("تعديل عدد الختمات المنجزة:", value=g_info.get("khatma_count", 0))
            e_text = st.text_area("تعديل الأسماء (30 اسماً):", value="\n".join(g_info["readers"]), height=300)
            if st.button("حفظ جميع التعديلات"):
                readers = e_text.splitlines()
                if len(readers) == 30:
                    db["groups"][e_id].update({"name": new_name, "khatma_count": new_count, "readers": readers})
                    save_data(db)
                    st.success("تم التحديث!")
                    st.rerun()
                else: st.error("يجب إدخال 30 اسماً.")
