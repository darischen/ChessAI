import pygame
from const import *
from board import Board
from dragger import Dragger
from square import Square
from config import Config

class Game:
    def __init__(self):
        self.next_player = 'white'
        self.hovered_sqr = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()
        self.game_over = False
    
    
    #Functions to show
    def show_bg(self, surface):
        theme = self.config.theme
        
        for row in range(ROWS):
            for col in range(COLS):
                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

                if col == 0:
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(str(ROWS-row), 1, color)
                    lbl_pos = (5, 5 + row * SQSIZE)
                    surface.blit(lbl, lbl_pos)

                if row == 7:
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    lbl = self.config.font.render(Square.get_alphacol(col), 1, color)
                    lbl_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)
                    surface.blit(lbl, lbl_pos)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):
                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece
                    
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = (col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2)
                        piece.texture_rect = img.get_rect(center=img_center)
                        surface.blit(img, piece.texture_rect)
                        
    def show_moves(self, surface):
        theme = self.config.theme
        if self.dragger.dragging:
            piece = self.dragger.piece
            for move in piece.moves:
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)
                
    def show_last_move(self, surface):
        theme = self.config.theme
        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final
            
            for pos in [initial, final]:
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_sqr:
            color = (180, 180, 180)
            rect = (self.hovered_sqr.col * SQSIZE, self.hovered_sqr.row * SQSIZE, SQSIZE, SQSIZE)
            pygame.draw.rect(surface, color, rect, width=3)
        
    def next_turn(self):
        # print (f"next_turn + {self.next_player}")
        self.next_player = 'white' if self.next_player == 'black' else 'black'
        
        self.board.update_position_history(self.next_player)
        
        if self.board.is_checkmate(self.next_player):
            self.game_over = True
            winner = "Black" if self.next_player == "white" else "White"
            print(f"Checkmate! {winner} wins!")
        elif self.board.is_stalemate(self.next_player):
            self.game_over = True
            print("Stalemate! It's a draw.")
        elif self.board.half_move_clock >= 100:
            self.game_over = True
            print("Draw! 50-move rule.")
        elif self.board.is_threefold_repetition():
            self.game_over = True
            print("Draw! Threefold repetition.")
        elif self.board.is_insufficient_material():
            self.game_over = True
            print("Draw! Insufficient material.")
        elif self.board.is_in_check(self.next_player):
            self.config.check_sound.play()
            
    def show_check(self, surface):
        theme = self.config.theme
        for row in range(ROWS):
            for col in range(COLS):
                square = self.board.squares[row][col]
                if square.has_piece():
                    piece = square.piece
                    if piece.__class__.__name__ == "King" and self.board.is_in_check(piece.color):
                        color = theme.moves.light if (row + col) % 2 == 0 else theme.moves.dark
                        rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)
                        pygame.draw.rect(surface, color, rect)
        
    def set_hover(self, row, col):
        self.hovered_sqr = self.board.squares[row][col]
        
    def change_theme(self):
        self.config.change_theme()
        
    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()

    def reset(self):
        self.__init__()