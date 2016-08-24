// Generated from /Users/ndt/Development/fyp/hop-ilp/res/spudd.g4 by ANTLR 4.5.3
package com.ndt;
import org.antlr.v4.runtime.atn.*;
import org.antlr.v4.runtime.dfa.DFA;
import org.antlr.v4.runtime.*;
import org.antlr.v4.runtime.misc.*;
import org.antlr.v4.runtime.tree.*;
import java.util.List;
import java.util.Iterator;
import java.util.ArrayList;

@SuppressWarnings({"all", "warnings", "unchecked", "unused", "cast"})
public class spuddParser extends Parser {
	static { RuntimeMetaData.checkVersion("4.5.3", RuntimeMetaData.VERSION); }

	protected static final DFA[] _decisionToDFA;
	protected static final PredictionContextCache _sharedContextCache =
		new PredictionContextCache();
	public static final int
		T__0=1, T__1=2, T__2=3, T__3=4, T__4=5, T__5=6, T__6=7, T__7=8, T__8=9, 
		T__9=10, T__10=11, T__11=12, T__12=13, ID=14, INT=15, FLOAT=16, WS=17, 
		COMMENT=18;
	public static final int
		RULE_init = 0, RULE_initBlock = 1, RULE_variablesBlock = 2, RULE_variable = 3, 
		RULE_actionBlock = 4, RULE_costBlock = 5, RULE_config = 6, RULE_rewardBlock = 7, 
		RULE_discount = 8, RULE_horizon = 9, RULE_ttree = 10, RULE_dtree = 11, 
		RULE_node = 12, RULE_number = 13;
	public static final String[] ruleNames = {
		"init", "initBlock", "variablesBlock", "variable", "actionBlock", "costBlock", 
		"config", "rewardBlock", "discount", "horizon", "ttree", "dtree", "node", 
		"number"
	};

	private static final String[] _LITERAL_NAMES = {
		null, "'init'", "'[*'", "']'", "'(variables'", "')'", "'('", "'action'", 
		"'endaction'", "'cost'", "'[+'", "'reward'", "'discount'", "'horizon'"
	};
	private static final String[] _SYMBOLIC_NAMES = {
		null, null, null, null, null, null, null, null, null, null, null, null, 
		null, null, "ID", "INT", "FLOAT", "WS", "COMMENT"
	};
	public static final Vocabulary VOCABULARY = new VocabularyImpl(_LITERAL_NAMES, _SYMBOLIC_NAMES);

	/**
	 * @deprecated Use {@link #VOCABULARY} instead.
	 */
	@Deprecated
	public static final String[] tokenNames;
	static {
		tokenNames = new String[_SYMBOLIC_NAMES.length];
		for (int i = 0; i < tokenNames.length; i++) {
			tokenNames[i] = VOCABULARY.getLiteralName(i);
			if (tokenNames[i] == null) {
				tokenNames[i] = VOCABULARY.getSymbolicName(i);
			}

			if (tokenNames[i] == null) {
				tokenNames[i] = "<INVALID>";
			}
		}
	}

	@Override
	@Deprecated
	public String[] getTokenNames() {
		return tokenNames;
	}

	@Override

	public Vocabulary getVocabulary() {
		return VOCABULARY;
	}

	@Override
	public String getGrammarFileName() { return "spudd.g4"; }

	@Override
	public String[] getRuleNames() { return ruleNames; }

	@Override
	public String getSerializedATN() { return _serializedATN; }

	@Override
	public ATN getATN() { return _ATN; }

	public spuddParser(TokenStream input) {
		super(input);
		_interp = new ParserATNSimulator(this,_ATN,_decisionToDFA,_sharedContextCache);
	}
	public static class InitContext extends ParserRuleContext {
		public VariablesBlockContext variablesBlock() {
			return getRuleContext(VariablesBlockContext.class,0);
		}
		public InitBlockContext initBlock() {
			return getRuleContext(InitBlockContext.class,0);
		}
		public List<ActionBlockContext> actionBlock() {
			return getRuleContexts(ActionBlockContext.class);
		}
		public ActionBlockContext actionBlock(int i) {
			return getRuleContext(ActionBlockContext.class,i);
		}
		public List<ConfigContext> config() {
			return getRuleContexts(ConfigContext.class);
		}
		public ConfigContext config(int i) {
			return getRuleContext(ConfigContext.class,i);
		}
		public InitContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_init; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitInit(this);
			else return visitor.visitChildren(this);
		}
	}

	public final InitContext init() throws RecognitionException {
		InitContext _localctx = new InitContext(_ctx, getState());
		enterRule(_localctx, 0, RULE_init);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(28);
			variablesBlock();
			setState(30);
			_la = _input.LA(1);
			if (_la==T__0) {
				{
				setState(29);
				initBlock();
				}
			}

			setState(33); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(32);
				actionBlock();
				}
				}
				setState(35); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==T__6 );
			setState(38); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(37);
				config();
				}
				}
				setState(40); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << T__10) | (1L << T__11) | (1L << T__12))) != 0) );
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class InitBlockContext extends ParserRuleContext {
		public List<DtreeContext> dtree() {
			return getRuleContexts(DtreeContext.class);
		}
		public DtreeContext dtree(int i) {
			return getRuleContext(DtreeContext.class,i);
		}
		public InitBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_initBlock; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitInitBlock(this);
			else return visitor.visitChildren(this);
		}
	}

	public final InitBlockContext initBlock() throws RecognitionException {
		InitBlockContext _localctx = new InitBlockContext(_ctx, getState());
		enterRule(_localctx, 2, RULE_initBlock);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(42);
			match(T__0);
			setState(43);
			match(T__1);
			setState(45); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(44);
				dtree();
				}
				}
				setState(47); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==T__5 );
			setState(49);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class VariablesBlockContext extends ParserRuleContext {
		public List<VariableContext> variable() {
			return getRuleContexts(VariableContext.class);
		}
		public VariableContext variable(int i) {
			return getRuleContext(VariableContext.class,i);
		}
		public VariablesBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_variablesBlock; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitVariablesBlock(this);
			else return visitor.visitChildren(this);
		}
	}

	public final VariablesBlockContext variablesBlock() throws RecognitionException {
		VariablesBlockContext _localctx = new VariablesBlockContext(_ctx, getState());
		enterRule(_localctx, 4, RULE_variablesBlock);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(51);
			match(T__3);
			setState(53); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(52);
				variable();
				}
				}
				setState(55); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==T__5 );
			setState(57);
			match(T__4);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class VariableContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(spuddParser.ID, 0); }
		public List<NodeContext> node() {
			return getRuleContexts(NodeContext.class);
		}
		public NodeContext node(int i) {
			return getRuleContext(NodeContext.class,i);
		}
		public VariableContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_variable; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitVariable(this);
			else return visitor.visitChildren(this);
		}
	}

	public final VariableContext variable() throws RecognitionException {
		VariableContext _localctx = new VariableContext(_ctx, getState());
		enterRule(_localctx, 6, RULE_variable);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(59);
			match(T__5);
			setState(60);
			match(ID);
			setState(62); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(61);
				node();
				}
				}
				setState(64); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( (((_la) & ~0x3f) == 0 && ((1L << _la) & ((1L << ID) | (1L << INT) | (1L << FLOAT))) != 0) );
			setState(66);
			match(T__4);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ActionBlockContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(spuddParser.ID, 0); }
		public CostBlockContext costBlock() {
			return getRuleContext(CostBlockContext.class,0);
		}
		public List<TtreeContext> ttree() {
			return getRuleContexts(TtreeContext.class);
		}
		public TtreeContext ttree(int i) {
			return getRuleContext(TtreeContext.class,i);
		}
		public ActionBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_actionBlock; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitActionBlock(this);
			else return visitor.visitChildren(this);
		}
	}

	public final ActionBlockContext actionBlock() throws RecognitionException {
		ActionBlockContext _localctx = new ActionBlockContext(_ctx, getState());
		enterRule(_localctx, 8, RULE_actionBlock);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(68);
			match(T__6);
			setState(69);
			match(ID);
			setState(71); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(70);
				ttree();
				}
				}
				setState(73); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==ID );
			setState(75);
			costBlock();
			setState(76);
			match(T__7);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class CostBlockContext extends ParserRuleContext {
		public List<DtreeContext> dtree() {
			return getRuleContexts(DtreeContext.class);
		}
		public DtreeContext dtree(int i) {
			return getRuleContext(DtreeContext.class,i);
		}
		public CostBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_costBlock; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitCostBlock(this);
			else return visitor.visitChildren(this);
		}
	}

	public final CostBlockContext costBlock() throws RecognitionException {
		CostBlockContext _localctx = new CostBlockContext(_ctx, getState());
		enterRule(_localctx, 10, RULE_costBlock);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(78);
			match(T__8);
			setState(79);
			match(T__9);
			setState(81); 
			_errHandler.sync(this);
			_la = _input.LA(1);
			do {
				{
				{
				setState(80);
				dtree();
				}
				}
				setState(83); 
				_errHandler.sync(this);
				_la = _input.LA(1);
			} while ( _la==T__5 );
			setState(85);
			match(T__2);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class ConfigContext extends ParserRuleContext {
		public RewardBlockContext rewardBlock() {
			return getRuleContext(RewardBlockContext.class,0);
		}
		public DiscountContext discount() {
			return getRuleContext(DiscountContext.class,0);
		}
		public HorizonContext horizon() {
			return getRuleContext(HorizonContext.class,0);
		}
		public ConfigContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_config; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitConfig(this);
			else return visitor.visitChildren(this);
		}
	}

	public final ConfigContext config() throws RecognitionException {
		ConfigContext _localctx = new ConfigContext(_ctx, getState());
		enterRule(_localctx, 12, RULE_config);
		try {
			setState(90);
			switch (_input.LA(1)) {
			case T__10:
				enterOuterAlt(_localctx, 1);
				{
				setState(87);
				rewardBlock();
				}
				break;
			case T__11:
				enterOuterAlt(_localctx, 2);
				{
				setState(88);
				discount();
				}
				break;
			case T__12:
				enterOuterAlt(_localctx, 3);
				{
				setState(89);
				horizon();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class RewardBlockContext extends ParserRuleContext {
		public DtreeContext dtree() {
			return getRuleContext(DtreeContext.class,0);
		}
		public RewardBlockContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_rewardBlock; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitRewardBlock(this);
			else return visitor.visitChildren(this);
		}
	}

	public final RewardBlockContext rewardBlock() throws RecognitionException {
		RewardBlockContext _localctx = new RewardBlockContext(_ctx, getState());
		enterRule(_localctx, 14, RULE_rewardBlock);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(92);
			match(T__10);
			setState(93);
			dtree();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class DiscountContext extends ParserRuleContext {
		public NumberContext number() {
			return getRuleContext(NumberContext.class,0);
		}
		public DiscountContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_discount; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitDiscount(this);
			else return visitor.visitChildren(this);
		}
	}

	public final DiscountContext discount() throws RecognitionException {
		DiscountContext _localctx = new DiscountContext(_ctx, getState());
		enterRule(_localctx, 16, RULE_discount);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(95);
			match(T__11);
			setState(96);
			number();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class HorizonContext extends ParserRuleContext {
		public NumberContext val;
		public NumberContext number() {
			return getRuleContext(NumberContext.class,0);
		}
		public HorizonContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_horizon; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitHorizon(this);
			else return visitor.visitChildren(this);
		}
	}

	public final HorizonContext horizon() throws RecognitionException {
		HorizonContext _localctx = new HorizonContext(_ctx, getState());
		enterRule(_localctx, 18, RULE_horizon);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(98);
			match(T__12);
			setState(99);
			((HorizonContext)_localctx).val = number();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class TtreeContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(spuddParser.ID, 0); }
		public DtreeContext dtree() {
			return getRuleContext(DtreeContext.class,0);
		}
		public TtreeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_ttree; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitTtree(this);
			else return visitor.visitChildren(this);
		}
	}

	public final TtreeContext ttree() throws RecognitionException {
		TtreeContext _localctx = new TtreeContext(_ctx, getState());
		enterRule(_localctx, 20, RULE_ttree);
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(101);
			match(ID);
			setState(102);
			dtree();
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class DtreeContext extends ParserRuleContext {
		public DtreeContext left;
		public DtreeContext right;
		public NodeContext node() {
			return getRuleContext(NodeContext.class,0);
		}
		public List<DtreeContext> dtree() {
			return getRuleContexts(DtreeContext.class);
		}
		public DtreeContext dtree(int i) {
			return getRuleContext(DtreeContext.class,i);
		}
		public DtreeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_dtree; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitDtree(this);
			else return visitor.visitChildren(this);
		}
	}

	public final DtreeContext dtree() throws RecognitionException {
		DtreeContext _localctx = new DtreeContext(_ctx, getState());
		enterRule(_localctx, 22, RULE_dtree);
		try {
			setState(119);
			_errHandler.sync(this);
			switch ( getInterpreter().adaptivePredict(_input,9,_ctx) ) {
			case 1:
				enterOuterAlt(_localctx, 1);
				{
				setState(104);
				match(T__5);
				setState(105);
				node();
				setState(106);
				match(T__4);
				}
				break;
			case 2:
				enterOuterAlt(_localctx, 2);
				{
				setState(108);
				match(T__5);
				setState(109);
				node();
				setState(110);
				((DtreeContext)_localctx).left = dtree();
				setState(111);
				match(T__4);
				}
				break;
			case 3:
				enterOuterAlt(_localctx, 3);
				{
				setState(113);
				match(T__5);
				setState(114);
				node();
				setState(115);
				((DtreeContext)_localctx).left = dtree();
				setState(116);
				((DtreeContext)_localctx).right = dtree();
				setState(117);
				match(T__4);
				}
				break;
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class NodeContext extends ParserRuleContext {
		public TerminalNode ID() { return getToken(spuddParser.ID, 0); }
		public NumberContext number() {
			return getRuleContext(NumberContext.class,0);
		}
		public NodeContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_node; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitNode(this);
			else return visitor.visitChildren(this);
		}
	}

	public final NodeContext node() throws RecognitionException {
		NodeContext _localctx = new NodeContext(_ctx, getState());
		enterRule(_localctx, 24, RULE_node);
		try {
			setState(123);
			switch (_input.LA(1)) {
			case ID:
				enterOuterAlt(_localctx, 1);
				{
				setState(121);
				match(ID);
				}
				break;
			case INT:
			case FLOAT:
				enterOuterAlt(_localctx, 2);
				{
				setState(122);
				number();
				}
				break;
			default:
				throw new NoViableAltException(this);
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static class NumberContext extends ParserRuleContext {
		public TerminalNode INT() { return getToken(spuddParser.INT, 0); }
		public TerminalNode FLOAT() { return getToken(spuddParser.FLOAT, 0); }
		public NumberContext(ParserRuleContext parent, int invokingState) {
			super(parent, invokingState);
		}
		@Override public int getRuleIndex() { return RULE_number; }
		@Override
		public <T> T accept(ParseTreeVisitor<? extends T> visitor) {
			if ( visitor instanceof spuddVisitor ) return ((spuddVisitor<? extends T>)visitor).visitNumber(this);
			else return visitor.visitChildren(this);
		}
	}

	public final NumberContext number() throws RecognitionException {
		NumberContext _localctx = new NumberContext(_ctx, getState());
		enterRule(_localctx, 26, RULE_number);
		int _la;
		try {
			enterOuterAlt(_localctx, 1);
			{
			setState(125);
			_la = _input.LA(1);
			if ( !(_la==INT || _la==FLOAT) ) {
			_errHandler.recoverInline(this);
			} else {
				consume();
			}
			}
		}
		catch (RecognitionException re) {
			_localctx.exception = re;
			_errHandler.reportError(this, re);
			_errHandler.recover(this, re);
		}
		finally {
			exitRule();
		}
		return _localctx;
	}

	public static final String _serializedATN =
		"\3\u0430\ud6d1\u8206\uad2d\u4417\uaef1\u8d80\uaadd\3\24\u0082\4\2\t\2"+
		"\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13"+
		"\t\13\4\f\t\f\4\r\t\r\4\16\t\16\4\17\t\17\3\2\3\2\5\2!\n\2\3\2\6\2$\n"+
		"\2\r\2\16\2%\3\2\6\2)\n\2\r\2\16\2*\3\3\3\3\3\3\6\3\60\n\3\r\3\16\3\61"+
		"\3\3\3\3\3\4\3\4\6\48\n\4\r\4\16\49\3\4\3\4\3\5\3\5\3\5\6\5A\n\5\r\5\16"+
		"\5B\3\5\3\5\3\6\3\6\3\6\6\6J\n\6\r\6\16\6K\3\6\3\6\3\6\3\7\3\7\3\7\6\7"+
		"T\n\7\r\7\16\7U\3\7\3\7\3\b\3\b\3\b\5\b]\n\b\3\t\3\t\3\t\3\n\3\n\3\n\3"+
		"\13\3\13\3\13\3\f\3\f\3\f\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r\3\r"+
		"\3\r\3\r\3\r\3\r\5\rz\n\r\3\16\3\16\5\16~\n\16\3\17\3\17\3\17\2\2\20\2"+
		"\4\6\b\n\f\16\20\22\24\26\30\32\34\2\3\3\2\21\22\u0080\2\36\3\2\2\2\4"+
		",\3\2\2\2\6\65\3\2\2\2\b=\3\2\2\2\nF\3\2\2\2\fP\3\2\2\2\16\\\3\2\2\2\20"+
		"^\3\2\2\2\22a\3\2\2\2\24d\3\2\2\2\26g\3\2\2\2\30y\3\2\2\2\32}\3\2\2\2"+
		"\34\177\3\2\2\2\36 \5\6\4\2\37!\5\4\3\2 \37\3\2\2\2 !\3\2\2\2!#\3\2\2"+
		"\2\"$\5\n\6\2#\"\3\2\2\2$%\3\2\2\2%#\3\2\2\2%&\3\2\2\2&(\3\2\2\2\')\5"+
		"\16\b\2(\'\3\2\2\2)*\3\2\2\2*(\3\2\2\2*+\3\2\2\2+\3\3\2\2\2,-\7\3\2\2"+
		"-/\7\4\2\2.\60\5\30\r\2/.\3\2\2\2\60\61\3\2\2\2\61/\3\2\2\2\61\62\3\2"+
		"\2\2\62\63\3\2\2\2\63\64\7\5\2\2\64\5\3\2\2\2\65\67\7\6\2\2\668\5\b\5"+
		"\2\67\66\3\2\2\289\3\2\2\29\67\3\2\2\29:\3\2\2\2:;\3\2\2\2;<\7\7\2\2<"+
		"\7\3\2\2\2=>\7\b\2\2>@\7\20\2\2?A\5\32\16\2@?\3\2\2\2AB\3\2\2\2B@\3\2"+
		"\2\2BC\3\2\2\2CD\3\2\2\2DE\7\7\2\2E\t\3\2\2\2FG\7\t\2\2GI\7\20\2\2HJ\5"+
		"\26\f\2IH\3\2\2\2JK\3\2\2\2KI\3\2\2\2KL\3\2\2\2LM\3\2\2\2MN\5\f\7\2NO"+
		"\7\n\2\2O\13\3\2\2\2PQ\7\13\2\2QS\7\f\2\2RT\5\30\r\2SR\3\2\2\2TU\3\2\2"+
		"\2US\3\2\2\2UV\3\2\2\2VW\3\2\2\2WX\7\5\2\2X\r\3\2\2\2Y]\5\20\t\2Z]\5\22"+
		"\n\2[]\5\24\13\2\\Y\3\2\2\2\\Z\3\2\2\2\\[\3\2\2\2]\17\3\2\2\2^_\7\r\2"+
		"\2_`\5\30\r\2`\21\3\2\2\2ab\7\16\2\2bc\5\34\17\2c\23\3\2\2\2de\7\17\2"+
		"\2ef\5\34\17\2f\25\3\2\2\2gh\7\20\2\2hi\5\30\r\2i\27\3\2\2\2jk\7\b\2\2"+
		"kl\5\32\16\2lm\7\7\2\2mz\3\2\2\2no\7\b\2\2op\5\32\16\2pq\5\30\r\2qr\7"+
		"\7\2\2rz\3\2\2\2st\7\b\2\2tu\5\32\16\2uv\5\30\r\2vw\5\30\r\2wx\7\7\2\2"+
		"xz\3\2\2\2yj\3\2\2\2yn\3\2\2\2ys\3\2\2\2z\31\3\2\2\2{~\7\20\2\2|~\5\34"+
		"\17\2}{\3\2\2\2}|\3\2\2\2~\33\3\2\2\2\177\u0080\t\2\2\2\u0080\35\3\2\2"+
		"\2\r %*\619BKU\\y}";
	public static final ATN _ATN =
		new ATNDeserializer().deserialize(_serializedATN.toCharArray());
	static {
		_decisionToDFA = new DFA[_ATN.getNumberOfDecisions()];
		for (int i = 0; i < _ATN.getNumberOfDecisions(); i++) {
			_decisionToDFA[i] = new DFA(_ATN.getDecisionState(i), i);
		}
	}
}