
import { Platform } from 'react-native';

// Add fallback for Android Emulator if physical IP doesn't work
const getLocalIP = () => {
  if (Platform.OS === 'web') return 'http://127.0.0.1:8001';
  if (Platform.OS === 'android' && !process.env.EXPO_PUBLIC_API_URL) {
    // If you're on emulator, 10.0.2.2 points to host's localhost
    return 'http://10.0.2.2:8001';
  }
  return 'http://192.168.137.232:8001';
};

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || getLocalIP();
