import pdfplumber
import re
from typing import Dict, Any

def extract_syllabus_info(pdf_path: str, topic: str, class_level: str = "Basic 8", subject: str = "Mathematics") -> Dict[str, Any]:
    result = {
        "subject": subject,
        "class": class_level,
        "topic": topic,
        "strand": "",
        "substrand": "",
        "content_standard": "",
        "learning_indicators": [],
        "performance_indicators": []
    }

    topic = topic.lower()

    with pdfplumber.open(pdf_path) as pdf:
        found_class = False
        found_topic = False
        strand = substrand = ""
        learning_indicators = []
        performance_indicators = []
        content_standard = ""

        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue

            lines = text.split("\n")
            for i, line in enumerate(lines):
                line_lower = line.lower()

                # Match class level
                if class_level.lower() in line_lower and not found_class:
                    found_class = True

                # Capture strand and substrand
                if found_class:
                    if "strand" in line_lower:
                        strand = line.split(":")[-1].strip()
                    if "substrand" in line_lower:
                        substrand = line.split(":")[-1].strip()

                # Match topic
                if topic in line_lower and found_class:
                    found_topic = True
                    # Backtrack to capture content standard
                    for j in range(i - 5, i):
                        if j >= 0 and "content standard" in lines[j].lower():
                            content_standard = lines[j].split(":")[-1].strip()
                            break

                    # Capture learning indicators
                    for j in range(i + 1, min(i + 10, len(lines))):
                        if re.match(r"B\d+\.\d+\.\d+\.\d+", lines[j]):
                            learning_indicators.append(lines[j].strip())
                        if "performance indicators" in lines[j].lower():
                            break

                    # Capture performance indicators
                    for j in range(i + 10, len(lines)):
                        if re.match(r"[-•*]", lines[j].strip()):
                            performance_indicators.append(lines[j].strip("-•* ").strip())
                        if lines[j].strip() == "":
                            break
                    break  # Stop after the first valid match

            if found_topic:
                result.update({
                    "strand": strand,
                    "substrand": substrand,
                    "content_standard": content_standard,
                    "learning_indicators": learning_indicators,
                    "performance_indicators": performance_indicators
                })
                break

    return result


if __name__ == "__main__":
    info = extract_syllabus_info(
    pdf_path="./assets/GES-New-JHS-Syllabus-MATHEMATICS-CCP-CURRICULUM-B7-B10.pdf",
    topic="Perfect Squares",
    class_level="Basic 8"
)

    from pprint import pprint
    pprint(info)
