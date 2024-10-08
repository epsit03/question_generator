import google.generativeai as palm
import openpyxl
import json
import re

def parse_unstructured_data(data):
    questions = []
    current_question = None

    for line in data.strip().split('\n'):
        line = line.strip()

        question_match = re.match(r'^\d+\.\s+(.*)$', line)
        if question_match:
            if current_question:
                questions.append(current_question)
            current_question = {
                "question": question_match.group(1),
                "options": [],
                "answer": None
            }

        option_match = re.match(r'^\(\w\)\s+(.*)$', line)
        if option_match:
            if current_question:
                current_question["options"].append(option_match.group(1))

        if "answer" in line.lower():
            answer_match = re.match(r'answer\s*:\s*(\w+)', line, re.IGNORECASE)
            if answer_match and current_question:
                current_question["answer"] = answer_match.group(1)




    if current_question:
        questions.append(current_question)

    return questions

def generate_prompt(num_of_que, topic, difficulty, domain):
    prompt = f"Create {num_of_que} single-choice questions based on the topic of {topic}. Each question should have four answer options (A, B, C, D), with its correct answer clearly mentioned in this format answer: A. The questions should be tailored to a difficulty level of {difficulty}. Ensure that the questions are suitable for Btech students and cover various key aspects of the {domain} domain. Give output in the Unstructured Format only."
    #prompt = "Hei how are you. Reply to this."
    API_KEY = "AIzaSyC-aekPBYfN3AWmEIXjXZAtOLvXF7loHjg"  # Replace with your PaLM API Key
    palm.configure(api_key=API_KEY)

    model_id = "models/text-bison-001"

    try:
        completion = palm.generate_text(
            model=model_id,
            prompt=prompt,
            temperature=0.6,
            max_output_tokens=5000,
            candidate_count=1
        )
        outputs = [output['output'] for output in completion.candidates]
        return outputs[0] if outputs else None
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

def save_to_excel(structured_data, topic):
    questions_list = structured_data

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = f"{topic} Questions"

    headers = ["Question", "Option 1", "Option 2", "Option 3", "Option 4", "Answer"]
    ws.append(headers)

    for q in questions_list:
        row = [
            q["question"],
            q["options"][0] if len(q["options"]) > 0 else '',
            q["options"][1] if len(q["options"]) > 1 else '',
            q["options"][2] if len(q["options"]) > 2 else '',
            q["options"][3] if len(q["options"]) > 3 else '',
            q["answer"]
        ]
        ws.append(row)

    wb.save(f"{topic}.xlsx")
    print(f"Questions have been successfully saved to '{topic}.xlsx'.")

def main():
    num_of_que = int(input("Enter the desired number of questions: (Maximum 20): " ))
    domain = input("Enter the Domain: ")
    topic = input("Enter the sub-domain: ")
    difficulty = input("Enter the level of difficulty: ")

    unstructured_data = generate_prompt(num_of_que, topic, difficulty, domain)
    if unstructured_data:
        print("Generated data:", unstructured_data)
        structured_data = parse_unstructured_data(unstructured_data)
        save_to_excel(structured_data, topic)
    else:
        print("No data received from the API.")

if __name__ == "__main__":
    main()
