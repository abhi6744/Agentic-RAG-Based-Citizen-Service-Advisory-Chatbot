// Centralized API config to prevent hardcoded localhost scattered across the app.
// Note on Platform-specific resolution:
// If device testing is planned, API_BASE_URL needs to be your machine's LAN IP 
// (or a tunneled URL) when running on a physical device, not localhost, because 
// 'localhost' on a device// For a downloadable APK tested on your local Wi-Fi, we use your computer's IP address.
// If you host the backend on the cloud later (e.g. Render/Heroku), change this to your cloud URL.
import { Platform } from 'react-native';

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 
  (Platform.OS === 'web' ? 'http://127.0.0.1:8001' : 'http://192.168.16.241:8001');
