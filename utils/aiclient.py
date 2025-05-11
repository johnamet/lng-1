#!/usr/bin/env python3
"""
Lesson Note Generator Client for Morning Star School
"""

import os
import json
import logging
from typing import Dict
from dotenv import load_dotenv
from openai import OpenAI
from template import create_lesson_notes_template

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    logger.error("OPENAI_API_KEY not set in .env file")
    raise EnvironmentError("OPENAI_API_KEY not set in .env file")

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

def validate_lesson_note(lesson_note: Dict) -> bool:
    """
    Validate that the lesson note contains all required fields with correct types
    """
    required_fields = {
        "WEEK_ENDING": str,
        "DAYS": str,
        "WEEK": str,
        "DURATION": str,
        "SUBJECT": str,
        "STRAND": str,
        "SUBSTRAND": str,
        "CLASS": str,
        "CLASS_SIZE": dict,
        "CONTENT_STANDARD": list,
        "LEARNING_INDICATORS": list,
        "PERFORMANCE_INDICATORS": list,
        "TEACHING_LEARNING_RESOURCES": list,
        "CORE_COMPETENCIES": list,
        "KEY_WORDS": list,
        "R.P.K": str,
        "PHASE_1": dict,
        "PHASE_2": dict,
        "PHASE_3": dict,
        "ASSESSMENTS": str,
        "HOMEWORK": str
    }

    for field, expected_type in required_fields.items():
        if field not in lesson_note:
            logger.error(f"Missing required field: {field}")
            return False
        if not isinstance(lesson_note[field], expected_type):
            logger.error(f"Field {field} has incorrect type: expected {expected_type}, got {type(lesson_note[field])}")
            return False
    
    # Validate nested phase fields
    for phase, key in [
        ("PHASE_1", "STARTER"),
        ("PHASE_2", "MAIN"),
        ("PHASE_3", "REFLECTION")
    ]:
        if key not in lesson_note[phase]:
            logger.error(f"Missing {key} in {phase}")
            return False

    # Validate PHASE_2 content length (approximate word count)
    phase_2_content = lesson_note["PHASE_2"]["MAIN"]
    word_count = len(phase_2_content.split())
    if not (500 <= word_count <= 800):
        logger.warning(f"PHASE_2: MAIN content is {word_count} words, expected 500–800 words")
        # Not failing validation, just logging a warning

    return True

def generate_lesson_note(subject: str, class_level: str, topic: str,
                         week_ending: str, cls_size: Dict[str, int],
                         duration: str, days: str, week: str) -> Dict:
    """
    Calls OpenAI API to generate a structured lesson note for Morning Star School
    """
    # Input validation
    if not all(isinstance(arg, str) for arg in [subject, class_level, topic, week_ending, duration, days, week]):
        raise ValueError("All string arguments must be strings")
    if not isinstance(cls_size, dict) or not all(isinstance(k, str) and isinstance(v, int) for k, v in cls_size.items()):
        raise ValueError("cls_size must be a dictionary with string keys and integer values")

    prompt = f"""
Generate a weekly lesson note for Morning Star School Ltd in **valid JSON format** with the following structure:

```json
{{
    "WEEK_ENDING": "{week_ending}",
    "DAYS": "{days}",
    "WEEK": "{week}",
    "DURATION": "{duration}",
    "SUBJECT": "{subject}",
    "STRAND": "[Insert strand number and title based on the Ghanaian curriculum for {subject} i.e. ( do a deep search GES core curriculum for the strand)]",
    "SUBSTRAND": "[Insert substrand number and title based on the Ghanaian curriculum for {subject} i.e. ( do a deep search GES core curriculum for the substrand)]",
    "CLASS": "{class_level}",
    "CLASS_SIZE": {json.dumps(cls_size)},
    "CONTENT_STANDARD": ["[Insert appropriate standard code and learning outcome from the Ghanaian curriculum]"],
    "LEARNING_INDICATORS": ["[Insert indicator code and description from the Ghanaian curriculum]"],
    "PERFORMANCE_INDICATORS": ["[Write 2–3 clear, measurable outcomes learners should achieve by the end of the lesson]"],
    "TEACHING_LEARNING_RESOURCES": ["[List resources such as charts, markers, whiteboard, real-life objects, etc.]"],
    "CORE_COMPETENCIES": ["[Include relevant competencies like Creativity and Innovation (CI), Critical Thinking (CP), Collaboration (CC)]"],
    "KEY_WORDS": ["[Include 5–7 key vocabulary terms related to {topic}]"],
    "R.P.K": "[State what learners already know that connects to {topic}]",
    "PHASE_1": {{
        "STARTER": "[Begin with an engaging activity, question, or discussion related to {topic}, 50–100 words]"
    }},
    "PHASE_2": {{
        "MAIN": "[Provide a comprehensive lesson plan for {topic} (500–800 words). Include: 1. Clear lesson objective aligned with the Ghanaian curriculum. 2. Detailed introduction of {topic} using at least two real-life examples relevant to Ghanaian students. 3. Step-by-step explanation and modeling of {topic} with clear examples. 4. Guided practice with at least two interactive activities or problems. 5. Independent practice with at least three problems for students to solve. Ensure the content is engaging, culturally relevant, and suitable for {class_level} students.]"
    }},
    "PHASE_3": {{
        "REFLECTION": "[Ask review questions, clarify common mistakes, connect {topic} to real life or other subjects, 100–150 words]"
    }},
    "ASSESSMENTS": "[Describe methods to observe participation, check classwork, and provide feedback, 50–100 words]",
    "HOMEWORK": "[Provide 1–2 practice problems or tasks connected to {topic}, 50–100 words]"
}}
```

Create a complete lesson note for the subject "{subject}" on the topic "{topic}" for class "{class_level}" based on the Ghanaian curriculum. Ensure all fields are filled with appropriate, detailed content, especially PHASE_2: MAIN, which must be 500–800 words and include all specified components.
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled Ghanaian curriculum planner familiar with the Ghanaian education system."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=3000  # Increased to accommodate longer PHASE_2 content
        )
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise RuntimeError(f"Failed to call OpenAI API: {e}")

    # Extract and parse response
    message = response.choices[0].message.content.strip()

    try:
        # Remove code block markers if present
        if message.startswith("```json"):
            message = message[7:-3].strip()
        elif message.startswith("```"):
            message = message[3:-3].strip()
        lesson_note = json.loads(message)
    except json.JSONDecodeError as e:
        logger.error(f"Could not parse GPT response as JSON: {e}\nRaw response:\n{message}")
        raise ValueError(f"Invalid JSON response from OpenAI: {e}")

    # Validate the lesson note
    if not validate_lesson_note(lesson_note):
        logger.error("Generated lesson note is invalid or missing required fields")
        raise ValueError("Generated lesson note is missing required fields or has incorrect types")

    logger.info("Lesson note generated successfully")
    return lesson_note

def main():
    """
    Example usage of the lesson note generator
    """
    # Example inputs
    subject = "Mathematics"
    class_level = "Basic Eight"
    topic = "Perfect Squares"
    week_ending = "2nd May, 2025"
    week = "1"
    duration = "4 periods per class"
    class_size = {"A": 28, "B": 28, "C": 28}
    days = "Monday - Friday"

    try:
        lesson_note = generate_lesson_note(
            subject=subject,
            class_level=class_level,
            topic=topic,
            week_ending=week_ending,
            cls_size=class_size,
            duration=duration,
            days=days,
            week=week
        )
        create_lesson_notes_template(lesson_note)
        logger.info("Lesson note document created successfully")
    except Exception as e:
        logger.error(f"Error generating lesson note: {e}")
        raise

if __name__ == "__main__":
    main()