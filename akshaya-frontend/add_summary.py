import sys

summary_card = """
      {/* Summary */}
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
      )}
"""

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Only add if it's not already there
if "Advisory Summary" not in content:
    target = '          <Text style={[styles.detailText, { color: colors.textMuted }]}>{serviceLabel}</Text>\n        </View>\n      </View>'
    
    content = content.replace(target, target + "\n\n" + summary_card)
    
    with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added Summary Card to index.tsx")
else:
    print("Summary Card already present.")
