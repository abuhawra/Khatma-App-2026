with tab3: # تبويب تعديل المجموعة
            if not db["groups"]:
                st.info("لا توجد مجموعات حالياً.")
            else:
                # اختيار المجموعة
                e_id = st.selectbox("اختر المجموعة:", list(db["groups"].keys()), format_func=lambda x: db["groups"][x]["name"])
                g_info = db["groups"][e_id]
                
                # بوكس لتعديل الاسم
                new_name = st.text_input("تعديل اسم الختمة:", value=g_info["name"])
                
                # --- هذا هو البوكس الجديد لتعديل الختمات المنجزة ---
                new_count = st.number_input(
                    "تعديل عدد الختمات المنجزة:", 
                    min_value=0, 
                    value=int(g_info.get("khatma_count", 0)), 
                    help="أدخل الرقم يدوياً لتحديث عدد الختمات التي أتمتها المجموعة"
                )
                # --------------------------------------------------
                
                # بوكس تعديل الأسماء
                e_text = st.text_area("تعديل أسماء القراء (30 اسماً):", value="\n".join(g_info["readers"]), height=300)
                
                if st.button("حفظ جميع التعديلات"):
                    readers = e_text.splitlines()
                    if len(readers) == 30:
                        g_info.update({
                            "name": new_name, 
                            "khatma_count": new_count, 
                            "readers": readers
                        })
                        save_data(db)
                        st.success("تم تحديث بيانات المجموعة بنجاح!")
                        st.rerun()
                    else:
                        st.error(f"يجب إدخال 30 اسماً بالضبط. (أدخلت حالياً {len(readers)} اسماً)")
