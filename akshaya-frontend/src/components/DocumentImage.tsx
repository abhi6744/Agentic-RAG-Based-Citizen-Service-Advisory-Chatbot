import React, { useState } from 'react';
import { Image, Platform, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useTheme } from '../contexts/ThemeContext';

export default function DocumentImage({ uri, style }: { uri: string; style?: any }) {
  const { colors } = useTheme();
  const [error, setError] = useState(false);

  if (!uri || error) {
    return (
      <View style={[style, { justifyContent: 'center', alignItems: 'center', backgroundColor: colors.surfaceMuted, borderRadius: 8 }]}>
        <Ionicons name="image-outline" size={32} color={colors.textMuted} />
      </View>
    );
  }

  const isWebUrl = uri.startsWith('http://') || uri.startsWith('https://');
  const isBlobOrData = uri.startsWith('blob:') || uri.startsWith('data:');

  if (Platform.OS === 'web' && (isBlobOrData || isWebUrl)) {
    return (
      <img
        src={uri}
        onError={() => setError(true)}
        style={{
          width: style?.width || 200,
          height: style?.height || 200,
          borderRadius: style?.borderRadius || 8,
          marginBottom: style?.marginBottom || 8,
          objectFit: 'contain',
          backgroundColor: '#E0E0E0',
          display: 'block'
        }}
      />
    );
  }

  return (
    <Image
      source={{ uri }}
      onError={() => setError(true)}
      style={[{ width: 200, height: 200, borderRadius: 8, marginBottom: 8, backgroundColor: '#E0E0E0' }, style]}
      resizeMode="contain"
    />
  );
}
