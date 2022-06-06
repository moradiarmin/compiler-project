from typing import Literal

from data_class.addressing_mode import AddressingMode, Arg
from data_class.symbol_table import Attribute, FuncAttribute, ItmtAttribute
from enums.addressing import AddressType
from enums.command import Command
from modules.semantic import Semantic
from modules.memory import Memory
from modules.symbol_table import SymbolTable
from utils.constants import TOP

def RECORD_STACK():
    Semantic().stack_recorder.append(len(Semantic().stack))

def PRUNE_STACK():
    recorder = Semantic().stack_recorder.pop()
    while len(Semantic().stack) > recorder:
        POP()

def APPEND_BREAK_PB():
    row = SymbolTable().find_row('while', Semantic().current_scope)
    row.attribute.breaks_PB.append(Memory().prog_p)
    SAVE()
    POP()

def APPEND_CONT_PB():
    row = SymbolTable().find_row('while', Semantic().current_scope)
    row.attribute.continues_PB.append(Memory().prog_p)
    SAVE()
    POP()

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
    arg = POP()
    Semantic().stack.append(Arg(AddressType.INDIRECT, arg.val))

def MATH(command: Literal[Command.ADD, Command.MULT, Command.SUB]):
    arg = Arg(AddressType.DIRECT, Memory().get_new_tmp())
    Memory().set_new_command(
        AddressingMode(
            command,
            Semantic().stack[TOP-1],
            Semantic().stack[TOP],
            arg
        )
    )
    POP()
    POP()
    Semantic().stack.append(arg)

def CALL(lexeme: str):
    row = SymbolTable().find_row(lexeme, Semantic().current_scope)
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
            Arg(AddressType.NUM, Memory().prog_p + 2),
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

    arg = Arg(AddressType.DIRECT, Memory().get_new_tmp())
    Memory().set_new_command(
        AddressingMode(
            Command.ASSIGN,
            Semantic().stack[TOP],
            arg,
            None,
        )
    )
    POP()
    Semantic().stack.append(arg)

def ASSIGN():
    arg2 = Semantic().stack[TOP-1]
    if int(arg2.val) >= Memory().start_tmp_p:
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
        return Semantic().stack.pop()
    else:
        return Semantic().stack.pop(idx)

def GIVE_BACK():
    Memory().data_p -= Memory().unit

def SET_RET_VAL():
    row = SymbolTable().find_func_scope(Semantic().current_scope)
    arg2 = Arg(AddressType.DIRECT, row.attribute.ret_val_addr)
    Memory().set_new_command(
        AddressingMode(
            Command.ASSIGN,
            Semantic().stack[TOP],
            arg2,
            None
        )
    )
    POP()

    arg2 = Arg(AddressType.INDIRECT, row.attribute.jp_addr)
    Memory().set_new_command(
        AddressingMode(
            Command.JP,
            arg2,
            None,
            None
        )
    )

def SET_RET_VAL2():
    Semantic().stack.append(Arg(AddressType.NUM, 0))
    SET_RET_VAL()
    
def CHG_SCOPE(lexeme: int):
    row = SymbolTable().find_row(lexeme, Semantic().current_scope)
    assert isinstance(row.attribute, FuncAttribute)

    if Semantic().current_scope == 0:
        SAVE()

    row.attribute.start_addr_in_PB = Memory().prog_p
    Semantic().create_new_scope()
    SymbolTable().scope_boundary[Semantic().current_scope] = (len(SymbolTable().table) - 1, None)
    row.attribute.mem_addr = Memory().get_new_data_addr()
    row.attribute.ret_val_addr = Memory().get_new_data_addr()
    row.attribute.jp_addr = Memory().get_new_data_addr()

def END_FUNC():
    # always make sure having a return at the end
    Semantic().stack.append(Arg(AddressType.NUM, 0))
    SET_RET_VAL()
    
    row = SymbolTable().find_func_scope(Semantic().current_scope)
    arg2 = Arg(AddressType.INDIRECT, row.attribute.jp_addr)
    Memory().set_new_command(
        AddressingMode(
            Command.JP,
            arg2,
            None,
            None
        )
    )


    Semantic().switch_scope(Semantic().scope_tree[Semantic().current_scope].father.scope_no)
    if Semantic().current_scope == 0:
        Memory().set_new_command(
            AddressingMode(
                Command.JP,
                Arg(AddressType.NUM, Memory().prog_p),
                None,
                None
            ),
            idx=Semantic().stack[TOP].val,
        )
        POP()

def NARG(lexeme: str):
    row = SymbolTable().find_func_scope(Semantic().current_scope)
    PID(lexeme)
    POP()
    arg = SymbolTable().table[-1]

    row.attribute.args_addr.append(arg.attribute.mem_addr)

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
    POP(-2)
    POP(-2)

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

def ITMT_ATTR():
    row = SymbolTable().find_row('while', Semantic().current_scope)
    if not isinstance(row.attribute, ItmtAttribute):
        row.attribute = ItmtAttribute(row.attribute.scope_no, row.attribute.mem_addr, [], [],
                                     [0], [0], [])
    else:
        row.attribute.SS_break.append(len(row.attribute.breaks_PB))
        row.attribute.SS_cont.append(len(row.attribute.continues_PB))
    
    row.attribute.start_addr_in_PBs.append(Memory().prog_p)

def SAVE_WHILE():
    row = SymbolTable().find_row('while', Semantic().current_scope)
    Memory().set_new_command(
        AddressingMode(
            Command.JPF,
            Semantic().stack[TOP-1],
            Arg(AddressType.NUM, Memory().prog_p + 1),
            None
        ),
        idx=Semantic().stack[TOP].val
    )
    POP()
    POP()
    start_break = row.attribute.SS_break.pop()
    while row.attribute.breaks_PB and len(row.attribute.breaks_PB) > start_break:
        Memory().set_new_command(
            AddressingMode(
                Command.JP,
                Arg(AddressType.NUM, Memory().prog_p + 1),
                None,
                None
            ),
            idx = row.attribute.breaks_PB.pop()
        )
    
    Memory().set_new_command(
        AddressingMode(
            Command.JP,
            Semantic().stack[TOP],
            None,
            None
        )
    )

    start_cont = row.attribute.SS_cont.pop()
    while row.attribute.continues_PB and len(row.attribute.continues_PB) > start_cont:
        Memory().set_new_command(
            AddressingMode(
                Command.JP,
                Arg(AddressType.NUM, row.attribute.start_addr_in_PBs[-1]),
                None,
                None
            ),
            idx = row.attribute.continues_PB.pop()
        )
    POP()
    row.attribute.start_addr_in_PBs.pop()

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

def POW_INC():
    Memory().pow_idx += 1

def CHK_POW():
    zero = Arg(AddressType.NUM, 0)
    
    while Memory().pow_idx > 0:
        R_itmt = Arg(AddressType.DIRECT, Memory().get_new_tmp())
        R_cond = Arg(AddressType.DIRECT, Memory().get_new_tmp())
        R_res  = Arg(AddressType.DIRECT, Memory().get_new_tmp())
        Memory().set_new_command(
            AddressingMode(
                Command.ASSIGN,
                Semantic().stack[TOP],
                R_itmt,
                None
            )
        ),
        Memory().set_new_command(
            AddressingMode(
                Command.ASSIGN,
                Arg(AddressType.NUM, 1),
                R_res,
                None
            )
        ),
        Memory().set_new_command(
            AddressingMode(
                Command.LT,
                zero,
                R_itmt,
                R_cond,
            )
        )
        Memory().set_new_command(
            AddressingMode(
                Command.JPF,
                R_cond,
                Arg(AddressType.NUM, Memory().prog_p + 4),
                None
            )
        )
        Memory().set_new_command(
            AddressingMode(
                Command.SUB,
                R_itmt,
                Arg(AddressType.NUM, 1),
                R_itmt
            )
        )
        Memory().set_new_command(
            AddressingMode(
                Command.MULT,
                Semantic().stack[TOP-1],
                R_res,
                R_res
            )
        )
        Memory().set_new_command(
            AddressingMode(
                Command.JP,
                Arg(AddressType.NUM,Memory().prog_p - 4),
                None,
                None
            )
        )
        POP()
        POP()
        Semantic().stack.append(R_res)
        Memory().pow_idx -= 1


def PID(lexeme: str):
    row = SymbolTable().find_row(lexeme, Semantic().current_scope)
    addr = row.attribute.mem_addr
    
    if addr is None:
        addr = Memory().get_new_data_addr()
        row.attribute.mem_addr = addr        
        row.attribute.scope_no = Semantic().current_scope
    
    Semantic().stack.append(Arg(AddressType.DIRECT, addr))

def PID2(lexeme: str):
    row = SymbolTable().find_row(lexeme, Semantic().current_scope, force_mem_addr=True)
    Semantic().stack.append(Arg(AddressType.DIRECT, row.attribute.mem_addr))
    # SHIT CODE :/
    Memory().pow_idx -= 1

def PNUM(NUM: str):
    Semantic().stack.append(Arg(AddressType.NUM, NUM))
    # SHIT CODE :/
    Memory().pow_idx -= 1

def PRINT():
    Memory().set_new_command(
        AddressingMode(
            Command.PRINT,
            Semantic().stack[TOP],
            None,
            None
        )
    )
    POP()