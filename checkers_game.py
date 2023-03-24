import pygame
import os
from minimax_alg import minimax
# pygame variables
x = 100
y = 100
os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)
pygame.init()
display = pygame.display.set_mode((800, 800), 0, 32)
font = pygame.font.SysFont("Times new roman", 120)
font1 = pygame.font.SysFont("Times new roman", 80)
font2 = pygame.font.SysFont("Times new roman", 50)

# game variables
rows = 8
columns = 8
square_size = 100


chop_sound = pygame.mixer.Sound("LD KWSnap.wav")
CROWN = pygame.transform.scale(pygame.image.load("crown.png"), (44, 25))

# colors
black = (0, 0, 0)
grey = (128, 128, 128)
blue = (0, 0, 255)
white = (255, 255, 255)
red = (255, 0, 0)
yellow = (255, 255, 0)


# the board
class Board:
    valid_moves = []
    skipped = []
    pieces_skipped = {}

    def __init__(self):
        self.board = []
        self.create_board()
        self.blue_left = self.white_left = 12
        self.blue_kings = self.white_kings = 0

    @ staticmethod
    def draw_squares(surface):
        surface.fill(black)
        for row in range(rows):
            for column in range(row % 2, columns, 2):
                pygame.draw.rect(surface, grey, (row * square_size, column * square_size, square_size, square_size))

    def create_board(self):
        for row in range(rows):
            self.board.append([])
            for column in range(columns):
                if column % 2 == ((row + 1) % 2):
                    if row < 3:
                        self.board[row].append(Piece(row, column, blue))
                    elif row > 4:
                        self.board[row].append(Piece(row, column, white))
                    else:
                        self.board[row].append(0)
                else:
                    self.board[row].append(0)

    def draw(self, surface):
        self.draw_squares(surface)
        for row in range(rows):
            for col in range(columns):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(surface)

    def selected_position(self, row, column):
        return self.board[row][column]

    def move(self, piece_selected, row, column):
        self.board[piece_selected.row][piece_selected.column], self.board[row][column] = \
            self.board[row][column], self.board[piece_selected.row][piece_selected.column]
        piece_selected.move(row, column)
        if row == rows - 1 or row == 0:
            piece_selected.make_king()
            if piece_selected.color == white:
                self.white_kings += 1
            else:
                self.blue_kings += 1
        return True

    def all_valid_moves(self, piece_selected):
        moves = []
        right = piece_selected.column + 1
        left = piece_selected.column - 1
        upward_row = piece_selected.row - 1
        downward_row = piece_selected.row + 1
        if piece_selected.color == white and not piece_selected.king:
            if upward_row >= 0 and right <= 7:
                if self.board[upward_row][right] == 0:
                    moves.append((upward_row, right))
                    self.pieces_skipped.update({(upward_row, right): [None]})
                    self.skipped.append(None)
                elif self.board[upward_row][right].color == blue:
                    moves.extend(self.upward_right(piece_selected.row, piece_selected.column, piece_selected,
                                                   skipped=[]))
            if upward_row >= 0 and left >= 0:
                if self.board[upward_row][left] == 0:
                    moves.append((upward_row, left))
                    self.pieces_skipped.update({(upward_row, left): [None]})
                    self.skipped.append(None)
                elif self.board[upward_row][left].color == blue:
                    moves.extend(self.upward_left(piece_selected.row, piece_selected.column, piece_selected,
                                                  skipped=[]))

        elif piece_selected.color == blue and not piece_selected.king:
            if downward_row <= 7 and right <= 7:
                if self.board[downward_row][right] == 0:
                    moves.append((downward_row, right))
                    self.pieces_skipped.update({(downward_row, right): [None]})
                    self.skipped.append(None)
                elif self.board[downward_row][right].color == white:
                    moves.extend(self.downward_right(piece_selected.row, piece_selected.column, piece_selected,
                                                     skipped=[]))
            if downward_row <= 7 and left >= 0:
                if self.board[downward_row][left] == 0:
                    moves.append((downward_row, left))
                    self.pieces_skipped.update({(downward_row, left): [None]})
                    self.skipped.append(None)
                elif self.board[downward_row][left].color == white:
                    moves.extend(self.downward_left(piece_selected.row, piece_selected.column, piece_selected,
                                                    skipped=[]))

        elif piece_selected.king:
            moves.extend(self.king_movement(piece_selected))
        self.valid_moves.extend(moves)
        return moves

    def king_movement(self, piece_selected):
        moves = []
        row = piece_selected.row
        right = piece_selected.column + 1
        left = piece_selected.column - 1

        if row < 8 and right < 8:
            right = piece_selected.column + 1
            for something in range(row, 8):
                if something + 1 < 8 and right <= 7 and self.board[something + 1][right] == 0:
                    moves.append((something + 1, right))
                    self.skipped.append(None)
                else:
                    moves.extend(self.downward_right(something, right - 1, piece_selected, skipped=[]))
                    break
                right += 1

        if left >= 0 and row < 8:
            left = piece_selected.column - 1
            for something in range(row, 8):
                if something + 1 < 8 and left >= 0 and self.board[something + 1][left] == 0:
                    moves.append((something + 1, left))
                    self.skipped.append(None)
                else:
                    moves.extend(self.downward_left(something, left + 1, piece_selected, skipped=[]))
                    break
                left -= 1

        if row >= 0 and right < 8:
            right = piece_selected.column + 1
            for something in range(row, 0, -1):
                if something - 1 >= 0 and right <= 7 and self.board[something - 1][right] == 0:
                    moves.append((something - 1, right))
                    self.skipped.append(None)
                else:
                    moves.extend(self.upward_right(something, right - 1, piece_selected, skipped=[]))
                    break
                right += 1

        if row >= 0 and left >= 0:
            left = piece_selected.column - 1
            for something in range(row, 0, -1):
                if something - 1 >= 0 and left >= 0 and self.board[something - 1][left] == 0:
                    moves.append((something - 1, left))
                    self.skipped.append(None)
                else:
                    moves.extend(self.upward_left(something, left + 1, piece_selected, skipped=[]))
                    break
                left -= 1
        return moves

    def upward_right(self, row, column, piece_selected, skipped, i=0):
        moves = []
        opp_color = None
        upward = row - 2
        right = column + 2
        if piece_selected.color == white:
            opp_color = blue
        elif piece_selected.color == blue:
            opp_color = white
        if upward >= 0 and right <= 7:
            if self.board[upward][right] == 0 and self.board[upward + 1][right - 1] != 0 \
                    and self.board[upward + 1][right - 1].color == opp_color:
                moves.append((upward, right))
                skipped.append(self.board[upward + 1][right - 1])
                pieces_skipped = checker(skipped)
                self.pieces_skipped.update({(upward, right): pieces_skipped[0:i+1]})
                moves.extend(self.upward_right(upward, right, piece_selected, skipped, i=i+1))
                moves.extend(self.upward_left(upward, right, piece_selected, skipped, i=i+1))
                if piece_selected.king:
                    moves.extend(self.downward_right(upward, right, piece_selected, skipped, i=i+1))
        return moves

    def upward_left(self, row, column, piece_selected, skipped, i=0):
        moves = []
        opp_color = None
        upward = row - 2
        left = column - 2
        if piece_selected.color == white:
            opp_color = blue
        elif piece_selected.color == blue:
            opp_color = white
        if upward >= 0 and left >= 0:
            if self.board[upward][left] == 0 and self.board[upward + 1][left + 1] != 0 \
                    and self.board[upward + 1][left + 1].color == opp_color:
                moves.append((upward, left))
                skipped.append(self.board[upward + 1][left + 1])
                pieces_skipped = checker(skipped)
                self.pieces_skipped.update({(upward, left): pieces_skipped[0:i+1]})
                moves.extend(self.upward_right(upward, left, piece_selected, skipped, i=i+1))
                moves.extend(self.upward_left(upward, left, piece_selected, skipped, i=i+1))
                if piece_selected.king:
                    moves.extend(self.downward_left(upward, left, piece_selected, skipped, i=i+1))
        return moves

    def downward_right(self, row, column, piece_selected, skipped, i=0):
        moves = []
        opp_color = None
        downward = row + 2
        right = column + 2
        if piece_selected.color == white:
            opp_color = blue
        elif piece_selected.color == blue:
            opp_color = white
        if downward <= 7 and right <= 7:
            if self.board[downward][right] == 0 and self.board[downward - 1][right - 1] != 0 \
                    and self.board[downward - 1][right - 1].color == opp_color:
                moves.append((downward, right))
                skipped.append(self.board[downward - 1][right - 1])
                pieces_skipped = checker(skipped)
                self.pieces_skipped.update({(downward, right): pieces_skipped[0:i+1]})
                moves.extend(self.downward_left(downward, right, piece_selected, skipped, i=i+1))
                moves.extend(self.downward_right(downward, right, piece_selected, skipped, i=i+1))
                if piece_selected.king:
                    moves.extend(self.upward_right(downward, right, piece_selected, skipped, i=i+1))
        return moves

    def downward_left(self, row, column, piece_selected, skipped, i=0):
        moves = []
        opp_color = None
        downward = row + 2
        left = column - 2
        if piece_selected.color == white:
            opp_color = blue
        elif piece_selected.color == blue:
            opp_color = white
        if downward <= 7 and left >= 0:
            if self.board[downward][left] == 0 and self.board[downward - 1][left + 1] != 0 \
                    and self.board[downward - 1][left + 1].color == opp_color:
                moves.append((downward, left))
                skipped.append(self.board[downward - 1][left + 1])
                pieces_skipped = checker(skipped)
                self.pieces_skipped.update({(downward, left): pieces_skipped[0:i + 1]})
                moves.extend(self.downward_right(downward, left, piece_selected, skipped, i=i+1))
                moves.extend(self.downward_left(downward, left, piece_selected, skipped, i=i+1))
                if piece_selected.king:
                    moves.extend(self.upward_left(downward, left, piece_selected, skipped, i=i+1))
        return moves

    def evaluate(self):
        return self.blue_left - self.white_left + (self.blue_kings * 0.5 - self.white_kings * 0.5)

    def get_all_pieces(self, color):
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces

    def winner(self):
        if self.blue_left <= 0:
            return white
        elif self.white_left <= 0:
            return blue
        return None

    def draw_valid_moves(self, surface, piece):
        moves = self.all_valid_moves(piece)
        for move in moves:
            row, column = move
            pygame.draw.circle(surface, red,
                               (column * square_size + square_size//2, row * square_size + square_size//2), 15)

    def remove(self, pieces_skipped):
        for piece in pieces_skipped:
            if piece is not None:
                self.board[piece.row][piece.column] = 0
                if piece.color == white:
                    self.white_left -= 1
                else:
                    self.blue_left -= 1
        pieces_skipped.clear()


class Piece:
    PADDING = 15
    OUTLINE = 5

    def __init__(self, row, column, color):
        self.row = row
        self.column = column
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.center_position()

    def center_position(self):
        self.x = square_size * self.column + square_size // 2
        self.y = square_size * self.row + square_size // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        radius = square_size//2 - self.PADDING
        pygame.draw.circle(win, grey, (self.x, self.y), radius + self.OUTLINE)
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width()//2, self.y - CROWN.get_height()//2))

    def move(self, row, column):
        self.row = row
        self.column = column
        self.center_position()

    def __repr__(self):
        return str(self.color)


class GameManager:
    valid_moves = Board.valid_moves

    def __init__(self, surface):
        self.selected = None
        self.board = Board()
        self.turn = white
        self.surface = surface

    def update(self):
        self.board.draw(self.surface)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def select(self, row, column):
        piece = self.board.selected_position(row, column)
        if self.selected:
            result = self.piece_movement(row, column)
            if not result:
                self.selected = None
                self.select(row, column)

        elif piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.board.all_valid_moves(self.selected)
            self.valid_moves = self.board.valid_moves

    def piece_movement(self, row, column):
        position_selected = self.board.selected_position(row, column)
        if self.selected and position_selected == 0 and (row, column) in self.valid_moves:
            self.board.move(self.selected, row, column)
            if (row, column) in self.board.pieces_skipped:
                skipped = self.board.pieces_skipped[(row, column)]
                self.board.remove(skipped)
            chop_sound.play()
            self.change_turn()
        else:
            self.board.valid_moves.clear()
            self.board.pieces_skipped.clear()
            self.board.skipped.clear()
            return False
        return True

    def change_turn(self):
        self.valid_moves.clear()
        if self.turn == white:
            self.turn = blue
        else:
            self.turn = white

    def draw_valid_moves(self, moves):
        for move in moves:
            row, column = move
            pygame.draw.circle(self.surface, red,
                               (column * square_size + square_size//2, row * square_size + square_size//2), 15)

    def get_board(self):
        return self.board

    def ai_move(self, board):
        self.board = board
        self.change_turn()


def checker(skipped):
    if len(skipped) > 1:
        if skipped[-1].row == skipped[-2].row:
            skipped.pop(-2)
    return skipped


def get_mouse_row_column(position):
    x, y = position
    row = x//square_size
    column = y//square_size
    return row, column

# Main Function
def main():
    running = True
    game = GameManager(display)
    while running:
        if game.turn == blue:
            value, new_board = minimax(game.get_board(), 3, True)
            game.ai_move(new_board)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_position = pygame.mouse.get_pos()
                row, column = get_mouse_row_column(mouse_position)
                game.select(column, row)

        game.update()

    pygame.quit()


main()
