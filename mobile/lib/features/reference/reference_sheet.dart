import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:url_launcher/url_launcher.dart';

import '../../core/api_client.dart';
import '../../core/settings_controller.dart';
import '../../core/theme.dart';

/// Shows the full Arabic text and translations of a cited ayah or hadith.
Future<void> showReferenceSheet(BuildContext context, String refKey) => showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (_) => DraggableScrollableSheet(
        expand: false,
        initialChildSize: 0.6,
        maxChildSize: 0.95,
        builder: (context, controller) => _ReferenceBody(refKey: refKey, controller: controller),
      ),
    );

class _ReferenceBody extends ConsumerWidget {
  const _ReferenceBody({required this.refKey, required this.controller});
  final String refKey;
  final ScrollController controller;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = ref.watch(stringsProvider);
    final source = ref.watch(referenceProvider(refKey));
    final textTheme = Theme.of(context).textTheme;

    return source.when(
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (_, _) => Center(child: Text(s.errorGeneric)),
      data: (src) => ListView(
        controller: controller,
        padding: const EdgeInsets.fromLTRB(20, 0, 20, 32),
        children: [
          Text(src.label, style: textTheme.titleLarge),
          if (src.grade != null)
            Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text('${s.grade}: ${src.grade}', style: textTheme.labelLarge),
            ),
          if (src.arabic != null) ...[
            const SizedBox(height: 16),
            SelectableText(src.arabic!, textDirection: TextDirection.rtl, style: arabicStyle(context)),
          ],
          for (final t in src.translations.entries) ...[
            const SizedBox(height: 16),
            Text(
              '${s.translation}${t.value.translator != null ? ' — ${t.value.translator}' : ''}',
              style: textTheme.labelMedium,
            ),
            const SizedBox(height: 4),
            SelectableText(
              t.value.text,
              textDirection: t.key == 'ur' ? TextDirection.rtl : TextDirection.ltr,
              style: t.key == 'ur' ? urduStyle(context) : textTheme.bodyLarge,
            ),
          ],
          const SizedBox(height: 20),
          Text(src.attribution, style: textTheme.bodySmall),
          if (src.sourceUrl != null)
            Align(
              alignment: AlignmentDirectional.centerStart,
              child: TextButton.icon(
                icon: const Icon(Icons.open_in_new, size: 16),
                label: Text(s.openSource),
                onPressed: () => launchUrl(Uri.parse(src.sourceUrl!), mode: LaunchMode.externalApplication),
              ),
            ),
        ],
      ),
    );
  }
}
