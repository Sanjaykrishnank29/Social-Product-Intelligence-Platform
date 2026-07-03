import zipfile
import xml.etree.ElementTree as ET
import sys
import os

def read_docx(file_path):
    if not os.path.exists(file_path):
        return f"File {file_path} not found."
    try:
        with zipfile.ZipFile(file_path) as z:
            xml_content = z.read('word/document.xml')
            root = ET.fromstring(xml_content)
            # Find all text tags
            texts = []
            for elem in root.iter():
                if elem.tag.endswith('t') and elem.text:
                    texts.append(elem.text)
            return "\n".join(texts)
    except Exception as e:
        return f"Error reading {file_path}: {e}"

if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    proposal = read_docx("c:/Users/DELL/Documents/Project/Social-Intelligence/Instructions/Social_Product_Intelligence_Project_Proposal.docx")
    review = read_docx("c:/Users/DELL/Documents/Project/Social-Intelligence/Instructions/Implementation_Review_Analysis.docx")
    
    print("=== PROPOSAL ===")
    print(proposal)
    print("\n=== REVIEW ===")
    print(review)

