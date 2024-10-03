from django.db import transaction
from game_progress_tracker.models import PlayerLevel, LevelPrize
from game_progress_tracker.utils.decorators import log_execution_time, retry
from game_progress_tracker.utils.logging_config import award_logger


@log_execution_time(award_logger)
@retry((Exception,), tries=3, delay=1, backoff=2, logger=award_logger)
def award_prize(player_id, level_id):
    try:
        with transaction.atomic():
            player_level = PlayerLevel.objects.select_for_update().get(
                player_id=player_id, level_id=level_id, is_completed=True, prize_awarded=False
            )

            level_prize = LevelPrize.objects.filter(level_id=level_id).first()
            if not level_prize:
                award_logger.warning(f"Приз не найден для уровня {level_id}")
                return False

            LevelPrize.objects.create(level_id=level_id, prize_id=level_prize.prize_id, player_id=player_id)
            player_level.prize_awarded = True
            player_level.save()

            award_logger.info(f"Приз успешно присвоен игроку {player_id} за уровень {level_id}")
            return True
    except PlayerLevel.DoesNotExist:
        award_logger.error(f"Не найден завершенный уровень {level_id} для игрока {player_id}")
        return False
    except Exception as e:
        award_logger.exception(f"Ошибка при присвоении приза игроку {player_id} за уровень {level_id}: {str(e)}")
        raise