import 'package:flutter/widgets.dart';

/// Languages the app answers in. Roman Urdu is Urdu written in Latin letters;
/// it uses a left-to-right layout but Urdu wording.
enum AppLanguage {
  en('en', 'English', TextDirection.ltr, Locale('en')),
  ur('ur', 'اردو', TextDirection.rtl, Locale('ur')),
  romanUr('roman_ur', 'Roman Urdu', TextDirection.ltr, Locale('en'));

  const AppLanguage(this.code, this.label, this.direction, this.locale);

  /// Code used by the backend API.
  final String code;
  final String label;
  final TextDirection direction;
  final Locale locale;

  static AppLanguage fromCode(String? code) =>
      AppLanguage.values.firstWhere((l) => l.code == code, orElse: () => AppLanguage.en);
}
