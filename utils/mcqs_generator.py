import random
import os
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import openai

# Load environment variables from .env
load_dotenv()

# Set OpenAI API Key securely
try:
    openai.api_key = os.environ["OPENAI_API_KEY"]
except KeyError:
    raise ValueError("OPENAI_API_KEY not set in environment. Please set it in a .env file.")

OPENAI_MODEL = "gpt-3.5-turbo"

def call_question_generation_pipeline(text_chunks):
    questions = []
    for chunk in text_chunks:
        prompt = f"Based on the following text, generate one concise question:\n\nText: {chunk}\n\nQuestion:"
        try:
            response = openai.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that generates questions."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=64,
                temperature=0.7,
                n=1
            )
            question = response.choices[0].message.content.strip()
            questions.append(question)
        except Exception as e:
            print(f"Error generating question: {e}")
            questions.append("Question not generated")
    return questions

def call_question_answering_pipeline(question, context):
    prompt = f"Answer the following question based on the context below. If the answer is not directly available, say 'Not found'.\n\nContext: {context}\n\nQuestion: {question}\n\nAnswer:"
    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "You extract answers from context."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=64,
            temperature=0.0,
            n=1
        )
        answer = response.choices[0].message.content.strip()
        return answer
    except Exception as e:
        print(f"Error answering question: {e}")
        return "Not found"

def generate_mcqs(text, num_questions=5):
    questions = []
    sentences = [sent.strip() for sent in text.split('.') if sent.strip()]
    random.shuffle(sentences)
    selected_chunks = sentences[:num_questions]

    generated_questions = call_question_generation_pipeline(selected_chunks)

    def extract_answer(q):
        return call_question_answering_pipeline(q, text)

    with ThreadPoolExecutor() as executor:
        answers = list(executor.map(extract_answer, generated_questions))

    for question, ans in zip(generated_questions, answers):
        distractors = [f"{ans} option A", f"{ans} option B", f"{ans} option C"]
        options = [ans] + distractors
        random.shuffle(options)
        questions.append({
            "question": question,
            "answer": ans,
            "options": options
        })

    return questions

# Example usage
if __name__ == "__main__":
    sample_text = """
    The Amazon rainforest is the largest rainforest in the world, covering an area of about 5.5 million square kilometers. It spans across nine countries, with the majority of it located in Brazil. The rainforest is home to an incredible diversity of plant and animal species, many of which are found nowhere else on Earth. It plays a crucial role in regulating the Earth's climate by absorbing vast amounts of carbon dioxide. Deforestation, primarily due to agriculture and logging, poses a significant threat to this vital ecosystem. Efforts are being made to conserve the Amazon and its unique biodiversity.
    """

    print("Generating MCQs...\n")
    mcqs = generate_mcqs(sample_text, num_questions=3)

    for i, mcq in enumerate(mcqs):
        print(f"\n--- MCQ {i+1} ---")
        print(f"Q: {mcq['question']}")
        for idx, option in enumerate(mcq["options"]):
            print(f"  {chr(65 + idx)}. {option}")
        print(f"✅ Correct Answer: {mcq['answer']}")
