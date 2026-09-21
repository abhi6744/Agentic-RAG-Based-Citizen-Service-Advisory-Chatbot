import * as fs from 'fs';

let content = fs.readFileSync('src/app/index.tsx', 'utf8');

// 1. Add cleanText import
content = content.replace(
    'import { getDeviceId } from "../utils/device";',
    'import { getDeviceId } from "../utils/device";\nimport { cleanText } from "../utils/cleanResponseText";'
);

// 2. Update BackendData type
const oldBackendDataType = 	ype BackendData = {
  message_id: number;
  conversation_id: number;
  response_type?: string;
  detected_service?: string;
  summary: string;
  documents_and_eligibility?: string;
  next_steps?: string;
  citations: SourceCitation[];
  confidence_score: number;
  confidence_level: string;
  requires_official_verification: boolean;
  verification_message?: string;
  image_description?: string;
  privacy_warning?: string;
};;

const newBackendDataType = 	ype AnswerData = {
  summary: string;
  eligibility: string[];
  documents: string[];
  next_steps: string[];
  where_to_go: string[];
  warning: string;
};

type BackendData = {
  message_id: number;
  conversation_id: number;
  response_type?: string;
  detected_service?: string;
  answer?: AnswerData;
  summary?: string;
  documents_and_eligibility?: string;
  next_steps?: string;
  citations: SourceCitation[];
  confidence_score: number;
  confidence_level: string;
  requires_official_verification: boolean;
  verification_message?: string;
  image_description?: string;
  privacy_warning?: string;
};;

content = content.replace(oldBackendDataType, newBackendDataType);

// 3. Update MessageBubble Image rendering
const oldImageRender = {message.imageUri ? (
            <ExpoImage
              source={{ uri: message.imageUri }}
              style={{ width: 200, height: 200, borderRadius: 8, marginBottom: 8, backgroundColor: '#E0E0E0' }}
              contentFit="cover"
              onLoad={() => console.log("[Image Render] Successfully loaded URI:", message.imageUri)}
              onError={(e) => console.error("[Image Render] Failed to load URI:", message.imageUri, e)}
            />
          ) : null};

const newImageRender = {message.imageUri ? (
            Platform.OS === 'web' && message.imageUri.startsWith('blob:') ? (
              <img 
                src={message.imageUri} 
                style={{ width: 200, height: 200, borderRadius: 8, marginBottom: 8, objectFit: 'cover', backgroundColor: '#E0E0E0', display: 'block' }} 
              />
            ) : (
              <Image
                source={{ uri: message.imageUri }}
                style={{ width: 200, height: 200, borderRadius: 8, marginBottom: 8, backgroundColor: '#E0E0E0' }}
                resizeMode="cover"
              />
            )
          ) : null};

content = content.replace(oldImageRender, newImageRender);

// 4. Update the text-rendering of message
const oldAssistantText = <FormattedText 
              text={message.text} 
              style={[
                styles.messageText,
                { color: colors.text, fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif' }
              ]} 
            />;

const newAssistantText = <Text style={[styles.messageText, { color: colors.text, fontFamily: Platform.OS === 'ios' ? 'System' : 'sans-serif' }]}>
              {cleanText(message.backendData?.answer?.summary || message.text)}
            </Text>;
content = content.replace(oldAssistantText, newAssistantText);

// 5. Rewrite AdvisoryDetails
const advisoryStart = content.indexOf('function AdvisoryDetails({ data }: { data: BackendData }) {');
const advisoryEnd = content.indexOf('const styles = StyleSheet.create({');

const newAdvisoryDetails = unction AdvisoryDetails({ data }: { data: BackendData }) {
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
    (answer?.summary || data.summary || "") + ". " +
    (answer?.documents?.join(". ") || data.documents_and_eligibility || "") + ". " +
    (answer?.next_steps?.join(". ") || data.next_steps || "")
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
      await fetch(\\/feedback\, {
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
            <>
                {hasDocuments && (
                    <View style={{ marginBottom: hasEligibility ? 16 : 0 }}>
                        <Text style={[styles.detailTitle, { color: colors.text, fontSize: 13, marginBottom: 6 }]}>Documents to prepare</Text>
                        {answer.documents.map((doc, idx) => (
                            <View key={\doc-\\} style={{ flexDirection: 'row', marginBottom: 6 }}>
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
                            <View key={\lig-\\} style={{ flexDirection: 'row', marginBottom: 6 }}>
                                <Text style={{ color: colors.primaryDark, fontSize: 16, fontWeight: 'bold', width: 16, lineHeight: 19 }}>•</Text>
                                <Text style={{ color: colors.text, flex: 1, fontSize: 13, lineHeight: 19 }}>{cleanText(elig)}</Text>
                            </View>
                        ))}
                    </View>
                )}
            </>
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
            <>
                {hasNextSteps && (
                    <View style={{ marginBottom: hasWhereToGo ? 16 : 0 }}>
                        {answer.next_steps.map((step, idx) => (
                            <View key={\step-\\} style={{ flexDirection: 'row', marginBottom: 8 }}>
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
                            <View key={\loc-\\} style={{ flexDirection: 'row', marginBottom: 6 }}>
                                <Text style={{ color: colors.primaryDark, fontSize: 16, fontWeight: 'bold', width: 16, lineHeight: 19 }}>•</Text>
                                <Text style={{ color: colors.text, flex: 1, fontSize: 13, lineHeight: 19 }}>{cleanText(loc)}</Text>
                            </View>
                        ))}
                    </View>
                )}
            </>
        )}
      </View>

      <View style={[styles.sourcesCard, { backgroundColor: colors.surface, borderColor: colors.border }]}>
        <View style={styles.sourcesHeader}>
          <Ionicons name="link-outline" size={19} color={colors.primaryDark} />
          <Text style={[styles.sourcesTitle, { color: colors.text }]}>
            Sources & Confidence ({cleanText((data.confidence_score * 100).toFixed(0))} - {cleanText(data.confidence_level.toUpperCase())})
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
;

content = content.substring(0, advisoryStart) + newAdvisoryDetails + content.substring(advisoryEnd);

fs.writeFileSync('src/app/index.tsx', content, 'utf8');
