from ast import Add
from ctypes import Union
from typing import Literal
from data_class.addressing_mode import AddressingMode, Arg
from data_class.symbol_table import ArrAttribute, Attribute, FuncAttribute
from data_class.token import Token
from enums.addressing import AddressType
from enums.command import Command
from modules.semantic_stack import Semantic
from modules.memory import Memory
from modules.symbol_table import SymbolTable
from utils.constants import TOP

def PID(lexeme: str):
    row = SymbolTable().find_row(lexeme)
    addr = row.attribute.mem_addr
    
    if row.attribute.mem_addr is None:
        addr = Memory().get_new_data_addr()
        row.attribute = Attribute(SymbolTable().scope_no, addr)
    
    elif isinstance(row, ArrAttribute):
        addr = row.attribute.pointer
    
    Semantic().stack.append(Arg(AddressType.DIRECT, addr))

def ADDR():
    Semantic().stack.append(Arg(AddressType.NUM, 4))
    MATH(Command.MULT)
    MATH(Command.ADD)


def MATH(command: Union[Command.ADD, Command.MULT, Command.SUB]):
    arg = Arg(AddressType.DIRECT, Memory().get_new_tmp())
    Memory().set_new_command(
        AddressingMode(
            command,
            Semantic().stack[TOP],
            Semantic().stack[TOP-1],
            arg
        )
    )
    POP()
    POP()
    Memory().prog_p += 1
    Semantic().stack.append(arg)

def CALL(lexeme: str):
    row = SymbolTable().find_row(lexeme)
    assert isinstance(row.attribute, FuncAttribute)

    SymbolTable().set_scope_no(row.attribute.scope_no)
    Semantic().stack.append(Arg(AddressType.NUM, row.attribute.start_addr_in_PB))
    
    for addr in row.attribute.args_addr[::-1]:
        Semantic().stack.append(Arg(AddressType.DIRECT, addr))

def JP_FUNC():
    Memory().set_new_command(
        AddressingMode(
            Command.JP,
            Semantic().stack[TOP],
            None,
            None))
    POP()

    Memory().prog_p += 1
    Semantic().stack.append(Arg(AddressType.NUM, Memory().prog_p))
    Semantic().stack.append(Arg(AddressType.DIRECT, Memory().get_new_tmp()))
    
def ASSIGN():
    Memory().set_new_command(
        AddressingMode(
            Command.ASSIGN,
            Semantic().stack[TOP],
            Semantic().stack[TOP-1],
            None))
    POP()
    POP()
    Memory().prog_p += 1

def ASSIGN2():
    Memory().set_new_command(
        AddressingMode(
            Command.ASSIGN,
            Semantic().stack[TOP],
            Semantic().stack[TOP-1],
            None))
    POP()

    arg = Semantic().stack[TOP]
    POP()
    Semantic().stack.append(Arg(AddressType.DIRECT, 4 + arg.val))
    Memory().prog_p += 1

def REF(lexeme: str):
    pointer_addr = Memory().get_new_data_addr()
    row = SymbolTable().find_row(lexeme)
    row.attribute = ArrAttribute(
            SymbolTable().scope_no,
            row.attribute.mem_addr,
            pointer_addr)
    
    POP()
    Semantic().stack.append(Arg(AddressType.DIRECT, pointer_addr))

def POP():
    Semantic().stack.pop()