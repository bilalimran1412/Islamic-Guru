import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api_client.dart';
import '../../core/models.dart';
import '../../core/settings_controller.dart';
import '../../core/strings.dart';
import '../../core/theme.dart';

class ScholarScreen extends ConsumerWidget {
  const ScholarScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = ref.watch(stringsProvider);
    final questions = ref.watch(scholarQuestionsProvider);
    return Scaffold(
      appBar: AppBar(title: Text(s.askScholar)),
      floatingActionButton: FloatingActionButton.extended(
        icon: const Icon(Icons.edit_outlined),
        label: Text(s.askScholar),
        onPressed: () => showModalBottomSheet(
          context: context,
          isScrollControlled: true,
          showDragHandle: true,
          builder: (_) => const _AskSheet(),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () => ref.refresh(scholarQuestionsProvider.future),
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 96),
          children: [
            Text(s.askScholarIntro),
            const SizedBox(height: 16),
            ...questions.when(
              loading: () => [const Center(child: CircularProgressIndicator())],
              error: (_, _) => [Text(s.errorGeneric)],
              data: (list) => list.isEmpty
                  ? [Padding(padding: const EdgeInsets.only(top: 24), child: Text(s.noScholarQuestions))]
                  : [for (final q in list) _QuestionCard(q: q, s: s)],
            ),
          ],
        ),
      ),
    );
  }
}

class _QuestionCard extends StatelessWidget {
  const _QuestionCard({required this.q, required this.s});
  final ScholarQuestion q;
  final S s;

  @override
  Widget build(BuildContext context) {
    final textTheme = Theme.of(context).textTheme;
    final answered = q.status == 'answered';
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Row(children: [
              Icon(answered ? Icons.mark_chat_read_outlined : Icons.hourglass_empty, size: 18),
              const SizedBox(width: 6),
              Text(s.scholarStatus(q.status), style: textTheme.labelLarge),
            ]),
            const SizedBox(height: 8),
            Text(q.question),
            if (q.status == 'awaiting_payment') ...[
              const SizedBox(height: 8),
              Text(s.paymentSoon, style: textTheme.bodySmall),
            ],
            if (answered && q.answer != null) ...[
              const Divider(height: 24),
              if (q.scholarName != null) Text(q.scholarName!, style: textTheme.titleSmall),
              const SizedBox(height: 4),
              SelectableText(q.answer!),
            ],
          ],
        ),
      ),
    );
  }
}

class _AskSheet extends ConsumerStatefulWidget {
  const _AskSheet();

  @override
  ConsumerState<_AskSheet> createState() => _AskSheetState();
}

class _AskSheetState extends ConsumerState<_AskSheet> {
  final _text = TextEditingController();
  bool _sending = false;

  @override
  void dispose() {
    _text.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    final s = ref.read(stringsProvider);
    if (_text.text.trim().length < 10) return;
    setState(() => _sending = true);
    final messenger = ScaffoldMessenger.of(context);
    final navigator = Navigator.of(context);
    try {
      await ref.read(apiClientProvider).askScholar(_text.text.trim(), ref.read(languageProvider).code);
      ref.invalidate(scholarQuestionsProvider);
      navigator.pop();
    } catch (_) {
      messenger.showSnackBar(SnackBar(content: Text(s.errorGeneric)));
      setState(() => _sending = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(stringsProvider);
    final lang = ref.watch(languageProvider);
    return Padding(
      padding: EdgeInsets.fromLTRB(16, 0, 16, 16 + MediaQuery.viewInsetsOf(context).bottom),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(s.yourQuestion, style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          TextField(
            controller: _text,
            minLines: 4,
            maxLines: 10,
            maxLength: 4000,
            autofocus: true,
            style: styleForLanguage(context, lang.code),
            decoration: const InputDecoration(border: OutlineInputBorder()),
          ),
          const SizedBox(height: 8),
          FilledButton(onPressed: _sending ? null : _submit, child: Text(s.submit)),
        ],
      ),
    );
  }
}
