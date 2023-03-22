from copy import deepcopy
from math import *

import pygame

blue = (0, 0, 255)
white = (255, 255, 255)
display = pygame.display.set_mode((800, 800), 0, 0)


def minimax(board, depth, max_player):
    if depth == 0 or board.winner() is not None:
        return board.evaluate(), board

    if max_player:
        max_evaluation = -inf
        best_board = None
        for move in get_all_moves(board, blue):
            evaluation = minimax(move, depth - 1, False)[0]
            # max_evaluation = max(max_evaluation, evaluation)
            if evaluation > max_evaluation:
                max_evaluation = evaluation
                best_board = move
        return max_evaluation, best_board
    else:
        min_evaluation = inf
        best_board = None
        for move in get_all_moves(board, white):
            evaluation = minimax(move, depth - 1, True)[0]
            # min_evaluation = min(min_evaluation, evaluation)
            if min_evaluation > evaluation:
                min_evaluation = evaluation
                best_board = move
        return min_evaluation, best_board


def get_all_moves(board, color):
    moves = []
    for piece in board.get_all_pieces(color):
        valid_moves = board.all_valid_moves(piece)
        for move in valid_moves:
            # draw_moves(board, piece)
            temp_board = deepcopy(board)
            temp_piece = temp_board.selected_position(piece.row, piece.column)
            new_board = simulate_move(temp_piece, move, temp_board)
            moves.append(new_board)
    return moves


def simulate_move(piece, move, board):
    board.move(piece, move[0], move[1])
    if move in board.pieces_skipped:
        board.remove(board.pieces_skipped[move])
    # draw_moves(board, piece)
    return board


def draw_moves(board, piece):
    board.draw(display)
    board.draw_valid_moves(display, piece)
    pygame.draw.circle(display, (0, 255, 0), (piece.x, piece.y), 50, 5)
    pygame.display.update()
