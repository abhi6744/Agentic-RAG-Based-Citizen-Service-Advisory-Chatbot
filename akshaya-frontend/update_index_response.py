import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_code = """      const data: BackendData = await response.json();
      
      setConversationId(data.conversation_id);

      LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: data.message_id.toString(),
          role: "assistant",
          text: data.answer?.summary || "I could not generate a clear summary for this response. Please review the verified sections below or try rephrasing your question.",
          backendData: data,
        },
      ]);"""

new_code = """      const rawData = await response.json();
      const data: BackendData = normalizeChatResponse(rawData);
      
      setConversationId(data.conversation_id);

      LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: data.message_id ? data.message_id.toString() : `msg-${Date.now()}`,
          role: "assistant",
          text: data.answer.summary,
          backendData: data,
        },
      ]);"""

content = content.replace(old_code, new_code)

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
