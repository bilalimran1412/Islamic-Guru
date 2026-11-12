import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:speech_to_text/speech_to_text.dart';

import '../../core/app_language.dart';
import '../../core/settings_controller.dart';
import 'chat_controller.dart';
import 'message_bubble.dart';

class ChatScreen extends ConsumerStatefulWidget {
  const ChatScreen({super.key});

  @override
  ConsumerState<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends ConsumerState<ChatScreen> {
  final _input = TextEditingController();
  final _scroll = ScrollController();
  final _speech = SpeechToText();
  bool _speechReady = false;
  bool _listening = false;

  @override
  void dispose() {
    _input.dispose();
    _scroll.dispose();
    _speech.cancel();
    super.dispose();
  }

  /// Speech locale for the app language. Roman Urdu users speak Urdu.
  static const _speechLocales = {
    AppLanguage.en: 'en_US',
    AppLanguage.ur: 'ur_PK',
    AppLanguage.romanUr: 'ur_PK',
    AppLanguage.ar: 'ar_SA',
  };

  Future<void> _toggleVoice() async {
    final s = ref.read(stringsProvider);
    if (_listening) {
      await _speech.stop();
      setState(() => _listening = false);
      return;
    }
    _speechReady = _speechReady ||
        await _speech.initialize(onStatus: (status) {
          if (status == SpeechToText.doneStatus || status == SpeechToText.notListeningStatus) {
            if (mounted) setState(() => _listening = false);
          }
        });
    if (!_speechReady) {
      if (mounted) ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(s.voiceUnavailable)));
      return;
    }
    final wanted = _speechLocales[ref.read(languageProvider)]!;
    final available = await _speech.locales();
    final localeId = available.any((l) => l.localeId == wanted) ? wanted : null;
    setState(() => _listening = true);
    await _speech.listen(
      onResult: (r) => setState(() => _input.text = r.recognizedWords),
      listenOptions: SpeechListenOptions(localeId: localeId, partialResults: true, cancelOnError: true),
    );
  }

  void _send() {
    final text = _input.text;
    _input.clear();
    ref.read(chatControllerProvider.notifier).send(text);
  }

  void _scrollToEnd() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scroll.hasClients) {
        _scroll.animateTo(_scroll.position.maxScrollExtent,
            duration: const Duration(milliseconds: 250), curve: Curves.easeOut);
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final s = ref.watch(stringsProvider);
    final state = ref.watch(chatControllerProvider);
    ref.listen(chatControllerProvider, (prev, next) {
      if (prev?.messages.length != next.messages.length) _scrollToEnd();
      if (next.error != null && prev?.error != next.error) {
        final msg = next.error == ChatError.dailyLimit ? s.dailyLimit : s.errorGeneric;
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(msg)));
      }
    });

    return Scaffold(
      appBar: AppBar(
        title: Text(s.appName),
        actions: [
          IconButton(
            tooltip: s.newChat,
            icon: const Icon(Icons.add_comment_outlined),
            onPressed: () => ref.read(chatControllerProvider.notifier).newChat(),
          ),
        ],
      ),
      drawer: _AppDrawer(),
      body: SafeArea(
        child: Column(
          children: [
            Expanded(
              child: state.messages.isEmpty && !state.sending
                  ? _Welcome(title: s.welcomeTitle, body: s.welcomeBody)
                  : ListView.builder(
                      controller: _scroll,
                      padding: const EdgeInsets.all(12),
                      itemCount: state.messages.length + (state.sending ? 1 : 0),
                      itemBuilder: (context, i) => i < state.messages.length
                          ? MessageBubble(message: state.messages[i])
                          : _Thinking(label: s.thinking),
                    ),
            ),
            Padding(
              padding: const EdgeInsets.fromLTRB(12, 4, 12, 12),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _input,
                      minLines: 1,
                      maxLines: 5,
                      maxLength: 2000,
                      textInputAction: TextInputAction.send,
                      onSubmitted: (_) => _send(),
                      decoration: InputDecoration(
                        hintText: _listening ? s.listening : s.askHint,
                        counterText: '',
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(24)),
                        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                      ),
                    ),
                  ),
                  const SizedBox(width: 4),
                  IconButton(
                    tooltip: _listening ? s.listening : s.voice,
                    onPressed: state.sending ? null : _toggleVoice,
                    icon: Icon(_listening ? Icons.mic : Icons.mic_none),
                    color: _listening ? Theme.of(context).colorScheme.error : null,
                  ),
                  IconButton.filled(
                    tooltip: s.send,
                    onPressed: state.sending ? null : _send,
                    icon: const Icon(Icons.send),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _Welcome extends StatelessWidget {
  const _Welcome({required this.title, required this.body});
  final String title;
  final String body;

  @override
  Widget build(BuildContext context) => Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(Icons.auto_stories_outlined, size: 56, color: Theme.of(context).colorScheme.primary),
              const SizedBox(height: 16),
              Text(title, style: Theme.of(context).textTheme.headlineSmall),
              const SizedBox(height: 8),
              Text(body, textAlign: TextAlign.center),
            ],
          ),
        ),
      );
}

class _Thinking extends StatelessWidget {
  const _Thinking({required this.label});
  final String label;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 12),
        child: Row(children: [
          const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)),
          const SizedBox(width: 10),
          Text(label),
        ]),
      );
}

class _AppDrawer extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = ref.watch(stringsProvider);
    void go(String path) {
      Navigator.pop(context);
      context.push(path);
    }

    return NavigationDrawer(
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(28, 20, 16, 12),
          child: Text(s.appName, style: Theme.of(context).textTheme.titleLarge),
        ),
        ListTile(
          leading: const Icon(Icons.add_comment_outlined),
          title: Text(s.newChat),
          onTap: () {
            ref.read(chatControllerProvider.notifier).newChat();
            Navigator.pop(context);
          },
        ),
        ListTile(leading: const Icon(Icons.history), title: Text(s.history), onTap: () => go('/history')),
        ListTile(leading: const Icon(Icons.menu_book_outlined), title: Text(s.library), onTap: () => go('/library')),
        ListTile(leading: const Icon(Icons.school_outlined), title: Text(s.askScholar), onTap: () => go('/scholar')),
        const Divider(),
        ListTile(leading: const Icon(Icons.settings_outlined), title: Text(s.settings), onTap: () => go('/settings')),
      ],
    );
  }
}
