import { Platform } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

const DEVICE_ID_KEY = 'akshaya_device_id';

function generateId(): string {
  return 'device_' + Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15);
}

let memoryDeviceId: string | null = null;

export async function getDeviceId(): Promise<string> {
  if (memoryDeviceId) {
    return memoryDeviceId;
  }

  try {
    if (Platform.OS === 'web') {
      let id = localStorage.getItem(DEVICE_ID_KEY);
      if (!id) {
        id = generateId();
        localStorage.setItem(DEVICE_ID_KEY, id);
      }
      memoryDeviceId = id;
      return id;
    } else {
      let id = await AsyncStorage.getItem(DEVICE_ID_KEY);
      if (!id) {
        id = generateId();
        await AsyncStorage.setItem(DEVICE_ID_KEY, id);
      }
      memoryDeviceId = id;
      return id;
    }
  } catch (error) {
    console.error("Failed to get/set device ID:", error);
    return "fallback-device-id";
  }
}
