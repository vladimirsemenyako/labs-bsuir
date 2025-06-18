# Generated from dnf.g4 by ANTLR 4.7.2
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .dnfParser import dnfParser
else:
    from dnfParser import dnfParser

# This class defines a complete listener for a parse tree produced by dnfParser.
class dnfListener(ParseTreeListener):

    # Enter a parse tree produced by dnfParser#dnf.
    def enterDnf(self, ctx:dnfParser.DnfContext):
        pass

    # Exit a parse tree produced by dnfParser#dnf.
    def exitDnf(self, ctx:dnfParser.DnfContext):
        pass


    # Enter a parse tree produced by dnfParser#disjunction.
    def enterDisjunction(self, ctx:dnfParser.DisjunctionContext):
        pass

    # Exit a parse tree produced by dnfParser#disjunction.
    def exitDisjunction(self, ctx:dnfParser.DisjunctionContext):
        pass


    # Enter a parse tree produced by dnfParser#conjunction.
    def enterConjunction(self, ctx:dnfParser.ConjunctionContext):
        pass

    # Exit a parse tree produced by dnfParser#conjunction.
    def exitConjunction(self, ctx:dnfParser.ConjunctionContext):
        pass


    # Enter a parse tree produced by dnfParser#literal.
    def enterLiteral(self, ctx:dnfParser.LiteralContext):
        pass

    # Exit a parse tree produced by dnfParser#literal.
    def exitLiteral(self, ctx:dnfParser.LiteralContext):
        pass


