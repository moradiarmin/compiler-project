from ctypes import Union
from typing import Literal
from data_class.addressing_mode import AddressingMode, Arg
from data_class.symbol_table import Attribute, FuncAttribute
from enums.addressing import AddressType
from enums.command import Command
from modules.semantic import Semantic
from modules.memory import Memory
from modules.symbol_table import SymbolTable
from utils.constants import TOP

def SET_PT():
    arg2 = Arg(AddressType.DIRECT, Memory().get_new_tmp())
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

def MATH(command: Literal[Command.ADD, Command.MULT, Command.SUB]):
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
    row = SymbolTable().find_row(lexeme, Semantic().scope_tree[Semantic().scope_no].father.scope_no)
    print(lexeme, row)
    assert isinstance(row.attribute, FuncAttribute)
    
    POP()
    Semantic().stack.append(Arg(AddressType.DIRECT, row.attribute.ret_val_addr))
    Semantic().stack.append(Arg(AddressType.NUM, row.attribute.start_addr_in_PB))
    Semantic().stack.append(Arg(AddressType.DIRECT, row.attribute.jp_addr))
    
    for addr in row.attribute.args_addr[::-1]:
        Semantic().stack.append(Arg(AddressType.DIRECT, addr))

def JP_FUNC():
    # fill jp_addr first
    Memory().set_new_command(
        AddressingMode(
            Command.ASSIGN,
            Arg(AddressType.NUM, Memory().prog_p + 2 * Memory().unit),
            Semantic().stack[TOP],
            None
        )
    )
    POP()

    Memory().set_new_command(
        AddressingMode(
            Command.JP,
            Semantic().stack[TOP],
            None,
            None))
    POP() 

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

    Semantic().stack.append(Arg(AddressType.DIRECT, Memory().get_new_data_addr()))

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
            None
        )
    )
    POP()
    Semantic().stack.append(Arg(AddressType.DIRECT, pointer_addr))

def POP(idx=None):
    if idx is None:
        Semantic().stack.pop()
    else:
        Semantic().stack.pop(idx)

def GIVE_BACK():
    Memory().data_p -= Memory().unit

def SET_RET_VAL():
    print(Semantic().scope_no)
    ret_val_addr, jp_addr = SymbolTable().find_func_ret_val_jp_addr(Semantic().scope_no)
    arg2 = Arg(AddressType.DIRECT, ret_val_addr)
    Memory().set_new_command(
        AddressingMode(
            Command.ASSIGN,
            Semantic().stack[TOP],
            arg2,
            None
        )
    )
    POP()

    arg2 = Arg(AddressType.INDIRECT, jp_addr)
    Memory().set_new_command(
        AddressingMode(
            Command.JP,
            arg2,
            None,
            None
        )
    )

def CHG_SCOPE(lexeme: int):
    row = SymbolTable().find_row(lexeme, Semantic().scope_no)
    assert isinstance(row.attribute, FuncAttribute)

    row.attribute.start_addr_in_PB = Memory().prog_p
    Semantic().create_new_scope()
    SymbolTable().scope_boundary[Semantic().scope_no] = (len(SymbolTable().table) - 1, None)
    row.attribute.scope_no = Semantic().scope_no
    row.attribute.mem_addr = Memory().get_new_data_addr()
    row.attribute.ret_val_addr = Memory().get_new_data_addr()
    row.attribute.jp_addr = Memory().get_new_data_addr()

def END_FUNC():
    _, jp_addr = SymbolTable().find_func_ret_val_jp_addr(Semantic().scope_no)
    arg2 = Arg(AddressType.INDIRECT, jp_addr)
    Memory().set_new_command(
        AddressingMode(
            Command.JP,
            arg2,
            None,
            None
        )
    )

def SAVE():
    Semantic().stack.append(Arg(AddressType.NUM, Memory().prog_p))
    Memory().prog_p += Memory().unit

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
            Arg(AddressType.NUM, Memory().prog_p),
            None,
            None
        ),
        idx=Semantic().stack[TOP].val
    )
    POP()

def WHILE_JPB():
    Semantic().stack.append(Arg(AddressType.NUM, Memory().prog_p))

def SAVE_WHILE():
    Memory().set_new_command(
        AddressingMode(
            Command.JPF,
            Semantic().stack[TOP-1],
            Arg(AddressType.NUM, Memory().prog_p + Memory().unit),
            None
        ),
        idx=Semantic().stack[TOP].val
    )
    POP()
    POP()

    Memory().set_new_command(
        AddressingMode(
            Command.JP,
            Semantic().stack[TOP],
            None,
            None
        )
    )
    POP()

def RELOP0():
    Semantic().stack.append(Arg(AddressType.NUM, 0))

def RELOP1():
    Semantic().stack.append(Arg(AddressType.NUM, 1))

def SET_RELOP():
    arg3 = Arg(AddressType.DIRECT, Memory().get_new_tmp())
    if Semantic().stack[TOP-1].val == 0:
        command = Command.EQ
    elif Semantic().stack[TOP-1].val == 1:
        command = Command.LT
    else:
        raise Exception()
    
    Memory().set_new_command(
        AddressingMode(
            command,
            Semantic().stack[TOP-2],
            Semantic().stack[TOP],
            arg3
        )
    )

    POP()
    POP()
    POP()
    Semantic().stack.append(arg3)

def POW_USED():
    if Memory().pow_idx is not None:
        Memory().pow_idx = len(Semantic().stack) - 1

def POW():
    if Memory().pow_idx is None:
        return
    # while len(Semantic().stack) - 1 > Memory().pow_idx:
    #     a = 

    Memory().pow_idx = None

def PID(lexeme: str):
    row = SymbolTable().find_row(lexeme, Semantic().scope_no)
    addr = row.attribute.mem_addr
    
    if addr is None:
        addr = Memory().get_new_data_addr()
        row.attribute.mem_addr = addr        
        row.attribute.scope_no = Semantic().scope_no
    
    Semantic().stack.append(Arg(AddressType.DIRECT, addr))

def PNUM(NUM: str):
    Semantic().stack.append(Arg(AddressType.NUM, NUM))


