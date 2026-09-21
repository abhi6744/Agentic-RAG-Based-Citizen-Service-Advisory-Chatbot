import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_backend_data = """type BackendData = {
  message_id: number;
  conversation_id: number;
  response_type?: string;
  detected_service?: string;
  answer?: AnswerData;
  summary?: string;
  documents_and_eligibility?: string;
  next_steps?: string;
  citations: SourceCitation[];
  confidence_score: number;
  confidence_level: string;
  requires_official_verification: boolean;
  verification_message?: string;
  image_description?: string;
  privacy_warning?: string;
};"""

new_backend_data = """type BackendData = {
  success?: boolean;
  status?: string;
  message_id: number;
  conversation_id: number;
  response_type?: string;
  detected_service?: string;
  answer: AnswerData;
  citations: SourceCitation[];
  confidence_score: number;
  confidence_level: string;
  requires_official_verification: boolean;
  verification_message?: string;
  image_description?: string;
  privacy_warning?: string;
  image_analysis?: {
    document_type: string;
    confidence: number;
    sensitive_data_hidden: boolean;
  };
};"""

content = content.replace(old_backend_data, new_backend_data)

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
