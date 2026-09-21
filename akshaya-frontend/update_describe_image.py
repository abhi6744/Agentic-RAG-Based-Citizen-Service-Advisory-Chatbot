import re

with open('../akshaya-backend/app/services/llm_client.py', 'r', encoding='utf-8') as f:
    content = f.read()

new_describe_image = """    def describe_image(self, image_path: str) -> dict:
        try:
            if not os.path.exists(image_path):
                return {"description": "Image file not found.", "document_type": "Unknown", "confidence": 0.0, "sensitive_data_hidden": False, "success": False}
                
            import mimetypes
            import json
            mime_type, _ = mimetypes.guess_type(image_path)
            if not mime_type:
                mime_type = "image/jpeg"
                
            with open(image_path, "rb") as image_file:
                base64_image = base64.b64encode(image_file.read()).decode('utf-8')
                
            prompt = \"\"\"
            Analyze this document image carefully.
            Identify the type of this document if visually clear (e.g., Aadhaar card, Ration card, Scholarship document, etc.).
            Extract relevant non-sensitive fields to help answer the user's query.
            CRITICAL PRIVACY RULE: Do NOT repeat or output full Aadhaar numbers, OTPs, passwords, bank account numbers, or biometric information. Mask them.
            If the image is unclear or not a supported document, state that clearly.
            
            Return your response STRICTLY as a valid JSON object with the following schema:
            {
                "description": "Your detailed description with masked sensitive fields",
                "document_type": "Aadhaar document | Ration Card | Scholarship document | Unknown",
                "confidence": 0.9,
                "sensitive_data_hidden": true
            }
            \"\"\"
            
            logger.info("Describing image with Grok Vision...")
            response = self.client.chat.completions.create(
                model=self.grok_vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                response_format={"type": "json_object"},
                max_tokens=400,
                temperature=0.1
            )
            raw_content = response.choices[0].message.content
            parsed = json.loads(raw_content)
            parsed["success"] = True
            return parsed
        except Exception as e:
            logger.error(f"Image description failed: {e}")
            return {"description": f"[Image description failed: {e}]", "document_type": "Unknown", "confidence": 0.0, "sensitive_data_hidden": False, "success": False}"""

content = re.sub(r'    def describe_image\(self, image_path: str\) -> str:[\s\S]*?return f"\[Image description failed: \{e\}\]"', new_describe_image, content)

with open('../akshaya-backend/app/services/llm_client.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated describe_image to return structured JSON.")
