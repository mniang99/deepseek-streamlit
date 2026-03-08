import streamlit as st
import requests
import json
import os
import fitz  # PyMuPDF pour lire les PDF

API_KEY = os.getenv("OPENROUTER_API_KEY")

# Fonction pour extraire le texte d'un PDF
def extract_text_from_pdf(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text

# Fonction pour générer des questions avec DeepSeek
def generate_questions(note_text):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek/deepseek-chat",
        "messages": [
            {
                "role": "system",
                "content": "Tu es un générateur de quiz. Retourne uniquement un JSON avec des questions et réponses."
            },
            {
                "role": "user",
                "content": f"Génère 5 questions ouvertes avec réponses basées sur ce texte : {note_text}"
            }
        ],
        "response_format": {"type": "json_object"}
    }

    response = requests.post(url, headers=headers, json=payload)
    data = response.json()
    try:
        return json.loads(data["choices"][0]["message"]["content"])
    except Exception as e:
        st.error(f"Erreur : {e}")
        return {}

# Interface Streamlit
st.title("📘 Quiz IA à partir de mes PDF")

uploaded_file = st.file_uploader("Choisis un PDF de cours :", type="pdf")

if uploaded_file is not None:
    st.success("✅ PDF chargé avec succès.")
    text = extract_text_from_pdf(uploaded_file)

    if st.button("Générer un quiz"):
        questions = generate_questions(text)
        if questions:
            st.subheader("Quiz généré :")
            score = 0
            total = len(questions.get("questions", []))

            for i, q in enumerate(questions.get("questions", []), 1):
                st.write(f"**Q{i}:** {q['question']}")
                user_answer = st.text_input(f"Ta réponse :", key=f"ans_{i}")

                if user_answer:
                    st.write(f"✅ Réponse attendue : {q['answer']}")
                    if any(word.lower() in user_answer.lower() for word in q['answer'].split()):
                        score += 1

            st.markdown("---")
            st.write(f"🎯 Ton score : {score}/{total}")
