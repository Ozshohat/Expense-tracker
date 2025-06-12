
import streamlit as st
import pandas as pd
import os
import tempfile

st.set_page_config(page_title="מערכת סיווג הוצאות", layout="wide")
st.title("📊 מערכת אונליין לסיווג הוצאות")

CATEGORY_OPTIONS = ["עוז ישראכרט", "עוז כאל", "עוז בנק", "בר ויזה", "בר בנק"]

# העלאת קובץ מסד נתונים ראשי
st.sidebar.header("1️⃣ העלאת מסד נתונים ראשי")
db_file = st.sidebar.file_uploader("בחר קובץ Excel של מסד הנתונים הראשי", type=["xlsx"])

# העלאת קבצים חדשים
st.sidebar.header("2️⃣ העלאת קבצים חדשים לפי קטגוריה")
uploaded_files = {}
for category in CATEGORY_OPTIONS:
    uploaded_files[category] = st.sidebar.file_uploader(f"העלה קובץ עבור {category}", type=["xlsx"], key=category)

if db_file:
    db_df = pd.read_excel(db_file)
    st.success("מסד הנתונים נטען בהצלחה ✅")
    st.dataframe(db_df.head())

    st.markdown("---")
    st.header("📂 עיבוד קבצים חדשים והצעת סיווג")

    all_new_data = []

    for category, file in uploaded_files.items():
        if file is not None:
            st.subheader(f"📎 קובץ {category}")
            df = pd.read_excel(file)
            df = df.dropna(how='all')

            # דוגמה לעיבוד לפי סוג הקובץ (היגיון יוחלף בקוד המלא בהמשך)
            df = df.rename(columns={df.columns[0]: "תאריך", df.columns[1]: "בית עסק", df.columns[-1]: "סכום"})
            df["קטגוריה"] = ""  # תתווסף הצעה אוטומטית מאוחר יותר
            df["שייך ל"] = category.split()[0]  # עוז/בר

            st.dataframe(df.head())
            all_new_data.append(df)

    # איחוד כל הקבצים החדשים
    if all_new_data:
        new_data_combined = pd.concat(all_new_data, ignore_index=True)
        st.markdown("---")
        st.header("🧠 סיווג אוטומטי להצעות")

        # שליפת קטגוריות קיימות ממסד הנתונים
        existing_categories = db_df["פירוט נוסף"].dropna().unique().tolist()

        def suggest_category(name):
            name_lower = str(name).lower()
            if any(w in name_lower for w in ["קפה", "מסעדה", "פיצה", "בייקרי"]):
                return "אוכל"
            elif any(w in name_lower for w in ["מלון", "הונגריה", "אירופה"]):
                return "חול"
            elif any(w in name_lower for w in ["רנואר", "ביגוד", "קסטרו"]):
                return "בגדים"
            elif any(w in name_lower for w in ["פז", "דלק", "ten"]):
                return "רכב"
            else:
                return "שונות"

        new_data_combined["קטגוריה מוצעת"] = new_data_combined["בית עסק"].apply(suggest_category)

        # רצועת עריכה
        edited = st.data_editor(new_data_combined, num_rows="dynamic", use_container_width=True,
                                column_order=["תאריך", "בית עסק", "סכום", "קטגוריה מוצעת", "קטגוריה", "שייך ל"])

        if st.button("📥 מיזוג למסד הנתונים"):
            edited["פירוט נוסף"] = edited["קטגוריה"].replace("", pd.NA).fillna(edited["קטגוריה מוצעת"])
            edited = edited.drop(columns=["קטגוריה מוצעת", "קטגוריה"])
            final_df = pd.concat([db_df, edited], ignore_index=True)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
                final_df.to_excel(tmp.name, index=False)
                st.success("הקבצים מוזגו בהצלחה ✅")
                st.download_button("📤 הורד קובץ מאוחד", tmp.name, file_name="מסד_נתונים_מעודכן.xlsx")
else:
    st.info("נא להעלות קודם את מסד הנתונים הראשי")
