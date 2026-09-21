import sys

missing_code = """
  function showToast(msg: string) {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  }

  async function startRecording() {
    try {
      if (Platform.OS === 'web') {
        showToast("Voice recording is not supported on Web. Please use the mobile app.");
        return;
      }
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status !== 'granted') {
        Alert.alert("Permission Denied", "Microphone permission is required to use voice input.");
        return;
      }
      await Audio.setAudioModeAsync({
        allowsRecordingIOS: true,
        playsInSilentModeIOS: true,
      });

      const { recording } = await Audio.Recording.createAsync(
        Audio.RecordingOptionsPresets.HIGH_QUALITY
      );
      setRecording(recording);
      setIsRecording(true);
    } catch (err) {
      console.error("Failed to start recording", err);
      Alert.alert("Error", "Failed to start recording.");
    }
  }

  async function stopRecording() {
    if (!recording) return;
    setIsRecording(false);
    
    try {
      await recording.stopAndUnloadAsync();
      const uri = recording.getURI();
      setRecording(null);
      
      if (uri) {
        setIsTranscribing(true);
        // Upload audio to transcribe endpoint
        const formData = new FormData();
        const fileType = Platform.OS === 'ios' ? 'audio/m4a' : 'audio/m4a';
        const fileExtension = Platform.OS === 'ios' ? 'm4a' : 'm4a';
        
        formData.append("audio", {
          uri: Platform.OS === 'android' ? uri : uri.replace('file://', ''),
          name: `audio.${fileExtension}`,
          type: fileType,
        } as any);

        const response = await fetch(`${API_BASE_URL}/transcribe`, {
          method: "POST",
          body: formData,
        });
        
        if (!response.ok) {
          throw new Error(`Transcription failed: ${response.status}`);
        }
        
        const data = await response.json();
        if (data.text) {
          setQuery(prev => prev ? `${prev} ${data.text}` : data.text);
          setInputOrigin("voice");
        } else {
          Alert.alert("No speech detected", "Could not transcribe any speech from the audio.");
        }
      }
    } catch (err) {
      console.error("Transcription error:", err);
      Alert.alert("Error", "Transcription failed. Please try again.");
    } finally {
      setIsTranscribing(false);
    }
  }
"""

with open('src/components/QueryComposer.tsx', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("  const canSubmit = (cleanedQuery.length > 0 || selectedImage !== null) && !disabled;", "  const canSubmit = (cleanedQuery.length > 0 || selectedImage !== null) && !disabled;\n" + missing_code)

with open('src/components/QueryComposer.tsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("Restored missing voice logic in QueryComposer.")
