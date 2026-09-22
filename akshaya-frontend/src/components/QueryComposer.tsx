import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import { useState } from "react";
import {
  Alert,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
  ActivityIndicator,
  Image,
} from "react-native";
import { API_BASE_URL } from "../config/api";
import { useTheme } from "../contexts/ThemeContext";

export type ChatImage = {
  uri: string;
  mimeType: string;
  fileName: string;
  width?: number;
  height?: number;
  webFile?: File;
};

type QueryComposerProps = {
  onSubmit: (query: string, image?: ChatImage, inputType?: "text" | "voice") => void;
  disabled?: boolean;
  placeholder?: string;
};

const MAX_QUERY_LENGTH = 1000;

export default function QueryComposer({
  onSubmit,
  disabled = false,
  placeholder = "Describe your issue or question...",
}: QueryComposerProps) {
  const { colors } = useTheme();
  const [query, setQuery] = useState("");
  const [selectedImage, setChatImage] = useState<ChatImage | null>(null);
  
  // Voice recording states
  const [recording, setRecording] = useState<any>(null);
  const [isRecording, setIsRecording] = useState(false);
  const [isTranscribing, setIsTranscribing] = useState(false);
  const [inputOrigin, setInputOrigin] = useState<"text" | "voice">("text");
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const cleanedQuery = query.trim();
  const canSubmit = (cleanedQuery.length > 0 || selectedImage !== null) && !disabled;

  function showToast(msg: string) {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  }

  async function startRecording() {
    try {
      if (Platform.OS === 'web') {
        showToast("Voice recording is not supported on Web. Please use the mobile app.");
        return;
      }
      
      // Temporarily bypassed for Viva deployment to prevent iOS Expo Go native crash
      Alert.alert(
        "Voice Not Supported", 
        "The native audio module is missing from your Expo Go client. Please update your Expo Go app or use text input for now."
      );
      return;
    } catch (err) {
      console.error("Failed to start recording", err);
      Alert.alert("Error", "Failed to start recording.");
    }
  }

  async function stopRecording() {
    if (!recording) return;
    setIsRecording(false);
    
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);
      
      if (uri) {
        setIsTranscribing(true);
        // Upload audio to transcribe endpoint
        const formData = new FormData();
        const fileType = Platform.OS === 'ios' ? 'audio/m4a' : 'audio/m4a';
        const fileExtension = Platform.OS === 'ios' ? 'm4a' : 'm4a';
        
        formData.append("audio", {
          uri: Platform.OS === 'android' ? uri : uri.replace('file://', ''),
          name: `audio.${fileExtension}`,
          type: fileType,
        } as any);

        const response = await fetch(`${API_BASE_URL}/transcribe`, {
          method: "POST",
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error(`Transcription failed: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.text) {
          setQuery(prev => prev ? `${prev} ${data.text}` : data.text);
          setInputOrigin("voice");
        } else {
          Alert.alert("No speech detected", "Could not transcribe any speech from the audio.");
        }
      }
    } catch (err) {
      console.error("Transcription error:", err);
      Alert.alert("Error", "Transcription failed. Please try again.");
    } finally {
      setIsTranscribing(false);
    }
  }


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
        setChatImage({
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
        setChatImage({
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
  }

  function showAttachmentOptions() {
    try {
      if (Platform.OS === 'web') {
        pickImage();
      } else {
        Alert.alert("Attach Document", "Choose an option", [
          { text: "Take Photo", onPress: takePhoto },
          { text: "Choose from Gallery", onPress: pickImage },
          { text: "Cancel", style: "cancel" },
        ]);
      }
    } catch (e) {
      console.error("[QueryComposer] Error in showAttachmentOptions:", e);
    }
  }

  function handleSubmit() {
    if (!canSubmit) return;
    const currentImg = selectedImage;
    onSubmit(cleanedQuery, currentImg || undefined, inputOrigin);
    setQuery("");
    setChatImage(null);
    setInputOrigin("text");
  }

  return (
    <View style={styles.container}>
      {toastMessage && (
        <View style={{ marginHorizontal: 20, marginBottom: 10, padding: 10, backgroundColor: colors.warningBackground, borderRadius: 8 }}>
          <Text style={{ color: colors.warning, fontSize: 12, textAlign: 'center', fontFamily: 'Manrope_600SemiBold' }}>
            {toastMessage}
          </Text>
        </View>
      )}

      {selectedImage && (
        <View style={styles.previewContainer}>
          <Image source={{ uri: selectedImage.uri }} style={styles.previewImage} />
          <Pressable
            style={[styles.removeButton, { backgroundColor: colors.surface }]}
            onPress={() => setChatImage(null)}
          >
            <Ionicons name="close" size={14} color={colors.text} />
          </Pressable>
        </View>
      )}

      <Text style={[styles.privacyWarning, { color: colors.textMuted }]}>
        Avoid uploading photos showing your Aadhaar number, OTP, or other sensitive numbers in full view.
      </Text>

      <View style={styles.inputRow}>
        <Pressable
          onPress={showAttachmentOptions}
          disabled={disabled || isRecording || isTranscribing}
          style={styles.attachButton}
          accessibilityLabel="Attach Document"
        >
          <Ionicons
            name="attach-outline"
            size={28}
            color={colors.primary}
            style={{ transform: [{ rotate: "45deg" }] }}
          />
          <Text style={{ fontSize: 10, color: colors.primary, marginTop: 2 }}>Attach</Text>
        </Pressable>

        <Pressable
          onPress={isRecording ? stopRecording : startRecording}
          disabled={disabled || isTranscribing}
          style={styles.micButton}
          accessibilityLabel={isRecording ? "Stop Recording" : "Start Voice Input"}
        >
          {isTranscribing ? (
            <ActivityIndicator size="small" color={colors.primary} />
          ) : (
            <>
              <View style={[styles.micIconContainer, isRecording && styles.recordingActive]}>
                <Ionicons
                  name={isRecording ? "stop" : "mic"}
                  size={24}
                  color={isRecording ? "#FFF" : colors.primary}
                />
              </View>
              <Text style={{ fontSize: 10, color: isRecording ? '#e74c3c' : colors.primary, marginTop: 2, fontWeight: isRecording ? 'bold' : 'normal' }}>
                {isRecording ? "Recording" : "Voice"}
              </Text>
            </>
          )}
        </Pressable>

        <View
          style={[
            styles.pillInputContainer,
            {
              backgroundColor: colors.surface,
              borderColor: colors.border,
            },
          ]}
        >
          <TextInput
            value={query}
            onChangeText={(text) => {
              if (text.length === 1 && query.length === 0) setInputOrigin("text");
              if (text.length <= MAX_QUERY_LENGTH) setQuery(text);
            }}
            onKeyPress={(e: any) => {
              if (e.nativeEvent.key === 'Enter' && !e.nativeEvent.shiftKey) {
                e.preventDefault();
                handleSubmit();
              }
            }}
            placeholder={isRecording ? "Listening..." : isTranscribing ? "Transcribing..." : placeholder}
            placeholderTextColor={isRecording ? "#e74c3c" : colors.textMuted}
            multiline
            maxLength={MAX_QUERY_LENGTH}
            editable={!disabled && !isRecording && !isTranscribing}
            style={[styles.input, { color: colors.text }]}
          />
        </View>

        <Pressable
          onPress={handleSubmit}
          disabled={!canSubmit || isRecording || isTranscribing}
          accessibilityLabel="Send Message"
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
          <Text style={{ fontSize: 10, color: canSubmit ? colors.primaryDark : colors.textMuted, marginTop: 2 }}>Send</Text>
        </Pressable>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
    paddingVertical: 10,
    backgroundColor: "#FFFFFF",
  },
  privacyWarning: {
    fontFamily: "Manrope_400Regular",
    fontSize: 11,
    marginBottom: 8,
    textAlign: "center",
    paddingHorizontal: 20,
  },
  previewContainer: {
    position: "relative",
    width: 60,
    height: 60,
    marginBottom: 10,
    marginLeft: 50,
  },
  previewImage: {
    width: "100%",
    height: "100%",
    borderRadius: 8,
  },
  removeButton: {
    position: "absolute",
    top: -8,
    right: -8,
    width: 24,
    height: 24,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.2,
    shadowRadius: 1.5,
    elevation: 2,
  },
  inputRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    paddingHorizontal: 12,
  },
  attachButton: {
    padding: 4,
    justifyContent: "center",
    alignItems: "center",
    width: 48,
  },
  micButton: {
    padding: 4,
    justifyContent: "center",
    alignItems: "center",
    width: 48,
  },
  micIconContainer: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "transparent",
  },
  recordingActive: {
    backgroundColor: "#e74c3c",
    shadowColor: "#e74c3c",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.8,
    shadowRadius: 5,
    elevation: 5,
  },
  pillInputContainer: {
    flex: 1,
    borderRadius: 20,
    borderWidth: 1.5,
    minHeight: 52,
    paddingHorizontal: 16,
    justifyContent: "center",
    paddingVertical: 8,
  },
  input: {
    fontFamily: "Manrope_400Regular",
    fontSize: 15,
    lineHeight: 20,
    maxHeight: 100,
    paddingTop: 0,
    paddingBottom: 0,
  },
  sendButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    justifyContent: "center",
    alignItems: "center",
  },
});