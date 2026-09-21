import { Ionicons } from "@expo/vector-icons";
import { router } from "expo-router";
import { useEffect, useMemo, useState } from "react";
import { getDeviceId } from "../utils/device";
import {
  Alert,
  FlatList,
  Platform,
  Pressable,
  SafeAreaView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";

import { useTheme } from "../contexts/ThemeContext";

type Category =
  | "all"
  | "aadhaar"
  | "ration_card"
  | "scholarship"
  | "general";

type Conversation = {
  id: string;
  title: string;
  preview: string;
  category: Exclude<Category, "all">;
  categoryLabel: string;
  updatedLabel: string;
  messageCount: number;
};

const filters: { label: string; value: Category }[] = [
  { label: "All", value: "all" },
  { label: "Aadhaar", value: "aadhaar" },
  { label: "Ration Card", value: "ration_card" },
  { label: "Scholarship", value: "scholarship" },
  { label: "General", value: "general" },
];

import { API_BASE_URL } from "../config/api";

const API_URL = API_BASE_URL;

export default function HistoryScreen() {
  const { colors } = useTheme();
  const [search, setSearch] = useState("");
    const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchHistory() {
      try {
        const actualDeviceId = await getDeviceId();
        const response = await fetch(`${API_URL}/conversations?device_id=${actualDeviceId}`);
        if (!response.ok) throw new Error("Failed to load history");
        const data = await response.json();
        setConversations(data);
      } catch (err) {
        console.error(err);
      } finally {
        setIsLoading(false);
      }
    }
    fetchHistory();
  }, []);

  const visibleConversations = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return conversations.filter((conversation) => {
      const textMatch =
        normalizedSearch.length === 0 ||
        conversation.title.toLowerCase().includes(normalizedSearch) ||
        conversation.preview.toLowerCase().includes(normalizedSearch) ||
        conversation.categoryLabel.toLowerCase().includes(normalizedSearch);

      return textMatch;
    });
  }, [conversations, search]);

    function removeConversation(conversation: Conversation) {
    const remove = async () => {
      try {
        await fetch(`${API_BASE_URL}/conversations/${conversation.id}`, { method: 'DELETE' });
        setConversations((current) =>
          current.filter((item) => item.id !== conversation.id),
        );
      } catch (e) {
        console.error("Failed to delete conversation", e);
      }
    };

    if (Platform.OS === "web") {
      if (
        window.confirm(
          `Remove "${conversation.title}" from your chat history?`,
        )
      ) {
        remove();
      }

      return;
    }

    Alert.alert(
      "Remove conversation",
      `Remove "${conversation.title}" from your chat history?`,
      [
        { text: "Cancel", style: "cancel" },
        { text: "Remove", style: "destructive", onPress: remove }
      ]
    );
  }

  function openConversation(conversation: Conversation) {
    router.push({
      pathname: "/",
      params: {
        conversation_id: conversation.id,
      },
    });
  }

  function clearFilters() {
    setSearch("");
      }

  return (
    <SafeAreaView
      style={[
        styles.safeArea,
        {
          backgroundColor: colors.background,
        },
      ]}
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
        <Pressable
          onPress={() => router.canGoBack() ? router.back() : router.replace('/')}
          accessibilityRole="button"
          accessibilityLabel="Go back"
          style={styles.headerIcon}
        >
          <Ionicons name="arrow-back" size={22} color={colors.text} />
        </Pressable>

        <View style={styles.headerText}>
          <Text
            style={[
              styles.headerTitle,
              {
                color: colors.text,
              },
            ]}
          >
            Chat history
          </Text>

          <Text
            style={[
              styles.headerSubtitle,
              {
                color: colors.textMuted,
              },
            ]}
          >
            Your saved advisory conversations
          </Text>
        </View>

        <Pressable
          onPress={() => router.replace("/")}
          accessibilityRole="button"
          accessibilityLabel="Start a new chat"
          style={[
            styles.newChatButton,
            {
              backgroundColor: colors.primary,
            },
          ]}
        >
          <Ionicons name="add" size={20} color="#FFFFFF" />
        </Pressable>
      </View>

      <FlatList
        data={visibleConversations}
        keyExtractor={(item) => item.id}
        showsVerticalScrollIndicator={false}
        contentContainerStyle={[
          styles.content,
          visibleConversations.length === 0 && styles.emptyContent,
        ]}
        ListHeaderComponent={
          <View>
            <View
              style={[
                styles.searchBox,
                {
                  backgroundColor: colors.surface,
                  borderColor: colors.border,
                },
              ]}
            >
              <Ionicons
                name="search-outline"
                size={19}
                color={colors.textMuted}
              />

              <TextInput
                value={search}
                onChangeText={setSearch}
                placeholder="Search conversations..."
                placeholderTextColor={colors.textMuted}
                style={[
                  styles.searchInput,
                  {
                    color: colors.text,
                  },
                ]}
                accessibilityLabel="Search chat history"
              />

              {search.length > 0 && (
                <Pressable
                  onPress={() => setSearch("")}
                  accessibilityRole="button"
                  accessibilityLabel="Clear search"
                >
                  <Ionicons
                    name="close-circle"
                    size={18}
                    color={colors.textMuted}
                  />
                </Pressable>
              )}
            </View>


            <Text
              style={[
                styles.listLabel,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              SAVED CONVERSATIONS
            </Text>
          </View>
        }
        renderItem={({ item }) => (
          <ConversationCard
            conversation={item}
            colors={colors}
            onOpen={() => openConversation(item)}
            onRemove={() => removeConversation(item)}
          />
        )}
        ListEmptyComponent={
          <EmptyHistory
            colors={colors}
            filtered={search.length > 0}
            onClear={clearFilters}
            onNewChat={() => router.replace("/")}
          />
        }
      />
    </SafeAreaView>
  );
}

function ConversationCard({
  conversation,
  colors,
  onOpen,
  onRemove,
}: {
  conversation: Conversation;
  colors: any;
  onOpen: () => void;
  onRemove: () => void;
}) {
  return (
    <View
      style={[
        styles.conversationCard,
        {
          backgroundColor: colors.surface,
          borderColor: colors.border,
        },
      ]}
    >
      <Pressable
        onPress={onOpen}
        accessibilityRole="button"
        accessibilityLabel={`Open ${conversation.title}`}
        style={({ pressed }) => [
          styles.conversationMain,
          {
            opacity: pressed ? 0.75 : 1,
          },
        ]}
      >
        <View
          style={[
            styles.conversationIcon,
            {
              backgroundColor: colors.primarySoft,
            },
          ]}
        >
          <Ionicons
            name={getIcon(conversation.category)}
            size={20}
            color={colors.primaryDark}
          />
        </View>

        <View style={styles.conversationTextArea}>
          <View style={styles.titleRow}>
            <Text
              numberOfLines={1}
              style={[
                styles.conversationTitle,
                {
                  color: colors.text,
                },
              ]}
            >
              {conversation.title}
            </Text>

            <Text
              style={[
                styles.updatedText,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              {conversation.updatedLabel}
            </Text>
          </View>

          <Text
            numberOfLines={2}
            style={[
              styles.previewText,
              {
                color: colors.textMuted,
              },
            ]}
          >
            {conversation.preview}
          </Text>

          <View style={styles.cardFooter}>
            <View
              style={[
                styles.categoryBadge,
                {
                  backgroundColor: colors.surfaceMuted,
                },
              ]}
            >
              <Text
                style={[
                  styles.categoryText,
                  {
                    color: colors.primaryDark,
                  },
                ]}
              >
                {conversation.categoryLabel}
              </Text>
            </View>

            <Text
              style={[
                styles.messageCount,
                {
                  color: colors.textMuted,
                },
              ]}
            >
              {conversation.messageCount} messages
            </Text>
          </View>
        </View>
      </Pressable>

      <Pressable
        onPress={onRemove}
        accessibilityRole="button"
        accessibilityLabel={`Remove ${conversation.title}`}
        style={({ pressed }) => [
          styles.removeButton,
          {
            backgroundColor: pressed
              ? colors.dangerBackground
              : "transparent",
          },
        ]}
      >
        <Ionicons
          name="ellipsis-horizontal"
          size={20}
          color={colors.textMuted}
        />
      </Pressable>
    </View>
  );
}

function EmptyHistory({
  colors,
  filtered,
  onClear,
  onNewChat,
}: {
  colors: any;
  filtered: boolean;
  onClear: () => void;
  onNewChat: () => void;
}) {
  return (
    <View
      style={[
        styles.emptyState,
        {
          backgroundColor: colors.surface,
          borderColor: colors.border,
        },
      ]}
    >
      <View
        style={[
          styles.emptyIcon,
          {
            backgroundColor: colors.primarySoft,
          },
        ]}
      >
        <Ionicons
          name={filtered ? "search-outline" : "chatbubbles-outline"}
          size={30}
          color={colors.primaryDark}
        />
      </View>

      <Text
        style={[
          styles.emptyTitle,
          {
            color: colors.text,
          },
        ]}
      >
        {filtered ? "No matching chats" : "No saved chats yet"}
      </Text>

      <Text
        style={[
          styles.emptyText,
          {
            color: colors.textMuted,
          },
        ]}
      >
        {filtered
          ? "Try another search or clear the current topic filter."
          : "Your advisory conversations will appear here after backend integration."}
      </Text>

      <View style={styles.emptyActions}>
        {filtered && (
          <Pressable
            onPress={onClear}
            accessibilityRole="button"
            accessibilityLabel="Clear filters"
            style={[
              styles.clearButton,
              {
                backgroundColor: colors.surfaceMuted,
                borderColor: colors.border,
              },
            ]}
          >
            <Text
              style={[
                styles.clearButtonText,
                {
                  color: colors.text,
                },
              ]}
            >
              Clear filters
            </Text>
          </Pressable>
        )}

        <Pressable
          onPress={onNewChat}
          accessibilityRole="button"
          accessibilityLabel="Start new chat"
          style={[
            styles.startButton,
            {
              backgroundColor: colors.primary,
            },
          ]}
        >
          <Ionicons name="add" size={18} color="#FFFFFF" />
          <Text style={styles.startButtonText}>New chat</Text>
        </Pressable>
      </View>
    </View>
  );
}

function getIcon(
  category: Exclude<Category, "all">,
): keyof typeof Ionicons.glyphMap {
  if (category === "aadhaar") {
    return "card-outline";
  }

  if (category === "ration_card") {
    return "fast-food-outline";
  }

  if (category === "scholarship") {
    return "school-outline";
  }

  return "documents-outline";
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
  },

  header: {
    alignItems: "center",
    borderBottomWidth: 1,
    flexDirection: "row",
    minHeight: 68,
    paddingHorizontal: 12,
  },

  headerIcon: {
    alignItems: "center",
    height: 42,
    justifyContent: "center",
    width: 42,
  },

  headerText: {
    flex: 1,
    marginHorizontal: 7,
  },

  headerTitle: {
    fontSize: 16,
    fontWeight: "800",
  },

  headerSubtitle: {
    fontSize: 10,
    marginTop: 3,
  },

  newChatButton: {
    alignItems: "center",
    borderRadius: 12,
    height: 40,
    justifyContent: "center",
    width: 40,
  },

  content: {
    alignSelf: "center",
    maxWidth: 760,
    padding: 16,
    paddingBottom: 42,
    width: "100%",
  },

  emptyContent: {
    flexGrow: 1,
  },

  searchBox: {
    alignItems: "center",
    borderRadius: 14,
    borderWidth: 1,
    flexDirection: "row",
    gap: 8,
    minHeight: 49,
    paddingHorizontal: 13,
  },

  searchInput: {
    flex: 1,
    fontSize: 14,
    minHeight: 42,
    padding: 0,
  },

  filterHeader: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 22,
  },

  filterTitle: {
    fontSize: 13,
    fontWeight: "800",
  },

  countText: {
    fontSize: 11,
  },

  filters: {
    gap: 8,
    paddingBottom: 5,
    paddingTop: 11,
  },

  filterChip: {
    borderRadius: 999,
    borderWidth: 1,
    paddingHorizontal: 13,
    paddingVertical: 8,
  },

  filterChipText: {
    fontSize: 11,
    fontWeight: "700",
  },

  listLabel: {
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 0.9,
    marginBottom: 11,
    marginTop: 21,
  },

  conversationCard: {
    alignItems: "center",
    borderRadius: 16,
    borderWidth: 1,
    flexDirection: "row",
    marginBottom: 9,
    minHeight: 108,
    padding: 7,
  },

  conversationMain: {
    alignItems: "flex-start",
    flex: 1,
    flexDirection: "row",
    gap: 10,
    minWidth: 0,
    padding: 7,
  },

  conversationIcon: {
    alignItems: "center",
    borderRadius: 11,
    height: 40,
    justifyContent: "center",
    width: 40,
  },

  conversationTextArea: {
    flex: 1,
    minWidth: 0,
  },

  titleRow: {
    alignItems: "center",
    flexDirection: "row",
    gap: 7,
  },

  conversationTitle: {
    flex: 1,
    fontSize: 13,
    fontWeight: "800",
  },

  updatedText: {
    fontSize: 10,
  },

  previewText: {
    fontSize: 11,
    lineHeight: 17,
    marginTop: 5,
  },

  cardFooter: {
    alignItems: "center",
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 10,
  },

  categoryBadge: {
    borderRadius: 7,
    paddingHorizontal: 7,
    paddingVertical: 4,
  },

  categoryText: {
    fontSize: 9,
    fontWeight: "800",
  },

  messageCount: {
    fontSize: 9,
  },

  removeButton: {
    alignItems: "center",
    borderRadius: 9,
    height: 38,
    justifyContent: "center",
    marginRight: 3,
    width: 38,
  },

  emptyState: {
    alignItems: "center",
    borderRadius: 18,
    borderWidth: 1,
    justifyContent: "center",
    marginTop: 20,
    minHeight: 290,
    padding: 25,
  },

  emptyIcon: {
    alignItems: "center",
    borderRadius: 18,
    height: 64,
    justifyContent: "center",
    marginBottom: 15,
    width: 64,
  },

  emptyTitle: {
    fontSize: 18,
    fontWeight: "800",
  },

  emptyText: {
    fontSize: 12,
    lineHeight: 18,
    marginTop: 8,
    maxWidth: 340,
    textAlign: "center",
  },

  emptyActions: {
    alignItems: "center",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 9,
    justifyContent: "center",
    marginTop: 19,
  },

  clearButton: {
    borderRadius: 10,
    borderWidth: 1,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },

  clearButtonText: {
    fontSize: 11,
    fontWeight: "700",
  },

  startButton: {
    alignItems: "center",
    borderRadius: 10,
    flexDirection: "row",
    gap: 5,
    paddingHorizontal: 13,
    paddingVertical: 10,
  },

  startButtonText: {
    color: "#FFFFFF",
    fontSize: 11,
    fontWeight: "800",
  },
});