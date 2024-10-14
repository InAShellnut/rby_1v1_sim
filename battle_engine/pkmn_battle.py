import random
import logging


def effectiveness(move, opponent):
    INDEXES = ('Normal', 'Fighting', 'Flying', 'Poison', 'Ground', 'Rock', 'Bug',
               'Ghost', 'Fire', 'Water', 'Grass', 'Electric', 'Psychic', 'Ice',
               'Dragon')
    TYPE_CHART = (
        (4, 4, 4, 4, 4, 2, 4, 0, 4, 4, 4, 4, 4, 4, 4),
        (8, 4, 2, 2, 4, 8, 2, 0, 4, 4, 4, 4, 2, 8, 4),
        (4, 8, 4, 4, 4, 2, 8, 4, 4, 4, 8, 2, 4, 4, 4),
        (4, 4, 4, 2, 2, 2, 8, 2, 4, 4, 8, 4, 4, 4, 4),
        (4, 4, 0, 8, 4, 8, 2, 4, 8, 4, 2, 8, 4, 4, 4),
        (4, 2, 8, 4, 2, 4, 8, 4, 8, 4, 4, 4, 4, 8, 4),
        (4, 2, 2, 8, 4, 4, 4, 2, 2, 4, 8, 4, 8, 4, 4),
        (0, 4, 4, 4, 4, 4, 4, 8, 4, 4, 4, 4, 0, 4, 4),
        (4, 4, 4, 4, 4, 2, 8, 4, 2, 2, 8, 4, 4, 8, 2),
        (4, 4, 4, 4, 8, 8, 4, 4, 8, 2, 2, 4, 4, 4, 2),
        (4, 4, 2, 2, 8, 8, 2, 4, 2, 8, 2, 4, 4, 4, 2),
        (4, 4, 8, 4, 0, 4, 4, 4, 4, 8, 2, 2, 4, 4, 2),
        (4, 8, 4, 8, 4, 4, 4, 4, 4, 4, 4, 4, 2, 4, 4),
        (4, 4, 8, 4, 8, 4, 4, 4, 4, 2, 8, 4, 4, 2, 8),
        (4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 8),
    )
    move_i = INDEXES.index(move.TYPE)
    result = 4
    for t in opponent.TYPES:
        opponent_i = INDEXES.index(t)
        result = (result * TYPE_CHART[move_i][opponent_i]) // 4
    if result == 0:
        logging.debug('It doesnt affect %s!', opponent.nickname)
    elif result < 4:
        logging.debug("It's not very effective!")
    elif result > 4:
        logging.debug("It's super effective!")
    return result


def rng(target):
    return random.randint(0, 255) < target


def check_hp(p1, p2):
    # TODO: figure out draws
    if p1.hp <= 0 and p2.hp <= 0:
        return (p1, p2)
    elif p2.hp <= 0:
        return (p1,)
    elif p1.hp <= 0:
        return (p2,)
    else:
        return ()


def battle(pokemon1, pokemon2, pokemon1_select_attack,
           pokemon2_select_attack, count_first_turn=False, check_result=None):
    winner = ()
    if count_first_turn:
        is_turn_1 = True
    else:
        is_turn_1 = False
    while winner == ():
        # select moves
        if count_first_turn:
            pokemon1_move = pokemon1_select_attack(pokemon1, pokemon2, is_turn_1)
            pokemon2_move = pokemon2_select_attack(pokemon2, pokemon1, is_turn_1)
            is_turn_1 = False
        else:
            pokemon1_move = pokemon1_select_attack(pokemon1, pokemon2)
            pokemon2_move = pokemon2_select_attack(pokemon2, pokemon1)
        if pokemon1.get_stat('speed') > pokemon2.get_stat('speed') \
                or pokemon1.get_stat('speed') == pokemon2.get_stat('speed') and random.randint(0, 1):
            logging.debug('--')
            pokemon1.attack(pokemon1_move, pokemon2)
            winner = check_hp(pokemon1, pokemon2)
            if winner:
                break
            pokemon2.attack(pokemon2_move, pokemon1)
            winner = check_hp(pokemon1, pokemon2)
            if winner:
                break
            logging.debug('%s at %s, %s at %s', pokemon1.nickname, pokemon1.hp, pokemon2.nickname, pokemon2.hp)
        else:
            logging.debug('--')
            pokemon2.attack(pokemon2_move, pokemon1)
            winner = check_hp(pokemon1, pokemon2)
            if winner:
                break
            pokemon1.attack(pokemon1_move, pokemon2)
            winner = check_hp(pokemon1, pokemon2)
            if winner:
                break
            logging.debug('%s at %s, %s at %s', pokemon1.nickname, pokemon1.hp, pokemon2.nickname, pokemon2.hp)
        if check_result is not None:
            winner = check_result(pokemon1, pokemon2)
    if len(winner) == 1:
        logging.debug('%s wins!',winner[0].nickname)
    else:
        logging.debug('draw')
    return winner


class PPError(Exception):
    pass
