import json
import os
import random
import time
from pathlib import Path

import blessed

SUITS = ['♠', '♥', '♦', '♣']  # ♠ ♥ ♦ ♣
RANKS = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
RED_SUITS = {'♥', '♦'}

CARD_W = 7
CARD_H = 5
W, H = 80, 24


def _card_lines(rank, suit, hidden=False):
    if hidden:
        return ['┌─────┐', '│░░░░░│', '│░░░░░│', '│░░░░░│', '└─────┘']
    rl, rr = rank.ljust(2), rank.rjust(2)
    return [
        '┌─────┐',
        f'│{rl}   │',
        f'│  {suit}  │',
        f'│   {rr}│',
        '└─────┘',
    ]


def _hand_value(cards):
    total, aces = 0, 0
    for rank, _ in cards:
        if rank in ('J', 'Q', 'K'):
            total += 10
        elif rank == 'A':
            aces += 1
            total += 11
        else:
            total += int(rank)
    while total > 21 and aces:
        total -= 10
        aces -= 1
    return total


def _is_blackjack(cards):
    return len(cards) == 2 and _hand_value(cards) == 21


def main():
    term = blessed.Terminal()

    left_key = os.environ.get('RETRO_KEY_LEFT', 'KEY_LEFT')
    right_key = os.environ.get('RETRO_KEY_RIGHT', 'KEY_RIGHT')
    confirm_key = os.environ.get('RETRO_KEY_A', 'z')

    cash = 100
    peak = 100

    deck = []

    def _refill():
        nonlocal deck
        deck = [(r, s) for s in SUITS for r in RANKS]
        random.shuffle(deck)

    def _deal(n=1):
        cards = []
        for _ in range(n):
            if not deck:
                _refill()
            cards.append(deck.pop())
        return cards

    _refill()

    def _at(x, y):
        ox = max(0, (term.width - W) // 2)
        oy = max(0, (term.height - H) // 2)
        return term.move_xy(ox + x, oy + y)

    def _draw_cards(cards, y, hide_first=False):
        n = len(cards)
        total_w = n * (CARD_W + 1) - 1
        sx = max(0, (W - total_w) // 2)
        for i, (rank, suit) in enumerate(cards):
            lines = _card_lines(rank, suit, hidden=(i == 0 and hide_first))
            cx = sx + i * (CARD_W + 1)
            for dy, line in enumerate(lines):
                use_red = (suit in RED_SUITS) and not (i == 0 and hide_first)
                col = term.red if use_red else ''
                print(_at(cx, y + dy) + col + line + term.normal)

    def _val_str(cards, hide_first=False):
        visible = cards[1:] if hide_first else cards
        v = _hand_value(visible)
        s = f'showing: {v}' if hide_first else f'total: {v}'
        if not hide_first:
            if v > 21:
                s += '  BUST'
            elif _is_blackjack(cards):
                s += '  BLACKJACK!'
        return s

    def _draw_table(player, dealer, hide_dealer=True, message='', actions=None, selected=0):
        out = [term.home + term.clear]

        title = '♠  B L A C K J A C K  ♠'
        cash_str = f'Cash: ${cash}'
        tx = (W - len(title)) // 2
        out.append(_at(tx, 1) + term.bold + title + term.normal)
        out.append(_at(W - len(cash_str) - 1, 1) + term.bold + cash_str + term.normal)

        dlabel = '─── DEALER ───'
        out.append(_at((W - len(dlabel)) // 2, 3) + dlabel)

        plabel = '─── YOU ───'
        out.append(_at((W - len(plabel)) // 2, 11) + plabel)

        if message:
            out.append(_at((W - len(message)) // 2, 19) + term.bold + message + term.normal)

        if actions:
            parts = []
            for i, act in enumerate(actions):
                label = f'  {act}  '
                parts.append((term.reverse + label + term.normal) if i == selected else label)
            clean_w = sum(len(f'  {a}  ') for a in actions) + 4 * (len(actions) - 1)
            ax = max(0, (W - clean_w) // 2)
            row = ('    '.join(parts))
            out.append(_at(ax, 21) + row)

        hint = 'LEFT/RIGHT: select   A/ENTER: confirm   Q: quit'
        out.append(_at((W - len(hint)) // 2, 23) + term.dim + hint + term.normal)

        print(''.join(out), end='', flush=True)

        # Cards drawn after main print to allow color sequences
        _draw_cards(dealer, 4, hide_first=hide_dealer)
        dv = _val_str(dealer, hide_first=hide_dealer)
        print(_at((W - len(dv)) // 2, 9) + dv, flush=True)

        _draw_cards(player, 12, hide_first=False)
        pv = _val_str(player)
        print(_at((W - len(pv)) // 2, 17) + pv, flush=True)

    def _get_action(player, dealer, hide_dealer=True, message='', actions=None):
        if actions is None:
            actions = ['NEXT HAND', 'QUIT']
        selected = 0
        while True:
            _draw_table(player, dealer, hide_dealer=hide_dealer, message=message,
                        actions=actions, selected=selected)
            with term.cbreak():
                key = term.inkey(timeout=120)
            if not key:
                continue
            k = key.name if key.is_sequence else str(key)
            if k in (left_key, 'KEY_LEFT'):
                selected = (selected - 1) % len(actions)
            elif k in (right_key, 'KEY_RIGHT'):
                selected = (selected + 1) % len(actions)
            elif k in (confirm_key, 'KEY_ENTER', '\n', '\r', ' '):
                return actions[selected]
            elif k in ('q', 'Q', 'KEY_ESCAPE'):
                return 'QUIT'

    # ── main game loop ──────────────────────────────────────────────────
    running = True
    while running and cash > 0:
        player = _deal(2)
        dealer = _deal(2)

        p_bj = _is_blackjack(player)
        d_bj = _is_blackjack(dealer)

        if p_bj or d_bj:
            if p_bj and d_bj:
                msg = 'Both Blackjack!  PUSH — no change.'
            elif p_bj:
                cash += 15  # 3:2 on $10 bet
                peak = max(peak, cash)
                msg = f'BLACKJACK!  You win $15!  Cash: ${cash}'
            else:
                cash -= 10
                msg = f'Dealer Blackjack!  You lose $10.  Cash: ${cash}'
            act = _get_action(player, dealer, hide_dealer=False, message=msg)
            if act == 'QUIT':
                running = False
            continue

        # ── player turn ──────────────────────────────────────────────
        busted = False
        doubled = False

        while True:
            if _hand_value(player) >= 21:
                break
            acts = ['HIT', 'STAND']
            if len(player) == 2:
                acts.append('DOUBLE')
            act = _get_action(player, dealer, message='Your turn', actions=acts)
            if act == 'HIT':
                player += _deal(1)
                if _hand_value(player) > 21:
                    busted = True
                    break
            elif act == 'STAND':
                break
            elif act == 'DOUBLE':
                player += _deal(1)
                doubled = True
                break
            elif act == 'QUIT':
                running = False
                break

        if not running:
            break

        # ── dealer turn ──────────────────────────────────────────────
        if not busted:
            _draw_table(player, dealer, hide_dealer=False, message='Dealer drawing...')
            time.sleep(0.8)
            while _hand_value(dealer) < 17:
                dealer += _deal(1)
                _draw_table(player, dealer, hide_dealer=False, message='Dealer drawing...')
                time.sleep(0.6)

        # ── resolve ──────────────────────────────────────────────────
        bet = 20 if doubled else 10
        p_val = _hand_value(player)
        d_val = _hand_value(dealer)

        if busted:
            cash -= bet
            msg = f'Bust!  You lose ${bet}.'
        elif d_val > 21:
            cash += bet
            peak = max(peak, cash)
            msg = f'Dealer busts!  You win ${bet}!'
        elif p_val > d_val:
            cash += bet
            peak = max(peak, cash)
            msg = f'You win ${bet}!'
        elif p_val == d_val:
            msg = 'Push — no change.'
        else:
            cash -= bet
            msg = f'Dealer wins.  You lose ${bet}.'

        cash = max(cash, 0)
        full_msg = f'{msg}  Cash: ${cash}'

        if cash == 0:
            _draw_table(player, dealer, hide_dealer=False, message=full_msg + '  — GAME OVER')
            with term.cbreak():
                term.inkey(timeout=4)
            break

        act = _get_action(player, dealer, hide_dealer=False, message=full_msg)
        if act == 'QUIT':
            running = False

    Path('result.json').write_text(json.dumps({'score': peak}))
    print(term.home + term.clear)
    gover = _at((W // 2) - 20, 10)
    print(gover + term.bold + f'  Final cash: ${cash}   |   Best cash (score): ${peak}' + term.normal)
    print(_at((W // 2) - 12, 12) + 'Thanks for playing Blackjack!')
    time.sleep(2)


if __name__ == '__main__':
    main()
