import re
from pathlib import Path

f = Path('src/components/QueryComposer.tsx')
text = f.read_text(encoding='utf-8')

old_attach = '''  function showAttachmentOptions() {
    Alert.alert("Attach Document", "Choose an option", [
      { text: "Take Photo", onPress: takePhoto },
      { text: "Choose from Gallery", onPress: pickImage },
      { text: "Cancel", style: "cancel" },
    ]);
  }'''

new_attach = '''  function showAttachmentOptions() {
    if (Platform.OS === 'web') {
      // Alert.alert with 3 options doesn't work on Web, and launchCamera doesn't work on Expo Web.
      // So on Web, we go straight to the gallery picker.
      pickImage();
    } else {
      Alert.alert("Attach Document", "Choose an option", [
        { text: "Take Photo", onPress: takePhoto },
        { text: "Choose from Gallery", onPress: pickImage },
        { text: "Cancel", style: "cancel" },
      ]);
    }
  }'''

text = text.replace(old_attach, new_attach)
f.write_text(text, encoding='utf-8')
