import random
import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import openai
import streamlit as st

# Load environment variables from .env
load_dotenv()

# Set OpenAI API Key securely
try:
    openai.api_key = st.secrets["OPENAI_API_KEY"]
except KeyError:
    raise ValueError("OPENAI_API_KEY not set in environment. Please set it in a .env file.")

OPENAI_MODEL = "gpt-3.5-turbo"

def generate_question_answer(chunk):
    prompt = f"""
Based on the following text, generate one multiple choice question. The question should have one correct answer and three incorrect but realistic distractors.

Return the response in the following JSON format without any explanation:

{{
  "question": "<insert question>",
  "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
  "answer": "<insert correct option text exactly as it appears in the options list>"
}}

Text:
\"\"\"
{chunk}
\"\"\"
"""
    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You are an assistant that generates educational multiple choice questions."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=512
        )
        content = response.choices[0].message.content.strip()
        import json
        return json.loads(content)
    except Exception as e:
        print(f"Error generating MCQ: {e}")
        return {
            "question": "Could not generate question.",
            "options": ["A", "B", "C", "D"],
            "answer": "A"
        }

def generate_mcqs(text, num_questions=5):
    questions = []
    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 30]
    random.shuffle(sentences)
    selected_chunks = sentences[:num_questions]

    with ThreadPoolExecutor() as executor:
        results = list(executor.map(generate_question_answer, selected_chunks))

    for result in results:
        question = result.get("question", "Missing question")
        options = result.get("options", ["A", "B", "C", "D"])
        answer_raw = result.get("answer", "")

        # Determine if the answer is a letter (A/B/C/D) or the actual answer text
        if len(answer_raw.strip()) == 1 and answer_raw.upper() in "ABCD":
            answer_index = ord(answer_raw.upper()) - 65
            correct_answer = options[answer_index] if answer_index < len(options) else options[0]
        else:
            # fallback if answer is text — match it to options (case-insensitive)
            match = [opt for opt in options if opt.strip().lower() == answer_raw.strip().lower()]
            correct_answer = match[0] if match else options[0]  # fallback to first

        questions.append({
            "question": question,
            "options": options,
            "answer": correct_answer
        })

    return questions

# Example usage
if __name__ == "__main__":
    sample_text = """
    The Amazon rainforest is the largest rainforest in the world, covering about 5.5 million square kilometers.
    It spans across nine countries, with most of it in Brazil. The rainforest has rich biodiversity, with many
    unique species. It plays a key role in regulating the Earth's climate by absorbing carbon dioxide.
    Deforestation due to farming and logging threatens this ecosystem. Conservation efforts aim to protect it.
    """

    print("Generating MCQs...\n")
    mcqs = generate_mcqs(sample_text, num_questions=3)

    for i, mcq in enumerate(mcqs):
        print(f"\n--- MCQ {i+1} ---")
        print(f"Q: {mcq['question']}")
        for idx, option in enumerate(mcq["options"]):
            print(f"  {chr(65 + idx)}. {option}")
        print(f"✅ Correct Answer: {mcq['answer']}")
