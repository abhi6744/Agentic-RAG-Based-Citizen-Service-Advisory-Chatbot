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

import ServiceCategoryCard from "../components/ServiceCategoryCard";
import { SERVICE_CATEGORIES } from "../constants/services";
import { useTheme } from "../contexts/ThemeContext";

const workflowSteps = [
  {
    number: "01",
    icon: "camera-outline" as const,
    title: "Capture clear images",
    text: "When uploading a document for analysis, ensure good lighting and clear text. Blurry images will be rejected.",
  },
  {
    number: "02",
    icon: "eye-off-outline" as const,
    title: "Hide sensitive numbers",
    text: "Physically cover full Aadhaar numbers, passwords, and CVVs before capturing the image to protect your privacy.",
  },
  {
    number: "03",
    icon: "folder-open-outline" as const,
    title: "Organize physical copies",
    text: "Before visiting an Akshaya center, gather all original documents and keep self-attested photocopies ready.",
  },
];

export default function DocumentsScreen() {
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
            <Ionicons
              name="arrow-back"
              size={22}
              color={colors.text}
            />
          </Pressable>

          <View style={styles.headerText}>
            <Text
              style={[
                styles.eyebrow,
                {
                  color: colors.primary,
                },
              ]}
            >
              DOCUMENT PREPARATION
            </Text>

            <Text
              style={[
                styles.title,
                {
                  color: colors.text,
                },
              ]}
            >
              How to prepare your documents
            </Text>

            <Text
              style={[
                styles.subtitle,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              Guidelines for submitting document images and gathering physical copies for your Akshaya visit.
            </Text>
          </View>
        </View>

        <View
          style={[
            styles.statusCard,
            {
              backgroundColor: colors.primarySoft,
            },
          ]}
        >
          <View
            style={[
              styles.statusIcon,
              {
                backgroundColor: colors.primary,
              },
            ]}
          >
            <Ionicons
              name="language-outline"
              size={21}
              color="#FFFFFF"
            />
          </View>

          <View style={styles.statusContent}>
            <Text
              style={[
                styles.statusTitle,
                {
                  color: colors.text,
                },
              ]}
            >
              English-first advisory mode
            </Text>

            <Text
              style={[
                styles.statusText,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              The first version is designed and tested in English. Malayalam
              support will be considered only after quality evaluation.
            </Text>
          </View>
        </View>

        <Text
          style={[
            styles.sectionTitle,
            {
              color: colors.text,
            },
          ]}
        >
          Supported service areas
        </Text>

        <Text
          style={[
            styles.sectionSubtitle,
            {
              color: colors.textMuted,
            },
          ]}
        >
          Choose the topic closest to your situation.
        </Text>

        <View style={styles.serviceGrid}>
          {SERVICE_CATEGORIES.map((service) => (
            <ServiceCategoryCard
              key={service.id}
              category={service.id}
              title={service.title}
              description={service.description}
              icon={service.icon}
            />
          ))}
        </View>

        <View style={styles.workflowHeader}>
          <Text
            style={[
              styles.sectionTitle,
              {
                color: colors.text,
              },
            ]}
          >
            How the advisory process works
          </Text>

          <Text
            style={[
              styles.sectionSubtitle,
              {
                color: colors.textMuted,
              },
            ]}
          >
            The final system will use a controlled agentic RAG workflow.
          </Text>
        </View>

        <View style={styles.workflowList}>
          {workflowSteps.map((step) => (
            <View
              key={step.number}
              style={[
                styles.workflowCard,
                {
                  backgroundColor: colors.surface,
                  borderColor: colors.border,
                },
              ]}
            >
              <View
                style={[
                  styles.stepNumber,
                  {
                    backgroundColor: colors.primarySoft,
                  },
                ]}
              >
                <Text
                  style={[
                    styles.stepNumberText,
                    {
                      color: colors.primary,
                    },
                  ]}
                >
                  {step.number}
                </Text>
              </View>

              <View
                style={[
                  styles.workflowIcon,
                  {
                    backgroundColor: colors.surfaceMuted,
                  },
                ]}
              >
                <Ionicons
                  name={step.icon}
                  size={20}
                  color={colors.primary}
                />
              </View>

              <View style={styles.workflowContent}>
                <Text
                  style={[
                    styles.workflowTitle,
                    {
                      color: colors.text,
                    },
                  ]}
                >
                  {step.title}
                </Text>

                <Text
                  style={[
                    styles.workflowText,
                    {
                      color: colors.textMuted,
                    },
                  ]}
                >
                  {step.text}
                </Text>
              </View>
            </View>
          ))}
        </View>

        <View
          style={[
            styles.capabilityCard,
            {
              backgroundColor: colors.surface,
              borderColor: colors.border,
            },
          ]}
        >
          <View style={styles.capabilityHeader}>
            <Ionicons
              name="checkmark-circle-outline"
              size={21}
              color={colors.accent}
            />

            <Text
              style={[
                styles.capabilityTitle,
                {
                  color: colors.text,
                },
              ]}
            >
              Supported document types
            </Text>
          </View>

          <CapabilityItem
            text="JPG, PNG, and WEBP images"
            colors={colors}
          />

          <CapabilityItem
            text="Maximum file size: 5MB"
            colors={colors}
          />

          <CapabilityItem
            text="Aadhaar update forms and letters"
            colors={colors}
          />

          <CapabilityItem
            text="Kerala Ration card applications"
            colors={colors}
          />

          <CapabilityItem
            text="Scholarship portal forms"
            colors={colors}
          />

          <CapabilityItem
            text="General identity proofs (Voter ID, PAN)"
            colors={colors}
          />
        </View>

        <View
          style={[
            styles.limitationsCard,
            {
              backgroundColor: colors.warningBackground,
            },
          ]}
        >
          <View style={styles.limitationsHeader}>
            <Ionicons
              name="alert-circle-outline"
              size={21}
              color={colors.warning}
            />

            <Text
              style={[
                styles.limitationsTitle,
                {
                  color: colors.warning,
                },
              ]}
            >
              Important limitations
            </Text>
          </View>

          <Text
            style={[
              styles.limitationsText,
              {
                color: colors.warning,
              },
            ]}
          >
            The vision capability is designed to identify the type of document to provide better context for your questions. It DOES NOT verify the authenticity of the document, process applications, or permanently store your uploads.
          </Text>
        </View>

        <Pressable
          onPress={() => router.push("/chat")}
          accessibilityRole="button"
          accessibilityLabel="Start an advisory chat"
          style={({ pressed }) => [
            styles.startButton,
            {
              backgroundColor: colors.primary,
              opacity: pressed ? 0.78 : 1,
            },
          ]}
        >
          <Ionicons
            name="chatbubble-ellipses-outline"
            size={20}
            color="#FFFFFF"
          />

          <Text style={styles.startButtonText}>
            Start an advisory chat
          </Text>

          <Ionicons
            name="arrow-forward"
            size={19}
            color="#FFFFFF"
          />
        </Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

function CapabilityItem({
  text,
  colors,
}: {
  text: string;
  colors: any;
}) {
  return (
    <View style={styles.capabilityItem}>
      <Ionicons
        name="checkmark"
        size={16}
        color={colors.accent}
      />

      <Text
        style={[
          styles.capabilityText,
          {
            color: colors.textMuted,
          },
        ]}
      >
        {text}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },

  content: {
    alignSelf: "center",
    maxWidth: 1000,
    padding: 22,
    paddingBottom: 55,
    width: "100%",
  },

  headerRow: {
    alignItems: "flex-start",
    flexDirection: "row",
    gap: 10,
  },

  backButton: {
    alignItems: "center",
    height: 40,
    justifyContent: "center",
    width: 40,
  },

  headerText: {
    flex: 1,
  },

  eyebrow: {
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 1.1,
    marginBottom: 9,
  },

  title: {
    fontSize: 30,
    fontWeight: "800",
    letterSpacing: -0.5,
    lineHeight: 37,
  },

  subtitle: {
    fontSize: 15,
    lineHeight: 23,
    marginTop: 10,
  },

  statusCard: {
    alignItems: "flex-start",
    borderRadius: 17,
    flexDirection: "row",
    gap: 12,
    marginTop: 25,
    padding: 16,
  },

  statusIcon: {
    alignItems: "center",
    borderRadius: 12,
    height: 42,
    justifyContent: "center",
    width: 42,
  },

  statusContent: {
    flex: 1,
  },

  statusTitle: {
    fontSize: 14,
    fontWeight: "800",
  },

  statusText: {
    fontSize: 13,
    lineHeight: 20,
    marginTop: 5,
  },

  sectionTitle: {
    fontSize: 20,
    fontWeight: "800",
    marginTop: 31,
  },

  sectionSubtitle: {
    fontSize: 13,
    lineHeight: 19,
    marginTop: 5,
  },

  serviceGrid: {
    alignItems: "stretch",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
    marginTop: 16,
  },

  workflowHeader: {
    marginTop: 22,
  },

  workflowList: {
    gap: 10,
    marginTop: 16,
  },

  workflowCard: {
    alignItems: "center",
    borderRadius: 16,
    borderWidth: 1,
    flexDirection: "row",
    gap: 11,
    padding: 14,
  },

  stepNumber: {
    alignItems: "center",
    borderRadius: 10,
    height: 38,
    justifyContent: "center",
    width: 38,
  },

  stepNumberText: {
    fontSize: 11,
    fontWeight: "800",
  },

  workflowIcon: {
    alignItems: "center",
    borderRadius: 10,
    height: 38,
    justifyContent: "center",
    width: 38,
  },

  workflowContent: {
    flex: 1,
  },

  workflowTitle: {
    fontSize: 14,
    fontWeight: "800",
  },

  workflowText: {
    fontSize: 12,
    lineHeight: 18,
    marginTop: 4,
  },

  capabilityCard: {
    borderRadius: 17,
    borderWidth: 1,
    marginTop: 24,
    padding: 17,
  },

  capabilityHeader: {
    alignItems: "center",
    flexDirection: "row",
    gap: 8,
    marginBottom: 13,
  },

  capabilityTitle: {
    fontSize: 15,
    fontWeight: "800",
  },

  capabilityItem: {
    alignItems: "flex-start",
    flexDirection: "row",
    gap: 9,
    marginBottom: 9,
  },

  capabilityText: {
    flex: 1,
    fontSize: 13,
    lineHeight: 19,
  },

  limitationsCard: {
    borderRadius: 17,
    marginTop: 12,
    padding: 17,
  },

  limitationsHeader: {
    alignItems: "center",
    flexDirection: "row",
    gap: 8,
    marginBottom: 8,
  },

  limitationsTitle: {
    fontSize: 15,
    fontWeight: "800",
  },

  limitationsText: {
    fontSize: 13,
    lineHeight: 20,
  },

  startButton: {
    alignItems: "center",
    borderRadius: 13,
    flexDirection: "row",
    gap: 9,
    justifyContent: "center",
    marginTop: 20,
    padding: 16,
  },

  startButtonText: {
    color: "#FFFFFF",
    flex: 1,
    fontSize: 15,
    fontWeight: "800",
  },
});