import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/models.dart';
import '../../core/settings_controller.dart';
import '../../core/theme.dart';
import '../reference/reference_sheet.dart';
import 'report_sheet.dart';

class MessageBubble extends ConsumerWidget {
  const MessageBubble({super.key, required this.message});
  final ChatMessage message;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final scheme = Theme.of(context).colorScheme;
    final s = ref.watch(stringsProvider);

    if (message.isUser) {
      return Align(
        alignment: AlignmentDirectional.centerEnd,
        child: Container(
          constraints: BoxConstraints(maxWidth: MediaQuery.sizeOf(context).width * 0.8),
          margin: const EdgeInsets.symmetric(vertical: 6),
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(color: scheme.primary, borderRadius: BorderRadius.circular(18)),
          child: Text(message.content, style: TextStyle(color: scheme.onPrimary)),
        ),
      );
    }

    // Answers in Urdu or Arabic are right-to-left even when the app UI is not.
    final answerDir = directionForLanguage(message.language);
    final answerStyle = styleForLanguage(context, message.language);

    return Container(
      margin: const EdgeInsets.symmetric(vertical: 6),
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: scheme.surfaceContainerHighest,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(message.content, textDirection: answerDir, style: answerStyle),
          if (message.citations.isNotEmpty) ...[
            const SizedBox(height: 10),
            Wrap(
              spacing: 6,
              runSpacing: 6,
              children: [
                for (final c in message.citations)
                  ActionChip(
                    avatar: Icon(c.kind == 'quran' ? Icons.menu_book : Icons.format_quote, size: 16),
                    label: Text('[${c.index}] ${c.label}'),
                    onPressed: () => showReferenceSheet(context, c.refKey),
                  ),
              ],
            ),
          ],
          if (message.consultScholar) ...[
            const SizedBox(height: 10),
            Row(children: [
              Icon(Icons.school_outlined, size: 18, color: scheme.tertiary),
              const SizedBox(width: 6),
              Expanded(child: Text(s.consultScholar, style: TextStyle(color: scheme.tertiary))),
            ]),
          ],
          if (message.disclaimer != null) ...[
            const SizedBox(height: 8),
            Text(message.disclaimer!, style: Theme.of(context).textTheme.bodySmall, textDirection: answerDir),
          ],
          if (message.id != null)
            Align(
              alignment: AlignmentDirectional.centerEnd,
              child: TextButton.icon(
                icon: const Icon(Icons.flag_outlined, size: 16),
                label: Text(s.report),
                onPressed: () => showReportSheet(context, message.id!),
              ),
            ),
        ],
      ),
    );
  }
}
