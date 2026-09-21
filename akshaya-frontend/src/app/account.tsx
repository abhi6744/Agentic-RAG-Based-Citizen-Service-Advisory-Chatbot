import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import {
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";

import { useTheme } from "../contexts/ThemeContext";

export default function AccountScreen() {
  const { colors } = useTheme();

  return (
    <SafeAreaView
      style={[
        styles.safeArea,
        {
          backgroundColor: colors.background,
        },
      ]}
    >
      <ScrollView
        contentContainerStyle={styles.content}
        showsVerticalScrollIndicator={false}
      >
        <View style={styles.headerRow}>
          <Pressable
            onPress={() => router.canGoBack() ? router.back() : router.replace('/')}
            accessibilityRole="button"
            accessibilityLabel="Go back"
            style={styles.backButton}
          >
            <Ionicons name="arrow-back" size={22} color={colors.text} />
          </Pressable>

          <View>
            <Text
              style={[
                styles.headerTitle,
                {
                  color: colors.text,
                },
              ]}
            >
              Account and privacy
            </Text>

            <Text
              style={[
                styles.headerSubtitle,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              Your advisory preferences and data boundaries
            </Text>
          </View>
        </View>

        <View
          style={[
            styles.profileCard,
            {
              backgroundColor: colors.surface,
              borderColor: colors.border,
            },
          ]}
        >
          <View
            style={[
              styles.avatar,
              {
                backgroundColor: colors.primary,
              },
            ]}
          >
            <Ionicons
              name="person-outline"
              size={28}
              color="#FFFFFF"
            />
          </View>

          <View style={styles.profileText}>
            <Text
              style={[
                styles.profileName,
                {
                  color: colors.text,
                },
              ]}
            >
              Guest user
            </Text>

            <Text
              style={[
                styles.profileSubtitle,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              No account or personal identity is required for the MVP.
            </Text>
          </View>
        </View>

        <InfoCard
          colors={colors}
          title="Privacy-first design"
          icon="shield-checkmark-outline"
          accent
          rows={[
            {
              icon: "lock-closed-outline",
              title: "Do not share sensitive data",
              text: "Do not enter full Aadhaar numbers, OTPs, passwords, bank information, or upload images showing sensitive biometric details in full view.",
            },
            {
              icon: "finger-print-outline",
              title: "No identity verification",
              text: "The app does not verify your identity, document authenticity, or eligibility in official systems.",
            },
            {
              icon: "document-text-outline",
              title: "Advisory query logging",
              text: "Later backend logs will be anonymized where possible for testing and feedback analysis.",
            },
          ]}
        />

        <InfoCard
          colors={colors}
          title="Accessibility and language"
          icon="accessibility-outline"
          rows={[
            {
              icon: "language-outline",
              title: "English-first MVP",
              text: "The initial version is designed for typed English queries and verified English responses.",
            },
            {
              icon: "mic-outline",
              title: "Voice typing",
              text: "You can use the voice typing feature provided by your mobile keyboard to enter questions.",
            },
            {
              icon: "volume-medium-outline",
              title: "Listen feature",
              text: "English text-to-speech will read verified final responses after backend integration.",
            },
          ]}
        />



        <View
          style={[
            styles.disclaimer,
            {
              backgroundColor: colors.warningBackground,
            },
          ]}
        >
          <Ionicons
            name="alert-circle-outline"
            size={21}
            color={colors.warning}
          />

          <Text
            style={[
              styles.disclaimerText,
              {
                color: colors.warning,
              },
            ]}
          >
            This is an advisory application. Always confirm important service
            requirements with an Akshaya operator or the responsible official
            department.
          </Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

function InfoCard({
  colors,
  title,
  icon,
  rows,
  accent = false,
}: {
  colors: any;
  title: string;
  icon: keyof typeof Ionicons.glyphMap;
  accent?: boolean;
  rows: {
    icon: keyof typeof Ionicons.glyphMap;
    title: string;
    text: string;
  }[];
}) {
  return (
    <View
      style={[
        styles.infoCard,
        {
          backgroundColor: colors.surface,
          borderColor: colors.border,
        },
      ]}
    >
      <View style={styles.infoHeader}>
        <View
          style={[
            styles.infoHeaderIcon,
            {
              backgroundColor: accent
                ? colors.primarySoft
                : colors.surfaceMuted,
            },
          ]}
        >
          <Ionicons
            name={icon}
            size={20}
            color={colors.primaryDark}
          />
        </View>

        <Text
          style={[
            styles.infoHeaderTitle,
            {
              color: colors.text,
            },
          ]}
        >
          {title}
        </Text>
      </View>

      {rows.map((row) => (
        <View key={row.title} style={styles.infoRow}>
          <Ionicons
            name={row.icon}
            size={17}
            color={colors.primaryDark}
          />

          <View style={styles.infoRowTextArea}>
            <Text
              style={[
                styles.infoRowTitle,
                {
                  color: colors.text,
                },
              ]}
            >
              {row.title}
            </Text>

            <Text
              style={[
                styles.infoRowText,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              {row.text}
            </Text>
          </View>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },

  content: {
    alignSelf: "center",
    maxWidth: 760,
    padding: 17,
    paddingBottom: 42,
    width: "100%",
  },

  headerRow: {
    alignItems: "flex-start",
    flexDirection: "row",
    gap: 9,
  },

  backButton: {
    alignItems: "center",
    height: 40,
    justifyContent: "center",
    width: 40,
  },

  headerTitle: {
    fontSize: 20,
    fontWeight: "800",
    marginTop: 2,
  },

  headerSubtitle: {
    fontSize: 11,
    lineHeight: 16,
    marginTop: 4,
  },

  profileCard: {
    alignItems: "center",
    borderRadius: 18,
    borderWidth: 1,
    flexDirection: "row",
    gap: 13,
    marginTop: 22,
    padding: 16,
  },

  avatar: {
    alignItems: "center",
    borderRadius: 18,
    height: 56,
    justifyContent: "center",
    width: 56,
  },

  profileText: {
    flex: 1,
  },

  profileName: {
    fontSize: 17,
    fontWeight: "800",
  },

  profileSubtitle: {
    fontSize: 12,
    lineHeight: 18,
    marginTop: 4,
  },

  infoCard: {
    borderRadius: 18,
    borderWidth: 1,
    marginTop: 12,
    padding: 16,
  },

  infoHeader: {
    alignItems: "center",
    flexDirection: "row",
    gap: 9,
    marginBottom: 15,
  },

  infoHeaderIcon: {
    alignItems: "center",
    borderRadius: 10,
    height: 38,
    justifyContent: "center",
    width: 38,
  },

  infoHeaderTitle: {
    fontSize: 15,
    fontWeight: "800",
  },

  infoRow: {
    alignItems: "flex-start",
    flexDirection: "row",
    gap: 10,
    marginBottom: 14,
  },

  infoRowTextArea: {
    flex: 1,
  },

  infoRowTitle: {
    fontSize: 12,
    fontWeight: "800",
  },

  infoRowText: {
    fontSize: 11,
    lineHeight: 17,
    marginTop: 3,
  },



  disclaimer: {
    alignItems: "flex-start",
    borderRadius: 18,
    flexDirection: "row",
    gap: 9,
    marginTop: 12,
    padding: 15,
  },

  disclaimerText: {
    flex: 1,
    fontSize: 11,
    fontWeight: "600",
    lineHeight: 17,
  },
});