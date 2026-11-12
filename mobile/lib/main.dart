import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'app.dart';

void main() {
  LicenseRegistry.addLicense(() async* {
    for (final (font, file) in [('Amiri', 'OFL-Amiri.txt'), ('Noto Nastaliq Urdu', 'OFL-NotoNastaliqUrdu.txt')]) {
      yield LicenseEntryWithLineBreaks([font], await rootBundle.loadString('assets/fonts/$file'));
    }
  });
  runApp(const ProviderScope(child: IslamicGuruApp()));
}
