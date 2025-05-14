#!/usr/bin/env python3
"""
Lesson Note Generator Client for Morning Star School
"""
# Standard library imports
import os
import json
import logging
from typing import Dict, Any

# Third-party imports
from pydantic import BaseModel
from dotenv import load_dotenv
from openai import OpenAI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize environment variables
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")
if not API_KEY:
    logger.error("OPENAI_API_KEY not set in .env file")
    raise EnvironmentError("OPENAI_API_KEY not set in .env file")

# Initialize OpenAI client
client = OpenAI(api_key=API_KEY)

# Validation functions
def validate_lesson_note(lesson_note: Dict) -> bool:
    """
    Validate lesson note structure and types
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

    for phase, key in [
        ("PHASE_1", "STARTER"),
        ("PHASE_2", "MAIN"),
        ("PHASE_3", "REFLECTION")
    ]:
        if key not in lesson_note[phase]:
            logger.error(f"Missing {key} in {phase}")
            return False

    phase_2_content = lesson_note["PHASE_2"]["MAIN"]
    word_count = len(phase_2_content.split())
    if not (500 <= word_count <= 800):
        logger.warning(f"PHASE_2: MAIN content is {word_count} words, expected 500–800 words")

    return True

       # Predefined subject-specific instruction templates
SUBJECT_INSTRUCTIONS = {
    "mathematics": """
For Mathematics, include at least three LaTeX-formatted equations or formulas in PHASE_2: MAIN,
using inline \\( ... \\) or display \\[ ... \\] formats. Ensure equations are relevant to the topic
"{topic}" and appropriate for {class_level}. Include step-by-step derivations or explanations.
""",
    "french": """
Pour le français, rédigez tout en français au lieu de l'anglais. Incluez au moins deux exercices de langue dans PHASE_2 : PRINCIPAL, tels que des appariements de vocabulaire, des complétions de phrases ou des tâches de traduction. Assurez-vous que les exercices sont culturellement pertinents pour les élèves ghanéens et adaptés au niveau {class_level}. Incluez 5 à 7 mots de vocabulaire français avec leurs traductions en anglais dans MOTS_CLÉS.
""",
    "science": """
For Science, include at least two hands-on experiments or demonstrations in PHASE_2: MAIN.
Ensure activities are safe, use locally available materials, and are relevant to {topic} and
{class_level}. Include 5–7 scientific terms in KEY_WORDS.
""",
    "english": """
For English, include at least two language activities in PHASE_2: MAIN, such as writing exercises,
reading comprehension, or grammar tasks. Ensure activities are culturally relevant to Ghanaian
students and appropriate for {class_level}. Include 5–7 vocabulary words in KEY_WORDS.
"""
}

# Lesson note generation
def generate_lesson_note(
    subject: str,
    class_level: str,
    topic: str,
    week_ending: str,
    cls_size: Dict[str, int],
    duration: str,
    days: str,
    week: str,
    custom_instructions: str = None
) -> Dict:
    """
    Generate a structured lesson note using OpenAI API
    """
    # Validate input types
    if not all(isinstance(arg, str) for arg in [subject, class_level, topic, week_ending, duration, days, week]):
        raise ValueError("All string arguments must be strings")
    if not isinstance(cls_size, dict) or not all(isinstance(k, str) and isinstance(v, int) for k, v in cls_size.items()):
        raise ValueError("cls_size must be a dictionary with string keys and integer values")
    
    # Determine instructions: prioritize custom, fall back to predefined
    if custom_instructions:
        logger.info(f"Using custom instructions for {subject} - {topic}")
        subject_instructions = custom_instructions.format(topic=topic, class_level=class_level)
    else:
        subject_instructions = SUBJECT_INSTRUCTIONS.get(
            subject.lower(), ""
        ).format(topic=topic, class_level=class_level)

    # Construct prompt
    prompt = f"""
Generate a weekly lesson note for Morning Star School Ltd in **valid JSON format** with the following structure:
```json
{{
    "WEEK_ENDING": "{week_ending}",
    "DAYS": "{days}",
    "WEEK": "{week}",
    "DURATION": "{duration}",
    "SUBJECT": "{subject}",
    "STRAND": "[Insert strand number and title based on the Ghanaian curriculum for {subject}]",
    "SUBSTRAND": "[Insert substrand number and title based on the Ghanaian curriculum for {subject}]",
    "CLASS": "{class_level}",
    "CLASS_SIZE": {json.dumps(cls_size)},
    "CONTENT_STANDARD": ["[Insert standard code and learning outcome from the Ghanaian curriculum]"],
    "LEARNING_INDICATORS": ["[Insert indicator code and description from the Ghanaian curriculum]"],
    "PERFORMANCE_INDICATORS": ["[Write 2–3 clear, measurable outcomes learners should achieve]"],
    "TEACHING_LEARNING_RESOURCES": ["[List resources like charts, markers, whiteboard, etc.]"],
    "CORE_COMPETENCIES": ["[Include competencies like Creativity, Critical Thinking, Collaboration]"],
    "KEY_WORDS": ["[Include 5–7 key vocabulary terms related to {topic}]"],
    "R.P.K": "[State what learners already know that connects to {topic}]",
    "PHASE_1": {{
        "STARTER": "[Engaging activity or question related to {topic}, 50–100 words]"
    }},
    "PHASE_2": {{
"MAIN": "[Comprehensive lesson plan for {topic} (500–800 words). Include: 1. Lesson objective aligned with Ghanaian curriculum. 2. Introduction with two Ghanaian-relevant examples. 3. Step-by-step explanation with examples. 4. Guided practice with two interactive activities. 5. Independent practice with three problems. Ensure engaging, culturally relevant content for {class_level}.]"    }},
    "PHASE_3": {{
        "REFLECTION": "[Review questions, clarify mistakes, connect to real life, 100–150 words]"
    }},
    "ASSESSMENTS": "[Methods to observe participation and provide feedback, 50–100 words]",
    "HOMEWORK": "[1–2 practice problems or tasks for {topic}, 50–100 words]"
}}
```
Create a lesson note for "{subject}" on "{topic}" for "{class_level}" based on the Ghanaian curriculum.
Ensure all fields are filled, especially PHASE_2: MAIN (500–800 words). {subject_instructions}    """

    # Call OpenAI API
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a skilled Ghanaian curriculum planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.6,
            max_tokens=3000
        )
    except Exception as e:
        logger.error(f"OpenAI API error: {e}")
        raise RuntimeError(f"Failed to call OpenAI API: {e}")

    # Parse response
    message = response.choices[0].message.content.strip()
    if message.startswith("```json"):
        message = message[7:-3].strip()
    elif message.startswith("```"):
        message = message[3:-3].strip()

    try:
        safe_message = message.replace('\\', '\\\\')
        lesson_note = json.loads(safe_message)
    except json.JSONDecodeError as e:
        logger.error(f"Could not parse GPT response as JSON: {e}\nRaw response:\n{message}")
        raise ValueError(f"Invalid JSON response from OpenAI: {e}")

    # Validate lesson note
    if not validate_lesson_note(lesson_note):
        logger.error("Generated lesson note is invalid or missing required fields")
        raise ValueError("Generated lesson note is missing required fields or has incorrect types")

    logger.info("Lesson note generated successfully")
    return lesson_note

# Pydantic models for input validation
class LessonNotesData(BaseModel):
    subject: str
    class_level: str
    topic: str
    week_ending: str
    cls_size: Dict[str, int]
    duration: str
    days: str
    week: str
    custom_instructions: str = None


class InputModel(BaseModel):
    lesson_notes: LessonNotesData | Dict[str, Any] | Any  # Allow flexibility for namespace or dict
    phone_number: str
    email: str


# Motia configuration
config = {
    "type": "event",
    "name": "Lesson Notes Generator",
    "subscribes": ["generate-notes", "generate-note"],
    "emits": ["openai-response"],
    "input": InputModel.model_json_schema(),
    "flows": ["default"]
}

# Motia event handler
async def handler(input: Any, context: Any) -> Dict[str, Any]:
    """
    Handle generate-notes event, generate lesson note, and emit openai-response
    """
    # Log raw input for debugging
    logger.info('Raw input: %s', input)
    logger.info('Input type: %s', type(input))

    def to_dict(obj):
        """
        Convert object to dict if it has __dict__ attribute
        """

        if hasattr(obj, '__dict__'):
            return {k: to_dict(v) for k, v in vars(obj).items()}
        elif isinstance(obj, dict):
            return {k: to_dict(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [to_dict(item) for item in obj]
        else:
            return obj
            


    # Convert input to dict if SimpleNamespace
    try:
        input_dict = to_dict(input)
        logger.info('Converted input dict: %s', input_dict)
    except Exception as e:
        context.logger.error(f"Failed to convert input to dict: {e}")
        return {
            'status': 400,
            'body': {'error': f"Failed to process input: {str(e)}"}
        }


    # Validate input
    try:
        validated_input = InputModel.model_validate(input_dict)
        lesson_notes = validated_input.lesson_notes
        logger.info('Validated lesson_notes: %s', lesson_notes)
    except Exception as e:
        context.logger.error(f"Input validation failed: {e}")
        return {
            'status': 400,
            'body': {'error': f"Invalid input format: {str(e)}"}
        }

    # Check for empty lesson_notes
    if not lesson_notes or (isinstance(lesson_notes, (dict, object)) and not any(vars(lesson_notes) if hasattr(lesson_notes, '__dict__') else lesson_notes)):
        context.logger.error("lesson_notes is empty or invalid")
        return {
            'status': 400,
            'body': {'error': "lesson_notes is empty or invalid"}
        }

    # Convert lesson_notes to LessonNotesData if it's a dict
    try:
        if isinstance(lesson_notes, dict):
            lesson_notes = LessonNotesData(**lesson_notes)
        elif not isinstance(lesson_notes, LessonNotesData):
            lesson_notes = LessonNotesData(**vars(lesson_notes))
        context.logger.info('Final lesson_notes data: %s', lesson_notes)
    except Exception as e:
        context.logger.error(f"Failed to convert lesson_notes to LessonNotesData: {e}")
        return {
            'status': 400,
            'body': {'error': f"Invalid lesson_notes format: {str(e)}"}
        }

    # Generate lesson note
    try:
        lesson_note = generate_lesson_note(
            subject=lesson_notes.subject,
            class_level=lesson_notes.class_level,
            topic=lesson_notes.topic,
            week_ending=lesson_notes.week_ending,
            cls_size=lesson_notes.cls_size,
            duration=lesson_notes.duration,
            days=lesson_notes.days,
            week=lesson_notes.week
        )
    except Exception as e:
        context.logger.error(f"Failed to generate lesson note: {e}")
        return {
            'status': 500,
            'body': {'error': f"Failed to generate lesson note: {str(e)}"}
        }

    # Emit lesson note
    await context.emit({
        "topic": "openai-response",
        "data":{ "lesson_note": lesson_note, "user_phone": validated_input.phone_number, "email": validated_input.email},
    })

    return {
        'status': 200,
        'body': {'message': 'Lesson note generated and emitted'}
    }