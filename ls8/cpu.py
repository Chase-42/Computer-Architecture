"""CPU functionality."""

import sys


EQL_fl = 0b001
GRTR_fl = 0b010
LESS_fl = 0b100

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.reg = [0]*8  # R0-R7 - variables in hardware w/ fixed names and number of registers.
        self.ram = [0]*256  # Memory 
        self.pc = 0  # Program Counter - address of the current excecuted instruction
        self.address = 0
        self.flag = 0
        self.runs = False
        self.sp = 7  # Stack Pointer
        self.reg[self.sp] = 0xF4
        self.bht = {
            0b00000001: self.op_HLT,
            0b10000010: self.op_LDI,
            0b01000111: self.op_PRN,
            0b10100000: self.op_ADD,
            0b10100010: self.op_MUL,
            0b01000101: self.op_PUSH,
            0b01000110: self.op_POP,
            0b01010000: self.op_CALL,
            0b00010001: self.op_RET,
            0b10101000: self.op_AND,
            0b01101001: self.op_NOT,
            0b10101010: self.op_OR,
            0b10101011: self.op_XOR,
            0b10100111: self.op_CMP,
            0b01010100: self.op_JMP,
            0b01010110: self.op_JNE,
            0b01010101: self.op_JEQ
           
        }

    def load(self):
        """Load a program into memory."""

        address = 0

        if len(sys.argv) < 2:
            print('Error, lacking arguments')
            sys.exit()
        try:
            with open(sys.argv[1]) as f:
                for line in f:
                    t = line.split('#')[0]
                    n = t.strip()

                    if n == '':
                        continue
                    command = int(n, 2)

                    self.ram[address] = command

                    address += 1

        except FileNotFoundError:
            print(f"Not a valid number - {t[0]}")
            sys.exit()

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        a = self.reg[reg_a]
        b = self.reg[reg_b]
        if op == "ADD":
            a += b
        elif op == 'SUB':
            a -= b
        elif op == 'MUL':
            a *= b
        elif op == 'DIV':
            a /= b
        else:
            raise Exception("Unsupported ALU operation")

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        self.runs = True
        while self.runs:
            command = self.ram[self.pc]
            if command in self.bht:
                func = self.bht[command]
                func()
            else:
                print(command, ': is not a valid command')
                self.runs = False

    def op_HLT(self):
        self.runs = False

    def op_LDI(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.reg[op_a] = op_b
        self.pc += 3

    def op_PRN(self):
        op_a = self.ram_read(self.pc + 1)
        print(self.reg[op_a])
        self.pc += 2

    def op_ADD(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.alu('ADD', op_a, op_b)
        self.pc += 3

    def op_MUL(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.reg[op_a] *= self.reg[op_b]
        self.pc += 3

    def op_AND(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.reg[self.ram_read(self.pc + 1)] = (op_a & op_b)
        self.pc += 3

    def op_OR(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.reg[self.ram_read(self.pc + 1)] = (op_a | op_b)
        self.pc += 3

    def op_XOR(self):
        op_a = self.ram_read(self.pc + 1)
        op_b = self.ram_read(self.pc + 2)
        self.reg[self.ram_read(self.pc + 1)] = (op_a ^ op_b)
        self.pc += 3

    def op_NOT(self):
        op_a = self.ram_read(self.pc + 1)
        self.reg[self.ram_read(self.pc + 1)] = ~op_a
        self.pc += 2

    def op_PUSH(self):
        # Push value to RAM @ PC into stack and save value 
        self.sp -= 1
        self.reg[self.sp] = self.reg[self.ram[self.pc + 1]]
        self.pc += 2

    def op_POP(self):
        # Pop from stack and add to register
        self.reg[self.ram[self.pc + 1]] = self.reg[self.sp]
        self.sp += 1
        self.pc += 2

    def op_CALL(self):
        # Return address
        return_address = self.pc + 2
        # Push onto the stack
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = return_address
        # Set COUNTER to the REGISTER'S value
        reg_num = self.ram[self.pc+1]
        dest_addr = self.reg[reg_num]
        self.pc = dest_addr

    def op_RET(self):
        # Get return address from top of stack
        return_address = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1
        # Set the pc
        self.pc = return_address

    def op_CMP(self):
        """compare the values in two registers"""
        op_a = self.reg[self.ram_read(self.pc + 1)]
        op_b = self.reg[self.ram_read(self.pc + 2)]

        if op_a > op_b:
            self.flag = GRTR_fl
        elif op_a < op_b:
            self.flag = LESS_fl
        else:
            self.flag = EQL_fl

        self.pc += 3

    def op_JMP(self):
        """Jump to the address stored in the given register"""
        j = self.ram_read(self.pc + 1)
        # Set the COUNTER to the given REGISTER'S ADDRESS
        self.pc = self.reg[j]

    def op_JNE(self):
        """if the EQUALS FLAG is FALSE,
        jump to the address stored in the given register"""
        if self.flag & EQL_fl == 0:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2

    def op_JEQ(self):
        """if the EQUALS FLAG is TRUE,
        jump to the address stored in the given register"""
        if self.flag & EQL_fl == 1:
            self.pc = self.reg[self.ram_read(self.pc + 1)]
        else:
            self.pc += 2
