import { API_BASE_URL } from '../config/api';
import { Ionicons } from "@expo/vector-icons";
import { router, useLocalSearchParams } from "expo-router";
import * as Speech from 'expo-speech';
import * as Clipboard from 'expo-clipboard';
import { Image as ExpoImage } from 'expo-image';
import React, { useEffect, useMemo, useRef, useState } from "react";
import {
  Alert,
  Animated,
  LayoutAnimation,
  Image,
  KeyboardAvoidingView,
  Linking,
  Modal,
  Platform,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  useWindowDimensions,
  View,
  UIManager,
} from "react-native";

import AppDrawerContent from "../components/AppDrawerContent";
import DocumentImage from "../components/DocumentImage";
import ChatImagePreview from "../components/ChatImagePreview";
import QueryComposer, { ChatImage } from "../components/QueryComposer";
import { useTheme } from "../contexts/ThemeContext";
import { getDeviceId } from "../utils/device";
import { cleanText } from "../utils/cleanResponseText";
import { normalizeChatResponse } from "../utils/responseAdapter";

if (Platform.OS === 'android' && UIManager.setLayoutAnimationEnabledExperimental) {
  UIManager.setLayoutAnimationEnabledExperimental(true);
}

const LOGO = require("../../assets/images/akshaya-logo.png");

const stripForSpeech = (text: string) => {
  if (!text) return "";
  return text.replace(/[#*%_]/g, "").trim();
};

const cleanString = (text: string) => {
  if (!text) return "";
  return text.replace(/[#%]/g, "").trim();
};

function FormattedText({ text, style }: { text: string; style?: any }) {
  if (!text) return null;
  // Remove # and % as requested, but keep ** for parsing
  const cleaned = text.replace(/[#%]/g, "");
  const parts = cleaned.split(/\*\*(.*?)\*\*/g);

  return (
    <Text style={style}>
      {parts.map((part, index) => {
        const isBold = index % 2 === 1;
        return (
          <Text key={index} style={isBold ? { fontWeight: "bold" } : {}}>
            {part}
          </Text>
        );
      })}
    </Text>
  );
}

type SourceCitation = {
  source_title: string;
  source_url?: string;
  authority: string;
  retrieved_date?: string;
};

type AnswerData = {
  summary: string;
  eligibility: string[];
  documents: string[];
  next_steps: string[];
  where_to_go: string[];
  warning: string;
};

type BackendData = {
  success?: boolean;
  status?: string;
  message_id: number;
  conversation_id: number;
  response_type?: string;
  detected_service?: string;
  answer: AnswerData;
  citations: SourceCitation[];
  confidence_score: number;
  confidence_level: string;
  requires_official_verification: boolean;
  verification_message?: string;
  image_description?: string;
  privacy_warning?: string;
  image_analysis?: {
    document_type: string;
    confidence: number;
    sensitive_data_hidden: boolean;
  };
};

type Message = {
  id: string;
  role: "assistant" | "user";
  text: string;
  inputType?: "text" | "voice";
  imageUri?: string;
  imageMimeType?: string;
  imageFileName?: string;
  backendData?: BackendData;
};

const suggestions = [
  { text: "What documents do I need for a new ration card in Kerala?", icon: "list-outline" as const },
  { text: "Am I eligible for a National Scholarship, and what documents are needed?", icon: "school-outline" as const },
  { text: "My name in Aadhaar doesn't match my certificate  -  how do I update it?", icon: "id-card-outline" as const },
];

const welcomeMessage: Message = {
  id: "welcome",
  role: "assistant",
  text: "Describe your issue in your own words  -  Aadhaar, ration card, or scholarship. You can also attach a photo of a document.",
};

async function uriToWebFile(
  uri: string,
  fileName: string,
  mimeType: string,
): Promise<File> {
  const response = await fetch(uri);

  if (!response.ok) {
    throw new Error("Unable to read selected image");
  }

  const blob = await response.blob();

  if (blob.size === 0) {
    throw new Error("Selected image is empty");
  }

  return new File([blob], fileName, {
    type: mimeType || blob.type || "image/jpeg",
  });
}

export default function HomeChatScreen() {
  const { colors } = useTheme();
  const { width } = useWindowDimensions();

  const params = useLocalSearchParams<{
    query?: string | string[];
    conversation_id?: string | string[];
  }>();

  const initialQuery = useMemo(() => {
    if (Array.isArray(params.query)) {
      return params.query[0] ?? "";
    }
    return params.query ?? "";
  }, [params.query]);

  const paramConvId = useMemo(() => {
    if (Array.isArray(params.conversation_id)) {
      return params.conversation_id[0] ?? null;
    }
    return params.conversation_id ?? null;
  }, [params.conversation_id]);

  const scrollRef = useRef<ScrollView>(null);
  const processedQueryRef = useRef<string | null>(null);

  const [drawerVisible, setDrawerVisible] = useState(false);
  const [transcriptVisible, setTranscriptVisible] = useState(false);

  const exportTranscript = () => {
    let transcriptText = "Conversation Transcript\n====================\n\n";
    messages.forEach(msg => {
      if (msg.role === "assistant") {
        transcriptText += `[Akshaya AI]:\n${msg.text}\n\n`;
      } else {
        const typeLabel = msg.inputType === "voice" ? " [Voice Input]" : "";
        transcriptText += `[You]${typeLabel}:\n${msg.text}\n\n`;
      }
    });

    if (Platform.OS === 'web') {
      const blob = new Blob([transcriptText], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `transcript-${new Date().getTime()}.txt`;
      a.click();
    } else {
      // In a real app we'd use expo-file-system and expo-sharing, but Alert is ok for now.
      Alert.alert("Transcript", transcriptText);
    }
  };

  const [messages, setMessages] = useState<Message[]>([welcomeMessage]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [conversationId, setConversationId] = useState<number | null>(null);

  const isDesktop = width >= 800;
  const API_URL = API_BASE_URL;

  useEffect(() => {
    async function loadConversation() {
      if (!paramConvId) return;
      
      const idStr = paramConvId.toString();
      // Only fetch if it changed
      if (conversationId?.toString() === idStr && messages.length > 1) return;

      try {
        setIsProcessing(true);
        const res = await fetch(`${API_URL}/conversations/${idStr}`);
        if (!res.ok) throw new Error("Failed to load conversation");
        const data = await res.json();
        
        setConversationId(data.conversation_id);
        
        const loadedMessages: Message[] = [welcomeMessage];
        for (const msg of data.messages) {
          if (msg.role === "user") {
                loadedMessages.push({
                  id: `user-${msg.id}`,
                  role: "user",
                  text: msg.text_content,
                  inputType: (msg as any).input_type || "text",
                  imageUri: msg.image_path ? (msg.image_path.startsWith('http') ? msg.image_path : `${API_URL}/uploads/${msg.image_path.split(/[/\\]/).pop()}`) : undefined,
                });
          } else {
            loadedMessages.push({
              id: `assistant-${msg.id}`,
              role: "assistant",
              text: msg.text_content,
              backendData: {
                message_id: msg.id,
                conversation_id: data.conversation_id,
                detected_service: msg.detected_service,
                answer: { summary: msg.text_content || "", eligibility: [], documents: [], next_steps: [], where_to_go: [], warning: "" },
                citations: msg.sources || [],
                confidence_score: msg.confidence_score,
                confidence_level: msg.confidence_score > 0.7 ? "high" : "low",
                requires_official_verification: msg.requires_verification,
              }
            });
          }
        }
        setMessages(loadedMessages);
      } catch (err) {
        console.error(err);
      } finally {
        setIsProcessing(false);
      }
    }
    
    loadConversation();
  }, [paramConvId]);

  useEffect(() => {
    if (
      initialQuery.length > 0 &&
      processedQueryRef.current !== initialQuery
    ) {
      processedQueryRef.current = initialQuery;
      submitQuestion(initialQuery);
    }
  }, [initialQuery]);

  useEffect(() => {
    const timer = setTimeout(() => {
      scrollRef.current?.scrollToEnd({ animated: true });
    }, 150);

    return () => clearTimeout(timer);
  }, [messages, isProcessing]);

  function startNewChat() {
    try {
      setMessages([welcomeMessage]);
      setConversationId(null);
      processedQueryRef.current = null;
      router.replace("/");
    } catch (e) {
      console.error("[App] Error in startNewChat:", e);
    }
  }

  async function submitQuestion(question: string, image?: ChatImage, inputType?: "text" | "voice") {
    const cleanedQuestion = question.trim();

    if ((!cleanedQuestion && !image) || isProcessing) {
      return;
    }

    LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
    setMessages((currentMessages) => [
      ...currentMessages,
      {
        id: `user-${Date.now()}`,
        role: "user",
        text: cleanedQuestion,
        inputType: inputType || "text",
        imageUri: image?.uri,
          imageMimeType: image?.mimeType,
          imageFileName: image?.fileName,
      },
    ]);

    setIsProcessing(true);

    try {
      const actualDeviceId = await getDeviceId();
      const formData = new FormData();
      formData.append("device_id", actualDeviceId);
      formData.append("input_type", inputType || "text");
      if (cleanedQuestion) {
        formData.append("text", cleanedQuestion);
      }

      if (image) {
        if (Platform.OS === 'web') {
          const file = await uriToWebFile(image.uri, image.fileName, image.mimeType);
          if (!file) {
            throw new Error("Invalid file object created");
          }
          if (file.size === 0) {
            throw new Error("The uploaded file is empty.");
          }
          const allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
          if (!allowedTypes.includes(file.type)) {
            throw new Error("Please upload a JPG, PNG, or WEBP document image.");
          }
          formData.append("image", file);
        } else {
          formData.append("image", {
            uri: image.uri,
            name: image.fileName,
            type: image.mimeType,
          } as any);
        }
      }

      if (conversationId) {
        formData.append("conversation_id", conversationId.toString());
      }

      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        body: formData,
      });

      const rawData = await response.json();

      if (!response.ok) {
        if (rawData && rawData.message) {
          throw new Error(rawData.message);
        }
        throw new Error(`API error: ${response.status}`);
      }
      const data: BackendData = normalizeChatResponse(rawData);
      
      setConversationId(data.conversation_id);

      LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: data.message_id ? data.message_id.toString() : `msg-${Date.now()}`,
          role: "assistant",
          text: data.answer.summary,
          backendData: data,
        },
      ]);
    } catch (error: any) {
      console.error("Chat error:", {
        message: error.message,
        name: error.name,
        url: `${API_URL}/chat`,
        method: "POST"
      });
      
      let errorMessage = "An unexpected error occurred.";
      
      if (error instanceof TypeError && error.message.includes("Failed to fetch")) {
        // Network-level failure (CORS, backend down, wrong URL)
        errorMessage = "Can't reach the assistant right now - check your connection and try again.";
      } else if (error.message && error.message.startsWith("API error:")) {
        // HTTP error (got a response, but it was 4xx/5xx)
        errorMessage = "The server encountered an error processing your request. Please try again.";
      } else if (error instanceof SyntaxError) {
        // JSON parsing failure
        errorMessage = "Received an invalid response from the server. Please try again.";
      } else {
        errorMessage = "Something went wrong: " + error.message;
      }

      LayoutAnimation.configureNext(LayoutAnimation.Presets.easeInEaseOut);
      setMessages((currentMessages) => [
        ...currentMessages,
        {
          id: `error-${Date.now()}`,
          role: "assistant",
          text: errorMessage,
        },
      ]);
    } finally {
      setIsProcessing(false);
    }
  }

  const hasUserMessage = messages.some(
    (message) => message.role === "user",
  );

  return (
    <SafeAreaView
      style={[
        styles.safeArea,
        {
          backgroundColor: colors.background,
        },
      ]}
    >
      <KeyboardAvoidingView
        style={styles.keyboardView}
        behavior={Platform.OS === "ios" ? "padding" : undefined}
      >
        <View
          style={[
            styles.header,
            {
              backgroundColor: colors.surface,
              borderBottomColor: colors.border,
            },
          ]}
        >
          <View
            style={[
              styles.headerInner,
              isDesktop && styles.desktopHeaderInner,
            ]}
          >
            <Pressable
              onPress={() => setDrawerVisible(true)}
              accessibilityRole="button"
              accessibilityLabel="Open application menu"
              style={[
                styles.headerButton,
                {
                  backgroundColor: colors.primarySoft,
                },
              ]}
            >
              <Ionicons
                name="menu-outline"
                size={25}
                color={colors.primaryDark}
              />
            </Pressable>

            <Pressable
              onPress={startNewChat}
              accessibilityRole="button"
              accessibilityLabel="Start a new chat"
              style={styles.brandButton}
            >
              <View style={[styles.brandLogoContainer, { borderWidth: 0 }]}>
                <Image
                  source={LOGO}
                  resizeMode="contain"
                  style={styles.brandLogoImage}
                  accessibilityLabel="Akshaya Advisory logo"
                />
              </View>

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
            </Pressable>

          </View>
        </View>

        <ScrollView
          ref={scrollRef}
          showsVerticalScrollIndicator={false}
          keyboardShouldPersistTaps="handled"
          contentContainerStyle={[
            styles.content,
            isDesktop && styles.desktopContent,
          ]}
        >
          {messages.length === 1 && (
            <View style={styles.welcomeArea}>
              <View style={[styles.heroLogoWrapper, { backgroundColor: colors.primarySoft, borderRadius: 40 }]}>
                <Ionicons
                  name="shield-checkmark-outline"
                  size={32}
                  color={colors.primaryDark}
                />
              </View>

              <Text style={[styles.welcomeTitle, { color: colors.text }]}>
                How can we help today?
              </Text>

              <Text style={[styles.welcomeSubtitle, { color: colors.textMuted }]}>
                {welcomeMessage.text}
              </Text>

              <View style={[styles.assuranceCard, { backgroundColor: colors.primarySoft }]}>
                <Ionicons name="shield-checkmark-outline" size={18} color={colors.primaryDark} />
                <Text style={[styles.assuranceText, { color: colors.primaryDark }]}>
                  Clear advisory guidance before you visit an Akshaya centre.
                </Text>
              </View>

              <Text style={[styles.suggestionHeading, { color: colors.textMuted, fontFamily: 'Manrope_600SemiBold', fontSize: 13 }]}>
                Try asking
              </Text>

              <View style={styles.suggestions}>
                {suggestions.map((suggestion, index) => (
                  <Pressable
                    key={index}
                    onPress={() => submitQuestion(suggestion.text)}
                    accessibilityRole="button"
                    accessibilityLabel={`Ask: ${suggestion.text}`}
                    style={({ pressed }) => [
                      styles.suggestionCard,
                      {
                        backgroundColor: colors.surface,
                        borderColor: colors.border,
                        opacity: pressed ? 0.76 : 1,
                      },
                    ]}
                  >
                    <View style={[styles.suggestionIcon, { backgroundColor: colors.primarySoft }]}>
                      <Ionicons name={suggestion.icon} size={18} color={colors.primaryDark} />
                    </View>
                    <Text style={[styles.suggestionText, { color: colors.text }]}>
                      {suggestion.text}
                    </Text>
                    <Ionicons name="chevron-forward" size={16} color={colors.textLight} />
                  </Pressable>
                ))}
              </View>
            </View>
          )}

          {messages.filter(msg => msg.id !== 'welcome').map((message, index, filteredMessages) => {
            // Find the immediately preceding user message for retries
            let lastUserQuery = "";
            let lastUserImage: ChatImage | undefined = undefined;
            if (message.backendData?.response_type === 'service_unavailable') {
              for (let i = index - 1; i >= 0; i--) {
                if (filteredMessages[i].role === 'user') {
                  lastUserQuery = filteredMessages[i].text;
                  lastUserImage = filteredMessages[i].imageUri ? { uri: filteredMessages[i].imageUri as string, mimeType: filteredMessages[i].imageMimeType || "image/jpeg", fileName: filteredMessages[i].imageFileName || "upload.jpg", width: 200, height: 200 } : undefined;
                  break;
                }
              }
            }
            
            return (
              <React.Fragment key={message.id}>
                <MessageBubble 
                  message={message} 
                  onRetry={lastUserQuery ? () => submitQuestion(lastUserQuery, lastUserImage) : undefined} 
                />
                {message.role === 'assistant' && message.backendData && 
                 (message.backendData.response_type === 'answer' || message.backendData.response_type === 'fallback') && (
                  <AdvisoryDetails data={message.backendData} />
                )}
              </React.Fragment>
            );
          })}

          {isProcessing && <TypingIndicator />}
        </ScrollView>

        <View style={styles.composerArea}>
          <View style={[styles.composerWrapper, isDesktop && styles.desktopComposerWrapper]}>
            <QueryComposer onSubmit={submitQuestion} disabled={isProcessing} placeholder="Describe your issue or question..." />
          </View>
        </View>
      </KeyboardAvoidingView>

      <Modal visible={drawerVisible} transparent animationType="slide" onRequestClose={() => setDrawerVisible(false)}>
        <View style={[styles.drawerOverlay, { backgroundColor: colors.overlay }]}>
          <View style={[styles.drawerPanel, { backgroundColor: colors.surface }]}>
            <Pressable onPress={() => setDrawerVisible(false)} style={[styles.closeButton, { backgroundColor: colors.primarySoft }]}>
              <Ionicons name="close" size={24} color={colors.primaryDark} />
            </Pressable>
            <AppDrawerContent onClose={() => setDrawerVisible(false)} onViewTranscript={() => setTranscriptVisible(true)} />
          </View>
          <Pressable onPress={() => setDrawerVisible(false)} style={styles.drawerDismissArea} />
        </View>
      </Modal>

      <Modal visible={transcriptVisible} animationType="slide" presentationStyle="pageSheet" onRequestClose={() => setTranscriptVisible(false)}>
        <SafeAreaView style={{ flex: 1, backgroundColor: colors.background }}>
          <View style={[styles.header, { backgroundColor: colors.surface, borderBottomColor: colors.border }]}>
            <View style={styles.headerInner}>
              <Pressable onPress={() => setTranscriptVisible(false)} style={[styles.headerButton, { backgroundColor: colors.primarySoft }]}>
                <Ionicons name="close" size={24} color={colors.primaryDark} />
              </Pressable>
              <View style={styles.brandTextArea}>
                <Text style={[styles.brandTitle, { color: colors.text }]}>Transcript</Text>
              </View>
              <Pressable onPress={exportTranscript} style={[styles.headerButton, { backgroundColor: colors.primarySoft }]}>
                <Ionicons name="download-outline" size={24} color={colors.primaryDark} />
              </Pressable>
            </View>
          </View>
          <ScrollView style={{ flex: 1, padding: 16 }}>
            {messages.map((msg, idx) => (
              <View key={`ts-${msg.id}-${idx}`} style={{ marginBottom: 16, backgroundColor: msg.role === 'user' ? colors.primarySoft : colors.surface, padding: 12, borderRadius: 8 }}>
                <Text style={{ fontWeight: 'bold', color: msg.role === 'user' ? colors.primaryDark : colors.text, marginBottom: 4 }}>
                  {msg.role === 'user' ? `You ${msg.inputType === 'voice' ? '(Voice Input)' : ''}` : 'Akshaya AI'}
                </Text>
                <Text style={{ color: msg.role === 'user' ? colors.primaryDark : colors.text, opacity: 0.9, lineHeight: 20 }}>
                  {msg.text}
                </Text>
              </View>
            ))}
          </ScrollView>
        </SafeAreaView>
      </Modal>
    </SafeAreaView>
  );
}

function MessageBubble({ message, onRetry }: { message: Message, onRetry?: () => void }) {
  const { colors } = useTheme();
  const isUser = message.role === "user";

  const copyToClipboard = async () => {
    await Clipboard.setStringAsync(message.text);
  };

  return (
    <View style={[styles.messageRow, isUser ? styles.userRow : styles.assistantRow]}>
      {!isUser && (
        <View style={styles.assistantAvatarImageContainer}>
          <Image source={LOGO} resizeMode="contain" style={styles.assistantAvatarImage} />
        </View>
      )}

      <View
        style={[
          styles.messageBubble,
          isUser ? styles.userBubble : styles.assistantBubble,
          {
            backgroundColor: isUser ? colors.primary : colors.surface,
            borderColor: isUser ? colors.primary : colors.border,
            borderWidth: 1, // Cleaner without border in dark mode
            shadowColor: "#000",
            shadowOffset: { width: 0, height: 1 },
            shadowOpacity: 0.05,
            shadowRadius: 2,
            elevation: 2,
            position: 'relative'
          },
        ]}
      >
          {message.imageUri ? (
            <DocumentImage 
              uri={message.imageUri} 
              style={{ width: 200, height: 200, borderRadius: 8, marginBottom: 8 }} 
            />
          ) : null}
          {isUser ? (
            <View>
              {message.inputType === "voice" && (
                <View style={{ flexDirection: "row", alignItems: "center", marginBottom: 4 }}>
                  <Ionicons name="mic" size={12} color={"#ffffff"} style={{ marginRight: 4 }} />
                  <Text style={{ fontSize: 10, color: "#ffffff", opacity: 0.8 }}>Voice Input</Text>
                </View>
              )}
              <Text style={[styles.messageText, { color: "#ffffff", fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif' }]}>
                {message.text}
              </Text>
            </View>
          ) : (
          <View>
            <FormattedText 
              text={message.text} 
              style={[
                styles.messageText, 
                { 
                  color: colors.text,
                  fontFamily: Platform.OS === 'ios' ? 'Times New Roman' : 'serif',
                  fontSize: 16,
                  lineHeight: 24,
                }
              ]} 
            />
            <Pressable 
              onPress={copyToClipboard}
              style={{ position: 'absolute', bottom: -5, right: -5, padding: 8 }}
            >
              <Ionicons name="copy-outline" size={16} color={colors.textMuted} />
            </Pressable>
          </View>
        )}
      </View>

      {isUser && (
        <View style={[styles.assistantAvatarImageContainer, { backgroundColor: colors.primary, marginLeft: 8, marginRight: 0 }]}>
          <Ionicons name="person" size={16} color="#FFF" />
        </View>
      )}
    </View>
  );
}

function TypingIndicator() {
  const { colors } = useTheme();
  
  const opacity1 = useRef(new Animated.Value(0.3)).current;
  const opacity2 = useRef(new Animated.Value(0.3)).current;
  const opacity3 = useRef(new Animated.Value(0.3)).current;

  useEffect(() => {
    const animateDot = (anim: Animated.Value, delay: number) => {
      Animated.loop(
        Animated.sequence([
          Animated.timing(anim, {
            toValue: 1,
            duration: 400,
            useNativeDriver: true,
          }),
          Animated.timing(anim, {
            toValue: 0.3,
            duration: 400,
            useNativeDriver: true,
          }),
        ])
      ).start();
    };

    setTimeout(() => animateDot(opacity1, 0), 0);
    setTimeout(() => animateDot(opacity2, 200), 200);
    setTimeout(() => animateDot(opacity3, 400), 400);
  }, []);

  return (
    <View style={styles.assistantRow}>
      <View style={styles.assistantAvatarImageContainer}>
        <Image source={LOGO} resizeMode="contain" style={styles.assistantAvatarImage} />
      </View>

      <View
        style={[
          styles.typingCard,
          {
            backgroundColor: colors.surface,
            borderColor: colors.border,
            borderWidth: 1,
            shadowColor: "#000",
            shadowOffset: { width: 0, height: 1 },
            shadowOpacity: 0.05,
            shadowRadius: 2,
            elevation: 2,
            flexDirection: 'row',
            alignItems: 'center',
            paddingHorizontal: 16,
            paddingVertical: 12,
            minHeight: 48,
          },
        ]}
      >
        <Animated.View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: colors.primary, opacity: opacity1, marginRight: 4 }} />
        <Animated.View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: colors.primary, opacity: opacity2, marginRight: 4 }} />
        <Animated.View style={{ width: 6, height: 6, borderRadius: 3, backgroundColor: colors.primary, opacity: opacity3 }} />
      </View>
    </View>
  );
}

function AdvisoryDetails({ data }: { data: BackendData }) {
  const { colors } = useTheme();
  const [speechState, setSpeechState] = useState<'stopped' | 'playing' | 'paused'>('stopped');
  const [feedbackState, setFeedbackState] = useState<'initial' | 'helpful-submitted' | 'needs-improvement' | 'not-helpful-submitted'>('initial');
  const [feedbackComment, setFeedbackComment] = useState('');
  const API_URL = API_BASE_URL;

  const answer = data.answer;
  const hasDocuments = answer?.documents && answer.documents.length > 0;
  const hasEligibility = answer?.eligibility && answer.eligibility.length > 0;
  const hasNextSteps = answer?.next_steps && answer.next_steps.length > 0;
  const hasWhereToGo = answer?.where_to_go && answer.where_to_go.length > 0;
  
  const textToRead = stripForSpeech(
    (answer?.summary || "") + ". " +
    (answer?.documents?.join(". ") || "") + ". " +
    (answer?.next_steps?.join(". ") || "")
  );

  const speechStateRef = useRef<'stopped' | 'playing' | 'paused'>('stopped');
  const segmentRef = useRef(0);
  const segments = useMemo(() => textToRead.match(/[^.!?]+[.!?]+/g) || [textToRead], [textToRead]);

  const syncState = (st: 'stopped' | 'playing' | 'paused') => {
    speechStateRef.current = st;
    setSpeechState(st);
  };

  const playNextSegment = (idx: number) => {
    if (speechStateRef.current !== 'playing') return;
    if (idx >= segments.length) {
      syncState('stopped');
      segmentRef.current = 0;
      return;
    }
    Speech.speak(segments[idx], {
      language: 'en-IN',
      rate: 0.9,
      onDone: () => {
        if (speechStateRef.current === 'playing') {
          segmentRef.current = idx + 1;
          playNextSegment(idx + 1);
        }
      },
      onStopped: () => {}
    });
  };

  const handlePlay = () => {
    try {
      if (Platform.OS === 'android') {
        if (speechStateRef.current === 'paused') {
          syncState('playing');
          playNextSegment(segmentRef.current);
        } else {
          Speech.stop();
          segmentRef.current = 0;
          syncState('playing');
          playNextSegment(0);
        }
      } else {
        if (speechStateRef.current === 'paused') {
          Speech.resume();
          syncState('playing');
        } else {
          Speech.stop();
          syncState('playing');
          Speech.speak(textToRead, { 
            language: 'en-IN', 
            rate: 0.9,
            onDone: () => syncState('stopped'),
            onStopped: () => { if (speechStateRef.current !== 'paused') syncState('stopped'); }
          });
        }
      }
    } catch (e) {
      console.error("[AdvisoryDetails] Error in handlePlay:", e);
    }
  };

  const handlePause = () => {
    try {
      if (speechStateRef.current === 'playing') {
        syncState('paused');
        if (Platform.OS === 'android') {
          Speech.stop();
        } else {
          Speech.pause();
        }
      }
    } catch (e) {
      console.error("[AdvisoryDetails] Error in handlePause:", e);
    }
  };

  const handleStop = () => {
    try {
      syncState('stopped');
      segmentRef.current = 0;
      Speech.stop();
    } catch (e) {
      console.error("[AdvisoryDetails] Error in handleStop:", e);
    }
  };

  const submitFeedback = async (type: 'helpful' | 'not_helpful', comment?: string) => {
    try {
      await fetch(`${API_URL}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message_id: data.message_id, 
          feedback_type: type,
          comment: comment || undefined
        })
      });
    } catch (e) {
      console.error('Failed to submit feedback', e);
    }
  };

  const serviceLabel = data.detected_service === 'ration_card' ? 'Ration Card Services' :
                       data.detected_service === 'aadhaar' ? 'Aadhaar Services' :
                       data.detected_service === 'scholarship' ? 'Scholarship Services' : 
                       'General Inquiry';

  return (
    <View style={styles.detailsArea}>
      {data.requires_official_verification && (
        <View
          style={[
            styles.verificationCard,
            { backgroundColor: colors.warningBackground },
          ]}
        >
          <Ionicons name="information-circle-outline" size={20} color={colors.warning} />
          <View style={styles.verificationTextArea}>
            <Text style={[styles.verificationTitle, { color: colors.warning }]}>
              Official Verification Required
            </Text>
            <Text style={[styles.verificationText, { color: colors.warning }]}>
              {cleanText(answer?.warning || data.verification_message || "This information requires verification at your local Akshaya centre before proceeding.")}
            </Text>
          </View>
        </View>
      )}

      {/* Service Identified */}
      <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <View style={[styles.detailIcon, { backgroundColor: colors.primarySoft }]}>
          <Ionicons name="search-outline" size={19} color={colors.primaryDark} />
        </View>
        <View style={styles.detailTextArea}>
          <Text style={[styles.detailTitle, { color: colors.text }]}>Identified Service</Text>
          <Text style={[styles.detailText, { color: colors.textMuted }]}>{serviceLabel}</Text>
        </View>
      </View>


      {/* Documents & Eligibility */}
      <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border, flexDirection: 'column', alignItems: 'stretch' }]}>
        <View style={{flexDirection: 'row', alignItems: 'center', marginBottom: 12}}>
            <View style={[styles.detailIcon, { backgroundColor: colors.primarySoft, marginBottom: 0 }]}>
            <Ionicons name="documents-outline" size={19} color={colors.primaryDark} />
            </View>
            <Text style={[styles.detailTitle, { color: colors.text }]}>Documents and eligibility</Text>
        </View>
        
        {(!hasDocuments && !hasEligibility) ? (
            <Text style={[styles.detailText, { color: colors.textMuted }]}>The retrieved official sources did not provide a detailed checklist for this specific question.</Text>
        ) : (
            <View>
                {hasDocuments && (
                    <View style={{ marginBottom: hasEligibility ? 16 : 0 }}>
                        <Text style={[styles.detailTitle, { color: colors.text, fontSize: 13, marginBottom: 6 }]}>Documents to prepare</Text>
                        {answer.documents.map((doc, idx) => (
                            <View key={`doc-${idx}`} style={{ flexDirection: 'row', marginBottom: 6 }}>
                                <Text style={{ color: colors.primaryDark, fontSize: 16, fontWeight: 'bold', width: 16, lineHeight: 19 }}>•</Text>
                                <Text style={{ color: colors.text, flex: 1, fontSize: 13, lineHeight: 19 }}>{cleanText(doc)}</Text>
                            </View>
                        ))}
                    </View>
                )}
                {hasEligibility && (
                    <View>
                        <Text style={[styles.detailTitle, { color: colors.text, fontSize: 13, marginBottom: 6 }]}>Eligibility or important conditions</Text>
                        {answer.eligibility.map((elig, idx) => (
                            <View key={`elig-${idx}`} style={{ flexDirection: 'row', marginBottom: 6 }}>
                                <Text style={{ color: colors.primaryDark, fontSize: 16, fontWeight: 'bold', width: 16, lineHeight: 19 }}>•</Text>
                                <Text style={{ color: colors.text, flex: 1, fontSize: 13, lineHeight: 19 }}>{cleanText(elig)}</Text>
                            </View>
                        ))}
                    </View>
                )}
            </View>
        )}
      </View>

      {/* Next Steps & Where to Go */}
      <View style={[styles.detailCard, { backgroundColor: colors.surface, borderColor: colors.border, flexDirection: 'column', alignItems: 'stretch' }]}>
        <View style={{flexDirection: 'row', alignItems: 'center', marginBottom: 12}}>
            <View style={[styles.detailIcon, { backgroundColor: colors.primarySoft, marginBottom: 0 }]}>
            <Ionicons name="navigate-outline" size={19} color={colors.primaryDark} />
            </View>
            <Text style={[styles.detailTitle, { color: colors.text }]}>Recommended next steps</Text>
        </View>
        
        {(!hasNextSteps && !hasWhereToGo) ? (
            <Text style={[styles.detailText, { color: colors.textMuted }]}>No additional steps identified in the official sources.</Text>
        ) : (
            <View>
                {hasNextSteps && (
                    <View style={{ marginBottom: hasWhereToGo ? 16 : 0 }}>
                        {answer.next_steps.map((step, idx) => (
                            <View key={`step-${idx}`} style={{ flexDirection: 'row', marginBottom: 8 }}>
                                <Text style={{ color: colors.primaryDark, fontSize: 13, fontWeight: 'bold', width: 22, lineHeight: 19 }}>{idx + 1}.</Text>
                                <Text style={{ color: colors.text, flex: 1, fontSize: 13, lineHeight: 19 }}>{cleanText(step)}</Text>
                            </View>
                        ))}
                    </View>
                )}
                {hasWhereToGo && (
                    <View>
                        <Text style={[styles.detailTitle, { color: colors.text, fontSize: 13, marginBottom: 6 }]}>Where to apply or seek help</Text>
                        {answer.where_to_go.map((loc, idx) => (
                            <View key={`loc-${idx}`} style={{ flexDirection: 'row', marginBottom: 6 }}>
                                <Text style={{ color: colors.primaryDark, fontSize: 16, fontWeight: 'bold', width: 16, lineHeight: 19 }}>•</Text>
                                <Text style={{ color: colors.text, flex: 1, fontSize: 13, lineHeight: 19 }}>{cleanText(loc)}</Text>
                            </View>
                        ))}
                    </View>
                )}
            </View>
        )}
      </View>

      <View style={[styles.sourcesCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <View style={styles.sourcesHeader}>
          <Ionicons name="link-outline" size={19} color={colors.primaryDark} />
          <Text style={[styles.sourcesTitle, { color: colors.text }]}>
            Sources & Confidence ({cleanText(data.confidence_score ? (data.confidence_score * 100).toFixed(0) : "0")} - {cleanText(data.confidence_level ? data.confidence_level.toUpperCase() : "N/A")})
          </Text>
        </View>
        <View style={{ marginTop: 8 }}>
          {data.citations && data.citations.length > 0 ? (
            data.citations.map((c, i) => (
              <Pressable
                key={i}
                onPress={() => { if (c.source_url) Linking.openURL(c.source_url); }}
                style={({ pressed }) => [{ marginBottom: 6, opacity: pressed ? 0.7 : 1 }]}
              >
                <Text style={[styles.sourcesText, { color: colors.primary, textDecorationLine: c.source_url ? "underline" : "none", marginTop: 0 }]}>
                    {cleanText(c.source_title)} ({cleanText(c.authority)})
                </Text>
              </Pressable>
            ))
          ) : (
            <Text style={[styles.sourcesText, { color: colors.textMuted }]}>
              No specific sources linked.
            </Text>
          )}
        </View>
      </View>

      <View style={styles.audioRow}>
        <AudioButton icon="play" label={speechState === 'paused' ? 'Resume' : 'Play audio'} onPress={handlePlay} />
        <AudioButton icon="pause" label="Pause" onPress={handlePause} />
        <AudioButton icon="stop" label="Stop" onPress={handleStop} />
      </View>

      <View style={[styles.feedbackCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        {feedbackState === 'initial' && (
          <>
            <Text style={[styles.feedbackTitle, { color: colors.text }]}>Was this guidance useful?</Text>
            <View style={styles.feedbackButtons}>
              <FeedbackButton
                icon="thumbs-up-outline"
                label="Helpful"
                onPress={() => {
                  setFeedbackState('helpful-submitted');
                  submitFeedback('helpful');
                }}
                color={colors.primaryDark}
                bg={colors.primarySoft}
              />
              <FeedbackButton
                icon="thumbs-down-outline"
                label="Not helpful"
                onPress={() => setFeedbackState('needs-improvement')}
                color={colors.textMuted}
                bg={colors.surfaceMuted}
              />
            </View>
          </>
        )}
        {feedbackState === 'needs-improvement' && (
          <>
            <Text style={[styles.feedbackTitle, { color: colors.text }]}>What could be better?</Text>
            <TextInput
              style={[
                styles.feedbackInput, 
                { backgroundColor: colors.background, color: colors.text, borderColor: colors.border }
              ]}
              placeholder="Tell us what was missing..."
              placeholderTextColor={colors.textMuted}
              value={feedbackComment}
              onChangeText={setFeedbackComment}
              multiline
            />
            <View style={styles.feedbackButtons}>
              <FeedbackButton
                icon="close-outline"
                label="Cancel"
                onPress={() => setFeedbackState('initial')}
                color={colors.textMuted}
                bg={colors.surfaceMuted}
              />
              <FeedbackButton
                icon="send-outline"
                label="Submit"
                onPress={() => {
                  setFeedbackState('not-helpful-submitted');
                  submitFeedback('not_helpful', feedbackComment);
                }}
                color={colors.primaryDark}
                bg={colors.primarySoft}
              />
            </View>
          </>
        )}
        {(feedbackState === 'helpful-submitted' || feedbackState === 'not-helpful-submitted') && (
          <View style={styles.feedbackSubmitted}>
            <Ionicons name="checkmark-circle-outline" size={20} color={colors.primaryDark} />
            <Text style={[styles.feedbackTitle, { color: colors.primaryDark, marginTop: 0 }]}>
              Thank you for your feedback
            </Text>
          </View>
        )}
      </View>
    </View>
  );
}



function AudioButton({
  icon,
  label,
  onPress,
}: {
  icon: "play" | "pause" | "stop";
  label: string;
  onPress?: () => void;
}) {
  const { colors } = useTheme();

  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={label}
      style={({ pressed }) => [
        styles.audioButton,
        {
          backgroundColor: colors.surface,
          borderColor: colors.borderStrong,
          opacity: pressed ? 0.75 : 1,
        },
      ]}
    >
      <Ionicons
        name={`${icon}-outline` as keyof typeof Ionicons.glyphMap}
        size={16}
        color={colors.primaryDark}
      />

      <Text
        style={[
          styles.audioButtonText,
          {
            color: colors.primaryDark,
          },
        ]}
      >
        {label}
      </Text>
    </Pressable>
  );
}

function FeedbackButton({
  icon,
  label,
  onPress,
  color,
  bg
}: {
  icon: keyof typeof Ionicons.glyphMap;
  label: string;
  onPress: () => void;
  color: string;
  bg: string;
}) {
  const { colors } = useTheme();

  return (
    <Pressable
      onPress={onPress}
      accessibilityRole="button"
      accessibilityLabel={label}
      style={({ pressed }) => [
        styles.feedbackButton,
        {
          backgroundColor: bg,
          borderColor: colors.border,
          opacity: pressed ? 0.75 : 1,
        },
      ]}
    >
      <Ionicons
        name={icon}
        size={17}
        color={color}
      />

      <Text
        style={[
          styles.feedbackButtonText,
          {
            color: colors.text,
          },
        ]}
      >
        {label}
      </Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  feedbackSubmitted: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    gap: 6,
  },
  safeArea: {
    flex: 1,
  },

  keyboardView: {
    flex: 1,
  },

  header: {
    borderBottomWidth: 1,
  },

  headerInner: {
    alignItems: "center",
    alignSelf: "center",
    flexDirection: "row",
    minHeight: 70,
    paddingHorizontal: 14,
    width: "100%",
  },

  desktopHeaderInner: {
    maxWidth: 760,
  },

  headerButton: {
    alignItems: "center",
    borderRadius: 12,
    height: 43,
    justifyContent: "center",
    width: 43,
  },

  brandButton: {
    alignItems: "center",
    flex: 1,
    flexDirection: "row",
    gap: 9,
    minWidth: 0,
    paddingHorizontal: 10,
  },

  brandLogoContainer: {
    alignItems: "center",
    borderRadius: 11,
    borderWidth: 1,
    height: 43,
    justifyContent: "center",
    overflow: "hidden",
    width: 43,
  },

  brandLogoImage: {
    height: 38,
    width: 38,
  },

  brandTextArea: {
    flex: 1,
  },

  brandTitle: {
    fontFamily: "Manrope_700Bold",
    fontSize: 15,
  },

  brandSubtitle: {
    fontFamily: "Manrope_400Regular",
    fontSize: 10,
    marginTop: 2,
  },

  content: {
    alignSelf: "center",
    maxWidth: 540,
    padding: 17,
    paddingBottom: 28,
    width: "100%",
  },

  desktopContent: {
    maxWidth: 700,
  },

  welcomeArea: {
    alignItems: "center",
    paddingTop: 25,
  },

  heroLogoContainer: {
    alignItems: "center",
    borderRadius: 55,
    borderWidth: 1,
    height: 110,
    justifyContent: "center",
    overflow: "hidden",
    width: 110,
  },

  heroLogo: {
    height: 96,
    width: 96,
  },

  welcomeTitle: {
    fontFamily: "Manrope_800ExtraBold",
    fontSize: 28,
    letterSpacing: -0.5,
    marginTop: 19,
    textAlign: "center",
  },

  welcomeSubtitle: {
    fontFamily: "Manrope_400Regular",
    fontSize: 14,
    lineHeight: 22,
    marginTop: 9,
    maxWidth: 480,
    textAlign: "center",
  },

  assuranceCard: {
    alignItems: "flex-start",
    borderRadius: 14,
    flexDirection: "row",
    gap: 9,
    marginTop: 21,
    maxWidth: 520,
    padding: 13,
  },

  assuranceText: {
    flex: 1,
    fontFamily: "Manrope_600SemiBold",
    fontSize: 11,
    lineHeight: 18,
  },

  suggestionHeading: {
    alignSelf: "flex-start",
    fontFamily: "Manrope_700Bold",
    fontSize: 15,
    marginBottom: 11,
    marginTop: 28,
  },

  suggestions: {
    alignSelf: "stretch",
    gap: 10,
  },

  suggestionCard: {
    alignItems: "center",
    borderRadius: 16,
    borderWidth: 1,
    flexDirection: "row",
    gap: 10,
    minHeight: 66,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },

  suggestionIcon: {
    alignItems: "center",
    borderRadius: 10,
    height: 37,
    justifyContent: "center",
    width: 37,
  },

  suggestionText: {
    flex: 1,
    fontFamily: "Manrope_500Medium",
    fontSize: 12,
    lineHeight: 19,
  },

  messageRow: {
    alignItems: "flex-end",
    flexDirection: "row",
    gap: 8,
    marginBottom: 14,
  },

  userRow: {
    justifyContent: "flex-end",
  },

  assistantRow: {
    justifyContent: "flex-start",
  },

  assistantAvatar: {
    alignItems: "center",
    borderRadius: 16,
    height: 31,
    justifyContent: "center",
    width: 31,
  },

  messageBubble: {
    borderRadius: 18,
    borderWidth: 1,
    maxWidth: "84%",
    paddingHorizontal: 15,
    paddingVertical: 13,
  },

  userBubble: {
    borderBottomRightRadius: 4,
  },

  assistantBubble: {
    borderBottomLeftRadius: 4,
  },

  messageText: {
    fontFamily: "Manrope_400Regular",
    fontSize: 13,
    lineHeight: 21,
  },

  typingCard: {
    borderBottomLeftRadius: 4,
    borderRadius: 16,
    borderWidth: 1,
    minWidth: 220,
    padding: 13,
  },

  typingText: {
    fontFamily: "Manrope_600SemiBold",
    fontSize: 12,
  },

  dots: {
    flexDirection: "row",
    gap: 5,
    marginTop: 9,
  },

  dot: {
    borderRadius: 4,
    height: 7,
    width: 7,
  },

  detailsArea: {
    marginTop: 9,
  },

  verificationCard: {
    alignItems: "flex-start",
    borderRadius: 16,
    flexDirection: "row",
    gap: 10,
    marginBottom: 10,
    padding: 14,
  },

  verificationTextArea: {
    flex: 1,
  },

  verificationTitle: {
    fontFamily: "Manrope_700Bold",
    fontSize: 12,
  },

  verificationText: {
    fontFamily: "Manrope_400Regular",
    fontSize: 11,
    lineHeight: 18,
    marginTop: 4,
  },

  detailCard: {
    alignItems: "flex-start",
    borderRadius: 16,
    borderWidth: 1,
    flexDirection: "row",
    gap: 10,
    marginBottom: 10,
    padding: 14,
  },

  detailIcon: {
    alignItems: "center",
    borderRadius: 10,
    height: 39,
    justifyContent: "center",
    width: 39,
  },

  audioRow: {
    flexDirection: "row",
    gap: 12,
    marginTop: 10,
    marginBottom: 6,
  },

  detailTextArea: {
    flex: 1,
  },

  detailTitle: {
    fontFamily: "Manrope_700Bold",
    fontSize: 12,
  },

  detailText: {
    fontFamily: "Manrope_400Regular",
    fontSize: 11,
    lineHeight: 18,
    marginTop: 4,
  },

  sourcesCard: {
    borderRadius: 16,
    borderWidth: 1,
    marginTop: 2,
    padding: 14,
  },

  sourcesHeader: {
    alignItems: "center",
    flexDirection: "row",
    gap: 7,
  },

  sourcesTitle: {
    fontFamily: "Manrope_700Bold",
    fontSize: 12,
  },

  sourcesText: {
    fontFamily: "Manrope_400Regular",
    fontSize: 11,
    lineHeight: 18,
    marginTop: 8,
  },

  audioCard: {
    borderRadius: 16,
    marginTop: 11,
    padding: 14,
  },

  audioTopRow: {
    alignItems: "center",
    flexDirection: "row",
    gap: 10,
  },

  audioIcon: {
    alignItems: "center",
    borderRadius: 10,
    height: 39,
    justifyContent: "center",
    width: 39,
  },

  audioTextArea: {
    flex: 1,
  },

  audioTitle: {
    fontFamily: "Manrope_700Bold",
    fontSize: 12,
  },

  audioText: {
    fontFamily: "Manrope_400Regular",
    fontSize: 11,
    lineHeight: 17,
    marginTop: 3,
  },

  audioButtons: {
    flexDirection: "row",
    gap: 8,
    marginTop: 12,
  },

  audioButton: {
    alignItems: "center",
    borderRadius: 9,
    borderWidth: 1,
    flexDirection: "row",
    gap: 5,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },

  audioButtonText: {
    fontFamily: "Manrope_600SemiBold",
    fontSize: 10,
  },

  feedbackCard: {
    borderRadius: 16,
    borderWidth: 1,
    marginTop: 11,
    padding: 14,
  },

  feedbackTitle: {
    fontFamily: "Manrope_700Bold",
    fontSize: 12,
  },

  feedbackButtons: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 11,
  },

  feedbackButton: {
    alignItems: "center",
    borderRadius: 9,
    borderWidth: 1,
    flexDirection: "row",
    gap: 5,
    paddingHorizontal: 10,
    paddingVertical: 8,
  },

  feedbackButtonText: {
    fontFamily: "Manrope_600SemiBold",
    fontSize: 10,
  },

  feedbackInput: {
    borderWidth: 1,
    borderRadius: 8,
    padding: 10,
    fontSize: 12,
    fontFamily: "Manrope_500Medium",
    minHeight: 60,
    textAlignVertical: "top",
  },

  feedbackSubmitButton: {
    alignItems: "center",
    justifyContent: "center",
    borderRadius: 8,
    paddingVertical: 10,
    marginTop: 5,
  },

  composerArea: {
    alignItems: "center",
    paddingHorizontal: 14,
    paddingBottom: 24, // Added bottom padding to ensure it floats nicely
  },

  composerWrapper: {
    width: "100%",
  },

  desktopComposerWrapper: {
    maxWidth: 700,
  },

  drawerOverlay: {
    flex: 1,
    flexDirection: "row",
  },

  drawerPanel: {
    maxWidth: 340,
    paddingTop: 48,
    width: "86%",
  },

  closeButton: {
    alignItems: "center",
    borderRadius: 11,
    height: 40,
    justifyContent: "center",
    position: "absolute",
    right: 11,
    top: 5,
    width: 40,
    zIndex: 3,
  },

  drawerDismissArea: {
    flex: 1,
  },

  heroLogoWrapper: {
    alignItems: "center",
    borderRadius: 28,
    height: 80,
    justifyContent: "center",
    marginBottom: 16,
    width: 80,
    overflow: "hidden",
  },

  heroLogoIcon: {
    height: "100%",
    width: "100%",
  },

  assistantAvatarImageContainer: {
    alignItems: "center",
    borderRadius: 12,
    height: 31,
    justifyContent: "center",
    width: 31,
    overflow: "hidden",
  },

  assistantAvatarImage: {
    height: "100%",
    width: "100%",
  },
});