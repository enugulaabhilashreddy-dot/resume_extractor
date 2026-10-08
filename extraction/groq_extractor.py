import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class ResumeInfo(BaseModel):
    name: str = "Not available"
    email: str = "Not available"
    phone: str = "Not available"
    skills: list[str] = Field(default_factory=list)
    years_of_experience: float | None = None
    qualifications: list[str] = Field(default_factory=list)

def clean_response(result: str) -> str:
    result = result.strip()

    if result.startswith("```json"):
        result = result[7:]
    elif result.startswith("```"):
        result = result[3:]

    if result.endswith("```"):
        result = result[:-3]

    return result.strip()


def extract_resume(resume_text: str) -> ResumeInfo:

    prompt = f"""
Extract information from the resume below.

Return ONLY valid JSON.

Extract ONLY these fields:

1. name
2. email
3. phone
4. skills
5. years_of_experience
6. qualifications

Rules:
- Extract the actual information from the resume whenever it is present.
- Do not invent, guess, or create information.
- If name is not found, return "Not available".
- If email is not found, return "Not available".
- If phone is not found, return "Not available".
- If skills are not found, return [].
- If qualifications are not found, return [].
- If years of experience is found, return it as a number.
- If it cannot be determined, return null.
- Keep the extracted information concise.

JSON format:

{{
    "name": null,
    "email": null,
    "phone": null,
    "skills": [],
    "years_of_experience": null,
    "qualifications": []
}}

Resume:
{resume_text}
"""

    max_retries = 3

    for attempt in range(1, max_retries + 1):

        try:
            print(f"  Groq attempt {attempt}/{max_retries}")

            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            result = response.choices[0].message.content

            if not result:
                raise ValueError("Groq returned an empty response")

            result = clean_response(result)

            data = json.loads(result)

            return ResumeInfo.model_validate(data)

        except Exception as e:

            print("  Attempt failed")
            print(f"  Error type: {type(e).__name__}")
            print(f"  Error: {e}")

            if attempt == max_retries:
                print("  Maximum retries reached.")
                raise
if __name__ == "__main__":
    input_folder = Path("../data/english_resumes")

    resume_files = sorted(input_folder.glob("*.txt"))

    if not resume_files:
        print("No English resume files found.")
    else:
        resume_file = resume_files[0]

     
        print("TESTING GROQ RESUME EXTRACTION")
        print(f"Resume: {resume_file.name}")

        text = resume_file.read_text(encoding="utf-8")

        result = extract_resume(text)

        print("\nEXTRACTED INFORMATION")
  
        print(result.model_dump_json(indent=2))


        