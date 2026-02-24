"""Счётчик карт по системе Hi-Lo.

Считает бегущий счёт (Running Count), истинный счёт (True Count),
и даёт рекомендацию по размеру ставки.
"""

from strategy import card_value

# Hi-Lo значения: мелкие карты +1, крупные -1, средние 0
HI_LO: dict[int, int] = {
    2: +1, 3: +1, 4: +1, 5: +1, 6: +1,   # мелкие
    7: 0, 8: 0, 9: 0,                      # нейтральные
    10: -1, 11: -1,                         # крупные (10,В,Д,К,Т)
}


class CardCounter:
    """Счётчик карт Hi-Lo для блэкджека.

    Attributes:
        total_decks: количество колод в шу (обычно 6 или 8).
        running_count: бегущий счёт.
        cards_dealt: сколько карт вышло.
    """

    def __init__(self, total_decks: int = 6) -> None:
        self.total_decks = total_decks
        self.running_count: int = 0
        self.cards_dealt: int = 0
        self._total_cards = total_decks * 52

    def add_card(self, rank: str) -> None:
        """Добавить карту в счёт.

        Args:
            rank: ранг карты ('2'-'9','10','В','Д','К','Т')
        """
        val = card_value(rank)
        count_val = HI_LO.get(val, 0)
        self.running_count += count_val
        self.cards_dealt += 1

    def add_cards(self, ranks: list[str]) -> None:
        """Добавить несколько карт."""
        for r in ranks:
            self.add_card(r)

    @property
    def cards_remaining(self) -> int:
        """Карт осталось в шу."""
        return max(self._total_cards - self.cards_dealt, 1)

    @property
    def decks_remaining(self) -> float:
        """Примерное количество оставшихся колод."""
        return self.cards_remaining / 52

    @property
    def true_count(self) -> float:
        """Истинный счёт = бегущий / оставшиеся колоды."""
        decks = self.decks_remaining
        if decks < 0.25:
            decks = 0.25  # защита от деления на ~0
        return self.running_count / decks

    @property
    def penetration(self) -> float:
        """Процент пройденных карт (0.0 - 1.0)."""
        return self.cards_dealt / self._total_cards

    def bet_recommendation(self) -> tuple[str, int]:
        """Рекомендация по размеру ставки.

        Returns:
            (текст, множитель) — напр. ("3x от минимума", 3)
        """
        tc = self.true_count
        if tc <= 0:
            return ("Минимум", 1)
        elif tc < 2:
            return ("2x от минимума", 2)
        elif tc < 4:
            return ("3x от минимума", 3)
        elif tc < 6:
            return ("5x от минимума", 5)
        else:
            return ("Максимум! 8x", 8)

    @property
    def player_advantage(self) -> float:
        """Примерное преимущество игрока в процентах.

        Базовое преимущество казино ~0.5%.
        Каждая единица TC даёт ~+0.5% игроку.
        """
        return -0.5 + self.true_count * 0.5

    def reset_shoe(self) -> None:
        """Сброс — новый шу (перемешали колоды)."""
        self.running_count = 0
        self.cards_dealt = 0

    def set_decks(self, n: int) -> None:
        """Изменить количество колод."""
        self.total_decks = n
        self._total_cards = n * 52
        self.reset_shoe()
