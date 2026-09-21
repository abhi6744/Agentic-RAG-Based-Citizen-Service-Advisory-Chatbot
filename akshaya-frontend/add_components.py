import sys

components_to_add = """
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

"""

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

if "function AudioButton" not in content:
    content = content.replace("const styles = StyleSheet.create({", components_to_add + "const styles = StyleSheet.create({")
    with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Added missing components.")
else:
    print("Components already exist.")
