/// Build-time configuration, passed with --dart-define.
///
/// Local backend on the Android emulator:
///   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000
///
/// Sign-in (values from Google Cloud Console / Apple Developer):
///   --dart-define=GOOGLE_SERVER_CLIENT_ID=WEB_CLIENT_ID.apps.googleusercontent.com
///   --dart-define=GOOGLE_IOS_CLIENT_ID=IOS_CLIENT_ID.apps.googleusercontent.com
///   --dart-define=APPLE_SERVICE_ID=SERVICES_ID (e.g. com.islamicguru.signin)
///   --dart-define=APPLE_REDIRECT_URI=https://API_DOMAIN/v1/auth/apple/callback
class AppConfig {
  static const apiBaseUrl = String.fromEnvironment('API_BASE_URL', defaultValue: 'http://10.0.2.2:8000');

  static const googleServerClientId = String.fromEnvironment('GOOGLE_SERVER_CLIENT_ID');
  static const googleIosClientId = String.fromEnvironment('GOOGLE_IOS_CLIENT_ID');
  static const appleServiceId = String.fromEnvironment('APPLE_SERVICE_ID');
  static const appleRedirectUri = String.fromEnvironment('APPLE_REDIRECT_URI');

  static bool get googleSignInConfigured => googleServerClientId.isNotEmpty;
  static bool get appleSignInConfigured => appleServiceId.isNotEmpty;
}
