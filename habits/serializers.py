from rest_framework import serializers

from habits.models import Habits
from habits.validators import (HabitRewardChoiceValidator,
                               PleasantHabitRestrictionsValidator,
                               RelatedHabitPleasantValidator)


class HabitsSerializer(serializers.ModelSerializer):
    """Класс-сериализатор с использованием класса *ModelSerializer* для осуществления базовой сериализация в DRF на
    основе модели *Habits*. Описывает то, какие поля модели *Habits* будут участвовать в сериализации и десериализации.
    """

    MIN_TIME = 1
    MAX_TIME = 120
    MIN_DAYS_FREQUENCY = 1
    MAX_DAYS_FREQUENCY = 7

    def validate_time_to_complete(self, value):
        """Кастомная валидация поля *time_to_complete*: привычка должна выполняться в допустимом диапазоне."""
        if not (self.MIN_TIME <= value <= self.MAX_TIME):
            raise serializers.ValidationError(
                f"Время выполнения должно быть от {self.MIN_TIME} до {self.MAX_TIME} секунд."
            )
        return value

    def validate_periodicity(self, value):
        """Кастомная валидация поля *periodicity*: привычка должна выполняться хотя бы 1 раз в 7 дней."""
        if not (self.MIN_DAYS_FREQUENCY <= value <= self.MAX_DAYS_FREQUENCY):
            raise serializers.ValidationError(
                f"Периодичность должна быть в диапазоне от {self.MIN_DAYS_FREQUENCY} "
                f"до {self.MAX_DAYS_FREQUENCY} дней. "
                f"Нельзя выполнять привычку реже 1 раза в {self.MAX_DAYS_FREQUENCY} дней."
            )
        return value

    def to_representation(self, instance):
        """Скрывает приватные данные (location, owner) у публичных привычек других пользователей."""
        data = super().to_representation(instance)
        request = self.context.get("request")  # Достаю request. В DRF request передается в сериализатор через context.
        if request and instance.owner != request.user:
            # Убираю location и owner. Лучше добавить default=None, чтобы не словить KeyError, если поле уже удалено.
            data.pop("location", None)
            data.pop("owner", None)
        return data

    class Meta:
        model = Habits
        fields = "__all__"
        validators = [
            HabitRewardChoiceValidator(),
            RelatedHabitPleasantValidator(),
            PleasantHabitRestrictionsValidator(),
        ]
        read_only_fields = ("created_at", "updated_at",)
