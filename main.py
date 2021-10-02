'''
WSL Python implementation of simple CPU
'''

import time
import signal
import os

def signal_handler(sig, frame):
	print("Exitting program")
	exit(0)

class Register:
	def __init__(self, val) -> None:
		if not isinstance(val, int):
			raise TypeError("val must be an int")
		self.val: int = val
		return

	def set(self, val):
		if not isinstance(val, int):
			raise TypeError("val must be an int")
		self.val = val

	def get(self) -> float:
		return self.val

	def __str__(self) -> str:
		'''
		Returns str of register value in hex
		'''
		return f"{hex(self.val)}"

class CPU:
	'''
	CPU class, contains 4 Registers in array
	'''
	def __init__(self) -> None:
		# Initialize all registers to 0
		self.R = [Register(0)] * 3
		self.clk_cycle: int = int(0)
		self.program = [str]
		self.pc: int = 0
		self.cur_instr: str = ""
		
		print(str(self))
		
		return

	def __str__(self) -> str:
		'''
		Print contents of cpu
		'''

		display: str = ""

		if self.cur_instr:
			display = f"Instruction: {self.cur_instr}\n"
		else:
			display = "Instruction: INIT\n"

		for i, r in enumerate(self.R):
			display = "".join([f"{display}R[{i}]: {r}\n"])

		return display
	
	def load_program(self, program: str) -> None:
		'''
		Loads txt file into RAM. Expects no newlines. Process per 4 characters
		'''
		buffer = []
		with open(program) as fp:
			while chunk := fp.read(4):
				if chunk:
					buffer.append(chunk)

		self.program = buffer

		return

	def fetch(self) -> None:
		'''
		Returns current instruction and increments program counter
		'''
		
		if self.pc >= len(self.program):
			self.pc = 0
		
		self.cur_instr = self.program[self.pc] 
		self.pc += 1		

		return

	def execute(self):
		'''
		Takes a string of the instruction and
		find the function pointer. Returns function
		ptr and arguments in a tuple.
		'''
	
		instr = int(self.cur_instr[0])
		k     = int(self.cur_instr[1])
		x     = int(self.cur_instr[2])
		y     = int(self.cur_instr[3])

		if instr == 0:
			# 0000: EXIT 
			# Stop execution

			print(str(self))
			os.kill(os.getpid(), signal.SIGINT)

		elif instr == 1:
			# 1knn: LD k, nn
			# Load value nn into register k

			if k > 2:
				raise OverflowError(f"Accessing invalid reg[{k}]")
			
			nn = int(f"{x}{y}")

			if nn.bit_length() > 8:
				raise OverflowError(f"{nn} bit length {nn.bit_length()} > 8")

			self.R[k] = nn 
		elif instr == 2:
			# 20xy: ADD x, y
			# Add the value of reg y to reg x and store value in reg x
			# if the result is greater than 8 bits set reg 2 to 1 else 0. 
			# Only the lowest 8-bits are stored in reg x 
		
			if x > 2:
				raise OverflowError(f"Accessing invalid reg[{x}]")
			elif y > 2:
				raise OverflowError(f"Accessing invalid reg[{y}]")

			sum: int = self.R[x] + self.R[y]
		
			if sum.bit_length() > 8:
				self.R[2] = 1
			else:
				self.R[2] = 0

			mask = 0b11111111
			self.R[x] = sum & mask 

		elif instr == 3:
			# 30xy: SUB x, y 
			# Subtract the value of register y from reg x and store the value
			# in the register x, if reg x < reg y set reg 2 to 1 else 0
			
			if x > 2:
				raise OverflowError(f"Accessing invalid reg[{x}]")
			elif y > 2:
				raise OverflowError(f"Accessing invalid reg[{y}]")

			diff: int = self.R[x] - self.R[y]
		
			if diff < 0:
				# Overflow
				self.R[x] = 256 + diff
				self.R[2] = 1
			else:
				self.R[x] = diff
				self.R[2] = 0
			
		elif instr == 4:
			# 40xy: OR x, y
			# bitwise or on value of reg x and reg y, store val in reg x
			
			if x > 2:
				raise OverflowError(f"Accessing invalid reg[{x}]")
			elif y > 2:
				raise OverflowError(f"Accessing invalid reg[{y}]")	

			self.R[x] = self.R[x] | self.R[y]

		elif instr == 5:
			# 50xy: AND x, y
			# Bitwise AND on val of reg x and reg y, store val in reg x
			if x > 2:
				raise OverflowError(f"Accessing invalid reg[{x}]")
			elif y > 2:
				raise OverflowError(f"Accessing invalid reg[{y}]")	

			self.R[x] = self.R[x] & self.R[y]
		elif instr == 6:
			# 60xy: XOR x, y
			# bitwise XOR on val of reg x and reg y, store val in reg x
			if x > 2:
				raise OverflowError(f"Accessing invalid reg[{x}]")
			elif y > 2:
				raise OverflowError(f"Accessing invalid reg[{y}]")	

			self.R[x] = self.R[x] ^ self.R[y]
		elif instr == 7:
			# 7knn: SE k, nn
			# skip next instruction if value of reg k equals nn
			
			if k > 2:
				raise OverflowError(f"Accessing invalid reg[{k}]")	
			
			nn = int(f"{x}{y}")

			if self.R[k] == nn:
				self.pc += 1 

		elif instr == 8:
			# 8knn: SNE k, nn
			# skip next instruction if val of reg k is not equal to nn
			if k > 2:
				raise OverflowError(f"Accessing invalid reg[{k}]")	
			
			nn = int(f"{x}{y}")

			if self.R[k] != nn:
				self.pc += 1 

		elif instr == 9:
			# 90xy: SE x, y
			# skip next instruction if reg x equals reg y
			if x > 2:
				raise OverflowError(f"Accessing invalid reg[{x}]")
			elif y > 2:
				raise OverflowError(f"Accessing invalid reg[{y}]")
			
			if self.R[x] == self.R[y]:
				self.pc += 1

		elif instr == 0xA:
			# A0xy: SNE x, y
			# skip next instruction if val of reg x is not equal to val of reg y 
			if x > 2:
				raise OverflowError(f"Accessing invalid reg[{x}]")
			elif y > 2:
				raise OverflowError(f"Accessing invalid reg[{y}]")	
			
			if self.R[x] == self.R[y]:
				self.pc += 1
		else:
			raise NameError(f"No op-code {self.cur_instr}")	

		# Display Memory
		print(str(self))

		return
	
def init() -> CPU:
	'''
	Initialize CPU memory, WSL file system
	'''
	cpu = CPU()

	cpu.load_program("marsh.txt")

	return cpu

def loop(cpu: CPU):
	'''
	CPU clock cycle
	'''

	cpu.fetch()
	cpu.execute()

	time.sleep(1)

	return


if __name__ == "__main__":
	signal.signal(signal.SIGINT, signal_handler)
	print("Press ^C to exit program")
	cpu: CPU = init()
	while True:
		loop(cpu)