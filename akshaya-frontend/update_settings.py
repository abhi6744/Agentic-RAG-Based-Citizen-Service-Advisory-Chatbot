import re

with open('src/app/settings.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Change component name
content = content.replace("export default function AccountScreen()", "export default function SettingsScreen()")

# Change header text
content = content.replace("GUEST ACCOUNT", "APPLICATION PREFERENCES")
content = content.replace("Account and privacy", "Settings and preferences")
content = content.replace("Your advisory preferences and data boundaries", "Configure your chat experience and interface settings")

# Replace Guest User profile card with Theme settings or similar
old_profile_card = r'<View\s+style=\{\[\s*styles\.profileCard[\s\S]*?No account or personal identity is required for the MVP\.\s*</Text>\s*</View>\s*</View>'
new_profile_card = """<View
          style={[
            styles.profileCard,
            {
              backgroundColor: colors.surface,
              borderColor: colors.border,
            },
          ]}
        >
          <View
            style={[
              styles.avatar,
              {
                backgroundColor: colors.primary,
              },
            ]}
          >
            <Ionicons
              name="color-palette-outline"
              size={28}
              color="#FFFFFF"
            />
          </View>

          <View style={styles.profileText}>
            <Text
              style={[
                styles.profileName,
                {
                  color: colors.text,
                },
              ]}
            >
              Ocean Blue Theme
            </Text>

            <Text
              style={[
                styles.profileSubtitle,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              Default mobile-first design applied.
            </Text>
          </View>
        </View>"""
content = re.sub(old_profile_card, new_profile_card, content)

# Replace Privacy-first design with Chat Preferences
content = content.replace('title="Privacy-first design"', 'title="Chat Preferences"')
content = content.replace('icon="shield-checkmark-outline"', 'icon="chatbubble-ellipses-outline"')
content = content.replace('icon: "lock-closed-outline"', 'icon: "notifications-outline"')
content = content.replace('title: "Do not share sensitive data"', 'title: "Notifications"')
content = content.replace('text: "Do not enter full Aadhaar numbers, OTPs, passwords, bank information, or upload images showing sensitive biometric details in full view."', 'text: "Push notifications are currently disabled for the MVP phase."')
content = content.replace('icon: "finger-print-outline"', 'icon: "trash-outline"')
content = content.replace('title: "No identity verification"', 'title: "History Management"')
content = content.replace('text: "The app does not verify your identity, document authenticity, or eligibility in official systems."', 'text: "Chat history can be cleared on a per-conversation basis from the history tab."')
content = content.replace('icon: "document-text-outline"', 'icon: "text-outline"')
content = content.replace('title: "Advisory query logging"', 'title: "Text size"')
content = content.replace('text: "Later backend logs will be anonymized where possible for testing and feedback analysis."', 'text: "The application scales dynamically with your device\'s native accessibility settings."')

# Remove Accessibility card from settings since it's in account or just keep it as is
content = content.replace('title="Accessibility and language"', 'title="Voice and Audio"')
content = content.replace('title: "English-first MVP"', 'title: "Language Support"')

with open('src/app/settings.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated settings.tsx")
