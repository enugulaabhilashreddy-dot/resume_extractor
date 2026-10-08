import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq
from pydantic import BaseModel, Field
from langfuse import get_client


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_ROOT / ".env")


# ============================================================
# CLIENTS
# ============================================================

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

langfuse = get_client()


# ============================================================
# PYDANTIC MODELS
# ============================================================

class FieldEvaluation(BaseModel):
    correct: bool
    score: float
    reason: str


class EvaluationResult(BaseModel):
    name: FieldEvaluation
    email: FieldEvaluation
    phone: FieldEvaluation
    skills: FieldEvaluation
    years_of_experience: FieldEvaluation
    qualifications: FieldEvaluation
    overall_score: float


# ============================================================
# EVALUATION FUNCTION
# ============================================================

def evaluate_resume(
    resume_text: str,
    extracted_data: dict
) -> EvaluationResult:

    extracted_json = json.dumps(
        extracted_data,
        indent=2,
        ensure_ascii=False
    )

    prompt = f"""
You are a resume information extraction evaluator.

Compare the extracted information with the original resume.

Evaluate ONLY these six fields:

1. name
2. email
3. phone
4. skills
5. years_of_experience
6. qualifications

Rules:

- Use ONLY information present in the original resume.
- Do not invent information.
- If the resume does not contain email or phone,
  "Not available" is correct.
- For skills, give partial credit if some skills are missing.
- For years_of_experience, allow small rounding differences.
- For qualifications, equivalent wording is acceptable.
- Score each field from 0.0 to 1.0.
- 1.0 = completely correct.
- 0.5 = partially correct.
- 0.0 = incorrect.
- Give a short reason for every score.
- overall_score must be the average of the six field scores.

Return ONLY valid JSON.

Expected JSON format:

{{
    "name": {{
        "correct": true,
        "score": 1.0,
        "reason": "..."
    }},
    "email": {{
        "correct": true,
        "score": 1.0,
        "reason": "..."
    }},
    "phone": {{
        "correct": true,
        "score": 1.0,
        "reason": "..."
    }},
    "skills": {{
        "correct": true,
        "score": 1.0,
        "reason": "..."
    }},
    "years_of_experience": {{
        "correct": true,
        "score": 1.0,
        "reason": "..."
    }},
    "qualifications": {{
        "correct": true,
        "score": 1.0,
        "reason": "..."
    }},
    "overall_score": 1.0
}}

ORIGINAL RESUME:
----------------
{resume_text}

EXTRACTED INFORMATION:
----------------
{extracted_json}
"""

    # ========================================================
    # LANGFUSE TRACE
    # ========================================================

    with langfuse.start_as_current_observation(
        as_type="span",
        name="resume-extraction-evaluation"
    ) as span:

        # CALL GROQ JUDGE

        response = groq_client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0,
            max_tokens=2000,
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content

        if not result:
            raise ValueError(
                "Groq returned an empty response"
            )

        # PARSE RESULT

        data = json.loads(result)

        evaluation = EvaluationResult.model_validate(data)


        # SEND FIELD SCORES TO LANGFUSE
       

        span.score(
            name="name_accuracy",
            value=float(evaluation.name.score),
            data_type="NUMERIC"
        )

        span.score(
            name="email_accuracy",
            value=float(evaluation.email.score),
            data_type="NUMERIC"
        )

        span.score(
            name="phone_accuracy",
            value=float(evaluation.phone.score),
            data_type="NUMERIC"
        )

        span.score(
            name="skills_accuracy",
            value=float(evaluation.skills.score),
            data_type="NUMERIC"
        )

        span.score(
            name="experience_accuracy",
            value=float(
                evaluation.years_of_experience.score
            ),
            data_type="NUMERIC"
        )

        span.score(
            name="qualification_accuracy",
            value=float(
                evaluation.qualifications.score
            ),
            data_type="NUMERIC"
        )

        span.score_trace(
            name="overall_score",
            value=float(evaluation.overall_score),
            data_type="NUMERIC"
        )

        return evaluation

# TEST ONE RESUME

if __name__ == "__main__":

    print("=" * 60)
    print("TESTING LANGFUSE RESUME EVALUATOR")
    print("=" * 60)

    # Resume to test
    resume_id = (
        "003ada45-7271-4e1d-8d61-6f5b5542b3d7"
    )

    resume_file = (
        PROJECT_ROOT
        / "data"
        / "english_resumes"
        / f"{resume_id}.txt"
    )

    extraction_file = (
        PROJECT_ROOT
        / "data"
        / "extractions"
        / f"{resume_id}.json"
    )

    print(f"Resume: {resume_id}")

    # CHECK FILES

    if not resume_file.exists():
        raise FileNotFoundError(
            f"Resume file not found: {resume_file}"
        )

    if not extraction_file.exists():
        raise FileNotFoundError(
            f"Extraction file not found: {extraction_file}"
        )
    # READ ORIGINAL RESUME

    resume_text = resume_file.read_text(
        encoding="utf-8",
        errors="ignore"
    )
    # READ EXTRACTED JSON
   

    extracted_data = json.loads(
        extraction_file.read_text(
            encoding="utf-8"
        )
    )

    print()
    print("Running evaluation...")

  
    result = evaluate_resume(
        resume_text,
        extracted_data
    )

    print()
    print("EVALUATION RESULT")


    print(
        result.model_dump_json(indent=2)
    )
    langfuse.flush()

    print()
    print("Evaluation sent to Langfuse")
    