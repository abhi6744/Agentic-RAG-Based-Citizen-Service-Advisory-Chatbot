import re

with open('src/components/AppDrawerContent.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Update AppRoute type
content = content.replace(
    '  | "/mvp-info"\n  | "/about";',
    '  | "/mvp-info"\n  | "/documents"\n  | "/settings"\n  | "/about";'
)

# Update the duplicate /mvp-info
old_docs_item = """        <DrawerItem
          icon="document-text-outline"
          label="Documents and preparation"
          subtitle="Understand the guidance scope"
          onPress={() => navigate("/mvp-info")}
        />"""
new_docs_item = """        <DrawerItem
          icon="document-text-outline"
          label="Documents and preparation"
          subtitle="Understand the guidance scope"
          onPress={() => navigate("/documents")}
        />"""
content = content.replace(old_docs_item, new_docs_item)

# Update the duplicate /account
old_settings_item = """        <DrawerItem
          icon="settings-outline"
          label="Settings and preferences"
          subtitle="Application behaviour and support"
          onPress={() => navigate("/account")}
        />"""
new_settings_item = """        <DrawerItem
          icon="settings-outline"
          label="Settings and preferences"
          subtitle="Application behaviour and support"
          onPress={() => navigate("/settings")}
        />"""
content = content.replace(old_settings_item, new_settings_item)

with open('src/components/AppDrawerContent.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated AppDrawerContent.tsx routing")
