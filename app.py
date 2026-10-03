import requests
import streamlit as st
from supabase import Client, create_client

# إعداد الصفحة وتفعيل وضع الموبايل الاحترافي
st.set_page_config(
    page_title="AniLootd - Official", page_icon="🍥", layout="centered"
)

# تصميم CSS مطابق تماماً لستايل وتماثل واجهات Lootd الداكنة
st.markdown(
    """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp { background-color: #14181c; color: #9ab; font-family: -apple-system, BlinkMacSystemFont, sans-serif; }
    h1, h2, h3 { color: #ffffff !important; font-weight: 700; }
    
    /* بطاقات الأنمي والمانغا المطابقة */
    .lootd-card {
        background-color: #1c242d;
        padding: 14px;
        border-radius: 12px;
        margin-bottom: 12px;
        border: 1px solid #2c3440;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.4);
    }
    
    /* الأزرار الخضراء الرسمية */
    .stButton>button {
        background-color: #00e054;
        color: #14181c;
        font-weight: bold;
        border-radius: 10px;
        border: none;
        width: 100%;
        padding: 10px;
        font-size: 1rem;
    }
    .stButton>button:hover {
        background-color: #00c048;
        color: #ffffff;
    }
    
    .badge {
        background-color: #0b1015;
        color: #00e054;
        padding: 3px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# الاتصال بقاعدة بيانات Supabase السحابية
try:
  SUPABASE_URL = st.secrets["SUPABASE_URL"]
  SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
  supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception:
  supabase = None

# إدارة حالة التطبيق والجلسات
if "logged_in" not in st.session_state:
  st.session_state.logged_in = False
  st.session_state.user_email = ""
if "active_tab" not in st.session_state:
  st.session_state.active_tab = "home"

# ----------------- 1. شاشة تسجيل الدخول المطابقة -----------------
if not st.session_state.logged_in:
  st.markdown(
      "<h2 style='text-align: center; margin-top: 40px;'>🍥 AniLootd</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center; color: #8899a6; margin-bottom: 30px;'>مجتمعك"
      " لتقييم الأنمي والمانغا</p>",
      unsafe_allow_html=True,
  )

  tab_in, tab_up = st.tabs(["تسجيل الدخول", "إنشاء حساب"])

  with tab_in:
    with st.form("login_form"):
      email = st.text_input("البريد الإلكتروني")
      password = st.text_input("كلمة المرور", type="password")
      if st.form_submit_button("دخول"):
        if supabase:
          try:
            res = supabase.auth.sign_in_with_password(
                {"email": email, "password": password}
            )
            st.session_state.logged_in = True
            st.session_state.user_email = res.user.email
            st.rerun()
          except Exception:
            st.error("خطأ في بيانات الدخول.")
        else:
          if email:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.rerun()

  with tab_up:
    with st.form("signup_form"):
      n_email = st.text_input("البريد الإلكتروني الجديد")
      n_pass = st.text_input("كلمة المرور الجديدة", type="password")
      if st.form_submit_button("إنشاء حساب"):
        if supabase:
          try:
            supabase.auth.sign_up({"email": n_email, "password": n_pass})
            st.success("تم إنشاء الحساب بنجاح! يمكنك تسجيل الدخول الآن.")
          except Exception:
            st.error("خطأ أثناء إنشاء الحساب.")

else:
  # ----------------- 2. الواجهة الرئيسية والتنقل السفلي المطابق -----------------

  # شريط التنقل السفلي (يشابه تماماً أزرار التطبيق الأصلي في الصور)
  st.markdown("---")
  b1, b2, b3, b4, b5 = st.columns(5)

  with b1:
    if st.button("🏠 الرئيسية"):
      st.session_state.active_tab = "home"
      st.rerun()
  with b2:
    if st.button("🔍 استكشاف"):
      st.session_state.active_tab = "explore"
      st.rerun()
  with b3:
    if st.button("➕ إضافة"):
      st.session_state.active_tab = "add"
      st.rerun()
  with b4:
    if st.button("📋 قوائم"):
      st.session_state.active_tab = "lists"
      st.rerun()
  with b5:
    if st.button("👤 الحساب"):
      st.session_state.active_tab = "profile"
      st.rerun()
  st.markdown("---")

  # --- الشاشة الأولى: الرئيسية والمجتمع (مطابقة للصورة الثانية) ---
  if st.session_state.active_tab == "home":
    sub_choice = st.radio(
        "التبويب العلوي",
        ["الرئيسية", "المجتمع"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if sub_choice == "الرئيسية":
      st.markdown("#### الأنمي والمانغا القادمة")
      st.info("🔥 عرض أحدث الأعمال المنتظرة لهذا الموسم عبر الأرشيف العالمي.")

      st.markdown("#### إصدارات جديدة")
      try:
        res = requests.get(
            "https://api.jikan.moe/v4/anime?status=airing&limit=4"
        ).json()
        if res.get("data"):
          cols = st.columns(2)
          for idx, anime in enumerate(res["data"][:4]):
            with cols[idx % 2]:
              st.image(anime["images"]["jpg"]["image_url"], use_container_width=True)
              st.markdown(
                  f"<p style='font-size:0.85rem; font-weight:bold;'>{anime['title'][:20]}...</p>",
                  unsafe_allow_html=True,
              )
      except Exception:
        pass

      st.markdown("#### آخر مراجعات المجتمع")
      if supabase:
        try:
          reviews = (
              supabase.table("reviews")
              .select("*")
              .order("id", desc=True)
              .limit(5)
              .execute()
          ).data
          if not reviews:
            st.write("لا توجد مراجعات حتى الآن.")
          for r in reviews:
            st.markdown(
                f"""
                        <div class="lootd-card">
                            <b>{r['title']}</b> <span class="badge">{r['media_type']}</span>
                            <p style="color: #f5c518; margin: 4px 0;">{'⭐' * r['rating']}</p>
                            <p style="font-size:0.9rem; color:#ccc;">{r['review']}</p>
                            <p style="font-size:0.7rem; color:#666;">بواسطة: {r.get('user_email', 'مستخدم')}</p>
                        </div>
                        """,
                unsafe_allow_html=True,
            )
        except Exception:
          st.error("جاري جلب المراجعات...")

    else:
      st.markdown("#### 🌐 مجتمع AniLootd النشط")
      st.write("تحديثات أصدقائك، التفاعلات، والنقاشات الحية تظهر هنا.")

  # --- الشاشة الثانية: الاستكشاف والتصنيفات (مطابقة للصورة الأولى) ---
  elif st.session_state.active_tab == "explore":
    st.markdown("#### 🔍 ابحث وتصفح حسب التصنيفات")

    # أزرار التصنيفات السريعة أفقياً تماماً مثل Lootd
    cat_col1, cat_col2, cat_col3, cat_col4 = st.columns(4)
    selected_genre = None
    with cat_col1:
      if st.button("أكشن"):
        selected_genre = 1
    with cat_col2:
      if st.button("مغامرة"):
        selected_genre = 2
    with cat_col3:
      if st.button("رومانسي"):
        selected_genre = 22
    with cat_col4:
      if st.button("خيال"):
        selected_genre = 10

    search_q = st.text_input(
        "ابحث عن أنمي أو مانغا...", placeholder="اكتب الاسم بالإنجليزية..."
    )

    if search_q or selected_genre:
      try:
        if search_q:
          url = f"https://api.jikan.moe/v4/anime?q={search_q}&limit=5"
        else:
          url = f"https://api.jikan.moe/v4/anime?genres={selected_genre}&limit=5"

        data = requests.get(url).json().get("data", [])
        if data:
          for item in data:
            st.markdown(
                f"""
                    <div class="lootd-card" style="display:flex; gap:12px; align-items:center;">
                        <img src="{item['images']['jpg']['image_url']}" width="70" style="border-radius:8px;">
                        <div>
                            <b style="color:#fff;">{item['title']}</b>
                            <p style="margin:4px 0; font-size:0.85rem; color:#9ab;">الحلقات: {item.get('episodes', 'N/A')} | التقييم: ⭐ {item.get('score', 'N/A')}</p>
                        </div>
                    </div>
                    """,
                unsafe_allow_html=True,
            )
        else:
          st.warning("لم يتم العثور على نتائج.")
      except Exception:
        st.error("خطأ في الاتصال بالخادم.")

  # --- الشاشة الثالثة: إضافة ونشر تقييم جديد ---
  elif st.session_state.active_tab == "add":
    st.markdown("#### ✍️ تدوين تقييم جديد للمجتمع")
    with st.form("new_review"):
      t_title = st.text_input("اسم الأنمي أو المانغا")
      t_type = st.selectbox("النوع", ["أنمي (Anime)", "مانغا (Manga)"])
      t_rate = st.slider("التقييم بالنجوم", 1, 5, 5)
      t_rev = st.text_area("انطباعك أو مراجعتك المفصلة...")

      if st.form_submit_button("نشر التقييم فوراً"):
        if t_title and supabase:
          try:
            supabase.table("reviews").insert({
                "title": t_title,
                "media_type": t_type,
                "rating": t_rate,
                "review": t_rev,
                "user_email": st.session_state.user_email,
            }).execute()
            st.success("تم النشر بنجاح!")
            st.rerun()
          except Exception:
            st.error("خطأ أثناء النشر.")
        elif t_title:
          st.success("تم النشر بنجاح!")

  # --- الشاشة الرابعة: القوائم الشخصية والعامة (مطابقة للصورة الرابعة) ---
  elif st.session_state.active_tab == "lists":
    st.markdown("#### 📋 القوائم")
    list_search = st.text_input(
        "ابحث في القوائم العامة...", placeholder="ابحث هنا..."
    )

    list_tabs = st.radio(
        "فلتر القوائم",
        ["القوائم", "الأصدقاء", "الرائجة", "الأعلى تقييماً"],
        horizontal=True,
        label_visibility="collapsed",
    )
    st.markdown("---")
    st.info(
        "📁 لا توجد قوائم محفوظة بعد. استخدم زر الإضافة لإنشاء قائمتك الأولى"
        " وتنظيم أعمالك المفضلة!"
    )

  # --- الشاشة الخامسة: الحساب والإعدادات ---
  elif st.session_state.active_tab == "profile":
    st.markdown("#### 👤 الملف الشخصي")
    st.write(f"**البريد النشط:** {st.session_state.user_email}")
    st.markdown("---")
    if st.button("تسجيل الخروج من الحساب"):
      st.session_state.logged_in = False
      st.rerun()
