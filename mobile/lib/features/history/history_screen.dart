import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:intl/intl.dart';

import '../../core/api_client.dart';
import '../../core/settings_controller.dart';
import '../chat/chat_controller.dart';

class HistoryScreen extends ConsumerWidget {
  const HistoryScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final s = ref.watch(stringsProvider);
    final chats = ref.watch(chatListProvider);
    return Scaffold(
      appBar: AppBar(title: Text(s.history)),
      body: chats.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (_, _) => Center(child: Text(s.errorGeneric)),
        data: (list) => list.isEmpty
            ? Center(child: Text(s.noHistory))
            : RefreshIndicator(
                onRefresh: () => ref.refresh(chatListProvider.future),
                child: ListView.separated(
                  itemCount: list.length,
                  separatorBuilder: (_, _) => const Divider(height: 1),
                  itemBuilder: (context, i) => ListTile(
                    title: Text(list[i].title, maxLines: 2, overflow: TextOverflow.ellipsis),
                    subtitle: Text(DateFormat.yMMMd().add_jm().format(list[i].createdAt.toLocal())),
                    onTap: () {
                      ref.read(chatControllerProvider.notifier).open(list[i].id);
                      context.pop();
                    },
                  ),
                ),
              ),
      ),
    );
  }
}
