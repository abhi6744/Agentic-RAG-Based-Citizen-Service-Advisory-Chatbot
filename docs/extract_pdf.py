from pypdf import PdfReader
reader = PdfReader('SRS.pdf')
print(reader.pages[0].extract_text())
