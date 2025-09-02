from rest_framework import serializers


class HabitRewardChoiceValidator:
    """Класс-валидатор для проверок:
    1) что в полезной привычке:
        - нельзя одновременно указать связанную привычку (related_pleasant_habit) и вознаграждение (reward);
        - должно быть указано хотя бы одно из двух полей.
    2) что в приятной привычке:
        - нельзя указывать ни вознаграждение (reward), ни связанную привычки (related_pleasant_habit)."""

    # ДЛЯ ИНФО:
    # DRF официально передаёт в __call__ именно ***attrs*** (словарь с данными), а не ****args***:
    # 1) Когда пишем ***def __call__(self, attrs)***, то явно называем параметр и читающему код сразу понятно,
    # что именно сюда придут такие данные из сериализатора.
    # 2) Теоретически я могу написать ***def __call__(self, *args, **kwargs)***, а потом достать attrs = args[0],
    # но это костыльное решение с точки зрения лучших практик:
    #   - менее читаемо для другого разработчика.
    #   - есть риск ошибки, если кто-то изменит сигнатуру вызова или перепутает, что лежит в args[0].
    #   - линтеры и IDE не смогут подсказать тип или автодополнение для attrs.

    def __call__(self, attrs):
        """Метод __call__() делает экземпляр класса вызываемым, как функцию.
        Используется в DRF как валидатор поля сериализатора."""
        is_pleasant = attrs.get("is_pleasant")
        reward = attrs.get("reward")
        related_pleasant_habit = attrs.get("related_pleasant_habit")

        # Если привычка полезная:
        if not is_pleasant:
            if related_pleasant_habit and reward:
                raise serializers.ValidationError(
                    "Нельзя одновременно выбрать и связанную приятную привычку, и вознаграждение."
                )

            if not related_pleasant_habit and not reward:
                raise serializers.ValidationError(
                    "Необходимо выбрать либо связанную приятную привычку, либо вознаграждение."
                )

            return attrs

        # Если привычка приятная:
        return attrs


class RelatedHabitPleasantValidator:
    """Класс-валидатор для проверки: в связанные привычки могут попадать только привычки с признаком приятной."""

    def __call__(self, attrs):
        """Метод __call__() делает экземпляр класса вызываемым, как функцию.
        Используется в DRF как валидатор поля сериализатора."""
        related_pleasant_habit = attrs.get("related_pleasant_habit")

        if related_pleasant_habit and not related_pleasant_habit.is_pleasant:
            raise serializers.ValidationError(
                "В связанные привычки могут попадать только привычки с признаком приятной."
            )

        return attrs


class PleasantHabitRestrictionsValidator:
    """Класс-валидатор для проверки: у приятной привычки не может быть вознаграждения или связанной привычки."""

    def __call__(self, attrs):
        """Метод __call__() делает экземпляр класса вызываемым, как функцию.
        Используется в DRF как валидатор поля сериализатора."""
        is_pleasant = attrs.get("is_pleasant")
        reward = attrs.get("reward")
        related_pleasant_habit = attrs.get("related_pleasant_habit")

        if is_pleasant and (reward or related_pleasant_habit):
            raise serializers.ValidationError(
                "У приятной привычки не может быть вознаграждения или связанной привычки."
            )

        return attrs
