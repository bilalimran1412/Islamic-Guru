/// Build-time configuration.
///
/// Run against a local backend with:
///   flutter run --dart-define=API_BASE_URL=http://10.0.2.2:8000   (Android emulator)
class AppConfig {
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );
}
