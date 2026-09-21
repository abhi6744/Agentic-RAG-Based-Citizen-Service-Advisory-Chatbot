import re

with open('src/app/history.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove SelectedFilter state and its usages
content = re.sub(r'const \[selectedFilter, setSelectedFilter\] = useState<Category>\("all"\);\n', '', content)

# 2. Fix useMemo
old_visible_conversations = """  const visibleConversations = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return conversations.filter((conversation) => {
      const categoryMatch =
        selectedFilter === "all" ||
        conversation.category === selectedFilter;

      const textMatch =
        normalizedSearch.length === 0 ||
        conversation.title.toLowerCase().includes(normalizedSearch) ||
        conversation.preview.toLowerCase().includes(normalizedSearch) ||
        conversation.categoryLabel.toLowerCase().includes(normalizedSearch);

      return categoryMatch && textMatch;
    });
  }, [conversations, search, selectedFilter]);"""

new_visible_conversations = """  const visibleConversations = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase();

    return conversations.filter((conversation) => {
      const textMatch =
        normalizedSearch.length === 0 ||
        conversation.title.toLowerCase().includes(normalizedSearch) ||
        conversation.preview.toLowerCase().includes(normalizedSearch) ||
        conversation.categoryLabel.toLowerCase().includes(normalizedSearch);

      return textMatch;
    });
  }, [conversations, search]);"""
content = content.replace(old_visible_conversations, new_visible_conversations)

# 3. Remove clearFilters changing selectedFilter
content = content.replace('setSelectedFilter("all");\n', '')

# 4. Remove the FlatList for filters
old_flatlist = """        <View>
          <FlatList
            data={filters}
            horizontal
            keyExtractor={(item) => item.value}
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.filters}
            renderItem={({ item }) => {
              const selected = item.value === selectedFilter;

              return (
                <Pressable
                  onPress={() => setSelectedFilter(item.value)}
                  accessibilityRole="button"
                  accessibilityLabel={`Filter by ${item.label}`}
                  accessibilityState={{ selected }}
                  style={[
                    styles.filterChip,
                    {
                      backgroundColor: selected
                        ? colors.primary
                        : colors.surface,
                      borderColor: selected
                        ? colors.primary
                        : colors.border,
                    },
                  ]}
                >
                  <Text
                    style={[
                      styles.filterChipText,
                      {
                        color: selected
                          ? "#FFFFFF"
                          : colors.textMuted,
                      },
                    ]}
                  >
                    {item.label}
                  </Text>
                </Pressable>
              );
            }}
          />
        </View>"""
content = content.replace(old_flatlist, '')

# 5. Fix EmptyHistory filtered prop
content = content.replace('filtered={search.length > 0 || selectedFilter !== "all"}', 'filtered={search.length > 0}')

with open('src/app/history.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Removed filters from history.tsx")
