import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_service_block = """      <View style={styles.detailsContainer}>
        {/* Identified Service */}
        <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={[styles.detailIcon, { backgroundColor: colors.primarySoft }]}>
            <Ionicons name="search-outline" size={19} color={colors.primaryDark} />
          </View>
          <View style={styles.detailTextArea}>
            <Text style={[styles.detailTitle, { color: colors.text }]}>Identified Service</Text>
            <Text style={[styles.detailText, { color: colors.textMuted }]}>{serviceLabel}</Text>
          </View>
        </View>"""

new_service_block = """      <View style={styles.detailsContainer}>
        {/* Identified Service */}
        {data.detected_service && (
          <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <View style={[styles.detailIcon, { backgroundColor: colors.primarySoft }]}>
              <Ionicons name="search-outline" size={19} color={colors.primaryDark} />
            </View>
            <View style={styles.detailTextArea}>
              <Text style={[styles.detailTitle, { color: colors.text }]}>Identified Service</Text>
              <Text style={[styles.detailText, { color: colors.textMuted }]}>{serviceLabel}</Text>
            </View>
          </View>
        )}"""

content = content.replace(old_service_block, new_service_block)

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
