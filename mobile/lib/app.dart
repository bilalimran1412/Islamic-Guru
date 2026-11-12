import 'package:flutter/material.dart';
import 'package:flutter_localizations/flutter_localizations.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'core/settings_controller.dart';
import 'core/theme.dart';
import 'features/chat/chat_screen.dart';
import 'features/history/history_screen.dart';
import 'features/library/fatwa_screen.dart';
import 'features/library/library_screen.dart';
import 'features/scholar/scholar_screen.dart';
import 'features/settings/settings_screen.dart';

final _router = GoRouter(
  routes: [
    GoRoute(path: '/', builder: (_, _) => const ChatScreen()),
    GoRoute(path: '/history', builder: (_, _) => const HistoryScreen()),
    GoRoute(path: '/settings', builder: (_, _) => const SettingsScreen()),
    GoRoute(path: '/library', builder: (_, _) => const LibraryScreen()),
    GoRoute(path: '/library/:id', builder: (_, state) => FatwaScreen(id: state.pathParameters['id']!)),
    GoRoute(path: '/scholar', builder: (_, _) => const ScholarScreen()),
  ],
);

class IslamicGuruApp extends ConsumerWidget {
  const IslamicGuruApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final lang = ref.watch(languageProvider);
    final s = ref.watch(stringsProvider);
    return MaterialApp.router(
      title: s.appName,
      debugShowCheckedModeBanner: false,
      theme: buildTheme(Brightness.light, lang),
      darkTheme: buildTheme(Brightness.dark, lang),
      locale: lang.locale,
      supportedLocales: const [Locale('en'), Locale('ur'), Locale('ar')],
      localizationsDelegates: GlobalMaterialLocalizations.delegates,
      routerConfig: _router,
    );
  }
}
