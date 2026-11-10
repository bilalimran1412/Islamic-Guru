import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api_client.dart';
import '../../core/settings_controller.dart';

Future<void> showReportSheet(BuildContext context, String messageId) => showModalBottomSheet(
      context: context,
      showDragHandle: true,
      builder: (_) => _ReportSheet(messageId: messageId),
    );

class _ReportSheet extends ConsumerWidget {
  const _ReportSheet({required this.messageId});
  final String messageId;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = ref.watch(stringsProvider);
    final reasons = {
      'wrong_reference': s.wrongReference,
      'wrong_answer': s.wrongAnswer,
      'sectarian': s.sectarian,
      'other': s.other,
    };
    return SafeArea(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Padding(
            padding: const EdgeInsets.all(8),
            child: Text(s.report, style: Theme.of(context).textTheme.titleMedium),
          ),
          for (final e in reasons.entries)
            ListTile(
              title: Text(e.value),
              onTap: () async {
                final messenger = ScaffoldMessenger.of(context);
                Navigator.pop(context);
                try {
                  await ref.read(apiClientProvider).report(messageId, e.key);
                  messenger.showSnackBar(SnackBar(content: Text(s.reportThanks)));
                } catch (_) {
                  messenger.showSnackBar(SnackBar(content: Text(s.errorGeneric)));
                }
              },
            ),
        ],
      ),
    );
  }
}
