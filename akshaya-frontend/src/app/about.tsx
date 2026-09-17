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

const principles = [
  {
    icon: "search-outline" as const,
    title: "Official-source retrieval",
    text: "The final backend will retrieve relevant evidence from curated official documents before generating a response.",
  },
  {
    icon: "git-compare-outline" as const,
    title: "Controlled agentic workflow",
    text: "The system can identify intent, evaluate retrieval relevance, rewrite weak queries once, verify citations, and issue low-confidence warnings.",
  },
  {
    icon: "document-text-outline" as const,
    title: "Structured guidance",
    text: "Responses will organize service identification, possible eligibility, documents, steps, fee information when available, warnings, and sources.",
  },
  {
    icon: "volume-medium-outline" as const,
    title: "English Listen feature",
    text: "The completed version will provide English text-to-speech for verified final responses while keeping citations visible on screen.",
  },
];

export default function AboutScreen() {
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
        showsVerticalScrollIndicator={false}
        contentContainerStyle={styles.content}
      >
        <View style={styles.headerRow}>
          <Pressable
            onPress={() => router.back()}
            accessibilityRole="button"
            accessibilityLabel="Go back"
            style={styles.backButton}
          >
            <Ionicons name="arrow-back" size={22} color={colors.text} />
          </Pressable>

          <View style={styles.headerTextArea}>
            <Text
              style={[
                styles.eyebrow,
                {
                  color: colors.primaryDark,
                },
              ]}
            >
              ABOUT THE PROJECT
            </Text>

            <Text
              style={[
                styles.title,
                {
                  color: colors.text,
                },
              ]}
            >
              Akshaya Advisory
            </Text>

            <Text
              style={[
                styles.subtitle,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              Agentic RAG-Based Citizen Service Advisory Application for
              Akshaya Centres
            </Text>
          </View>
        </View>

        <View
          style={[
            styles.introCard,
            {
              backgroundColor: colors.primarySoft,
            },
          ]}
        >
          <View
            style={[
              styles.introIcon,
              {
                backgroundColor: colors.primary,
              },
            ]}
          >
            <Ionicons
              name="sparkles"
              size={26}
              color="#FFFFFF"
            />
          </View>

          <Text
            style={[
              styles.introTitle,
              {
                color: colors.primaryDark,
              },
            ]}
          >
            Clear preparation before visiting a service centre
          </Text>

          <Text
            style={[
              styles.introText,
              {
                color: colors.primaryDark,
              },
            ]}
          >
            The project helps citizens understand possible services, document
            requirements, eligibility information, identity-mismatch guidance,
            and recommended next steps before visiting an Akshaya centre.
          </Text>
        </View>

        <Text
          style={[
            styles.sectionTitle,
            {
              color: colors.text,
            },
          ]}
        >
          Project principles
        </Text>

        <View style={styles.principleList}>
          {principles.map((principle) => (
            <View
              key={principle.title}
              style={[
                styles.principleCard,
                {
                  backgroundColor: colors.surface,
                  borderColor: colors.border,
                },
              ]}
            >
              <View
                style={[
                  styles.principleIcon,
                  {
                    backgroundColor: colors.primarySoft,
                  },
                ]}
              >
                <Ionicons
                  name={principle.icon}
                  size={20}
                  color={colors.primaryDark}
                />
              </View>

              <View style={styles.principleTextArea}>
                <Text
                  style={[
                    styles.principleTitle,
                    {
                      color: colors.text,
                    },
                  ]}
                >
                  {principle.title}
                </Text>

                <Text
                  style={[
                    styles.principleText,
                    {
                      color: colors.textMuted,
                    },
                  ]}
                >
                  {principle.text}
                </Text>
              </View>
            </View>
          ))}
        </View>

        <View
          style={[
            styles.warningCard,
            {
              backgroundColor: colors.warningBackground,
            },
          ]}
        >
          <Ionicons
            name="alert-circle-outline"
            size={22}
            color={colors.warning}
          />

          <View style={styles.warningTextArea}>
            <Text
              style={[
                styles.warningTitle,
                {
                  color: colors.warning,
                },
              ]}
            >
              Important advisory limitation
            </Text>

            <Text
              style={[
                styles.warningText,
                {
                  color: colors.warning,
                },
              ]}
            >
              The application does not approve or submit government
              applications, perform biometric verification, access private
              Aadhaar data, confirm a citizen’s official identity, verify
              document authenticity, or replace government portals and Akshaya
              operators.
            </Text>
          </View>
        </View>

        <View
          style={[
            styles.futureCard,
            {
              backgroundColor: colors.surface,
              borderColor: colors.border,
            },
          ]}
        >
          <Ionicons
            name="language-outline"
            size={22}
            color={colors.primaryDark}
          />

          <View style={styles.futureTextArea}>
            <Text
              style={[
                styles.futureTitle,
                {
                  color: colors.text,
                },
              ]}
            >
              Malayalam as a future enhancement
            </Text>

            <Text
              style={[
                styles.futureText,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              Malayalam support will be added only after testing multilingual
              models, retrieval quality, government terminology, citation
              preservation, translation quality, and text-to-speech
              pronunciation. The English MVP remains the priority.
            </Text>
          </View>
        </View>

        <Text
          style={[
            styles.footerText,
            {
              color: colors.textMuted,
            },
          ]}
        >
          Prototype status: the mobile frontend is complete in structure. The
          next stage connects FastAPI, curated official documents, RAG
          retrieval, citation verification, confidence scoring, and English
          text-to-speech.
        </Text>
      </ScrollView>
    </SafeAreaView>
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
    paddingBottom: 43,
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

  headerTextArea: {
    flex: 1,
  },

  eyebrow: {
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 1,
    marginBottom: 7,
  },

  title: {
    fontSize: 26,
    fontWeight: "800",
    letterSpacing: -0.4,
  },

  subtitle: {
    fontSize: 12,
    lineHeight: 18,
    marginTop: 7,
  },

  introCard: {
    alignItems: "center",
    borderRadius: 19,
    marginTop: 22,
    padding: 20,
  },

  introIcon: {
    alignItems: "center",
    borderRadius: 16,
    height: 56,
    justifyContent: "center",
    width: 56,
  },

  introTitle: {
    fontSize: 18,
    fontWeight: "800",
    lineHeight: 24,
    marginTop: 14,
    textAlign: "center",
  },

  introText: {
    fontSize: 12,
    lineHeight: 19,
    marginTop: 9,
    maxWidth: 520,
    textAlign: "center",
  },

  sectionTitle: {
    fontSize: 18,
    fontWeight: "800",
    marginTop: 26,
  },

  principleList: {
    gap: 9,
    marginTop: 14,
  },

  principleCard: {
    alignItems: "flex-start",
    borderRadius: 16,
    borderWidth: 1,
    flexDirection: "row",
    gap: 10,
    padding: 13,
  },

  principleIcon: {
    alignItems: "center",
    borderRadius: 11,
    height: 39,
    justifyContent: "center",
    width: 39,
  },

  principleTextArea: {
    flex: 1,
  },

  principleTitle: {
    fontSize: 13,
    fontWeight: "800",
  },

  principleText: {
    fontSize: 11,
    lineHeight: 17,
    marginTop: 4,
  },

  warningCard: {
    alignItems: "flex-start",
    borderRadius: 17,
    flexDirection: "row",
    gap: 10,
    marginTop: 17,
    padding: 15,
  },

  warningTextArea: {
    flex: 1,
  },

  warningTitle: {
    fontSize: 13,
    fontWeight: "800",
  },

  warningText: {
    fontSize: 11,
    fontWeight: "600",
    lineHeight: 18,
    marginTop: 5,
  },

  futureCard: {
    alignItems: "flex-start",
    borderRadius: 17,
    borderWidth: 1,
    flexDirection: "row",
    gap: 10,
    marginTop: 11,
    padding: 15,
  },

  futureTextArea: {
    flex: 1,
  },

  futureTitle: {
    fontSize: 13,
    fontWeight: "800",
  },

  futureText: {
    fontSize: 11,
    lineHeight: 18,
    marginTop: 4,
  },

  footerText: {
    fontSize: 10,
    lineHeight: 16,
    marginTop: 24,
    textAlign: "center",
  },
});