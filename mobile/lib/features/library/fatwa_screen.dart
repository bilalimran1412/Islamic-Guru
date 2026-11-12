import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/api_client.dart';
import '../../core/settings_controller.dart';
import '../../core/theme.dart';

/// A single approved fatwa, shown exactly as published, with a link to the original.
class FatwaScreen extends ConsumerWidget {
  const FatwaScreen({super.key, required this.id});
  final String id;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = ref.watch(stringsProvider);
    final fatwa = ref.watch(fatwaProvider(id));
    final textTheme = Theme.of(context).textTheme;
    return Scaffold(
      appBar: AppBar(title: Text(s.library)),
      body: fatwa.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(child: Text(s.errorGeneric)),
        data: (f) {
          final dir = directionForLanguage(f.language);
          final style = styleForLanguage(context, f.language);
          return ListView(
            padding: const EdgeInsets.all(20),
            children: [
              Text(f.title, textDirection: dir, style: textTheme.titleLarge?.merge(style)),
              const SizedBox(height: 6),
              Text([
                f.publisher,
                if (f.scholar != null) f.scholar!,
                if (f.madhhab != null) s.madhhabName(f.madhhab!),
              ].join(' · '), style: textTheme.labelLarge),
              if (f.question != null) ...[
                const SizedBox(height: 20),
                Text(s.question, style: textTheme.titleSmall),
                const SizedBox(height: 6),
                SelectableText(f.question!, textDirection: dir, style: style),
              ],
              const SizedBox(height: 20),
              Text(s.answer, style: textTheme.titleSmall),
              const SizedBox(height: 6),
              SelectableText(f.answer, textDirection: dir, style: style),
              const SizedBox(height: 24),
              Align(
                alignment: AlignmentDirectional.centerStart,
                child: FilledButton.tonalIcon(
                  icon: const Icon(Icons.open_in_new),
                  label: Text(s.readOriginal),
                  onPressed: () => launchUrl(Uri.parse(f.originalUrl), mode: LaunchMode.externalApplication),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}
