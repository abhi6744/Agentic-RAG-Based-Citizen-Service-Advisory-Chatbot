import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import {
  Pressable,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { useTheme } from "../contexts/ThemeContext";

type ServiceCategoryCardProps = {
  category: string;
  title: string;
  description: string;
  icon: keyof typeof Ionicons.glyphMap;
};

export default function ServiceCategoryCard({
  category,
  title,
  description,
  icon,
}: ServiceCategoryCardProps) {
  const { colors } = useTheme();

  function openChat() {
    router.push({
      pathname: "/",
      params: {
        category,
      },
    });
  }

  return (
    <Pressable
      onPress={openChat}
      accessibilityRole="button"
      accessibilityLabel={`Ask about ${title}`}
      accessibilityHint="Opens the main chat with this topic as context"
      style={({ pressed }) => [
        styles.card,
        {
          backgroundColor: colors.surface,
          borderColor: colors.border,
          opacity: pressed ? 0.78 : 1,
        },
      ]}
    >
      <View
        style={[
          styles.iconBox,
          {
            backgroundColor: colors.primarySoft,
          },
        ]}
      >
        <Ionicons name={icon} size={23} color={colors.primaryDark} />
      </View>

      <Text
        style={[
          styles.title,
          {
            color: colors.text,
          },
        ]}
      >
        {title}
      </Text>

      <Text
        style={[
          styles.description,
          {
            color: colors.textMuted,
          },
        ]}
      >
        {description}
      </Text>

      <View style={styles.footer}>
        <Text
          style={[
            styles.footerText,
            {
              color: colors.primaryDark,
            },
          ]}
        >
          Ask about this
        </Text>

        <Ionicons
          name="arrow-forward"
          size={16}
          color={colors.primaryDark}
        />
      </View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    borderRadius: 18,
    borderWidth: 1,
    minHeight: 205,
    padding: 15,
    width: 170,
  },

  iconBox: {
    alignItems: "center",
    borderRadius: 12,
    height: 42,
    justifyContent: "center",
    width: 42,
  },

  title: {
    fontSize: 14,
    fontWeight: "800",
    lineHeight: 19,
    marginTop: 14,
  },

  description: {
    fontSize: 11,
    lineHeight: 17,
    marginTop: 7,
  },

  footer: {
    alignItems: "center",
    bottom: 14,
    flexDirection: "row",
    gap: 5,
    position: "absolute",
    right: 14,
  },

  footerText: {
    fontSize: 10,
    fontWeight: "800",
  },
});