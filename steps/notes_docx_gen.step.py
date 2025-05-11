#!/usr/bin/env python3
"""
Module to generate lesson notes template for Morning Star School
"""
# Standard library imports
import os
import re
import logging
from typing import Dict, Any

# Third-party imports
import warnings
from pydantic import BaseModel
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn
from markdown2 import markdown
from bs4 import BeautifulSoup
# Suppress deprecated style_id warning
warnings.filterwarnings("ignore", category=UserWarning, module="docx.styles.styles")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Helper functions for DOCX formatting
def set_cell_text(cell, text, bold=False, font_size=12, align='center'):
    """
    Helper to insert styled text into a cell
    """
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    p = cell.paragraphs[0]
    p.alignment = getattr(WD_ALIGN_PARAGRAPH, align.upper())
    run = p.add_run(str(text))  # Convert to string to handle non-string inputs
    run.font.size = Pt(font_size)
    run.font.name = 'Times New Roman'
    run.bold = bold
    run._element.rPr.rFonts.set(qn('w:eastAsia'), 'Times New Roman')

def apply_html_styles(cell, html_content):
    """
    Parse HTML content and apply equivalent Word styles to a cell
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    def process_node(node, paragraph, run_bold=False, run_italic=False, run_underline=False):
        if node.name == 'p':
            # Add a new paragraph for <p> tags
            p = cell.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            for child in node.children:
                process_node(child, p, run_bold, run_italic, run_underline)
        elif node.name:
            # Handle style tags
            new_bold = run_bold or node.name in ('strong', 'b')
            new_italic = run_italic or node.name in ('em', 'i')
            new_underline = run_underline or node.name == 'u'
            for child in node.children:
                process_node(child, paragraph, new_bold, new_italic, new_underline)
        elif node.string and node.string.strip():
            # Add text as a run with the accumulated styles
            run = paragraph.add_run(node.string.strip())
            run.font.name = 'Times New Roman'
            run.font.size = Pt(14)
            run.bold = run_bold
            run.italic = run_italic
            run.underline = run_underline

    # Handle top-level content
    first_paragraph = cell.paragraphs[0]
    first_paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    for child in soup.find_all(recursive=False):
        if child.name == 'p':
            p = cell.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            for subchild in child.children:
                process_node(subchild, p)
        else:
            process_node(child, first_paragraph)

def add_markdown_to_paragraph(cell, text):
    """
    Parse Markdown or HTML text and apply Word styling to a cell
    """
    if re.search(r'<[a-zA-Z]+>', text):
        apply_html_styles(cell, text)
    else:
        html = markdown(text, extras=["fenced-code-blocks"])
        apply_html_styles(cell, html)

def add_bulleted_list(cell, items):
    """
    Add a bulleted list to a cell, with each item supporting HTML/Markdown styling
    """
    for item in items:
        p = cell.add_paragraph(style='List Bullet')
        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
        # Create a temporary cell to handle styling within the bullet
        temp_doc = Document()
        temp_cell = temp_doc.add_table(1, 1).rows[0].cells[0]
        add_markdown_to_paragraph(temp_cell, item.strip())
        # Copy runs to the bullet paragraph
        for temp_para in temp_cell.paragraphs:
            for run in temp_para.runs:
                new_run = p.add_run(run.text)
                new_run.font.name = run.font.name
                new_run.font.size = run.font.size
                new_run.bold = run.bold
                new_run.italic = run.italic
                new_run.underline = run.underline

def add_paragraphs_to_cell(cell, text):
    """
    Split text into paragraphs and add to a cell with HTML/Markdown styling
    """
    # Split by double newlines or HTML paragraph tags
    if re.search(r'<p>', text, re.IGNORECASE):
        add_markdown_to_paragraph(cell, text)
    else:
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        for i, para in enumerate(paragraphs):
            p = cell.paragraphs[0] if i == 0 else cell.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_markdown_to_paragraph(cell, para)

def sanitize_filename(filename):
    """
    Sanitize filename to remove invalid characters
    """
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def create_lesson_notes_template(data=None, logo_path='./assets/images/MostarLogo.png'):
    """
    Creates a lesson notes template for Morning Star School and returns the file path
    """
    if data is None:
        data = {}
    
    doc = Document()

    # Set the page to landscape orientation
    section = doc.sections[-1]
    section.orientation = WD_ORIENT.LANDSCAPE
    section.page_width, section.page_height = section.page_height, section.page_width

    # Estimate usable page width (subtract ~2 inches total for 1-inch margins)
    PAGE_WIDTH = section.page_width - Inches(2)

    # Header with School Name and Logo
    try:
        paragraph = doc.add_paragraph()
        run = paragraph.add_run("THE MORNING STAR SCHOOL LTD.\n")
        run.bold = True
        run.font.size = Pt(20)
        run.font.name = 'Times New Roman'

        run.add_break()
        if os.path.exists(logo_path):
            run.add_picture(logo_path, width=Inches(1.5))
        else:
            logger.warning(f"Logo file not found at {logo_path}")
        run.add_break()
        run.add_text("WEEKLY LESSON PLAN")
        paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    except Exception as e:
        logger.error(f"Error adding header: {e}")
        raise

    doc.add_paragraph()  # Add spacing

    # Table structure
    rows_data = [
        ("WEEK ENDING", data.get("WEEK_ENDING", "")),
        ("DAYS", " ".join(data.get("DAYS", []))),
        ("DURATION", data.get("DURATION", "")),
        ("SUBJECT", data.get("SUBJECT", "")),
        ("STRAND", data.get("STRAND", "")),
        ("SUBSTRAND", data.get("SUBSTRAND", "")),
        ("CLASS", data.get("CLASS", "")),
        ("CLASS SIZE", " ".join(f"{cls}({size})" for cls, size in data.get("CLASS_SIZE", {}).items())),
        ("CONTENT STANDARD (ANNOTATION)", data.get("CONTENT_STANDARD", [])),
        ("LEARNING INDICATOR(S)", data.get("LEARNING_INDICATORS", [])),
        ("PERFORMANCE INDICATOR(S)", data.get("PERFORMANCE_INDICATORS", [])),
        ("TEACHING/LEARNING RESOURCES (TLMS)", data.get("TEACHING_LEARNING_RESOURCES", [])),
        ("CORE COMPETENCIES", data.get("CORE_COMPETENCIES", [])),
        ("KEY WORDS", data.get("KEY_WORDS", [])),
        ("R.P.K", data.get("R.P.K", "")),
    ]

    table = doc.add_table(rows=len(rows_data), cols=2)
    table.style = 'Table Grid'
    table.autofit = False

    col1_width = PAGE_WIDTH * 0.3
    col2_width = PAGE_WIDTH * 0.7

    for i, (label, value) in enumerate(rows_data):
        cell1, cell2 = table.rows[i].cells
        cell1.width = col1_width
        cell2.width = col2_width
        set_cell_text(cell1, label, bold=True, font_size=16)
        if isinstance(value, list):
            add_bulleted_list(cell2, value)
        else:
            add_markdown_to_paragraph(cell2, value)

    doc.add_paragraph()

    # The Content of the Lesson Notes
    phase_headers = ["PHASE 1: STARTER", "PHASE 2: MAIN", "PHASE 3: REFLECTION"]
    phase_data = (
        data.get("PHASE_1", {}).get("STARTER", ""),
        data.get("PHASE_2", {}).get("MAIN", ""),
        data.get("PHASE_3", {}).get("REFLECTION", "")
    )

    table2 = doc.add_table(rows=2, cols=3)
    table2.style = 'Table Grid'
    table2.autofit = False

    col1_width = PAGE_WIDTH * 0.2
    col2_width = PAGE_WIDTH * 0.6
    col3_width = PAGE_WIDTH * 0.2

    for i, row_data in enumerate([phase_headers, phase_data]):
        cell1, cell2, cell3 = table2.rows[i].cells
        cell1.width = col1_width
        cell2.width = col2_width
        cell3.width = col3_width
        if i == 0:  # Headers
            set_cell_text(cell1, row_data[0], bold=True, font_size=14, align="justify")
            set_cell_text(cell2, row_data[1], bold=True, font_size=14, align="center")
            set_cell_text(cell3, row_data[2], bold=True, font_size=14, align="center")
        else:  # Content
            add_markdown_to_paragraph(cell1, row_data[0])
            add_paragraphs_to_cell(cell2, row_data[1])  # Use paragraph splitting for PHASE_2: MAIN
            add_markdown_to_paragraph(cell3, row_data[2])

    doc.add_paragraph()

    table3 = doc.add_table(rows=2, cols=2)
    table3.style = 'Table Grid'
    table3.autofit = False
    col1_width = PAGE_WIDTH * 0.3
    col2_width = PAGE_WIDTH * 0.7

    assessment_data = [
        ("ASSESSMENTS", ""),
        ("", f"{data.get('ASSESSMENTS', '')}\n\n\n{data.get('HOMEWORK', '')}"),
    ]

    for i, (label, content) in enumerate(assessment_data):
        cell1, cell2 = table3.rows[i].cells
        cell1.width = col1_width
        cell2.width = col2_width
        set_cell_text(cell1, label, bold=True, font_size=16)
        add_markdown_to_paragraph(cell2, content)

    # Save the document
    subject = data.get("SUBJECT", "Unknown")
    week = data.get("WEEK", "Unknown")
    cls = data.get("CLASS", "Unknown")
    filename = sanitize_filename(f"{cls} Lesson Notes {subject} WEEK {week}.docx")
    try:
        doc.save(filename)
        file_path = os.path.abspath(filename)
        logger.info(f"Lesson notes template created successfully: {file_path}")
        return file_path
    except Exception as e:
        logger.error(f"Error saving document: {e}")
        raise

# Pydantic model for input validation
class InputModel(BaseModel):
    lesson_note: Dict[str, Any]

# Motia configuration
config = {
    "type": "event",
    "name": "Create Lesson Notes",
    "description": "Generate lesson notes docx for Morning Star School",
    "subscribes": ["openai-response"],
    "emits": [],
    "input": InputModel.model_json_schema(),
    "flows": ["default"]
}

# Motia event handler
async def handler(input: Any, context: Any) -> Dict[str, Any]:
    """
    Handle openai-response event and generate a .docx file
    """
    logger.info('Processing input: %s', input)

    
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

    # Validate input
    try:
        input_dict = to_dict(input)
        validated_input = InputModel.model_validate(input_dict)
        lesson_note_data = validated_input.lesson_note
        logger.info("lesson_note_data", lesson_note_data)
    except Exception as e:
        context.logger.error(f"Input validation failed: {e}")
        return {
            'status': 400,
            'body': {'error': f"Invalid input format: {str(e)}"}
        }

    # Generate .docx file
    try:
        file_path = create_lesson_notes_template(data=lesson_note_data)
        return {
            'status': 200,
            'body': {'file_path': file_path}
        }
    except Exception as e:
        context.logger.error(f"Failed to create lesson notes template: {e}")
        return {
            'status': 500,
            'body': {'error': f"Failed to create lesson notes template: {str(e)}"}
        }