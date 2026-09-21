import re

with open('src/app/history.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

new_remove = """  function removeConversation(conversation: Conversation) {
    const remove = async () => {
      try {
        await fetch(`${API_BASE_URL}/conversations/${conversation.id}`, { method: 'DELETE' });
        setConversations((current) =>
          current.filter((item) => item.id !== conversation.id),
        );
      } catch (e) {
        console.error("Failed to delete conversation", e);
      }
    };"""

content = re.sub(r'function removeConversation\(conversation: Conversation\) \{\s*const remove = \(\) => \{\s*setConversations\(\(current\) =>\s*current.filter\(\(item\) => item.id !== conversation.id\),\s*\);\s*\};', new_remove, content)

with open('src/app/history.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated history.tsx remove()")
