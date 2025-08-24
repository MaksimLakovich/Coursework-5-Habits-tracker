from rest_framework import serializers


class HabitRewardChoiceValidator:
    """Класс-валидатор для проверки:
    - нельзя одновременно указать связанную привычки и вознаграждение;
    - должно быть указано хотя бы одно из двух полей."""

    def __call__(self, attrs):
        """Метод __call__() делает экземпляр класса вызываемым, как функцию.
        Используется в DRF как валидатор поля сериализатора."""
        related_pleasant_habit = attrs.get("related_pleasant_habit")
        reward = attrs.get("reward")

        if related_pleasant_habit and reward:
            raise serializers.ValidationError(
                "Нельзя одновременно выбрать и связанную приятную привычку, и вознаграждение."
            )

        if not related_pleasant_habit and not reward:
            raise serializers.ValidationError(
                "Необходимо выбрать либо связанную приятную привычку, либо вознаграждение."
            )

        return attrs
