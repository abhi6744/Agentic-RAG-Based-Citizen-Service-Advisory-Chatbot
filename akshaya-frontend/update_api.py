import re

with open('src/config/api.ts', 'r', encoding='utf-8') as f:
    content = f.read()

# Update API config to be safe and robust
old_config = """export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || 
  (Platform.OS === 'web' ? 'http://127.0.0.1:8001' : 'http://192.168.16.241:8001');"""
new_config = """// Add fallback for Android Emulator if physical IP doesn't work
const getLocalIP = () => {
  if (Platform.OS === 'web') return 'http://127.0.0.1:8001';
  if (Platform.OS === 'android' && !process.env.EXPO_PUBLIC_API_URL) {
    // If you're on emulator, 10.0.2.2 points to host's localhost
    return 'http://10.0.2.2:8001';
  }
  return 'http://192.168.16.241:8001';
};

export const API_BASE_URL = process.env.EXPO_PUBLIC_API_URL || getLocalIP();"""

content = content.replace(old_config, new_config)

with open('src/config/api.ts', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated API base URL configuration")
