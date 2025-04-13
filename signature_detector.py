import fitz  # PyMuPDF
import re

# 🔍 Keywords to look for
signature_keywords = [
    'signature',
    'sign here',
    'signed by',
    'authorized signatory',
    'signature of',
    'please sign',
    'sign:'
]

import os

def find_signature_mentions(text, page, page_num, output_dir="signature_snips"):
    matches = []
    lower_text = text.lower()

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for keyword in signature_keywords:
        pattern = re.compile(rf'(.{{0,40}}{keyword}.{{0,40}})', re.IGNORECASE)
        results = pattern.findall(text)

        for match in results:
            cleaned = match.replace('\n', ' ').strip()


            has_signature_line = re.search(r'_{4,}', cleaned)
            has_trailing_space = re.search(rf'{keyword}[\s:]*[\s]{{5,}}', cleaned, re.IGNORECASE)
            has_colon_spacing = re.search(r':\s{4,}', cleaned)

            if has_signature_line or has_trailing_space or has_colon_spacing:

                keyword_rects = page.search_for(keyword)
                for i, rect in enumerate(keyword_rects):
                    expanded_rect = fitz.Rect(rect.x0 - 50, rect.y0 - 20, rect.x1 + 300, rect.y1 + 60) 
                    
                    pix = page.get_pixmap(clip=expanded_rect, dpi=200)
                    image_path = os.path.join(output_dir, f'signature_page{page_num}_match{i + 1}.png')
                    pix.save(image_path)

                    matches.append({
                        'keyword': keyword,
                        'context': cleaned,
                        'page': page_num,
                        'bbox': expanded_rect,
                        'image': image_path
                    })

    return matches


def analyze_pdf_for_signatures(pdf_path, output_txt_path=None):
    doc = fitz.open(pdf_path)
    matches = []
    all_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text()
        all_text += f"\n\n--- Page {page_num + 1} ---\n{text}"
        found = find_signature_mentions(text, page, page_num + 1)
        matches.extend(found)


    if output_txt_path:
        with open(output_txt_path, 'w', encoding='utf-8') as f:
            f.write(all_text)
        print(f"✅ PDF text exported to: {output_txt_path}")

    return matches

pdf_path = '/Users/vinaysmac/Downloads/Construction-Contract-Template-Signaturely.pdf'
output_txt = 'output_text.txt'


if __name__ == '__main__':
    try:
        results = analyze_pdf_for_signatures(pdf_path)
        if not results:
            print("\nNo signature fields or prompts detected.")
        else:
            print("\nSignature prompts detected:")
            for idx, match in enumerate(results, 1):
                print(f"\n#{idx}")
                print(f"📄 Page: {match['page']}")
                print(f"🔍 Keyword: \"{match['keyword']}\"")
                print(f"🧾 Context: ...{match['context']}...")
    except Exception as e:
        print("❌ Error reading PDF:", str(e)) 