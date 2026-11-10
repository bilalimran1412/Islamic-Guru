import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/api_client.dart';
import '../../core/models.dart';
import '../../core/settings_controller.dart';

enum ChatError { generic, dailyLimit }

class ChatState {
  const ChatState({this.chatId, this.messages = const [], this.sending = false, this.error});

  final String? chatId;
  final List<ChatMessage> messages;
  final bool sending;
  final ChatError? error;

  ChatState copyWith({String? chatId, List<ChatMessage>? messages, bool? sending, ChatError? error}) =>
      ChatState(
        chatId: chatId ?? this.chatId,
        messages: messages ?? this.messages,
        sending: sending ?? this.sending,
        error: error,
      );
}

class ChatController extends Notifier<ChatState> {
  @override
  ChatState build() => const ChatState();

  ApiClient get _api => ref.read(apiClientProvider);

  void newChat() => state = const ChatState();

  Future<void> open(String chatId) async {
    state = ChatState(chatId: chatId, sending: true);
    try {
      state = ChatState(chatId: chatId, messages: await _api.chatMessages(chatId));
    } catch (_) {
      state = ChatState(chatId: chatId, error: ChatError.generic);
    }
  }

  Future<void> send(String question) async {
    final q = question.trim();
    if (q.isEmpty || state.sending) return;
    state = state.copyWith(
      messages: [...state.messages, ChatMessage(role: 'user', content: q)],
      sending: true,
    );
    try {
      final res = await _api.ask(q, chatId: state.chatId, language: ref.read(languageProvider).code);
      state = state.copyWith(chatId: res.chatId, messages: [...state.messages, res.answer], sending: false);
      ref.invalidate(chatListProvider);
    } on DailyLimitReached {
      state = state.copyWith(sending: false, error: ChatError.dailyLimit);
    } catch (_) {
      state = state.copyWith(sending: false, error: ChatError.generic);
    }
  }
}

final chatControllerProvider = NotifierProvider<ChatController, ChatState>(ChatController.new);
