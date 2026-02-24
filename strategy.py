"""Базовая стратегия блэкджека.

Содержит полные таблицы оптимальных решений для:
- Жёстких рук (hard hands)
- Мягких рук (soft hands, с тузом за 11)
- Пар (splitting)

Действия: H=ЕЩЁ, S=ХВАТИТ, D=ДАБЛ, P=СПЛИТ
"""

# Карта дилера → индекс столбца (2..11, где 11 = туз)
# Формат таблиц: {сумма_игрока: {карта_дилера: действие}}
# H = Hit (ЕЩЁ), S = Stand (ХВАТИТ), D = Double (ДАБЛ), P = Split (СПЛИТ)

# =====================================================================
# Жёсткие руки (hard) — нет туза за 11
# =====================================================================
HARD_TABLE: dict[int, dict[int, str]] = {
    # hard 5-8: всегда ЕЩЁ
    5:  {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    6:  {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    7:  {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    8:  {2: "H", 3: "H", 4: "H", 5: "H", 6: "H", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    # hard 9: дабл на 3-6
    9:  {2: "H", 3: "D", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    # hard 10: дабл на 2-9
    10: {2: "D", 3: "D", 4: "D", 5: "D", 6: "D", 7: "D", 8: "D", 9: "D", 10: "H", 11: "H"},
    # hard 11: дабл на 2-10
    11: {2: "D", 3: "D", 4: "D", 5: "D", 6: "D", 7: "D", 8: "D", 9: "D", 10: "D", 11: "H"},
    # hard 12: стоим на 4-6
    12: {2: "H", 3: "H", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    # hard 13-16: стоим на 2-6
    13: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    14: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    15: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    16: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    # hard 17+: всегда ХВАТИТ
    17: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 11: "S"},
    18: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 11: "S"},
    19: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 11: "S"},
    20: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 11: "S"},
    21: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 11: "S"},
}

# =====================================================================
# Мягкие руки (soft) — туз считается за 11
# Ключ = общая сумма (туз=11 + другая карта), т.е. soft 13 = A+2
# =====================================================================
SOFT_TABLE: dict[int, dict[int, str]] = {
    # A+2 (soft 13), A+3 (soft 14)
    13: {2: "H", 3: "H", 4: "H", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    14: {2: "H", 3: "H", 4: "H", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    # A+4 (soft 15), A+5 (soft 16)
    15: {2: "H", 3: "H", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    16: {2: "H", 3: "H", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    # A+6 (soft 17)
    17: {2: "H", 3: "D", 4: "D", 5: "D", 6: "D", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    # A+7 (soft 18): дабл 2-6, стоим 7-8, бьём 9-A
    18: {2: "D", 3: "D", 4: "D", 5: "D", 6: "D", 7: "S", 8: "S", 9: "H", 10: "H", 11: "H"},
    # A+8 (soft 19): всегда ХВАТИТ
    19: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 11: "S"},
    # A+9 (soft 20), A+10 (soft 21): ХВАТИТ
    20: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 11: "S"},
    21: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 11: "S"},
}

# =====================================================================
# Пары (pair) — решение о сплите
# Ключ = значение одной карты из пары (2..11, где 11=A)
# P = Split (СПЛИТ), иначе смотри hard/soft таблицу
# =====================================================================
PAIR_TABLE: dict[int, dict[int, str]] = {
    # 2-2: сплит на 2-7
    2:  {2: "P", 3: "P", 4: "P", 5: "P", 6: "P", 7: "P", 8: "H", 9: "H", 10: "H", 11: "H"},
    # 3-3: сплит на 2-7
    3:  {2: "P", 3: "P", 4: "P", 5: "P", 6: "P", 7: "P", 8: "H", 9: "H", 10: "H", 11: "H"},
    # 4-4: сплит на 5-6
    4:  {2: "H", 3: "H", 4: "H", 5: "P", 6: "P", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    # 5-5: никогда не сплитим (играем как hard 10)
    5:  {2: "D", 3: "D", 4: "D", 5: "D", 6: "D", 7: "D", 8: "D", 9: "D", 10: "H", 11: "H"},
    # 6-6: сплит на 2-6
    6:  {2: "P", 3: "P", 4: "P", 5: "P", 6: "P", 7: "H", 8: "H", 9: "H", 10: "H", 11: "H"},
    # 7-7: сплит на 2-7
    7:  {2: "P", 3: "P", 4: "P", 5: "P", 6: "P", 7: "P", 8: "H", 9: "H", 10: "H", 11: "H"},
    # 8-8: ВСЕГДА сплит
    8:  {2: "P", 3: "P", 4: "P", 5: "P", 6: "P", 7: "P", 8: "P", 9: "P", 10: "P", 11: "P"},
    # 9-9: сплит на 2-6, 8-9; стоим на 7, 10, A
    9:  {2: "P", 3: "P", 4: "P", 5: "P", 6: "P", 7: "S", 8: "P", 9: "P", 10: "S", 11: "S"},
    # 10-10: НИКОГДА не сплитим
    10: {2: "S", 3: "S", 4: "S", 5: "S", 6: "S", 7: "S", 8: "S", 9: "S", 10: "S", 11: "S"},
    # A-A: ВСЕГДА сплит
    11: {2: "P", 3: "P", 4: "P", 5: "P", 6: "P", 7: "P", 8: "P", 9: "P", 10: "P", 11: "P"},
}

# Названия действий на русском
ACTION_NAMES = {
    "H": "ЕЩЁ",
    "S": "ХВАТИТ",
    "D": "ДАБЛ",
    "P": "СПЛИТ",
}

# Объяснения на русском
_EXPLANATIONS = {
    "H": "Рука слабая, нужно брать ещё",
    "S": "Рука достаточно сильная, стоим",
    "D": "Выгодная позиция — удваиваем ставку",
    "P": "Пару лучше разделить",
}


def card_value(rank: str) -> int:
    """Преобразовать ранг карты в числовое значение.

    '2'-'9' → 2-9, '10','В','Д','К' → 10, 'Т' → 11 (туз).
    """
    rank = rank.upper().strip()
    if rank in ("10", "В", "Д", "К", "J", "Q", "K", "T"):
        return 10
    if rank in ("Т", "A", "1", "ACE"):
        return 11  # туз (кириллическая Т)
    if rank.isdigit():
        return int(rank)
    return 0


def hand_value(cards: list[str]) -> tuple[int, bool]:
    """Вычислить сумму руки.

    Returns:
        (total, is_soft) — сумма очков и мягкая ли рука.
    """
    values = [card_value(c) for c in cards]
    total = sum(values)
    aces = values.count(11)

    # Понижаем тузы с 11 до 1 если перебор
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1

    is_soft = aces > 0  # есть хотя бы один туз, считающийся за 11
    return total, is_soft


def is_pair(cards: list[str]) -> bool:
    """Проверить, является ли рука парой (ровно 2 карты одного номинала)."""
    if len(cards) != 2:
        return False
    return card_value(cards[0]) == card_value(cards[1])


def get_recommendation(
    player_cards: list[str],
    dealer_upcard: str,
    can_double: bool = True,
    can_split: bool = True,
) -> dict:
    """Получить рекомендацию по базовой стратегии.

    Args:
        player_cards: список рангов карт игрока, напр. ["8", "7"]
        dealer_upcard: ранг открытой карты дилера, напр. "10"
        can_double: доступен ли дабл (обычно только на первых 2 картах)
        can_split: доступен ли сплит

    Returns:
        dict с ключами:
        - action: "H"/"S"/"D"/"P"
        - action_ru: "ЕЩЁ"/"ХВАТИТ"/"ДАБЛ"/"СПЛИТ"
        - explanation: объяснение на русском
        - hand_total: сумма руки
        - is_soft: мягкая ли рука
        - is_pair_hand: пара ли
    """
    dealer_val = card_value(dealer_upcard)
    total, is_soft = hand_value(player_cards)
    pair = is_pair(player_cards)

    action = "S"  # по умолчанию ХВАТИТ

    # 1. Блэкджек (21 с двух карт)
    if total == 21 and len(player_cards) == 2:
        action = "S"
        explanation = "Блэкджек! Поздравляю!"
        return {
            "action": action,
            "action_ru": ACTION_NAMES[action],
            "explanation": explanation,
            "hand_total": total,
            "is_soft": is_soft,
            "is_pair_hand": pair,
        }

    # 2. Перебор
    if total > 21:
        action = "S"
        explanation = "Перебор!"
        return {
            "action": action,
            "action_ru": ACTION_NAMES[action],
            "explanation": explanation,
            "hand_total": total,
            "is_soft": False,
            "is_pair_hand": False,
        }

    # 3. Пара — проверяем таблицу сплитов
    if pair and can_split and len(player_cards) == 2:
        pair_val = card_value(player_cards[0])
        pair_action = PAIR_TABLE.get(pair_val, {}).get(dealer_val)
        if pair_action == "P":
            action = "P"
            explanation = _pair_explanation(pair_val, dealer_val)
            return {
                "action": action,
                "action_ru": ACTION_NAMES[action],
                "explanation": explanation,
                "hand_total": total,
                "is_soft": is_soft,
                "is_pair_hand": True,
            }
        # Если таблица пар не говорит сплитить — переходим к hard/soft

    # 4. Мягкая рука (есть туз = 11)
    if is_soft and total in SOFT_TABLE:
        action = SOFT_TABLE[total].get(dealer_val, "H")
    # 5. Жёсткая рука
    elif total in HARD_TABLE:
        action = HARD_TABLE[total].get(dealer_val, "H")
    elif total >= 17:
        action = "S"
    else:
        action = "H"

    # Если дабл недоступен (>2 карт), заменяем D на H
    if action == "D" and not can_double:
        action = "H"

    # Генерируем объяснение
    explanation = _build_explanation(total, is_soft, dealer_val, action)

    return {
        "action": action,
        "action_ru": ACTION_NAMES[action],
        "explanation": explanation,
        "hand_total": total,
        "is_soft": is_soft,
        "is_pair_hand": pair and len(player_cards) == 2,
    }


def _pair_explanation(pair_val: int, dealer_val: int) -> str:
    """Объяснение для сплита."""
    names = {11: "тузы", 8: "восьмёрки", 9: "девятки", 7: "семёрки",
             6: "шестёрки", 4: "четвёрки", 3: "тройки", 2: "двойки"}
    name = names.get(pair_val, f"{pair_val}-{pair_val}")
    if pair_val == 11:
        return "Тузы — ВСЕГДА разделяй"
    if pair_val == 8:
        return "Восьмёрки — ВСЕГДА разделяй"
    return f"Разделяй {name} против дилера {dealer_val}"


def _build_explanation(total: int, is_soft: bool, dealer_val: int, action: str) -> str:
    """Построить объяснение решения."""
    hand_type = "Soft" if is_soft else "Hard"
    action_word = ACTION_NAMES[action]
    dealer_str = "Т" if dealer_val == 11 else str(dealer_val)

    if action == "S" and total >= 17:
        return f"{hand_type} {total} — сильная рука, стоим"
    if action == "S" and dealer_val <= 6:
        return f"{hand_type} {total} vs {dealer_str} — дилер слабый, стоим"
    if action == "H" and dealer_val >= 7:
        return f"{hand_type} {total} vs {dealer_str} — дилер сильный, берём"
    if action == "H":
        return f"{hand_type} {total} vs {dealer_str} — рука слабая, берём"
    if action == "D":
        return f"{hand_type} {total} vs {dealer_str} — выгодная позиция, удваиваем!"
    return f"{hand_type} {total} vs {dealer_str} → {action_word}"
