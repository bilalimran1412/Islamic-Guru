import 'package:flutter/widgets.dart';

/// Languages the app answers in. Roman Urdu is Urdu written in Latin letters;
/// it uses a left-to-right layout but Urdu wording.
enum AppLanguage {
  en('en', 'English', Locale('en')),
  ur('ur', 'اردو', Locale('ur')),
  romanUr('roman_ur', 'Roman Urdu', Locale('en')),
  ar('ar', 'العربية', Locale('ar'));

  const AppLanguage(this.code, this.label, this.locale);

  /// Code used by the backend API.
  final String code;
  final String label;

  /// Material locale; it also sets the layout direction (ur and ar are right-to-left).
  final Locale locale;

  static AppLanguage fromCode(String? code) =>
      AppLanguage.values.firstWhere((l) => l.code == code, orElse: () => AppLanguage.en);
}

/// Font family for UI text in a given language (bundled in assets/fonts).
String? uiFontFamily(AppLanguage lang) => switch (lang) {
      AppLanguage.ur => 'NotoNastaliqUrdu',
      AppLanguage.ar => 'Amiri',
      _ => null, // platform default (Roboto / San Francisco)
    };
