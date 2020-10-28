"""CPU functionality."""
import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.pc = 0
        # Hold 256 bytes of memory 8 bit 2^8 = 256
        self.ram = [0] * 256  
        # Hold 8 general-purpose registers
        self.registers = [0] * 8  
        # Stack pointer
        self.sp = 7  
        self.fl = 0b00000000  
        

    def ram_read(self, mar): 
        return self.ram[mar]

    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def load(self):
        """Load a program into memory."""
        address = 0

        file_name = sys.argv[1]

        with open(file_name) as file:
            for line in file:
                command = line.split("#")[0].strip()
                if command == '':
                    continue
                instructions = int(command,2)
                self.ram[address] = instructions
                address += 1


    def alu(self, op, registers_a, registers_b):
        """ALU operations."""

        if op == "ADD":
            self.registers[registers_a] += self.registers[registers_b]
        
        elif op == "MUL":
            self.registers[registers_a] *= self.registers[registers_b]
     
        elif op == "CMP":
            if self.registers[registers_a] < self.registers[registers_b]:
                self.fl = 0
            
            if self.registers[registers_a] > self.registers[registers_b]:
                self.fl = 0
           
            if self.registers[registers_a] == self.registers[registers_b]:
                self.fl = 1
               
        
        else:
            raise Exception("Unsupported ALU operation")

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
            print(" %02X" % self.registers[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        LDI = 0b10000010  # Set the value of a register to an integer.
        PRN = 0b01000111 
        HLT = 0b00000001  # stop the CPU
        ADD = 0b10100000
        MUL = 0b10100010
        PUSH = 0b01000101  # Push the value in the given register on stack
        POP = 0b01000110   # Pop the value at the top of the stack inside the given register
        CALL = 0b01010000
        RET = 0b00010001
        running = True

        CMP = 0b10100111
        
    

        JMP = 0b01010100
        # Jump to address stored in given registers
        # Set PC to address stored in given registers

        JEQ = 0b01010101
        # If E(equal) flag is true jump to address stored in the given registers

        JNE = 0b01010110
        # If E flag is clear (0), jump to address stored in the given registers

        while running:
            instruction = self.ram_read(self.pc)
            oper_a = self.ram_read(self.pc + 1)
            oper_b = self.ram_read(self.pc + 2)

            if instruction == LDI:
                # Set value of a registers to an integer
                self.registers[oper_a] = oper_b
                self.pc += 3

            elif instruction == PRN:
                # Print numeric value stored in a given registers
                print(self.registers[oper_a])
                self.pc += 2

            elif instruction == ADD:
                self.alu("ADD", oper_a, oper_b)
                self.pc += 3

            elif instruction == MUL:
                # * the values in two registers and the result in registers A.
                self.alu("MUL", oper_a, oper_b)
                self.pc += 3

            elif instruction == PUSH:
                # Decrease the SP
                self.registers[self.sp] -= 1
                # Store value in memory at SP & push the value in the given register on the stack
                self.ram[self.registers[self.sp]] = self.registers[oper_a]
                self.pc += 2

            elif instruction == POP:
                # Store value in memeroy at SP & get value out of the registers
                self.registers[oper_a] = self.ram[self.registers[self.sp]]
                # Increase the SP
                self.registers[self.sp] += 1
                self.pc += 2

            elif instruction == CALL:
                # Push if it is on the stack
                self.registers[self.sp] -= 1
                self.ram[self.registers[self.sp]] = self.pc + 2
                # Set the PC to the subroutine address
                self.pc = self.registers[oper_a]

            elif instruction == RET:
                # Pop the return address off the stack
                top_stack = self.registers[self.sp]
                self.registers[self.sp] += 1
                # Store in PC
                self.pc = self.ram[top_stack]

            elif instruction == CMP:
                self.alu("CMP", oper_a, oper_b)
                self.pc +=3

            elif instruction == JEQ:
                if self.fl == 1:
                    self.pc = self.registers[self.ram_read(self.pc+1)]
                else:
                    self.pc +=2

            elif instruction == JNE:
                if self.fl == 0:
                    self.pc = self.registers[self.ram_read(self.pc + 1)]
                else:
                    self.pc +=2

            elif instruction == JMP:
                self.pc = self.registers[self.ram_read(self.pc + 1)]

            elif instruction == HLT:
                # Stop the CPU 
                running = False  # Get out of while loop

            else:
                print(
                    F" unknown instruction {instruction} at place {self.pc}")
                sys.exit()  # Stops the python program
            