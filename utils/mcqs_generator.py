import random
from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor

# Load Hugging Face pipelines
qg_pipeline = pipeline("text2text-generation", model="valhalla/t5-small-qg-hl")
qa_pipeline = pipeline("question-answering", model="deepset/roberta-base-squad2")

def call_question_generation_pipeline(text_chunks):
    formatted_inputs = [f"generate question: {chunk}" for chunk in text_chunks]
    results = qg_pipeline(formatted_inputs, max_length=64, do_sample=False)
    questions = [item["generated_text"] for item in results]
    return questions

def call_question_answering_pipeline(question, context):
    result = qa_pipeline(question=question, context=context)
    return result.get("answer", "")

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
