# 📱 Android AAB Configuration Reference for CeliacShield Mobile

## Key Configuration Files

### 1. Main App Build Configuration
```gradle
// android/app/build.gradle
android {
    compileSdkVersion 34
    defaultConfig {
        applicationId "com.celiogix.mobile"
        minSdkVersion 24
        targetSdkVersion 34
        versionCode 1
        versionName "1.0.0"
        multiDexEnabled true
    }
    
    bundle {
        language { enableSplit = true }
        density { enableSplit = true }
        abi { enableSplit = true }
    }
    
    buildTypes {
        release {
            minifyEnabled true
            shrinkResources true
            proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
        }
    }
    
    dynamicFeatures = [
        ':feature_barcode_scanner',
        ':feature_restaurant_finder'
    ]
}

dependencies {
    implementation 'com.google.android.play:core:1.10.3'
    implementation 'com.google.mlkit:barcode-scanning:17.2.0'
}
```

### 2. Dynamic Feature Module
```gradle
// android/feature_barcode_scanner/build.gradle
apply plugin: 'com.android.dynamic-feature'

android {
    compileSdkVersion 34
    defaultConfig {
        minSdkVersion 24
        targetSdkVersion 34
    }
}

dependencies {
    implementation project(':app')
    implementation 'com.google.mlkit:barcode-scanning:17.2.0'
}
```

### 3. Android Manifest
```xml
<!-- android/app/src/main/AndroidManifest.xml -->
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" />
    
    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/AppTheme">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTask"
            android:theme="@style/AppTheme.NoActionBarLaunch">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        
        <meta-data
            android:name="com.google.android.gms.version"
            android:value="@integer/google_play_services_version" />
            
    </application>
</manifest>
```

### 4. ProGuard Rules
```proguard
# proguard-rules.pro
-keep class com.celiogix.** { *; }
-keep class com.google.mlkit.** { *; }
-keep class com.capacitor.** { *; }

-keepclasseswithmembernames class * {
    native <methods>;
}

-keep class com.getcapacitor.** { *; }
-keep class com.google.android.play.core.** { *; }
```

### 5. Capacitor Configuration
```typescript
// capacitor.config.ts
import { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.celiogix.mobile',
  appName: 'CeliacShield Mobile',
  webDir: 'www',
  server: {
    androidScheme: 'https'
  },
  plugins: {
    Camera: {
      permissions: ['camera']
    },
    BarcodeScanner: {
      permissions: ['camera']
    },
    Geolocation: {
      permissions: ['location']
    }
  }
};

export default config;
```

### 6. Build Script
```bash
#!/bin/bash
# build-aab.sh

echo "🚀 Building CeliacShield Mobile AAB..."

# Clean and build
ionic capacitor clean android
ionic build --prod
ionic capacitor sync android

# Build AAB
cd android
./gradlew bundleRelease

echo "✅ AAB build complete!"
echo "📱 Location: android/app/build/outputs/bundle/release/app-release.aab"
```

### 7. Package.json Scripts
```json
{
  "scripts": {
    "build:android": "ionic build && ionic capacitor sync android",
    "build:aab": "ionic build --prod && ionic capacitor sync android && cd android && ./gradlew bundleRelease",
    "build:aab-debug": "ionic build && ionic capacitor sync android && cd android && ./gradlew bundleDebug",
    "open:android": "ionic capacitor open android",
    "sync:android": "ionic capacitor sync android"
  }
}
```

## Quick Commands Reference

```bash
# Development
ionic capacitor run android
ionic capacitor open android

# Building AAB
ionic build --prod
ionic capacitor sync android
cd android && ./gradlew bundleRelease

# Testing AAB
bundletool build-apks --bundle=app-release.aab --output=app.apks
bundletool install-apks --apks=app.apks
```

## Key AAB Features for CeliacShield

1. **Dynamic Feature Modules**: Barcode scanner and restaurant finder as on-demand modules
2. **Asset Packs**: Large gluten-free product database delivered efficiently
3. **Language Splits**: Support for multiple languages without bloating base app
4. **Density Splits**: Optimized resources for different screen densities
5. **ABI Splits**: Architecture-specific optimizations

This configuration ensures optimal AAB performance and distribution for the CeliacShield Mobile Companion.
