# Generated from dnf.g4 by ANTLR 4.7.2
# encoding: utf-8
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\3\t")
        buf.write("8\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\3\2\3\2\3\2\3\2\3\2")
        buf.write("\3\2\3\2\3\2\5\2\23\n\2\3\3\3\3\3\3\7\3\30\n\3\f\3\16")
        buf.write("\3\33\13\3\3\3\3\3\3\3\3\3\5\3!\n\3\3\4\3\4\3\4\7\4&\n")
        buf.write("\4\f\4\16\4)\13\4\3\4\3\4\3\4\3\4\5\4/\n\4\3\5\3\5\3\5")
        buf.write("\3\5\3\5\5\5\66\n\5\3\5\2\2\6\2\4\6\b\2\2\29\2\22\3\2")
        buf.write("\2\2\4 \3\2\2\2\6.\3\2\2\2\b\65\3\2\2\2\n\13\7\7\2\2\13")
        buf.write("\f\5\4\3\2\f\r\7\b\2\2\r\16\7\2\2\3\16\23\3\2\2\2\17\20")
        buf.write("\5\4\3\2\20\21\7\2\2\3\21\23\3\2\2\2\22\n\3\2\2\2\22\17")
        buf.write("\3\2\2\2\23\3\3\2\2\2\24\31\5\6\4\2\25\26\7\4\2\2\26\30")
        buf.write("\5\6\4\2\27\25\3\2\2\2\30\33\3\2\2\2\31\27\3\2\2\2\31")
        buf.write("\32\3\2\2\2\32!\3\2\2\2\33\31\3\2\2\2\34\35\7\7\2\2\35")
        buf.write("\36\5\4\3\2\36\37\7\b\2\2\37!\3\2\2\2 \24\3\2\2\2 \34")
        buf.write("\3\2\2\2!\5\3\2\2\2\"\'\5\b\5\2#$\7\5\2\2$&\5\b\5\2%#")
        buf.write("\3\2\2\2&)\3\2\2\2\'%\3\2\2\2\'(\3\2\2\2(/\3\2\2\2)\'")
        buf.write("\3\2\2\2*+\7\7\2\2+,\5\6\4\2,-\7\b\2\2-/\3\2\2\2.\"\3")
        buf.write("\2\2\2.*\3\2\2\2/\7\3\2\2\2\60\66\7\3\2\2\61\62\7\7\2")
        buf.write("\2\62\63\7\6\2\2\63\64\7\3\2\2\64\66\7\b\2\2\65\60\3\2")
        buf.write("\2\2\65\61\3\2\2\2\66\t\3\2\2\2\b\22\31 \'.\65")
        return buf.getvalue()


class dnfParser ( Parser ):

    grammarFileName = "dnf.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "<INVALID>", "'\\/'", "'/\\'", "'!'", 
                     "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "VAR", "OR", "AND", "NOT", "OPB", "CLB", 
                      "WS" ]

    RULE_dnf = 0
    RULE_disjunction = 1
    RULE_conjunction = 2
    RULE_literal = 3

    ruleNames =  [ "dnf", "disjunction", "conjunction", "literal" ]

    EOF = Token.EOF
    VAR=1
    OR=2
    AND=3
    NOT=4
    OPB=5
    CLB=6
    WS=7

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.2")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class DnfContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def OPB(self):
            return self.getToken(dnfParser.OPB, 0)

        def disjunction(self):
            return self.getTypedRuleContext(dnfParser.DisjunctionContext,0)


        def CLB(self):
            return self.getToken(dnfParser.CLB, 0)

        def EOF(self):
            return self.getToken(dnfParser.EOF, 0)

        def getRuleIndex(self):
            return dnfParser.RULE_dnf

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDnf" ):
                listener.enterDnf(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDnf" ):
                listener.exitDnf(self)




    def dnf(self):

        localctx = dnfParser.DnfContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_dnf)
        try:
            self.state = 16
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,0,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 8
                self.match(dnfParser.OPB)
                self.state = 9
                self.disjunction()
                self.state = 10
                self.match(dnfParser.CLB)
                self.state = 11
                self.match(dnfParser.EOF)
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 13
                self.disjunction()
                self.state = 14
                self.match(dnfParser.EOF)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class DisjunctionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def conjunction(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(dnfParser.ConjunctionContext)
            else:
                return self.getTypedRuleContext(dnfParser.ConjunctionContext,i)


        def OR(self, i:int=None):
            if i is None:
                return self.getTokens(dnfParser.OR)
            else:
                return self.getToken(dnfParser.OR, i)

        def OPB(self):
            return self.getToken(dnfParser.OPB, 0)

        def disjunction(self):
            return self.getTypedRuleContext(dnfParser.DisjunctionContext,0)


        def CLB(self):
            return self.getToken(dnfParser.CLB, 0)

        def getRuleIndex(self):
            return dnfParser.RULE_disjunction

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterDisjunction" ):
                listener.enterDisjunction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitDisjunction" ):
                listener.exitDisjunction(self)




    def disjunction(self):

        localctx = dnfParser.DisjunctionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_disjunction)
        self._la = 0 # Token type
        try:
            self.state = 30
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,2,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 18
                self.conjunction()
                self.state = 23
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==dnfParser.OR:
                    self.state = 19
                    self.match(dnfParser.OR)
                    self.state = 20
                    self.conjunction()
                    self.state = 25
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 26
                self.match(dnfParser.OPB)
                self.state = 27
                self.disjunction()
                self.state = 28
                self.match(dnfParser.CLB)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class ConjunctionContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def literal(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(dnfParser.LiteralContext)
            else:
                return self.getTypedRuleContext(dnfParser.LiteralContext,i)


        def AND(self, i:int=None):
            if i is None:
                return self.getTokens(dnfParser.AND)
            else:
                return self.getToken(dnfParser.AND, i)

        def OPB(self):
            return self.getToken(dnfParser.OPB, 0)

        def conjunction(self):
            return self.getTypedRuleContext(dnfParser.ConjunctionContext,0)


        def CLB(self):
            return self.getToken(dnfParser.CLB, 0)

        def getRuleIndex(self):
            return dnfParser.RULE_conjunction

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterConjunction" ):
                listener.enterConjunction(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitConjunction" ):
                listener.exitConjunction(self)




    def conjunction(self):

        localctx = dnfParser.ConjunctionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_conjunction)
        self._la = 0 # Token type
        try:
            self.state = 44
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,4,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 32
                self.literal()
                self.state = 37
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while _la==dnfParser.AND:
                    self.state = 33
                    self.match(dnfParser.AND)
                    self.state = 34
                    self.literal()
                    self.state = 39
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)

                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 40
                self.match(dnfParser.OPB)
                self.state = 41
                self.conjunction()
                self.state = 42
                self.match(dnfParser.CLB)
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class LiteralContext(ParserRuleContext):

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def VAR(self):
            return self.getToken(dnfParser.VAR, 0)

        def OPB(self):
            return self.getToken(dnfParser.OPB, 0)

        def NOT(self):
            return self.getToken(dnfParser.NOT, 0)

        def CLB(self):
            return self.getToken(dnfParser.CLB, 0)

        def getRuleIndex(self):
            return dnfParser.RULE_literal

        def enterRule(self, listener:ParseTreeListener):
            if hasattr( listener, "enterLiteral" ):
                listener.enterLiteral(self)

        def exitRule(self, listener:ParseTreeListener):
            if hasattr( listener, "exitLiteral" ):
                listener.exitLiteral(self)




    def literal(self):

        localctx = dnfParser.LiteralContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_literal)
        try:
            self.state = 51
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [dnfParser.VAR]:
                self.enterOuterAlt(localctx, 1)
                self.state = 46
                self.match(dnfParser.VAR)
                pass
            elif token in [dnfParser.OPB]:
                self.enterOuterAlt(localctx, 2)
                self.state = 47
                self.match(dnfParser.OPB)
                self.state = 48
                self.match(dnfParser.NOT)
                self.state = 49
                self.match(dnfParser.VAR)
                self.state = 50
                self.match(dnfParser.CLB)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





