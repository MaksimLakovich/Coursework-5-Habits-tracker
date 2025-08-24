from rest_framework import serializers

from habits.models import Habits


class HabitsSerializer(serializers.ModelSerializer):
    """Класс-сериализатор с использованием класса *ModelSerializer* для осуществления базовой сериализация в DRF на
    основе модели *Habits*. Описывает то, какие поля модели *Habits* будут участвовать в сериализации и десериализации.
    """

    MIN_TIME = 1
    MAX_TIME = 120

    def validate_time_to_complete(self, value):
        """Кастомная валидация поля *time_to_complete*: привычка должна выполняться в допустимом диапазоне."""
        if not (self.MIN_TIME <= value <= self.MAX_TIME):
            raise serializers.ValidationError(
                f"Время выполнения должно быть от {self.MIN_TIME} до {self.MAX_TIME} секунд."
            )
        return value

    class Meta:
        model = Habits
        fields = "__all__"
        # validators = ...
        read_only_fields = ("created_at", "updated_at",)
