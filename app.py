import os
import sqlite3
import requests
import streamlit as st

# إعداد الصفحة بواجهة عریضة
st.set_page_config(
    page_title="Lootd - Anime & Fiction", page_icon="🎬", layout="wide"
)

# تخصيص التصميم السينمائي المظلم (Dark Cinematic Theme)
st.markdown(
    """
    <style>
    .stApp { background-color: #14181c; color: #9ab; }
    h1, h2, h3 { color: #ffffff !important; }
    .review-card {
        background-color: #1c242d;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 15px;
        border: 1px solid #2c3440;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .stButton>button {
        background-color: #00e054;
        color: #14181c;
        font-weight: bold;
        border-radius: 8px;
        border: none;
    }
    .stButton>button:hover {
        background-color: #00c048;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# إعداد قاعدة البيانات وتخزين الصور
DB_NAME = "lootd_platform.db"
IMAGE_DIR = "uploads"
if not os.path.exists(IMAGE_DIR):
  os.makedirs(IMAGE_DIR)


def init_db():
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            category TEXT,
            rating INTEGER,
            review TEXT,
            poster_url TEXT,
            user_image TEXT
        )
    """)
  conn.commit()
  conn.close()


init_db()

st.title("🎬 Lootd | منصة تقييم الأنمي والروايات")
st.write(
    "مساحتك الخاصة لمشاركة الانطباعات، استعراض البوسترات، وإرفاق لقطات الشاشة"
    " بستايل عالمي."
)

tab1, tab2 = st.tabs(["🏠 استكشاف المجتمع", "✍️ تدوين تقييم جديد (Log)"])

# تبويب استكشاف المراجعات
with tab1:
  st.subheader("أحدث تدوينات المجتمع")
  conn = sqlite3.connect(DB_NAME)
  c = conn.cursor()
  c.execute(
      "SELECT title, category, rating, review, poster_url, user_image FROM"
      " reviews ORDER BY id DESC"
  )
  rows = c.fetchall()
  conn.close()

  if not rows:
    st.info("لا توجد مراجعات حتى الآن. كن أول من يضيف تقييماً!")
  else:
    for row in rows:
      title, category, rating, review, poster_url, user_image = row
      st.markdown(
          f"""
                <div class="review-card">
                    <h3>{title} <span style="font-size: 0.8rem; color: #00e054; background: #0b1015; padding: 4px 8px; border-radius: 4px;">{category}</span></h3>
                    <p style="color: #f5c518; font-size: 1.1rem;">{'⭐' * rating} ({rating}/5)</p>
                    <p style="color: #c0c0c0;">{review}</p>
                </div>
                """,
          unsafe_allow_html=True,
      )

      col_img1, col_img2 = st.columns(2)
      if poster_url:
        with col_img1:
          st.image(poster_url, caption="الستر الرسمي", width=140)
      if user_image and os.path.exists(user_image):
        with col_img2:
          st.image(user_image, caption="لقطة الشاشة المرفقة", width=180)
      st.markdown("---")

# تبويب إضافة تقييم
with tab2:
  st.subheader("سجل عملاً جديداً (Anime / Fiction)")

  choice_type = st.selectbox(
      "اختر القسم", ["أنمي (جلب تلقائي بالـ API)", "رواية خيالية / كتاب (يدوي)"]
  )

  if "أنمي" in choice_type:
    search_term = st.text_input("ابحث عن اسم الأنمي بالإنجليزية (مثل: Naruto):")
    poster_url = ""
    title = ""

    if search_term:
      try:
        res = requests.get(
            f"https://api.jikan.moe/v4/anime?q={search_term}&limit=1"
        ).json()
        if res.get("data"):
          anime_data = res["data"][0]
          title = anime_data["title"]
          poster_url = anime_data["images"]["jpg"]["image_url"]
          st.success(f"تم العثور على: {title}")
          st.image(poster_url, width=140)
        else:
          st.warning("لم يتم العثور على نتائج.")
      except Exception:
        st.error("فشل الاتصال بالخادم.")

    with st.form("anime_log_form"):
      rating = st.slider("التقييم بالنجوم ⭐", 1, 5, 5)
      review_text = st.text_area("اكتب انطباعك أو مراجعتك المفصلة...")
      uploaded_file = st.file_uploader(
          "أرفق لقطة شاشة مفضلة لديك", type=["jpg", "png", "jpeg"]
      )

      submitted = st.form_submit_button("نشر التقييم في المنصة")
      if submitted and title:
        user_image_path = ""
        if uploaded_file:
          user_image_path = os.path.join(IMAGE_DIR, uploaded_file.name)
          with open(user_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO reviews (title, category, rating, review, poster_url,"
            " user_image) VALUES (?, ?, ?, ?, ?, ?)",
            (title, "أنمي", rating, review_text, poster_url, user_image_path),
        )
        conn.commit()
        conn.close()
        st.success("تم نشر التقييم بنجاح!")
        st.rerun()

  else:
    with st.form("fiction_log_form"):
      fiction_title = st.text_input("عنوان الرواية أو الكتاب الخيالي:")
      rating = st.slider("التقييم بالنجوم ⭐", 1, 5, 5)
      review_text = st.text_area("اكتب رأيك عن القصة وتفاصيلها...")
      uploaded_file = st.file_uploader(
          "أرفق صورة الغلاف أو لقطة تعبيرية", type=["jpg", "png", "jpeg"]
      )

      submitted = st.form_submit_button("نشر الرواية")
      if submitted and fiction_title:
        user_image_path = ""
        if uploaded_file:
          user_image_path = os.path.join(IMAGE_DIR, uploaded_file.name)
          with open(user_image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        c.execute(
            "INSERT INTO reviews (title, category, rating, review, poster_url,"
            " user_image) VALUES (?, ?, ?, ?, ?, ?)",
            (
                fiction_title,
                "رواية",
                rating,
                review_text,
                "",
                user_image_path,
            ),
        )
        conn.commit()
        conn.close()
        st.success("تم نشر الرواية بنجاح!")
        st.rerun()
