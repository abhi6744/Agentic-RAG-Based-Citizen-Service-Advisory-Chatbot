import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Add import
if "normalizeChatResponse" not in content:
    content = content.replace('import { cleanText } from "../utils/cleanResponseText";', 'import { cleanText } from "../utils/cleanResponseText";\nimport { normalizeChatResponse } from "../utils/responseAdapter";')

# Patch the successful response processing
old_response = """        const data = await response.json();
        
        setConversationId(data.conversation_id);
  
        LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
        setMessages((currentMessages) => [
          ...currentMessages,
          {
            id: data.message_id.toString(),
            role: "assistant",
            text: data.summary || "No summary provided.",
            backendData: data,
          },
        ]);"""

new_response = """        const rawData = await response.json();
        const data = normalizeChatResponse(rawData);
        
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

content = content.replace(old_response, new_response)

# Remove Advisory Summary card
old_advisory_summary = """        {/* Summary */}
        {(answer?.summary || data.summary) && (
          <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border, flexDirection: 'column', alignItems: 'stretch' }]}>
            <View style={{flexDirection: 'row', alignItems: 'center', marginBottom: 12}}>
              <View style={[styles.detailIcon, { backgroundColor: colors.primarySoft, marginBottom: 0 }]}>
                <Ionicons name="chatbubbles-outline" size={19} color={colors.primaryDark} />
              </View>
              <Text style={[styles.detailTitle, { color: colors.text }]}>Advisory Summary</Text>
            </View>
            <Text style={[styles.detailText, { color: colors.text, lineHeight: 20 }]}>{cleanText(answer?.summary || data.summary || "")}</Text>
          </View>
        )}"""

content = content.replace(old_advisory_summary, "")

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
