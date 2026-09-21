with open('../akshaya-backend/app/schemas/chat.py', 'r', encoding='utf-8') as f:
    content = f.read()

image_analysis_class = """class ImageAnalysisData(BaseModel):
    document_type: str
    confidence: float
    sensitive_data_hidden: bool

class ChatResponse"""
if "class ImageAnalysisData" not in content:
    content = content.replace("class ChatResponse", image_analysis_class)
    
if "image_analysis:" not in content:
    content = content.replace("image_description: Optional[str] = None", "image_description: Optional[str] = None\n    image_analysis: Optional[ImageAnalysisData] = None")

with open('../akshaya-backend/app/schemas/chat.py', 'w', encoding='utf-8') as f:
    f.write(content)
