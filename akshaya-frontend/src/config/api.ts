// Centralized API config to prevent hardcoded localhost scattered across the app.
// Note on Platform-specific resolution:
// If device testing is planned, API_BASE_URL needs to be your machine's LAN IP 
// (or a tunneled URL) when running on a physical device, not localhost, because 
// 'localhost' on a device// For a downloadable APK tested on your local Wi-Fi, we use your computer's IP address.
// If you host the backend on the cloud later (e.g. Render/Heroku), change this to your cloud URL.
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
