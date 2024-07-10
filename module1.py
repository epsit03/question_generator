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

def generate_prompt():
    prompt = "Generate 10 single-choice questions suitable for Btech students at an easy difficulty level, focusing on chemical technology in the chemical domain in the Unstructured Format only."
    
    API_KEY = "AIzaSyAfWJvudjvBwaauVFVt-TaqFHzabYpV7sU"  # Replace with your PaLM API Key
    palm.configure(api_key=API_KEY)

    model_id = "models/text-bison-001"

    try:
        completion = palm.generate_text(
            model=model_id,
            prompt=prompt,
            temperature=0.8,
            max_output_tokens=5000,
            candidate_count=1
        )
        outputs = [output['output'] for output in completion.candidates]
        return outputs[0] if outputs else None
    except Exception as e:
        print(f"Error generating text: {e}")
        return None

def save_to_excel(structured_data):
    questions_list = structured_data
    
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Chemical Technology Questions"
    
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
    
    wb.save("Chemical_Domain_Easy_Questions.xlsx")
    print("Questions have been successfully saved to 'Chemical_Domain_Easy_Questions.xlsx'.")

def main():
    unstructured_data = generate_prompt()
    if unstructured_data:
        print("Generated data:", unstructured_data)
        structured_data = parse_unstructured_data(unstructured_data)
        save_to_excel(structured_data)
    else:
        print("No data received from the API.")

if __name__ == "__main__":
    main()
