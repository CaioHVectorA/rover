import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Video, Glasses, Settings, SlidersHorizontal, Activity } from 'lucide-react-native';
import { AppTab } from '../types';
import { theme } from '../theme';

interface FloatingNavBarProps {
  currentTab: AppTab;
  onSelectTab: (tab: AppTab) => void;
}

export const FloatingNavBar: React.FC<FloatingNavBarProps> = ({ currentTab, onSelectTab }) => {
  const insets = useSafeAreaInsets();

  return (
    <View style={[styles.wrapper, { bottom: Math.max(insets.bottom, 10) + 4 }]} pointerEvents="box-none">
      <View style={styles.dock}>
        <TouchableOpacity
          style={[styles.tab, currentTab === 'drive' && styles.tabActive]}
          onPress={() => onSelectTab('drive')}
          activeOpacity={0.7}
        >
          <Video
            size={16}
            color={currentTab === 'drive' ? '#ffffff' : theme.colors.textSubtle}
          />
          <Text style={[styles.tabText, currentTab === 'drive' && styles.tabTextActive]}>
            Pilotar
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, currentTab === 'pocs' && styles.tabActive]}
          onPress={() => onSelectTab('pocs')}
          activeOpacity={0.7}
        >
          <Activity
            size={16}
            color={currentTab === 'pocs' ? '#00e5ff' : theme.colors.textSubtle}
          />
          <Text style={[styles.tabText, currentTab === 'pocs' && styles.tabTextActive]}>
            POCs
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, currentTab === 'calibrate' && styles.tabActive]}
          onPress={() => onSelectTab('calibrate')}
          activeOpacity={0.7}
        >
          <SlidersHorizontal
            size={16}
            color={currentTab === 'calibrate' ? '#ffffff' : theme.colors.textSubtle}
          />
          <Text style={[styles.tabText, currentTab === 'calibrate' && styles.tabTextActive]}>
            Servos
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, currentTab === 'vr' && styles.tabActive]}
          onPress={() => onSelectTab('vr')}
          activeOpacity={0.7}
        >
          <Glasses
            size={16}
            color={currentTab === 'vr' ? '#ffffff' : theme.colors.textSubtle}
          />
          <Text style={[styles.tabText, currentTab === 'vr' && styles.tabTextActive]}>
            VR
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, currentTab === 'settings' && styles.tabActive]}
          onPress={() => onSelectTab('settings')}
          activeOpacity={0.7}
        >
          <Settings
            size={16}
            color={currentTab === 'settings' ? '#ffffff' : theme.colors.textSubtle}
          />
          <Text style={[styles.tabText, currentTab === 'settings' && styles.tabTextActive]}>
            Rede
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  wrapper: {
    position: 'absolute',
    left: 0,
    right: 0,
    alignItems: 'center',
    zIndex: 100,
  },
  dock: {
    flexDirection: 'row',
    backgroundColor: 'rgba(20, 20, 24, 0.94)',
    borderRadius: theme.radius.full,
    paddingHorizontal: 6,
    paddingVertical: 5,
    gap: 2,
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.1)',
  },
  tab: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 5,
    paddingHorizontal: 11,
    paddingVertical: 7,
    borderRadius: theme.radius.full,
  },
  tabActive: {
    backgroundColor: 'rgba(255, 255, 255, 0.14)',
  },
  tabText: {
    color: theme.colors.textSubtle,
    fontSize: 11,
    fontWeight: '500',
  },
  tabTextActive: {
    color: '#ffffff',
    fontWeight: '700',
  },
});
