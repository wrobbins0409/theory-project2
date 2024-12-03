from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
import copy


@dataclass
class Transition:
    current_state: str
    read_symbols: List[str]  # k symbols to match
    next_state: str
    write_symbols: List[str]  # k symbols to write
    moves: List[str]         # k moves (L,R,S)


class Tape:
    def __init__(self):
        self.tape = ['_']  # Use underscore for blank
        self.head = 0

    def read(self) -> str:
        return self.tape[self.head]

    def write(self, symbol: str):
        if symbol != '*':  # Don't change if wildcard
            self.tape[self.head] = symbol

    def move(self, direction: str):
        if direction == 'L':
            if self.head == 0:
                self.tape.insert(0, '_')
            else:
                self.head -= 1
        elif direction == 'R':
            self.head += 1
            if self.head == len(self.tape):
                self.tape.append('_')

    def reset(self):
        self.tape = ['_']
        self.head = 0

    def __str__(self) -> str:
        result = ''.join(self.tape[:self.head])
        # Make head position more visible
        result += '[' + self.tape[self.head] + ']'
        result += ''.join(self.tape[self.head + 1:])
        return result


class KTapeTM:
    def __init__(self, name: str, file_name: str, num_tapes: int = 1):
        self.name = name
        self.file_name = file_name
        self.num_tapes = num_tapes
        self.tapes = [Tape() for _ in range(num_tapes)]
        self.transitions: Dict[str, List[Transition]] = {}
        self.current_state = 'q0'
        self.step = 0
        self.accepting_states = {'qaccept'}  # New: set of accepting states
        self.rejecting_states = {'qreject'}  # New: set of rejecting states

    def reset(self):
        """Reset the TM to initial state"""
        self.current_state = 'q0'
        self.step = 0
        for tape in self.tapes:
            tape.reset()

    @classmethod
    def from_file(cls, filename: str) -> 'KTapeTM':
        """Parse a TM definition from a file"""
        with open(filename, 'r') as f:
            lines = [line.strip() for line in f.readlines()
                     if line.strip() and not line.startswith('#')]

        # Parse first line: [name, k]
        first_line = eval(lines[0])  # Safely evaluate list literal
        if isinstance(first_line, list):
            name = first_line[0]
            num_tapes = first_line[1] if len(first_line) > 1 else 1
        else:
            name = first_line
            num_tapes = 1

        tm = cls(name, filename.replace("test/", ""), num_tapes)

        # Parse transitions
        for line in lines[1:]:
            # Evaluate the list literal safely
            try:
                trans_list = eval(line)
                if not isinstance(trans_list, list):
                    continue

                # Each transition should have 2 + 3k elements
                expected_len = 2 + (3 * num_tapes)
                if len(trans_list) != expected_len:
                    raise ValueError(
                        f"Transition {trans_list} has wrong number of elements. Expected {expected_len}")

                # Parse transition components
                current_state = trans_list[0]
                read_symbols = trans_list[1:num_tapes+1]
                next_state = trans_list[num_tapes+1]
                write_symbols = trans_list[num_tapes+2:2*num_tapes+2]
                moves = trans_list[2*num_tapes+2:]

                # Validate moves
                if not all(move in ['L', 'R', 'S'] for move in moves):
                    raise ValueError(
                        f"Invalid move direction in transition {trans_list}")

                transition = Transition(
                    current_state=current_state,
                    read_symbols=read_symbols,
                    next_state=next_state,
                    write_symbols=write_symbols,
                    moves=moves
                )
                tm.add_transition(transition)

            except Exception as e:
                print(f"Error parsing transition: {line}")
                print(f"Error details: {str(e)}")
                continue

        return tm

    def add_transition(self, transition: Transition):
        if transition.current_state not in self.transitions:
            self.transitions[transition.current_state] = []
        self.transitions[transition.current_state].append(transition)

    def matches(self, symbols: List[str], patterns: List[str]) -> bool:
        return all(p == '*' or s == p for s, p in zip(symbols, patterns))

    def find_transition(self) -> Optional[Transition]:
        if self.current_state not in self.transitions:
            return None

        current_symbols = [tape.read() for tape in self.tapes]

        for transition in self.transitions[self.current_state]:
            if self.matches(current_symbols, transition.read_symbols):
                return transition
        return None

    def print_state(self):
        print(f"Step {self.step}:")
        for i, tape in enumerate(self.tapes):
            print(f"Tape {i + 1}: {tape}")
        print(f"Current state: {self.current_state}")
        print()

    def run(self, input_string: str, save_output: bool = False):
        """
        Run the Turing Machine on an input string.
        If save_output is True, append the output to a file.
        """
        # Reset the TM before each run
        self.reset()

        # Set up input
        self.tapes[0].tape = list(input_string) + ['_']
        output_lines = []  # Store output lines if saving

        # Add a separator line if saving output
        if save_output:
            # Clear section break between runs
            output_lines.append("\n" + "=" * 50 + "\n")

        header = f"Running {self.name} on input: {input_string}\n"
        header += "----------------------------------------\n"
        if save_output:
            output_lines.append(header)
        else:
            print(header)

        while True:
            # Format current state info
            state_info = f"Step {self.step}:\n"
            for i, tape in enumerate(self.tapes):
                state_info += f"Tape {i + 1}: {tape}\n"
            state_info += f"Current state: {self.current_state}\n\n"

            if save_output:
                output_lines.append(state_info)
            else:
                print(state_info)

            # Check if we're in an accepting or rejecting state
            if self.current_state in self.accepting_states:
                result = f"ACCEPT: Halted in accepting state {self.current_state}\n"
                if save_output:
                    output_lines.append(result)
                    # Append to output file
                    with open("output/" + self.file_name, 'a') as f:
                        f.write(''.join(output_lines))
                else:
                    print(result)
                return True

            if self.current_state in self.rejecting_states:
                result = f"REJECT: Halted in rejecting state {self.current_state}\n"
                if save_output:
                    output_lines.append(result)
                    with open("output/" + self.file_name, 'a') as f:
                        f.write(''.join(output_lines))
                else:
                    print(result)
                return False

            transition = self.find_transition()
            if not transition:
                result = f"REJECT: No valid transition from state {self.current_state}\n"
                if save_output:
                    output_lines.append(result)
                    with open("output/" + self.file_name, 'a') as f:
                        f.write(''.join(output_lines))
                else:
                    print(result)
                return False

            for i, (symbol, move) in enumerate(zip(transition.write_symbols, transition.moves)):
                self.tapes[i].write(symbol)
                self.tapes[i].move(move)

            self.current_state = transition.next_state
            self.step += 1
