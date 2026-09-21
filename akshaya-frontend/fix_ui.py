import re
from pathlib import Path

f = Path('src/app/index.tsx')
text = f.read_text(encoding='utf-8')

# 1. Add response_type: service_unavailable if it's missing in types
if "service_unavailable" not in text:
    pass # I already verified the interface allows string so it's fine.

# 2. Update MessageBubble signature and prop
old_bubble_sig = 'function MessageBubble({ message }: { message: Message }) {'
new_bubble_sig = 'function MessageBubble({ message, onRetry }: { message: Message, onRetry?: () => void }) {'
text = text.replace(old_bubble_sig, new_bubble_sig)

# 3. Add Retry button to MessageBubble
old_formatted = '''          ) : (
            <FormattedText 
              text={message.text} 
              style={[styles.messageText, { color: colors.text }]} 
            />
          )}
        </View>
      </View>
    );
  }'''

new_formatted = '''          ) : (
            <>
              <FormattedText 
                text={message.text} 
                style={[styles.messageText, { color: colors.text }]} 
              />
              {message.backendData?.response_type === 'service_unavailable' && onRetry && (
                <Pressable
                  onPress={onRetry}
                  style={({ pressed }) => [{
                    backgroundColor: colors.primarySoft,
                    borderColor: colors.primary,
                    borderWidth: 1,
                    borderRadius: 8,
                    paddingVertical: 8,
                    paddingHorizontal: 16,
                    marginTop: 12,
                    alignSelf: 'flex-start',
                    flexDirection: 'row',
                    alignItems: 'center',
                    gap: 6,
                    opacity: pressed ? 0.7 : 1
                  }]}
                >
                  <Ionicons name="refresh" size={16} color={colors.primaryDark} />
                  <Text style={{ color: colors.primaryDark, fontFamily: "Manrope_600SemiBold", fontSize: 13 }}>Retry Request</Text>
                </Pressable>
              )}
            </>
          )}
        </View>
      </View>
    );
  }'''
text = text.replace(old_formatted, new_formatted)

# 4. Update the map in index.tsx
old_map = '''          {messages.map((message) => (
            <MessageBubble key={message.id} message={message} />
          ))}'''
          
new_map = '''          {messages.map((message, index) => {
            // Find the immediately preceding user message for retries
            let lastUserQuery = "";
            let lastUserImage = undefined;
            if (message.backendData?.response_type === 'service_unavailable') {
              for (let i = index - 1; i >= 0; i--) {
                if (messages[i].role === 'user') {
                  lastUserQuery = messages[i].text;
                  lastUserImage = messages[i].imageUri;
                  break;
                }
              }
            }
            
            return (
              <MessageBubble 
                key={message.id} 
                message={message} 
                onRetry={lastUserQuery ? () => submitQuestion(lastUserQuery, lastUserImage === 'has-image' ? undefined : lastUserImage) : undefined} 
              />
            );
          })}'''
text = text.replace(old_map, new_map)

f.write_text(text, encoding='utf-8')
