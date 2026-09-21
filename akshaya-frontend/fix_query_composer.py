import re
from pathlib import Path

f = Path('src/components/QueryComposer.tsx')
text = f.read_text(encoding='utf-8')

# Fix 1: Missing Platform import
import_block = """import {
  Alert,
  Image,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";"""

fixed_import_block = """import {
  Alert,
  Image,
  Platform,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";"""

text = text.replace(import_block, fixed_import_block)

# Fix 3: Wrap interactive handlers with try/catch to make errors visible
old_pick = """  async function pickImage() {
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
  }"""

new_pick = """  async function pickImage() {
    try {
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
    } catch (e) {
      console.error("[QueryComposer] Error in pickImage:", e);
    }
  }"""
text = text.replace(old_pick, new_pick)

old_take = """  async function takePhoto() {
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
  }"""

new_take = """  async function takePhoto() {
    try {
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
    } catch (e) {
      console.error("[QueryComposer] Error in takePhoto:", e);
    }
  }"""
text = text.replace(old_take, new_take)

old_show = """  function showAttachmentOptions() {
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
  }"""

new_show = """  function showAttachmentOptions() {
    try {
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
    } catch (e) {
      console.error("[QueryComposer] Error in showAttachmentOptions:", e);
    }
  }"""
text = text.replace(old_show, new_show)

f.write_text(text, encoding='utf-8')
