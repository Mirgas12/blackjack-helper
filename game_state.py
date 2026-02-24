"""Состояние игры и статистика сессии блэкджека."""

from strategy import card_value, hand_value, is_pair


class Hand:
    """Рука игрока или дилера."""

    def __init__(self) -> None:
        self.cards: list[str] = []

    def add(self, rank: str) -> None:
        self.cards.append(rank)

    def clear(self) -> None:
        self.cards.clear()

    @property
    def total(self) -> int:
        val, _ = hand_value(self.cards)
        return val

    @property
    def is_soft(self) -> bool:
        _, soft = hand_value(self.cards)
        return soft

    @property
    def is_pair_hand(self) -> bool:
        return is_pair(self.cards)

    @property
    def is_blackjack(self) -> bool:
        return len(self.cards) == 2 and self.total == 21

    @property
    def is_bust(self) -> bool:
        return self.total > 21

    @property
    def can_double(self) -> bool:
        """Дабл доступен только на первых двух картах."""
        return len(self.cards) == 2

    @property
    def can_split(self) -> bool:
        """Сплит доступен если ровно 2 карты одного номинала."""
        return self.is_pair_hand

    def display(self) -> str:
        """Отображение карт для UI."""
        if not self.cards:
            return "—"
        return " ".join(self.cards)

    def __len__(self) -> int:
        return len(self.cards)


class SessionStats:
    """Статистика текущей сессии."""

    def __init__(self) -> None:
        self.hands_played: int = 0
        self.wins: int = 0
        self.losses: int = 0
        self.pushes: int = 0
        self.blackjacks: int = 0
        self.doubles_won: int = 0
        self.doubles_lost: int = 0

    def record_win(self) -> None:
        self.hands_played += 1
        self.wins += 1

    def record_loss(self) -> None:
        self.hands_played += 1
        self.losses += 1

    def record_push(self) -> None:
        self.hands_played += 1
        self.pushes += 1

    def record_blackjack(self) -> None:
        self.hands_played += 1
        self.wins += 1
        self.blackjacks += 1

    @property
    def win_rate(self) -> float:
        """Процент выигрышей."""
        if self.hands_played == 0:
            return 0.0
        return self.wins / self.hands_played * 100

    def reset(self) -> None:
        self.hands_played = 0
        self.wins = 0
        self.losses = 0
        self.pushes = 0
        self.blackjacks = 0
        self.doubles_won = 0
        self.doubles_lost = 0


class GameState:
    """Текущее состояние игры блэкджек.

    Хранит руки игрока и дилера, режим ввода, статистику.
    """

    # Режимы ввода: куда пойдёт следующая нажатая карта
    INPUT_DEALER = "dealer"
    INPUT_PLAYER = "player"
    INPUT_OTHERS = "others"  # чужие карты (только для счётчика)

    def __init__(self) -> None:
        self.player = Hand()
        self.dealer = Hand()
        self.others_cards: list[str] = []  # видимые карты других игроков
        self.stats = SessionStats()
        self.input_mode: str = self.INPUT_DEALER  # сначала вводим карту дилера

    def new_hand(self) -> None:
        """Начать новую раздачу (очистить карты, не статистику)."""
        self.player.clear()
        self.dealer.clear()
        self.others_cards.clear()
        self.input_mode = self.INPUT_DEALER

    def set_input_mode(self, mode: str) -> None:
        """Переключить режим ввода."""
        self.input_mode = mode

    def add_card(self, rank: str) -> str:
        """Добавить карту в текущий режим ввода.

        Returns:
            Куда добавлена карта: 'dealer', 'player' или 'others'.
        """
        if self.input_mode == self.INPUT_DEALER and len(self.dealer) == 0:
            self.dealer.add(rank)
            self.input_mode = self.INPUT_PLAYER  # после дилера → игрок
            return self.INPUT_DEALER
        elif self.input_mode == self.INPUT_OTHERS:
            self.others_cards.append(rank)
            return self.INPUT_OTHERS
        else:
            self.player.add(rank)
            return self.INPUT_PLAYER

    def undo_last(self) -> bool:
        """Отменить последнюю карту.

        Returns:
            True если удалось отменить.
        """
        if self.input_mode == self.INPUT_OTHERS and self.others_cards:
            self.others_cards.pop()
            return True
        if self.player.cards:
            self.player.cards.pop()
            return True
        if self.dealer.cards:
            self.dealer.cards.pop()
            self.input_mode = self.INPUT_DEALER
            return True
        return False

    @property
    def is_ready(self) -> bool:
        """Готовы ли данные для рекомендации (дилер + минимум 2 карты игрока)."""
        return len(self.dealer) >= 1 and len(self.player) >= 2

    @property
    def all_cards_in_hand(self) -> list[str]:
        """Все карты текущей раздачи (для счётчика)."""
        return self.dealer.cards + self.player.cards + self.others_cards
