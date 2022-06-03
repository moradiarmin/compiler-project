from ctypes import Union
from data_class.addressing_mode import AddressingMode, Arg
from data_class.symbol_table import ArrAttribute, Attribute, FuncAttribute
from enums.addressing import AddressType
from enums.command import Command
from modules.semantic import Semantic
from modules.memory import Memory
from modules.symbol_table import SymbolTable
from utils.constants import TOP

def PID(lexeme: str):
    row = SymbolTable().find_row(lexeme, Semantic().scope_no)
    addr = row.attribute.mem_addr
    
    if addr is None:
        addr = Memory().get_new_data_addr()
        row.attribute = Attribute(Semantic().scope_no, addr)
    
    # elif isinstance(row, ArrAttribute):
    #     addr = row.attribute.pointer
    
    Semantic().stack.append(Arg(AddressType.DIRECT, addr))

def SET_PT():
    arg2 = Arg(AddressType.DIRECT, Memory.get_new_tmp())
    Memory().set_new_command(
        AddressingMode(
            Command.ASSIGN,
            Semantic().stack[TOP],
            arg2,
            None,
        )
    )
    POP()
    Semantic().stack.append(arg2)

def MOVE_PT():
    Semantic().stack.append(Arg(AddressType.NUM, Memory().unit))
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
    Semantic().stack.append(arg)

def CALL(lexeme: str):
    row = SymbolTable().find_row(lexeme, Semantic().scope_no)
    assert isinstance(row.attribute, FuncAttribute)

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

    Semantic().stack.append(Arg(AddressType.NUM, Memory().prog_p))
    Semantic().stack.append(Arg(AddressType.DIRECT, Memory().get_new_tmp()))
    
def ASSIGN():
    arg2 = Semantic().stack[TOP-1]
    if arg2.val >= Memory().start_tmp_p:
        Semantic().stack[TOP-1] = Arg(AddressType.INDIRECT, arg2.val)
        
    Memory().set_new_command(
        AddressingMode(
            Command.ASSIGN,
            Semantic().stack[TOP],
            Semantic().stack[TOP-1],
            None))
    POP()
    POP()

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
    Semantic().stack.append(Arg(AddressType.DIRECT, Memory().unit + arg.val))

def CREATE_P():
    pointer_addr = Memory().get_new_data_addr()
    # reference in register
    arg2 = Semantic().stack[TOP]
    if arg2.val >= Memory().start_tmp_p:
        Semantic().stack[TOP] = Arg(AddressType.INDIRECT, arg2.val)
    
    Memory().set_new_command(
        AddressingMode(
            Command.ASSIGN,
            Arg(AddressType.NUM, pointer_addr),
            Semantic().stack[TOP],
        )
    )
    POP()
    Semantic().stack.append(Arg(AddressType.DIRECT, pointer_addr))

def POP(idx=None):
    if idx is None:
        Semantic().stack.pop()
    else:
        Semantic().stack.pop(idx)

def CHG_SCOPE(lexeme: int):
    row = SymbolTable().find_row(lexeme, Semantic().scope_no)
    assert isinstance(row.attribute, FuncAttribute)

    row.attribute.start_addr_in_PB = Memory().prog_p
    Semantic().create_new_scope()

def SAVE():
    Semantic().stack.append(Arg(AddressType.NUM, Memory().prog_p))
    Memory().prog_p += 1

def SAVE_JPF():
    Memory().set_new_command(
        AddressingMode(
            Command.JPF,
            Semantic().stack[TOP-2],
            Arg(AddressType.NUM, Memory().prog_p),
            None
        ),
        idx=Semantic().stack[TOP-1].val
    )
    POP(1)
    POP(1)

def SAVE_JPT():
    Memory().set_new_command(
        AddressingMode(
            Command.JP,
            
        )
    )
