import streamlit as st
from openai import OpenAI
import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
from io import BytesIO

# ---------------- TEST MODE ----------------
TEST_MODE = True  # 🔥 True = ohne API testen | False = echte KI

# ---------------- CONFIG ----------------
st.set_page_config(
    page_title="Salon Content AI Pro",
    page_icon="✂️",
    layout="centered"
)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- MOBILE CSS ----------------
st.markdown("""
<style>
div.stButton > button {
    width: 100%;
    height: 60px;
    font-size: 18px;
    border-radius: 12px;
}
input, textarea {
    font-size: 18px !important;
}
.block-container {
    padding-top: 1rem;
    padding-bottom: 2rem;
}
img {
    border-radius: 12px;
}
.stDownloadButton button {
    width: 100%;
    height: 50px;
    font-size: 16px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- UI ----------------
st.title("✂️ Salon Content AI Pro")
st.markdown("Erstelle Instagram Posts mit Branding & Design")

# ---------------- INPUTS ----------------
st.header("📋 Business Infos")

business_name = st.text_input("🏪 Salon Name")
location = st.text_input("📍 Stadt")
service = st.text_input("💇 Service")

style = st.selectbox(
    "🎨 Stil",
    ["Modern", "Luxus", "Minimalistisch", "Trendy"]
)

template = st.selectbox(
    "🖼️ Design",
    ["Luxury Dark", "Minimal Clean", "Bold Promo", "Soft Beauty"]
)

brand_color = st.color_picker("🎨 Markenfarbe", "#000000")

logo_file = st.file_uploader("📤 Logo (optional)", type=["png", "jpg"])

num_posts = st.slider("🧠 Anzahl Posts", 1, 6, 3)

# ---------------- FUNCTIONS ----------------

def generate_text(prompt):
    if TEST_MODE:
        return f"""✨ Beispiel Post für {business_name}

Perfekter Look mit {service} ✂️  
Jetzt Termin sichern!

#friseur #{location} #beauty #style"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content


def generate_image():
    if TEST_MODE:
        return "https://via.placeholder.com/1024"

    image_response = client.images.generate(
        model="gpt-image-1",
        prompt="modern hair salon interior, aesthetic, instagram style, no text",
        size="1024x1024"
    )
    return image_response.data[0].url


def apply_template(base_image, template, brand_color, business_name, service):
    width, height = base_image.size
    draw = ImageDraw.Draw(base_image)

    try:
        font_title = ImageFont.truetype("arial.ttf", 48)
        font_sub = ImageFont.truetype("arial.ttf", 28)
    except:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()

    r = int(brand_color[1:3], 16)
    g = int(brand_color[3:5], 16)
    b = int(brand_color[5:7], 16)

    if template == "Luxury Dark":
        overlay = Image.new("RGBA", base_image.size, (0, 0, 0, 140))
        base_image = Image.alpha_composite(base_image, overlay)

        draw.text((40, 40), business_name, fill="white", font=font_title)
        draw.text((40, 120), service, fill="white", font=font_sub)

    elif template == "Minimal Clean":
        enhancer = ImageEnhance.Brightness(base_image)
        base_image = enhancer.enhance(1.2)

        draw.text((40, height - 100), service, fill="black", font=font_title)

    elif template == "Bold Promo":
        overlay = Image.new("RGBA", base_image.size, (r, g, b, 120))
        base_image = Image.alpha_composite(base_image, overlay)

        draw.text((40, 40), "ANGEBOT", fill="white", font=font_title)
        draw.text((40, 140), service.upper(), fill="white", font=font_title)

    elif template == "Soft Beauty":
        overlay = Image.new("RGBA", base_image.size, (255, 182, 193, 80))
        base_image = Image.alpha_composite(base_image, overlay)

        draw.text((40, height - 140), service, fill="white", font=font_title)

    return base_image

# ---------------- MAIN ----------------

if st.button("✨ Posts generieren"):

    if not business_name or not service:
        st.error("Bitte mindestens Salon Name und Service eingeben")
        st.stop()

    posts = []

    with st.spinner("Erstelle Content..."):

        try:
            image_url = generate_image()
            image_data = requests.get(image_url).content

            for i in range(num_posts):

                prompt = f"""
                Instagram Post für Friseur:
                Name: {business_name}
                Stadt: {location}
                Service: {service}
                Stil: {style}
                """

                text = generate_text(prompt)

                base_image = Image.open(BytesIO(image_data)).convert("RGBA")

                final_image = apply_template(
                    base_image.copy(),
                    template,
                    brand_color,
                    business_name,
                    service
                )

                if logo_file:
                    logo = Image.open(logo_file).convert("RGBA")
                    logo.thumbnail((120, 120))
                    final_image.paste(logo, (900, 20), logo)

                posts.append((final_image, text))

        except Exception as e:
            st.error(f"Fehler: {e}")
            st.stop()

    st.success("✅ Fertig!")

    # ---------------- GRID ----------------
    st.subheader("📱 Feed Vorschau")

    cols = st.columns(2)

    for i, (img, txt) in enumerate(posts):
        with cols[i % 2]:
            st.image(img)

    # ---------------- DETAIL ----------------
    st.subheader("📄 Einzelne Posts")

    for i, (img, txt) in enumerate(posts):
        st.markdown(f"### Post {i+1}")

        st.image(img)

        buf = BytesIO()
        img.save(buf, format="PNG")

        st.download_button(
            f"📥 Download Post {i+1}",
            data=buf.getvalue(),
            file_name=f"post_{i+1}.png"
        )

        st.code(txt)

    # ---------------- UX GUIDE ----------------
    st.info("📲 So nutzen:\n1. Bild herunterladen\n2. Text kopieren\n3. Auf Instagram posten")
