import re
from pathlib import Path

f = Path('src/components/QueryComposer.tsx')
text = f.read_text(encoding='utf-8')

# Fix attach button
old_attach = '''      <View style={styles.inputRow}>
        <Pressable
          onPress={showAttachmentOptions}
          disabled={disabled}
          style={styles.attachButton}
        >
          <Ionicons
            name="attach-outline"
            size={28}
            color={colors.primary}
            style={{ transform: [{ rotate: "45deg" }] }}
          />
        </Pressable>'''

new_attach = '''      <View style={styles.inputRow}>
        <Pressable
          onPress={showAttachmentOptions}
          disabled={disabled}
          style={styles.attachButton}
          accessibilityLabel="Attach Document"
          accessibilityRole="button"
        >
          <Ionicons
            name="attach-outline"
            size={28}
            color={colors.primary}
            style={{ transform: [{ rotate: "45deg" }] }}
          />
          <Text style={{ fontSize: 10, color: colors.primary, marginTop: 2 }}>Attach</Text>
        </Pressable>'''
text = text.replace(old_attach, new_attach)

# Fix send button
old_send = '''        <Pressable
          onPress={handleSubmit}
          disabled={!canSubmit}
          style={({ pressed }) => [
            styles.sendButton,
            {
              backgroundColor: colors.primarySoft,
              opacity: pressed && canSubmit ? 0.7 : 1,
            },
          ]}
        >
          <Ionicons
            name="paper-plane-outline"
            size={20}
            color={canSubmit ? colors.primaryDark : colors.textMuted}
            style={{ marginLeft: 2, transform: [{ rotate: "45deg" }] }}
          />
        </Pressable>'''

new_send = '''        <Pressable
          onPress={handleSubmit}
          disabled={!canSubmit}
          accessibilityLabel="Send Message"
          accessibilityRole="button"
          style={({ pressed }) => [
            styles.sendButton,
            {
              backgroundColor: colors.primarySoft,
              opacity: pressed && canSubmit ? 0.7 : 1,
              flexDirection: "column",
            },
          ]}
        >
          <Ionicons
            name="paper-plane-outline"
            size={20}
            color={canSubmit ? colors.primaryDark : colors.textMuted}
            style={{ marginLeft: 2, transform: [{ rotate: "45deg" }] }}
          />
          <Text style={{ fontSize: 10, color: canSubmit ? colors.primaryDark : colors.textMuted, marginTop: 2 }}>Send</Text>
        </Pressable>'''
text = text.replace(old_send, new_send)

# Fix onKeyPress
old_input = '''          <TextInput
            value={query}
            onChangeText={(text) => {
              if (text.length <= MAX_QUERY_LENGTH) setQuery(text);
            }}
            placeholder={placeholder}
            placeholderTextColor={colors.textMuted}
            multiline
            maxLength={MAX_QUERY_LENGTH}
            editable={!disabled}
            style={[styles.input, { color: colors.text }]}
          />'''

new_input = '''          <TextInput
            value={query}
            onChangeText={(text) => {
              if (text.length <= MAX_QUERY_LENGTH) setQuery(text);
            }}
            onKeyPress={(e: any) => {
              if (e.nativeEvent.key === 'Enter' && !e.nativeEvent.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            placeholder={placeholder}
            placeholderTextColor={colors.textMuted}
            multiline
            maxLength={MAX_QUERY_LENGTH}
            editable={!disabled}
            style={[styles.input, { color: colors.text }]}
          />'''
text = text.replace(old_input, new_input)

f.write_text(text, encoding='utf-8')
