import constants
def predict_snakes(board, enemy_snakes):
    for snake in enemy_snakes:
        predict_moves(board, snake)

def predict_moves(board, snake):
    curr_pos = snake.head

    moves = board.safe_moves(curr_pos, ignored=[constants.ENEMY_TAIL, constants.ENEMY_NEXT_MOVE, constants.ENEMY_MOVE_2])

    for pos in moves.values():
        board.board[pos] = constants.ENEMY_NEXT_MOVE
        moves2 = board.safe_moves(pos, ignored=[constants.ENEMY_TAIL])
        for pos2 in moves2.values():
            board.board[pos2] = constants.ENEMY_MOVE_2