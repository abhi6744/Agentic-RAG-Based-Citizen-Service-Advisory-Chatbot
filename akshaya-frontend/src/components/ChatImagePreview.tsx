import React, { useState } from "react";
import { Image, Platform, View, Text, StyleSheet } from "react-native";
import { Ionicons } from "@expo/vector-icons";
import { useTheme } from "../contexts/ThemeContext";

export default function ChatImagePreview({ uri, width = 200, height = 250 }: { uri: string; width?: number; height?: number }) {
  const { colors } = useTheme();
  const [error, setError] = useState(false);

  if (!uri || error) {
    return (
      <View style={[styles.errorContainer, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <Ionicons name="image-outline" size={24} color={colors.textMuted} />
        <Text style={[styles.errorText, { color: colors.textMuted }]}>Preview unavailable</Text>
      </View>
    );
  }

  const isWebBlob = Platform.OS === "web" && uri.startsWith("blob:");

  return (
    <View style={styles.container}>
      {isWebBlob ? (
        <img
          src={uri}
          alt="Document preview"
          style={{
            maxWidth: '100%',
            maxHeight: height,
            objectFit: 'contain',
            borderRadius: 8,
            border: `1px solid ${colors.primarySoft}`,
          }}
          onError={() => setError(true)}
        />
      ) : (
        <Image
          source={{ uri }}
          style={[styles.image, { borderColor: colors.primarySoft, maxWidth: width, maxHeight: height }]}
          resizeMode="contain"
          onError={() => setError(true)}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    marginVertical: 8,
    alignItems: "flex-start",
  },
  image: {
    width: "100%",
    borderRadius: 8,
    borderWidth: 1,
  },
  errorContainer: {
    width: 150,
    height: 100,
    justifyContent: "center",
    alignItems: "center",
    borderRadius: 8,
    borderWidth: 1,
    marginVertical: 8,
  },
  errorText: {
    fontSize: 10,
    marginTop: 4,
    fontFamily: "Manrope_400Regular",
  }
});
