import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/app_language.dart';
import '../../core/settings_controller.dart';

class SettingsScreen extends ConsumerWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = ref.watch(stringsProvider);
    final lang = ref.watch(languageProvider);
    return Scaffold(
      appBar: AppBar(title: Text(s.settings)),
      body: ListView(
        children: [
          ListTile(title: Text(s.language, style: Theme.of(context).textTheme.titleSmall)),
          RadioGroup<AppLanguage>(
            groupValue: lang,
            onChanged: (v) => v == null ? null : ref.read(languageProvider.notifier).set(v),
            child: Column(
              children: [
                for (final l in AppLanguage.values) RadioListTile<AppLanguage>(value: l, title: Text(l.label)),
              ],
            ),
          ),
          const Divider(),
          ListTile(title: Text(s.about, style: Theme.of(context).textTheme.titleSmall)),
          Padding(padding: const EdgeInsets.fromLTRB(16, 0, 16, 24), child: Text(s.aboutBody)),
        ],
      ),
    );
  }
}
