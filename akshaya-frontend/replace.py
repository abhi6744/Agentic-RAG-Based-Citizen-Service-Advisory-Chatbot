import sys

new_code = """
function AdvisoryDetails({ data }: { data: BackendData }) {
  const { colors } = useTheme();
  const [speechState, setSpeechState] = useState<'stopped' | 'playing' | 'paused'>('stopped');
  const [feedbackState, setFeedbackState] = useState<'initial' | 'helpful-submitted' | 'needs-improvement' | 'not-helpful-submitted'>('initial');
  const [feedbackComment, setFeedbackComment] = useState('');
  const API_URL = process.env.EXPO_PUBLIC_API_URL || (Platform.OS === 'android' ? 'http://10.0.2.2:8000' : 'http://127.0.0.1:8000');

  const detailCards = [
    {
      icon: "search-outline" as const,
      title: "Identified Service",
      text: data.detected_service || "General Inquiry",
    },
    {
      icon: "documents-outline" as const,
      title: "Documents and eligibility",
      text: data.documents_and_eligibility || "No specific documents listed.",
    },
    {
      icon: "navigate-outline" as const,
      title: "Recommended next steps",
      text: data.next_steps || "No additional steps identified.",
    },
  ];

  const textToRead = stripForSpeech(
    (data.summary || "") + ". " +
    (data.documents_and_eligibility || "") + ". " +
    (data.next_steps || "")
  );

  const handlePlay = () => {
    if (speechState === 'paused') {
      Speech.resume();
      setSpeechState('playing');
    } else {
      Speech.stop();
      Speech.speak(textToRead, { 
        language: 'en-IN', 
        rate: 0.9,
        onDone: () => setSpeechState('stopped'),
        onStopped: () => setSpeechState('stopped')
      });
      setSpeechState('playing');
    }
  };
  
  const handlePause = () => {
    if (speechState === 'playing') {
      Speech.pause();
      setSpeechState('paused');
    }
  };
  
  const handleStop = () => {
    Speech.stop();
    setSpeechState('stopped');
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
              {cleanString(data.verification_message || "This information requires verification at your local Akshaya centre before proceeding.")}
            </Text>
          </View>
        </View>
      )}

      {detailCards.map((detail) => (
        <View
          key={detail.title}
          style={[
            styles.detailCard,
            { backgroundColor: colors.surface, borderColor: colors.border },
          ]}
        >
          <View style={[styles.detailIcon, { backgroundColor: colors.primarySoft }]}>
            <Ionicons name={detail.icon} size={19} color={colors.primaryDark} />
          </View>
          <View style={styles.detailTextArea}>
            <Text style={[styles.detailTitle, { color: colors.text }]}>{detail.title}</Text>
            <FormattedText text={detail.text} style={[styles.detailText, { color: colors.textMuted }]} />
          </View>
        </View>
      ))}

      <View style={[styles.sourcesCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <View style={styles.sourcesHeader}>
          <Ionicons name="link-outline" size={19} color={colors.primaryDark} />
          <Text style={[styles.sourcesTitle, { color: colors.text }]}>
            Sources & Confidence ({cleanString((data.confidence_score * 100).toString())} - {cleanString(data.confidence_level.toUpperCase())})
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
                    {cleanString(c.source_title)} ({cleanString(c.authority)})
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
        <AudioButton icon="play" label={speechState === 'paused' ? 'Resume' : 'Play audio'} onPress={handlePlay} colors={colors} />
        <AudioButton icon="pause" label="Pause" onPress={handlePause} colors={colors} />
        <AudioButton icon="stop" label="Stop" onPress={handleStop} colors={colors} />
      </View>

      <View style={[styles.feedbackCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        {feedbackState === 'initial' && (
          <>
            <Text style={[styles.feedbackTitle, { color: colors.text }]}>Was this guidance useful?</Text>
            <View style={styles.feedbackButtons}>
              <FeedbackButton
                icon="thumbs-up-outline"
                label="Helpful"
                selected={false}
                onPress={() => {
                  setFeedbackState('helpful-submitted');
                  submitFeedback('helpful');
                }}
              />
              <FeedbackButton
                icon="thumbs-down-outline"
                label="Needs improvement"
                selected={false}
                onPress={() => {
                  setFeedbackState('needs-improvement');
                }}
              />
            </View>
          </>
        )}

        {feedbackState === 'helpful-submitted' && (
          <Text style={[styles.feedbackTitle, { color: colors.primaryDark }]}>
            Thank you for your feedback!
          </Text>
        )}

        {feedbackState === 'needs-improvement' && (
          <View style={{ gap: 10 }}>
            <Text style={[styles.feedbackTitle, { color: colors.text }]}>
              Thank you for your feedback. How can we improve this answer?
            </Text>
            <TextInput
              style={[
                styles.feedbackInput,
                { color: colors.text, borderColor: colors.border, backgroundColor: colors.background }
              ]}
              placeholder="Tell us what was missing or unclear (optional)"
              placeholderTextColor={colors.textMuted}
              value={feedbackComment}
              onChangeText={setFeedbackComment}
              multiline
            />
            <Pressable
              style={({ pressed }) => [
                styles.feedbackSubmitButton,
                { backgroundColor: colors.primary, opacity: pressed ? 0.8 : 1 }
              ]}
              onPress={() => {
                setFeedbackState('not-helpful-submitted');
                submitFeedback('not_helpful', feedbackComment);
              }}
            >
              <Text style={{ color: "#fff", fontSize: 12, fontFamily: "Manrope_700Bold" }}>Submit feedback</Text>
            </Pressable>
          </View>
        )}

        {feedbackState === 'not-helpful-submitted' && (
          <Text style={[styles.feedbackTitle, { color: colors.primaryDark }]}>
            Thank you for helping us improve!
          </Text>
        )}
      </View>
    </View>
  );
}
"""

with open('src/app/index.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

start_idx = -1
for i, line in enumerate(lines):
    if 'function AdvisoryDetails(' in line:
        start_idx = i
        break

if start_idx != -1:
    end_idx = -1
    brace_count = 0
    in_function = False
    for i in range(start_idx, len(lines)):
        line = lines[i]
        if '{' in line:
            brace_count += line.count('{')
            in_function = True
        if '}' in line:
            brace_count -= line.count('}')
        if in_function and brace_count == 0:
            end_idx = i
            break
            
    lines = lines[:start_idx] + [new_code + '\n'] + lines[end_idx+1:]
    with open('src/app/index.tsx', 'w', encoding='utf-8') as f:
        f.writelines(lines)
    print('Replaced AdvisoryDetails successfully.')
else:
    print('Could not find AdvisoryDetails.')
