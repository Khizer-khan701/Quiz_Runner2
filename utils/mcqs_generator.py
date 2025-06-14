import os
import json
from dotenv import load_dotenv
import openai  # Correct import for openai>=1.0.0

# Load environment variables from .env
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


def generate_question_answer(text_chunk, retries=2):
    prompt = f"""
Generate one multiple choice question based on the following text:

\"\"\"{text_chunk}\"\"\"

Return the response ONLY as a JSON object like this:

{{
  "question": "Your question here",
  "options": ["Option A", "Option B", "Option C", "Option D"],
  "answer": "Correct answer text from options"
}}

No explanation. Only JSON.
"""

    for attempt in range(retries):
        try:
            print(f"\n[Attempt {attempt+1}] Sending chunk to GPT:\n{text_chunk[:100]}...\n")

            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )

            content = response.choices[0].message.content.strip()
            print(f"[Attempt {attempt+1}] GPT Response:\n{repr(content)}\n")

            cleaned = (
                content
                .replace("“", "\"")
                .replace("”", "\"")
                .replace("‘", "'")
                .replace("’", "'")
                .strip("```json")
                .strip("```")
                .strip()
            )

            parsed = json.loads(cleaned)
            return parsed

        except json.JSONDecodeError as e:
            print("JSON Decode Error:", e)
        except Exception as e:
            print("OpenAI API Error:", e)

    return {
        "question": "Could not generate question.",
        "options": ["A", "B", "C", "D"],
        "answer": "A"
    }


def generate_mcqs(text, num_questions=3):
    print("\n--- Extracted Text Preview ---\n")
    print(text[:500], "\n------------------------------\n")

    sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 20]

    if not sentences:
        return [{
            "question": "No valid content found in PDF to generate questions.",
            "options": ["A", "B", "C", "D"],
            "answer": "A"
        }]

    chunks = []
    chunk = ""
    for sentence in sentences:
        if len(chunk) + len(sentence) < 500:
            chunk += sentence + ". "
        else:
            chunks.append(chunk.strip())
            chunk = sentence + ". "
    if chunk:
        chunks.append(chunk.strip())

    mcqs = []
    for i, chunk in enumerate(chunks[:num_questions]):
        print(f"\nGenerating Q{i+1} from chunk...")
        qa = generate_question_answer(chunk)
        mcqs.append(qa)

    return mcqs
