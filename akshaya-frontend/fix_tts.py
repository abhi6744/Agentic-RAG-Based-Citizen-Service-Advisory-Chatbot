import re
from pathlib import Path

f = Path('src/app/index.tsx')
text = f.read_text(encoding='utf-8')

old_tts = '''  const handlePlay = () => {
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
  };'''

new_tts = '''  const speechStateRef = React.useRef<'stopped' | 'playing' | 'paused'>('stopped');
  const segmentRef = React.useRef(0);
  const segments = React.useMemo(() => textToRead.match(/[^.!?]+[.!?]+/g) || [textToRead], [textToRead]);

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
  };
  
  const handlePause = () => {
    if (speechStateRef.current === 'playing') {
      syncState('paused');
      if (Platform.OS === 'android') {
        Speech.stop();
      } else {
        Speech.pause();
      }
    }
  };
  
  const handleStop = () => {
    syncState('stopped');
    segmentRef.current = 0;
    Speech.stop();
  };'''

text = text.replace(old_tts, new_tts)
f.write_text(text, encoding='utf-8')
