from rest_framework import serializers

from habits.models import Habits


class HabitsSerializer(serializers.ModelSerializer):
    """Класс-сериализатор с использованием класса *ModelSerializer* для осуществления базовой сериализация в DRF на
    основе модели *Habits*. Описывает то, какие поля модели *Habits* будут участвовать в сериализации и десериализации.
    """

    def validate_time_to_complete(self, value):
        """Кастомная валидация поля *time_to_complete*: привычка должна выполняться не дольше 120 секунд."""
        if value and value > 120:
            raise serializers.ValidationError("Время выполнения должно быть не больше 120 секунд.")
        return value

    class Meta:
        model = Habits
        fields = "__all__"
        # validators = ...
        read_only_fields = ("created_at", "updated_at",)
