import 'package:flutter/material.dart';

import 'app_language.dart';

const _seed = Color(0xFF0F6B4F); // deep green

ThemeData buildTheme(Brightness brightness, AppLanguage lang) => ThemeData(
      colorScheme: ColorScheme.fromSeed(seedColor: _seed, brightness: brightness),
      fontFamily: uiFontFamily(lang),
      useMaterial3: true,
    );

/// Style for Quranic / hadith Arabic text.
TextStyle arabicStyle(BuildContext context) => TextStyle(
      fontFamily: 'Amiri',
      fontSize: 22,
      height: 1.9,
      color: Theme.of(context).colorScheme.onSurface,
    );

/// Style for Urdu text shown outside an Urdu UI (e.g. Urdu translation in an English UI).
TextStyle urduStyle(BuildContext context) => TextStyle(
      fontFamily: 'NotoNastaliqUrdu',
      fontSize: 16,
      height: 2.0,
      color: Theme.of(context).colorScheme.onSurface,
    );

/// Style for a block of text in the given API language code.
TextStyle? styleForLanguage(BuildContext context, String? code) => switch (code) {
      'ur' => urduStyle(context),
      'ar' => arabicStyle(context).copyWith(fontSize: 18),
      _ => null,
    };

TextDirection? directionForLanguage(String? code) =>
    code == 'ur' || code == 'ar' ? TextDirection.rtl : null;
