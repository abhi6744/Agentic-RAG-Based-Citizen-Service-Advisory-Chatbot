import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix welcome message
old_welcome = """    backendData: {
      message_id: -1,
      conversation_id: -1,
      summary: "Welcome to Akshaya Advisory.",
      citations: [],
      confidence_score: 1.0,
      confidence_level: "high",
      requires_official_verification: false,
    } as BackendData,"""
new_welcome = """    backendData: {
      message_id: -1,
      conversation_id: -1,
      answer: {
        summary: "Welcome to Akshaya Advisory.",
        eligibility: [],
        documents: [],
        next_steps: [],
        where_to_go: [],
        warning: ""
      },
      citations: [],
      confidence_score: 1.0,
      confidence_level: "high",
      requires_official_verification: false,
    } as BackendData,"""
content = content.replace(old_welcome, new_welcome)

# Fix speech reading
old_speech = """    const textToRead = stripForSpeech(
      (answer?.summary || data.summary || "") + ". " +
      (answer?.documents?.join(". ") || data.documents_and_eligibility || "") + ". " +
      (answer?.next_steps?.join(". ") || data.next_steps || "")
    );"""
new_speech = """    const textToRead = stripForSpeech(
      (answer?.summary || "") + ". " +
      (answer?.documents?.join(". ") || "") + ". " +
      (answer?.next_steps?.join(". ") || "")
    );"""
content = content.replace(old_speech, new_speech)

# Fix random occurrences
content = content.replace('(answer?.summary || data.summary)', '(answer?.summary)')
content = content.replace('(answer?.summary || data.summary || "")', '(answer?.summary || "")')

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
