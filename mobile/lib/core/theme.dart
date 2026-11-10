import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

import 'app_language.dart';

const _seed = Color(0xFF0F6B4F); // deep green

ThemeData buildTheme(Brightness brightness, AppLanguage lang) {
  final base = ThemeData(
    colorScheme: ColorScheme.fromSeed(seedColor: _seed, brightness: brightness),
    useMaterial3: true,
  );
  final textTheme = lang == AppLanguage.ur
      ? GoogleFonts.notoNastaliqUrduTextTheme(base.textTheme)
      : GoogleFonts.interTextTheme(base.textTheme);
  return base.copyWith(textTheme: textTheme);
}

/// Style for Quranic / hadith Arabic text.
TextStyle arabicStyle(BuildContext context) => GoogleFonts.amiri(
      fontSize: 22,
      height: 1.9,
      color: Theme.of(context).colorScheme.onSurface,
    );

/// Style for Urdu text shown outside an Urdu UI (e.g. Urdu translation in an English UI).
TextStyle urduStyle(BuildContext context) => GoogleFonts.notoNastaliqUrdu(
      fontSize: 16,
      height: 2.0,
      color: Theme.of(context).colorScheme.onSurface,
    );
