import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """

        mines = set()

        if len(self.cells) == self.count:
            for cell in self.cells:
                mines.add(cell)

        return mines

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """

        if self.count == 0:
            return self.cells
        else:
            return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        
        if cell in self.cells:
            self.count -= 1
            self.cells.remove(cell)

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        
        if cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def check_knowledge(self):
        """
        Runs through knowledge sentences and compares them to see whether any new sentences can be deduced
        """
        end_function = False

        # Iterates sentances in the knowledge base to find definite mines and safes
        for sentence in self.knowledge:
            new_mines, new_safes = [], []

            for found_mine in sentence.known_mines():
                new_mines.append(found_mine)
            for found_safe in sentence.known_safes():
                new_safes.append(found_safe)

            for new in new_mines:
                self.mark_mine(new)
            for new in new_safes:
                self.mark_safe(new)

        # Compares all sentences to each other to see whether subsets can exclude each other (restarts if new info is found)
        sentence_no = len(self.knowledge)
        for sen_1_index, sentence_1 in enumerate(self.knowledge[:-2]):
            for sentence_2 in self.knowledge[(sen_1_index + 1):(sentence_no)]:
                if len(sentence_1.cells) > len(sentence_2.cells):
                    long_sentence, short_sentence = sentence_1, sentence_2
                elif len(sentence_1.cells) < len(sentence_2.cells):
                    long_sentence, short_sentence = sentence_2, sentence_1
                else:
                    continue
                
                subset = True

                # Checks whether the shorter sentence is a subset of the larger
                for cell in short_sentence.cells:
                    if cell not in long_sentence.cells:
                        subset = False
                        break

                if subset == False:
                    continue
                
                new_set = long_sentence.cells - short_sentence.cells

                # If the new set is already in a sentence, it discards it
                already_present = False
                for sentence in self.knowledge:
                    if new_set == sentence.cells:
                        already_present = True
                        break
                
                # If a new sentence is found the knowledge base is appended and the check re-run
                if already_present == False:
                    new_sentence = Sentence(long_sentence.cells - short_sentence.cells, long_sentence.count - short_sentence.count)
                    self.knowledge.append(new_sentence)
                    self.check_knowledge()
                    end_function = True
                    break
            
            if end_function == True:
                break
    
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        # Marks the known safe move as a being made and add to safe moves
        self.moves_made.add(cell)
        self.mark_safe(cell)

        surrounding_cells = set()

        # Iterates through 9 by 9 grid around the cell if within board bounds
        for i in range(-1, 2, 1):
            if (cell[0] + i) < self.width and (cell[0] + i) >= 0:
                for j in range(-1, 2, 1):
                    if (cell[1] + j) < self.height and (cell[1] + j) >= 0:

                        new_cell = (cell[0] + i, cell[1] + j)

                        # Excludes central cell
                        if i == 0 and j == 0:
                            pass
                        # Doesn't count any cells which have already been accounted for
                        elif new_cell not in self.moves_made:
                            if new_cell in self.mines:
                                count -= 1
                            elif new_cell not in self.safes:
                                surrounding_cells.add(new_cell)
                
        # Adds the new sentence to the knowledge base before inferring more data
        self.knowledge.append(Sentence(surrounding_cells, count))
        self.check_knowledge()

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
            
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """

        # Creates a set of all possible cells
        remaining = set()
        for i in range(self.width):
            for j in range(self.height):
                remaining.add((i, j))

        # Removes mined and taken cells from the total set
        remaining = remaining - self.moves_made
        remaining = remaining - self.mines

        # Returns a random cell unless there are no possible moves (in which case AI wins!)
        remaining_length = len(remaining)
        if remaining_length == 0:
            return None
        else:
            for random_cell in remaining:
                return random_cell
