import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """

        # Runs through variable domains and removes words which don't match the variable length
        for var in self.domains:
            remove_word = []
            for word in self.domains[var]:
                if len(word) != var.length:
                    remove_word.append(word)

            for word in remove_word:
                self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """

        overlap = self.crossword.overlaps[x, y]
        if overlap == None:
            return False
        else:
            changed = False

            # Goes through words in the X var domain and checks whether there's a suitable match in the Y var domain
            remove_list = []
            for x_word in self.domains[x]:
                arc_consistent = False
                for y_word in self.domains[y]:
                    if x_word[overlap[0]] == y_word[overlap[1]]:
                        arc_consistent = True

                if arc_consistent == False:
                    changed = True
                    remove_list.append(x_word)

            for word in remove_list:
                self.domains[x].remove(word)

            return changed

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # Populates a list with all arcs in the problem
        arc_list = []
        if arcs == None:
            for x in self.domains:
                neighbour = self.crossword.neighbors(x)
                for var in neighbour:
                    arc_list.append((x, var))
        else:
            arc_list = arcs

        # Runs through arcs until all have been removed or a domain is empty
        while len(arc_list) != 0:
            current_arc = arc_list.pop(0)

            # If a revision needs to be made for arc consistency, all of the nodes other
            # neighbours must be double checked.
            if self.revise(current_arc[0], current_arc[1]) == True:
                if len(self.domains[current_arc[0]]) == 0:
                    return False
                else:
                    for var in self.crossword.neighbors(current_arc[0]):
                        if var != current_arc[1]:
                            arc_list.insert(0, (current_arc[0], var))

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """

        if len(assignment) == len(self.domains):
            return True
        else:
            return False

        for var in assignment:
            if assignment[var] == None:
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """

        used_words = []

        for var in assignment:
            # Ensures word is unique
            if assignment[var] in used_words:
                return False
            # Ensures path length
            elif var.length != len(assignment[var]):
                return False

            # Checks that the overlaps use the same character
            neighbours = self.crossword.neighbors(var)
            for neighbour in neighbours:
                if neighbour in assignment:
                    overlap = self.crossword.overlaps[var, neighbour]
                    if assignment[var][overlap[0]] != assignment[neighbour][overlap[1]]:
                        return False

            used_words.append(assignment[var])

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """

        # Populates a dictionary of words to act as a counter
        unordered_domain = {}
        for word in self.domains[var]:
            unordered_domain[word] = 0

        # If a neighbour of var isn't yet in the assignment overlap is found and then conflicts found between domains
        for neighbour in self.crossword.neighbors(var):
            if neighbour not in assignment:
                overlap = self.crossword.overlaps[var, neighbour]

                # Iterates through words in the var's domain and compares the neighbouring overlap
                for word in unordered_domain:
                    for neighbour_word in self.domains[neighbour]:
                        if word[overlap[0]] != neighbour_word[overlap[1]]:
                            unordered_domain[word] += 1

        ordered_domain = []

        # Goes through the unordered domain, removing the least constraining word and adding it to the ordered list
        while len(unordered_domain) != 0:
            least_const = min(unordered_domain, key=unordered_domain.get)
            unordered_domain.pop(least_const)
            ordered_domain.append(least_const)

        return ordered_domain

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """

        # Puts all unassigned varibales into dictionary
        unassigned_vars = {}
        for var in self.domains:
            if var not in assignment:
                unassigned_vars[var] = len(self.domains[var])

        var_options = {}

        # Retrieves the minimum valued variables from the list
        min_domains = -1
        for i in range(len(unassigned_vars)):
            min_var = min(unassigned_vars, key=unassigned_vars.get)
            min_var_value = unassigned_vars[min_var]
            unassigned_vars.pop(min_var)

            # Ensures the variable value is the min and saves it to dictionary with neighbour no.
            if min_domains == -1:
                min_domains = min_var_value
                var_options[min_var] = len(self.crossword.neighbors(min_var))
            elif min_domains == min_var_value:
                var_options[min_var] = len(self.crossword.neighbors(min_var))
            else:
                break

        # Returns variable with most neighbours
        return max(var_options, key=var_options.get)

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """

        # Returns the assignment if all variables are used
        if len(assignment) == len(self.domains):
            return assignment

        var = self.select_unassigned_variable(assignment)

        # Tries words in domain in order of least conflict
        for domain_word in self.order_domain_values(var, assignment):
            assignment[var] = domain_word

            # Checks consistency of assigned word
            if self.consistent(assignment) == False:
                assignment.pop(var)
                continue

            try_backtrack = self.backtrack(assignment)

            # If a correct assignment is found then it is returned
            if try_backtrack != None:
                return try_backtrack

            assignment.pop(var)

        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
