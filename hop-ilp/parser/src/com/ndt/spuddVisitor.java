// Generated from /Users/ndt/Development/fyp/hop-ilp/res/spudd.g4 by ANTLR 4.5.3
package com.ndt;
import org.antlr.v4.runtime.tree.ParseTreeVisitor;

/**
 * This interface defines a complete generic visitor for a parse tree produced
 * by {@link spuddParser}.
 *
 * @param <T> The return type of the visit operation. Use {@link Void} for
 * operations with no return type.
 */
public interface spuddVisitor<T> extends ParseTreeVisitor<T> {
	/**
	 * Visit a parse tree produced by {@link spuddParser#init}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitInit(spuddParser.InitContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#initBlock}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitInitBlock(spuddParser.InitBlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#variablesBlock}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitVariablesBlock(spuddParser.VariablesBlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#variable}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitVariable(spuddParser.VariableContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#actionBlock}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitActionBlock(spuddParser.ActionBlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#costBlock}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitCostBlock(spuddParser.CostBlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#config}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitConfig(spuddParser.ConfigContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#rewardBlock}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitRewardBlock(spuddParser.RewardBlockContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#discount}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDiscount(spuddParser.DiscountContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#horizon}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitHorizon(spuddParser.HorizonContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#ttree}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitTtree(spuddParser.TtreeContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#dtree}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitDtree(spuddParser.DtreeContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#node}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNode(spuddParser.NodeContext ctx);
	/**
	 * Visit a parse tree produced by {@link spuddParser#number}.
	 * @param ctx the parse tree
	 * @return the visitor result
	 */
	T visitNumber(spuddParser.NumberContext ctx);
}