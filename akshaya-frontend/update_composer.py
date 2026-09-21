import re

with open('src/components/QueryComposer.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace QueryComposerProps
props_replacement = """export type SelectedImage = {
  uri: string;
  mimeType: string;
  fileName: string;
  width: number;
  height: number;
};

type QueryComposerProps = {
  onSubmit: (query: string, image?: SelectedImage, inputType?: "text" | "voice") => void;
  disabled?: boolean;
  placeholder?: string;
};"""
content = re.sub(r'type QueryComposerProps = \{\n[^\}]+?\};', props_replacement, content)

# Replace state and image pickers
picker_replacement = """  const [selectedImage, setSelectedImage] = useState<SelectedImage | null>(null);
  
  // Voice recording states
  const [recording, setRecording] = useState<Audio.Recording | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [inputOrigin, setInputOrigin] = useState<"text" | "voice">("text");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const cleanedQuery = query.trim();
  const canSubmit = (cleanedQuery.length > 0 || selectedImage !== null) && !disabled;

  async function pickImage() {
    try {
      const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
      if (permissionResult.granted === false) {
        setToastMessage("Permission to access camera roll is required!");
        return;
      }
      const result = await ImagePicker.launchImageLibraryAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: false,
        quality: 0.85,
      });
      if (!result.canceled && result.assets?.length) {
        const asset = result.assets[0];
        setSelectedImage({
          uri: asset.uri,
          mimeType: asset.mimeType ?? "image/jpeg",
          fileName: asset.fileName ?? `document-${Date.now()}.jpg`,
          width: asset.width,
          height: asset.height,
        });
      }
    } catch (e) {
      console.error("[QueryComposer] Error in pickImage:", e);
    }
  }

  async function takePhoto() {
    try {
      const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
      if (permissionResult.granted === false) {
        setToastMessage("Permission to access camera is required!");
        return;
      }
      const result = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: false,
        quality: 0.85,
      });
      if (!result.canceled && result.assets?.length) {
        const asset = result.assets[0];
        setSelectedImage({
          uri: asset.uri,
          mimeType: asset.mimeType ?? "image/jpeg",
          fileName: asset.fileName ?? `document-${Date.now()}.jpg`,
          width: asset.width,
          height: asset.height,
        });
      }
    } catch (e) {
      console.error("[QueryComposer] Error in takePhoto:", e);
    }
  }"""
content = re.sub(r'  const \[imageUri, setImageUri\] = useState<string \| null>\(null\);\s*// Voice recording states[\s\S]*?console\.error\("\[QueryComposer\] Error in takePhoto:", e\);\n    \}\n  \}', picker_replacement, content)

# Replace handleSubmit
submit_replacement = """  function handleSubmit() {
    if (!canSubmit) return;
    const currentImg = selectedImage;
    onSubmit(cleanedQuery, currentImg || undefined, inputOrigin);
    setQuery("");
    setSelectedImage(null);
    setInputOrigin("text");
  }"""
content = re.sub(r'  function handleSubmit\(\) \{\n[\s\S]*?setInputOrigin\("text"\);\n  \}', submit_replacement, content)

# Replace imageUri references in render
content = content.replace("imageUri !== null", "selectedImage !== null")
content = content.replace("{imageUri && (", "{selectedImage && (")
content = content.replace("source={{ uri: imageUri }}", "source={{ uri: selectedImage.uri }}")
content = content.replace("onPress={() => setImageUri(null)}", "onPress={() => setSelectedImage(null)}")

with open('src/components/QueryComposer.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated QueryComposer.tsx")
