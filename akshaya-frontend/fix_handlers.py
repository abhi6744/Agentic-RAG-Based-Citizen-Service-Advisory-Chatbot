import re
from pathlib import Path

f = Path('src/app/index.tsx')
text = f.read_text(encoding='utf-8')

# Let's add try/catch to TTS handlers in AdvisoryDetails
old_play = """  const handlePlay = () => {
    if (Platform.OS === 'android') {"""
new_play = """  const handlePlay = () => {
    try {
      if (Platform.OS === 'android') {"""
text = text.replace(old_play, new_play)

old_play_end = """        }
      }
    }
  };
  
  const handlePause = () => {"""
new_play_end = """        }
      }
    } catch (e) {
      console.error("[AdvisoryDetails] Error in handlePlay:", e);
    }
  };
  
  const handlePause = () => {"""
text = text.replace(old_play_end, new_play_end)


old_pause = """  const handlePause = () => {
    if (speechStateRef.current === 'playing') {"""
new_pause = """  const handlePause = () => {
    try {
      if (speechStateRef.current === 'playing') {"""
text = text.replace(old_pause, new_pause)

old_pause_end = """      }
    }
  };
  
  const handleStop = () => {"""
new_pause_end = """      }
    } catch (e) {
      console.error("[AdvisoryDetails] Error in handlePause:", e);
    }
  };
  
  const handleStop = () => {"""
text = text.replace(old_pause_end, new_pause_end)

old_stop = """  const handleStop = () => {
    syncState('stopped');
    segmentRef.current = 0;
    Speech.stop();
  };"""
new_stop = """  const handleStop = () => {
    try {
      syncState('stopped');
      segmentRef.current = 0;
      Speech.stop();
    } catch (e) {
      console.error("[AdvisoryDetails] Error in handleStop:", e);
    }
  };"""
text = text.replace(old_stop, new_stop)

old_start = """  function startNewChat() {
    setMessages([welcomeMessage]);
    setConversationId(null);
    processedQueryRef.current = null;
    router.replace("/");
  }"""
new_start = """  function startNewChat() {
    try {
      setMessages([welcomeMessage]);
      setConversationId(null);
      processedQueryRef.current = null;
      router.replace("/");
    } catch (e) {
      console.error("[App] Error in startNewChat:", e);
    }
  }"""
text = text.replace(old_start, new_start)

f.write_text(text, encoding='utf-8')
