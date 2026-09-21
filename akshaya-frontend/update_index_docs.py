import re

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

old_docs_block = """        {/* Documents & Eligibility */}
        <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border, flexDirection: 'column', alignItems: 'stretch' }]}>
"""

new_docs_block = """        {/* Documents & Eligibility */}
        {data.success !== false && (
          <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border, flexDirection: 'column', alignItems: 'stretch' }]}>
"""

content = content.replace(old_docs_block, new_docs_block)

old_docs_end = """        </View>
  
        {/* Next Steps */}"""
new_docs_end = """          </View>
        )}
  
        {/* Next Steps */}"""
content = content.replace(old_docs_end, new_docs_end, 1)

old_steps_block = """        {/* Next Steps */}
        <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border, flexDirection: 'column', alignItems: 'stretch' }]}>"""
new_steps_block = """        {/* Next Steps */}
        {data.success !== false && (
          <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border, flexDirection: 'column', alignItems: 'stretch' }]}>"""
content = content.replace(old_steps_block, new_steps_block)

old_steps_end = """        </View>
  
        {/* Verification Warning */}"""
new_steps_end = """          </View>
        )}
  
        {/* Verification Warning */}"""
content = content.replace(old_steps_end, new_steps_end, 1)

with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
