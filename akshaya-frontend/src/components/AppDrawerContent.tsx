import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import {
  Image,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { useTheme } from "../contexts/ThemeContext";

const LOGO = require("../../assets/images/akshaya-logo.png");

type AppDrawerContentProps = {
  onClose?: () => void;
};

type AppRoute =
  | "/"
  | "/history"
  | "/account"
  | "/mvp-info"
  | "/about";

export default function AppDrawerContent({
  onClose,
}: AppDrawerContentProps) {
  const { colors } = useTheme();

  function navigate(path: AppRoute) {
    onClose?.();
    router.push(path);
  }

  return (
    <View
      style={[
        styles.container,
        {
          backgroundColor: colors.surface,
        },
      ]}
    >
      <View
        style={[
          styles.brandCard,
          {
            backgroundColor: colors.primarySoft,
          },
        ]}
      >
        <Image
          source={LOGO}
          resizeMode="contain"
          style={styles.logo}
          accessibilityLabel="Akshaya Advisory logo"
        />

        <View style={styles.brandTextArea}>
          <Text
            style={[
              styles.brandTitle,
              {
                color: colors.text,
              },
            ]}
          >
            Akshaya Advisory
          </Text>

          <Text
            style={[
              styles.brandSubtitle,
              {
                color: colors.textMuted,
              },
            ]}
          >
            Citizen-service assistant
          </Text>
        </View>
      </View>

      <Pressable
        onPress={() => navigate("/")}
        accessibilityRole="button"
        accessibilityLabel="Start a new chat"
        style={({ pressed }) => [
          styles.newChatButton,
          {
            backgroundColor: colors.primary,
            opacity: pressed ? 0.8 : 1,
          },
        ]}
      >
        <Ionicons name="add-circle-outline" size={21} color="#FFFFFF" />

        <Text style={styles.newChatText}>Start a new chat</Text>
      </Pressable>

      <ScrollView
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.menuContent}
      >
        <Text
          style={[
            styles.menuLabel,
            {
              color: colors.textMuted,
            },
          ]}
        >
          MAIN
        </Text>

        <DrawerItem
          icon="chatbubbles-outline"
          label="Chat"
          subtitle="Ask about your situation"
          onPress={() => navigate("/")}
        />

        <DrawerItem
          icon="time-outline"
          label="Chat history"
          subtitle="Open previous conversations"
          onPress={() => navigate("/history")}
        />

        <Text
          style={[
            styles.menuLabel,
            styles.sectionSpacing,
            {
              color: colors.textMuted,
            },
          ]}
        >
          SERVICE INFORMATION
        </Text>

        <DrawerItem
          icon="grid-outline"
          label="MVP service guidance"
          subtitle="Supported citizen-service areas"
          onPress={() => navigate("/mvp-info")}
        />

        <DrawerItem
          icon="document-text-outline"
          label="Documents and preparation"
          subtitle="Understand the guidance scope"
          onPress={() => navigate("/mvp-info")}
        />

        <Text
          style={[
            styles.menuLabel,
            styles.sectionSpacing,
            {
              color: colors.textMuted,
            },
          ]}
        >
          PERSONAL
        </Text>

        <DrawerItem
          icon="person-circle-outline"
          label="Account and privacy"
          subtitle="Data and accessibility information"
          onPress={() => navigate("/account")}
        />

        <DrawerItem
          icon="settings-outline"
          label="Settings and preferences"
          subtitle="Application behaviour and support"
          onPress={() => navigate("/account")}
        />

        <Text
          style={[
            styles.menuLabel,
            styles.sectionSpacing,
            {
              color: colors.textMuted,
            },
          ]}
        >
          INFORMATION
        </Text>

        <DrawerItem
          icon="information-circle-outline"
          label="About and limitations"
          subtitle="Project scope and disclaimer"
          onPress={() => navigate("/about")}
        />
      </ScrollView>

      <View
        style={[
          styles.footer,
          {
            backgroundColor: colors.primarySoft,
          },
        ]}
      >
        <Ionicons
          name="shield-checkmark-outline"
          size={20}
          color={colors.primaryDark}
        />

        <Text
          style={[
            styles.footerText,
            {
              color: colors.primaryDark,
            },
          ]}
        >
          Advisory only. Verify important information with official sources.
        </Text>
      </View>
    </View>
  );
}

function DrawerItem({
  icon,
  label,
  subtitle,
  onPress,
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  subtitle: string;
  onPress: () => void;
}) {
  const { colors } = useTheme();

  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={label}
      accessibilityHint={subtitle}
      style={({ pressed }) => [
        styles.menuItem,
        {
          backgroundColor: pressed
            ? colors.primarySoft
            : "transparent",
          borderColor: pressed
            ? colors.borderStrong
            : "transparent",
        },
      ]}
    >
      <View
        style={[
          styles.menuIcon,
          {
            backgroundColor: colors.surfaceMuted,
          },
        ]}
      >
        <Ionicons
          name={icon}
          size={20}
          color={colors.primaryDark}
        />
      </View>

      <View style={styles.menuTextArea}>
        <Text
          style={[
            styles.menuTitle,
            {
              color: colors.text,
            },
          ]}
        >
          {label}
        </Text>

        <Text
          style={[
            styles.menuSubtitle,
            {
              color: colors.textMuted,
            },
          ]}
        >
          {subtitle}
        </Text>
      </View>

      <Ionicons
        name="chevron-forward"
        size={17}
        color={colors.textMuted}
      />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 17,
  },

  brandCard: {
    alignItems: "center",
    borderRadius: 16,
    flexDirection: "row",
    gap: 11,
    marginBottom: 15,
    padding: 12,
  },

  logo: {
    borderRadius: 10,
    height: 50,
    width: 50,
  },

  brandTextArea: {
    flex: 1,
  },

  brandTitle: {
    fontFamily: "Manrope_800ExtraBold",
    fontSize: 15,
  },

  brandSubtitle: {
    fontFamily: "Manrope_400Regular",
    fontSize: 10,
    marginTop: 3,
  },

  newChatButton: {
    alignItems: "center",
    borderRadius: 14,
    flexDirection: "row",
    gap: 8,
    justifyContent: "center",
    minHeight: 50,
  },

  newChatText: {
    color: "#FFFFFF",
    fontFamily: "Manrope_700Bold",
    fontSize: 13,
  },

  menuContent: {
    paddingBottom: 15,
    paddingTop: 23,
  },

  menuLabel: {
    fontFamily: "Manrope_700Bold",
    fontSize: 10,
    letterSpacing: 1,
    marginBottom: 8,
  },

  sectionSpacing: {
    marginTop: 23,
  },

  menuItem: {
    alignItems: "center",
    borderRadius: 13,
    borderWidth: 1,
    flexDirection: "row",
    gap: 10,
    marginBottom: 5,
    minHeight: 66,
    paddingHorizontal: 9,
    paddingVertical: 9,
  },

  menuIcon: {
    alignItems: "center",
    borderRadius: 11,
    height: 39,
    justifyContent: "center",
    width: 39,
  },

  menuTextArea: {
    flex: 1,
  },

  menuTitle: {
    fontFamily: "Manrope_700Bold",
    fontSize: 12,
  },

  menuSubtitle: {
    fontFamily: "Manrope_400Regular",
    fontSize: 10,
    lineHeight: 15,
    marginTop: 3,
  },

  footer: {
    alignItems: "flex-start",
    borderRadius: 14,
    flexDirection: "row",
    gap: 8,
    marginTop: 8,
    padding: 12,
  },

  footerText: {
    flex: 1,
    fontFamily: "Manrope_600SemiBold",
    fontSize: 10,
    lineHeight: 15,
  },
});