import { Ionicons } from "@expo/vector-icons";
import * as ImagePicker from "expo-image-picker";
import { useState } from "react";
import {
  Alert,
  Image,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { useTheme } from "../contexts/ThemeContext";

type QueryComposerProps = {
  onSubmit: (query: string, imageUri?: string) => void;
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
  const [imageUri, setImageUri] = useState<string | null>(null);

  const cleanedQuery = query.trim();
  const canSubmit = (cleanedQuery.length > 0 || imageUri !== null) && !disabled;

  async function pickImage() {
    const permissionResult = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (permissionResult.granted === false) {
      alert("Permission to access camera roll is required!");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });
    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  }

  async function takePhoto() {
    const permissionResult = await ImagePicker.requestCameraPermissionsAsync();
    if (permissionResult.granted === false) {
      alert("Permission to access camera is required!");
      return;
    }
    const result = await ImagePicker.launchCameraAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: true,
      quality: 0.8,
    });
    if (!result.canceled) {
      setImageUri(result.assets[0].uri);
    }
  }

  function showAttachmentOptions() {
    Alert.alert("Attach Document", "Choose an option", [
      { text: "Take Photo", onPress: takePhoto },
      { text: "Choose from Gallery", onPress: pickImage },
      { text: "Cancel", style: "cancel" },
    ]);
  }

  function handleSubmit() {
    if (!canSubmit) return;
    onSubmit(cleanedQuery, imageUri || undefined);
    setQuery("");
    setImageUri(null);
  }

  return (
    <View style={styles.container}>
      {imageUri && (
        <View style={styles.previewContainer}>
          <Image source={{ uri: imageUri }} style={styles.previewImage} />
          <Pressable
            style={[styles.removeButton, { backgroundColor: colors.surface }]}
            onPress={() => setImageUri(null)}
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
          disabled={disabled}
          style={styles.attachButton}
        >
          <Ionicons
            name="attach-outline"
            size={28}
            color={colors.primary}
            style={{ transform: [{ rotate: "45deg" }] }}
          />
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
              if (text.length <= MAX_QUERY_LENGTH) setQuery(text);
            }}
            placeholder={placeholder}
            placeholderTextColor={colors.textMuted}
            multiline
            maxLength={MAX_QUERY_LENGTH}
            editable={!disabled}
            style={[styles.input, { color: colors.text }]}
          />
        </View>

        <Pressable
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
    gap: 12,
    paddingHorizontal: 12,
  },
  attachButton: {
    padding: 4,
    justifyContent: "center",
    alignItems: "center",
  },
  pillInputContainer: {
    flex: 1,
    borderRadius: 30,
    borderWidth: 1.5,
    minHeight: 52,
    paddingHorizontal: 18,
    justifyContent: "center",
    paddingVertical: 10,
  },
  input: {
    fontFamily: "Manrope_400Regular",
    fontSize: 16,
    lineHeight: 22,
    maxHeight: 120,
    paddingTop: 0,
    paddingBottom: 0,
  },
  sendButton: {
    width: 52,
    height: 52,
    borderRadius: 26,
    justifyContent: "center",
    alignItems: "center",
  },
});