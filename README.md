# Небольшая инструкция по запуску:

1) Папку task_2 необходимо сделать Sources Root -> ПКМ на папке -> Mark Directory as -> Sources Root -> папка становится cинего цвета

2) Основные функции протестировал с помощью следующих команд в консоль:

python manage.py shell

# Импорты:

from game_progress_tracker.models import Player, Level, Prize, PlayerLevel, LevelPrize
from game_progress_tracker.services.award_service import award_prize
from game_progress_tracker.services.export_service import export_player_data_to_csv
from django.utils import timezone

# Тестовые данные

player1 = Player.objects.create(player_id="player1")
player2 = Player.objects.create(player_id="player2")
level1 = Level.objects.create(title="Level 1", order=1)
level2 = Level.objects.create(title="Level 2", order=2)
prize1 = Prize.objects.create(title="Prize 1")
prize2 = Prize.objects.create(title="Prize 2")

# Присвоение уровня игроку и отметка о завершении

player_level1 = PlayerLevel.objects.create(player=player1, level=level1, is_completed=True, completed=timezone.now())
LevelPrize.objects.create(level=level1, prize=prize1, player=player1)

# Вызов метода award_prize
result = award_prize(player1.id, level1.id)
print(f"Результат присвоения приза: {result}")

# Проверка присвоения приза
player_level1.refresh_from_db()
print(f"Приз присвоен: {player_level1.prize_awarded}")

# Создание дополнительных записей для тестирования экспорта
PlayerLevel.objects.create(player=player2, level=level1, is_completed=True, completed=timezone.now())
PlayerLevel.objects.create(player=player1, level=level2, is_completed=False)
PlayerLevel.objects.create(player=player2, level=level2, is_completed=True, completed=timezone.now())
LevelPrize.objects.create(level=level2, prize=prize2, player=player2)

# Вызов метода export_player_data_to_csv
export_player_data_to_csv('player_data_export.csv')

exit()

3) В файле player_data_export.csv уже есть записи появившиеся в результате работы команд выше.

4) Проблему что записей может быть 100 000 и более решил следующим образом:

  Использовал select_related и prefetch_related 

  Использовал метод iterator() для обрабаботки данных порциями

  Сделал логирование для отслеживания прогресса обработки больших объемов данных.
