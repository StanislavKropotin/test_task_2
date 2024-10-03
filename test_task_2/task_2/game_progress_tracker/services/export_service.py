import csv
from django.db.models import Prefetch
from game_progress_tracker.models import PlayerLevel, LevelPrize
from game_progress_tracker.utils.decorators import log_execution_time, retry
from game_progress_tracker.utils.logging_config import export_logger


@log_execution_time(export_logger)
@retry((Exception,), tries=3, delay=1, backoff=2, logger=export_logger)
def export_player_data_to_csv(output_file):
    try:
        queryset = PlayerLevel.objects.select_related('player', 'level').prefetch_related(
            Prefetch('level__levelprize_set', queryset=LevelPrize.objects.select_related('prize'))
        ).values(
            'player__player_id',
            'level__title',
            'is_completed',
            'level__levelprize__prize__title'
        )

        total_records = queryset.count()
        export_logger.info(f"Начало экспорта {total_records} записей в {output_file}")

        with open(output_file, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=['player_id', 'level_title', 'is_completed', 'prize_title'])
            writer.writeheader()

            for i, chunk in enumerate(queryset.iterator(chunk_size=1000)):
                row = {
                    'player_id': chunk['player__player_id'],
                    'level_title': chunk['level__title'],
                    'is_completed': 'Yes' if chunk['is_completed'] else 'No',
                    'prize_title': chunk['level__levelprize__prize__title'] or 'No prize'
                }
                writer.writerow(row)

                if (i + 1) % 10000 == 0:
                    progress = (i + 1) / total_records * 100
                    export_logger.info(f"Прогресс экспорта: {progress:.2f}% ({i + 1} из {total_records})")

        export_logger.info(f"Экспорт успешно завершен. Файл сохранен: {output_file}")
    except Exception as e:
        export_logger.exception(f"Ошибка при экспорте данных в CSV: {str(e)}")
        raise