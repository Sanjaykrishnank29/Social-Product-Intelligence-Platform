import zipfile
import xml.etree.ElementTree as ET
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
    proposal_path = "c:/Users/DELL/Documents/Project/Social-Intelligence/Instructions/Social_Product_Intelligence_Project_Proposal.docx"
    review_path = "c:/Users/DELL/Documents/Project/Social-Intelligence/Instructions/Implementation_Review_Analysis.docx"
    
    proposal = read_docx(proposal_path)
    review = read_docx(review_path)
    
    scratch_dir = "c:/Users/DELL/Documents/Project/Social-Intelligence/brain/5ba7786b-0906-4930-9bfd-fb1f5c375820/scratch"
    os.makedirs(scratch_dir, exist_ok=True)
    
    with open(os.path.join(scratch_dir, "proposal.txt"), "w", encoding="utf-8") as f:
        f.write(proposal)
        
    with open(os.path.join(scratch_dir, "review.txt"), "w", encoding="utf-8") as f:
        f.write(review)
        
    print("Done extracting texts to proposal.txt and review.txt")
