"""Majestic Blackjack Assistant — помощник для блэкджека.

Компактное окно поверх игры. Вводишь карты кнопками —
получаешь оптимальное действие + подсчёт карт Hi-Lo.
"""

import sys
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QGridLayout, QFrame, QSpinBox,
)

from strategy import get_recommendation, card_value
from card_counter import CardCounter, HI_LO
from game_state import GameState


# =====================================================================
# Цвета для действий
# =====================================================================
ACTION_COLORS = {
    "H": "#2ecc71",   # зелёный — ЕЩЁ
    "S": "#e74c3c",   # красный — ХВАТИТ
    "D": "#3498db",   # синий — ДАБЛ
    "P": "#f39c12",   # оранжевый — СПЛИТ
}

# Стиль карточных кнопок
CARD_BTN_STYLE = """
    QPushButton {{
        background-color: {bg};
        color: {fg};
        border: 1px solid #555;
        border-radius: 4px;
        font-size: 14px;
        font-weight: bold;
        min-width: 36px;
        min-height: 32px;
        padding: 2px 6px;
    }}
    QPushButton:hover {{
        background-color: {hover};
        border: 1px solid #aaa;
    }}
    QPushButton:pressed {{
        background-color: {pressed};
    }}
"""

# Стиль управляющих кнопок
CONTROL_BTN_STYLE = """
    QPushButton {
        background-color: #34495e;
        color: white;
        border: 1px solid #555;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
        padding: 6px 12px;
    }
    QPushButton:hover {
        background-color: #4a6785;
    }
    QPushButton:pressed {
        background-color: #2c3e50;
    }
"""

# Стиль активной кнопки режима
MODE_BTN_ACTIVE = """
    QPushButton {{
        background-color: {bg};
        color: {fg};
        border: 2px solid {fg};
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        padding: 4px 10px;
    }}
"""

MODE_BTN_INACTIVE = """
    QPushButton {
        background-color: #2a2a3a;
        color: #7f8c8d;
        border: 1px solid #555;
        border-radius: 4px;
        font-size: 11px;
        padding: 4px 10px;
    }
    QPushButton:hover {
        background-color: #3a3a5a;
        color: #bdc3c7;
    }
"""


class BlackjackAssistant(QWidget):
    """Главное окно помощника блэкджека."""

    def __init__(self) -> None:
        super().__init__()
        self.game = GameState()
        self.counter = CardCounter(total_decks=6)
        self._hand_cards: list[str] = []  # карты текущей раздачи для отката

        self._setup_window()
        self._build_ui()
        self._update_display()

    # -----------------------------------------------------------------
    # Настройка окна
    # -----------------------------------------------------------------

    def _setup_window(self) -> None:
        self.setWindowTitle("Блэкджек Помощник")
        self.setWindowFlags(
            Qt.WindowStaysOnTopHint | Qt.WindowCloseButtonHint
        )
        self.setFixedWidth(430)
        self.setMinimumHeight(580)

        # Тёмная тема
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(30, 30, 40))
        palette.setColor(QPalette.WindowText, QColor(220, 220, 220))
        palette.setColor(QPalette.Base, QColor(40, 40, 55))
        palette.setColor(QPalette.Text, QColor(220, 220, 220))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

    # -----------------------------------------------------------------
    # Построение UI
    # -----------------------------------------------------------------

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(10, 8, 10, 8)

        # --- Заголовок ---
        title = QLabel("БЛЭКДЖЕК ПОМОЩНИК")
        title.setFont(QFont("Consolas", 14, QFont.Bold))
        title.setStyleSheet("color: #f1c40f;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # --- Информация о руках ---
        self.dealer_label = QLabel("Дилер: —")
        self.dealer_label.setFont(QFont("Consolas", 13))
        self.dealer_label.setStyleSheet("color: #e74c3c;")
        layout.addWidget(self.dealer_label)

        self.player_label = QLabel("Мои карты: —")
        self.player_label.setFont(QFont("Consolas", 13))
        self.player_label.setStyleSheet("color: #2ecc71;")
        layout.addWidget(self.player_label)

        self.total_label = QLabel("")
        self.total_label.setFont(QFont("Consolas", 11))
        self.total_label.setStyleSheet("color: #bdc3c7;")
        layout.addWidget(self.total_label)

        # Чужие карты
        self.others_label = QLabel("")
        self.others_label.setFont(QFont("Consolas", 10))
        self.others_label.setStyleSheet("color: #9b59b6;")
        layout.addWidget(self.others_label)

        # --- Разделитель ---
        layout.addWidget(self._separator())

        # --- Рекомендация ---
        self.rec_label = QLabel("Введите карты")
        self.rec_label.setFont(QFont("Consolas", 20, QFont.Bold))
        self.rec_label.setAlignment(Qt.AlignCenter)
        self.rec_label.setStyleSheet(
            "color: #95a5a6; padding: 8px; "
            "background-color: #1a1a2e; border-radius: 6px;"
        )
        layout.addWidget(self.rec_label)

        self.explain_label = QLabel("")
        self.explain_label.setFont(QFont("Consolas", 10))
        self.explain_label.setStyleSheet("color: #bdc3c7;")
        self.explain_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.explain_label)

        # --- Разделитель ---
        layout.addWidget(self._separator())

        # --- Счётчик карт ---
        count_layout = QHBoxLayout()

        self.rc_label = QLabel("RC: 0")
        self.rc_label.setFont(QFont("Consolas", 11, QFont.Bold))
        self.rc_label.setStyleSheet("color: #3498db;")
        count_layout.addWidget(self.rc_label)

        self.tc_label = QLabel("TC: 0.0")
        self.tc_label.setFont(QFont("Consolas", 11, QFont.Bold))
        self.tc_label.setStyleSheet("color: #3498db;")
        count_layout.addWidget(self.tc_label)

        self.decks_label = QLabel("Колод: 6.0")
        self.decks_label.setFont(QFont("Consolas", 10))
        self.decks_label.setStyleSheet("color: #7f8c8d;")
        count_layout.addWidget(self.decks_label)

        layout.addLayout(count_layout)

        # Ставка и преимущество
        bet_layout = QHBoxLayout()

        self.bet_label = QLabel("Ставка: минимум")
        self.bet_label.setFont(QFont("Consolas", 11, QFont.Bold))
        self.bet_label.setStyleSheet("color: #f39c12;")
        bet_layout.addWidget(self.bet_label)

        self.advantage_label = QLabel("Перевес: -0.5%")
        self.advantage_label.setFont(QFont("Consolas", 10))
        self.advantage_label.setStyleSheet("color: #7f8c8d;")
        bet_layout.addWidget(self.advantage_label)

        layout.addLayout(bet_layout)

        # --- Разделитель ---
        layout.addWidget(self._separator())

        # --- Режим ввода: кнопки переключения ---
        mode_layout = QHBoxLayout()
        mode_layout.setSpacing(4)

        self.btn_mode_dealer = QPushButton("Дилер")
        self.btn_mode_dealer.clicked.connect(
            lambda: self._set_input_mode(GameState.INPUT_DEALER))
        mode_layout.addWidget(self.btn_mode_dealer)

        self.btn_mode_player = QPushButton("Мои")
        self.btn_mode_player.clicked.connect(
            lambda: self._set_input_mode(GameState.INPUT_PLAYER))
        mode_layout.addWidget(self.btn_mode_player)

        self.btn_mode_others = QPushButton("Чужие")
        self.btn_mode_others.clicked.connect(
            lambda: self._set_input_mode(GameState.INPUT_OTHERS))
        mode_layout.addWidget(self.btn_mode_others)

        layout.addLayout(mode_layout)

        # --- Подсказка режима ввода ---
        self.input_hint = QLabel("Нажмите карту ДИЛЕРА")
        self.input_hint.setFont(QFont("Consolas", 10, QFont.Bold))
        self.input_hint.setStyleSheet("color: #e74c3c;")
        self.input_hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.input_hint)

        # --- Кнопки карт (английские) ---
        card_grid = QGridLayout()
        card_grid.setSpacing(3)

        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        for i, rank in enumerate(ranks):
            btn = QPushButton(rank)
            val = card_value(rank)

            # Цвета по Hi-Lo
            if 2 <= val <= 6:
                # мелкие +1 — зеленоватый
                bg, hover, pressed = "#1a3a2a", "#2a5a3a", "#0a2a1a"
                fg = "#2ecc71"
            elif val >= 10:
                # крупные -1 — красноватый
                bg, hover, pressed = "#3a1a1a", "#5a2a2a", "#2a0a0a"
                fg = "#e74c3c"
            else:
                # нейтральные 0 — серый
                bg, hover, pressed = "#2a2a3a", "#3a3a5a", "#1a1a2a"
                fg = "#bdc3c7"

            btn.setStyleSheet(CARD_BTN_STYLE.format(
                bg=bg, fg=fg, hover=hover, pressed=pressed
            ))
            btn.clicked.connect(lambda checked, r=rank: self._on_card_click(r))

            row = 0 if i < 9 else 1
            col = i if i < 9 else (i - 9)
            card_grid.addWidget(btn, row, col)

        layout.addLayout(card_grid)

        # --- Управляющие кнопки ---
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(4)

        btn_new = QPushButton("Новая рука")
        btn_new.setStyleSheet(CONTROL_BTN_STYLE)
        btn_new.clicked.connect(self._on_new_hand)
        ctrl_layout.addWidget(btn_new)

        btn_undo = QPushButton("Отмена")
        btn_undo.setStyleSheet(CONTROL_BTN_STYLE)
        btn_undo.clicked.connect(self._on_undo)
        ctrl_layout.addWidget(btn_undo)

        btn_shoe = QPushButton("Новый шу")
        btn_shoe.setStyleSheet(CONTROL_BTN_STYLE)
        btn_shoe.clicked.connect(self._on_new_shoe)
        ctrl_layout.addWidget(btn_shoe)

        layout.addLayout(ctrl_layout)

        # --- Настройка колод + результат руки ---
        bottom_layout = QHBoxLayout()
        decks_lbl = QLabel("Колод:")
        decks_lbl.setFont(QFont("Consolas", 10))
        decks_lbl.setStyleSheet("color: #7f8c8d;")
        bottom_layout.addWidget(decks_lbl)

        self.decks_spin = QSpinBox()
        self.decks_spin.setRange(1, 8)
        self.decks_spin.setValue(6)
        self.decks_spin.setStyleSheet(
            "QSpinBox { background: #2a2a3a; color: white; "
            "border: 1px solid #555; border-radius: 3px; padding: 2px; }"
        )
        self.decks_spin.valueChanged.connect(self._on_decks_changed)
        bottom_layout.addWidget(self.decks_spin)
        bottom_layout.addStretch()

        # Кнопки результата руки
        for text, result, bg, fg in [
            ("W", "win", "#1a3a2a", "#2ecc71"),
            ("L", "loss", "#3a1a1a", "#e74c3c"),
            ("P", "push", "#2a2a3a", "#f39c12"),
        ]:
            btn = QPushButton(text)
            btn.setToolTip({"W": "Выиграл", "L": "Проиграл", "P": "Ничья"}[text])
            btn.setStyleSheet(
                f"QPushButton {{ background: {bg}; color: {fg}; "
                f"border: 1px solid {fg}; border-radius: 4px; "
                f"font-size: 12px; font-weight: bold; "
                f"min-width: 30px; padding: 4px 8px; }}"
                f"QPushButton:hover {{ background: #3a3a5a; }}"
            )
            btn.clicked.connect(lambda checked, r=result: self._record_result(r))
            bottom_layout.addWidget(btn)

        layout.addLayout(bottom_layout)

        # --- Разделитель ---
        layout.addWidget(self._separator())

        # --- Статистика сессии ---
        self.stats_label = QLabel("Сессия: 0 рук")
        self.stats_label.setFont(QFont("Consolas", 10))
        self.stats_label.setStyleSheet("color: #7f8c8d;")
        self.stats_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stats_label)

    # -----------------------------------------------------------------
    # Обработка событий
    # -----------------------------------------------------------------

    def _set_input_mode(self, mode: str) -> None:
        """Переключить режим ввода карт."""
        self.game.set_input_mode(mode)
        self._update_display()

    def _on_card_click(self, rank: str) -> None:
        """Обработка нажатия на кнопку карты."""
        self.game.add_card(rank)
        self._hand_cards.append(rank)
        self.counter.add_card(rank)
        self._update_display()

    def _on_new_hand(self) -> None:
        """Новая раздача — очистить карты, сохранить счёт."""
        self.game.new_hand()
        self._hand_cards.clear()
        self._update_display()

    def _on_undo(self) -> None:
        """Отменить последнюю карту."""
        if self._hand_cards:
            removed = self._hand_cards.pop()
            # Откатить счётчик
            val = card_value(removed)
            self.counter.running_count -= HI_LO.get(val, 0)
            self.counter.cards_dealt = max(0, self.counter.cards_dealt - 1)
            # Откатить состояние
            self.game.undo_last()
        self._update_display()

    def _on_new_shoe(self) -> None:
        """Новый шу — сброс счётчика и карт."""
        self.counter.reset_shoe()
        self.game.new_hand()
        self._hand_cards.clear()
        self._update_display()

    def _on_decks_changed(self, value: int) -> None:
        """Изменение количества колод."""
        self.counter.set_decks(value)
        self._update_display()

    def _record_result(self, result: str) -> None:
        """Записать результат руки."""
        if result == "win":
            if self.game.player.is_blackjack:
                self.game.stats.record_blackjack()
            else:
                self.game.stats.record_win()
        elif result == "loss":
            self.game.stats.record_loss()
        elif result == "push":
            self.game.stats.record_push()
        self._on_new_hand()

    # -----------------------------------------------------------------
    # Обновление отображения
    # -----------------------------------------------------------------

    def _update_display(self) -> None:
        """Обновить все элементы UI."""
        mode = self.game.input_mode

        # Дилер
        if self.game.dealer.cards:
            d_val = card_value(self.game.dealer.cards[0])
            d_str = self.game.dealer.display()
            self.dealer_label.setText(f"Дилер: [{d_str}] ({d_val})")
        else:
            self.dealer_label.setText("Дилер: —")

        # Игрок
        if self.game.player.cards:
            total = self.game.player.total
            soft_str = "мягкая" if self.game.player.is_soft else "жёсткая"
            p_str = self.game.player.display()

            if self.game.player.is_blackjack:
                self.player_label.setText(f"Мои карты: [{p_str}]")
                self.total_label.setText("БЛЭКДЖЕК!")
                self.total_label.setStyleSheet("color: #f1c40f; font-weight: bold;")
            elif self.game.player.is_bust:
                self.player_label.setText(f"Мои карты: [{p_str}]")
                self.total_label.setText(f"Сумма: {total} — ПЕРЕБОР!")
                self.total_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
            else:
                self.player_label.setText(f"Мои карты: [{p_str}]")
                pair_str = " | ПАРА" if self.game.player.is_pair_hand else ""
                self.total_label.setText(f"Сумма: {total} ({soft_str}){pair_str}")
                self.total_label.setStyleSheet("color: #bdc3c7;")
        else:
            self.player_label.setText("Мои карты: —")
            self.total_label.setText("")

        # Чужие карты
        if self.game.others_cards:
            o_str = " ".join(self.game.others_cards)
            self.others_label.setText(f"Чужие карты: [{o_str}] ({len(self.game.others_cards)} шт)")
        else:
            self.others_label.setText("")

        # Кнопки режимов — подсветка активной
        for btn, btn_mode, color in [
            (self.btn_mode_dealer, GameState.INPUT_DEALER, "#e74c3c"),
            (self.btn_mode_player, GameState.INPUT_PLAYER, "#2ecc71"),
            (self.btn_mode_others, GameState.INPUT_OTHERS, "#9b59b6"),
        ]:
            if mode == btn_mode:
                btn.setStyleSheet(MODE_BTN_ACTIVE.format(bg="#1a1a2e", fg=color))
            else:
                btn.setStyleSheet(MODE_BTN_INACTIVE)

        # Подсказка ввода
        hints = {
            GameState.INPUT_DEALER: ("Нажмите карту ДИЛЕРА", "#e74c3c"),
            GameState.INPUT_PLAYER: ("Нажмите свои карты", "#2ecc71"),
            GameState.INPUT_OTHERS: ("Нажмите карты ДРУГИХ игроков", "#9b59b6"),
        }
        hint_text, hint_color = hints.get(mode, ("", "#bdc3c7"))
        self.input_hint.setText(hint_text)
        self.input_hint.setStyleSheet(f"color: {hint_color}; font-weight: bold;")

        # Рекомендация
        if self.game.is_ready:
            rec = get_recommendation(
                self.game.player.cards,
                self.game.dealer.cards[0],
                can_double=self.game.player.can_double,
                can_split=self.game.player.can_split,
            )
            action = rec["action"]
            action_ru = rec["action_ru"]
            color = ACTION_COLORS.get(action, "#95a5a6")
            self.rec_label.setText(f">> {action_ru} <<")
            self.rec_label.setStyleSheet(
                f"color: {color}; padding: 8px; font-weight: bold; "
                f"background-color: #1a1a2e; border-radius: 6px; "
                f"border: 2px solid {color};"
            )
            self.explain_label.setText(rec["explanation"])
        else:
            self.rec_label.setText("Введите карты")
            self.rec_label.setStyleSheet(
                "color: #95a5a6; padding: 8px; "
                "background-color: #1a1a2e; border-radius: 6px;"
            )
            self.explain_label.setText("")

        # Счётчик карт
        rc = self.counter.running_count
        tc = self.counter.true_count
        decks_rem = self.counter.decks_remaining

        rc_color = "#2ecc71" if rc > 0 else "#e74c3c" if rc < 0 else "#3498db"
        tc_color = "#2ecc71" if tc > 0 else "#e74c3c" if tc < 0 else "#3498db"

        self.rc_label.setText(f"RC: {rc:+d}")
        self.rc_label.setStyleSheet(f"color: {rc_color}; font-weight: bold;")

        self.tc_label.setText(f"TC: {tc:+.1f}")
        self.tc_label.setStyleSheet(f"color: {tc_color}; font-weight: bold;")

        self.decks_label.setText(f"Колод: {decks_rem:.1f}")

        # Ставка
        bet_text, _ = self.counter.bet_recommendation()
        adv = self.counter.player_advantage
        adv_color = "#2ecc71" if adv > 0 else "#e74c3c"
        self.bet_label.setText(f"Ставка: {bet_text}")
        self.advantage_label.setText(f"Перевес: {adv:+.1f}%")
        self.advantage_label.setStyleSheet(f"color: {adv_color};")

        # Статистика
        s = self.game.stats
        if s.hands_played > 0:
            self.stats_label.setText(
                f"Сессия: {s.hands_played} рук | "
                f"W:{s.wins} L:{s.losses} P:{s.pushes} | "
                f"Винрейт: {s.win_rate:.0f}%"
            )
        else:
            self.stats_label.setText("Сессия: 0 рук")

    # -----------------------------------------------------------------
    # Горячие клавиши
    # -----------------------------------------------------------------

    def keyPressEvent(self, event) -> None:
        key = event.key()
        if key == Qt.Key_Return or key == Qt.Key_Enter:
            self._on_new_hand()
        elif key == Qt.Key_Escape:
            self._on_new_hand()
        elif key == Qt.Key_Backspace:
            self._on_undo()
        elif key == Qt.Key_F1:
            if self.isVisible():
                self.hide()
            else:
                self.show()
        else:
            super().keyPressEvent(event)

    # -----------------------------------------------------------------
    # Утилиты
    # -----------------------------------------------------------------

    @staticmethod
    def _separator() -> QFrame:
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #3a3a5a;")
        return sep


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = BlackjackAssistant()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
