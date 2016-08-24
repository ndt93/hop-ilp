package com.ndt.builder;

import com.ndt.parser.spuddParser;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class TransitionTreeBuilder {
    public static Map<String, Tree> createTransitionTrees(Iterable<String> variables, List<String> actions,
                                                          List<spuddParser.ActionBlockContext> actionsBlocks) {
        List<List<String>> actionsGroups = Utils.getAllActionsGroups(actionsBlocks);
        Tree baseTree = Utils.createBaseTree(actions, actionsGroups);

        Map<String, Tree> result = new HashMap<>();
        for (String v : variables) {
            result.put(v, new Tree(baseTree));
        }

        for (spuddParser.ActionBlockContext actionsBlock : actionsBlocks) {
            extendTreesFromActionBlock(result, actionsBlock);
        }

        return result;
    }

    /**
     * Extends all transitions trees with trees found in an actionBlock AST
     * @param trees
     * @param actionsBlock
     */
    private static void extendTreesFromActionBlock(Map<String, Tree> trees,
                                                  spuddParser.ActionBlockContext actionsBlock) {
        List<String> actions = Utils.getActionsGroup(actionsBlock);

        for (spuddParser.TtreeContext ttree : actionsBlock.ttree()) {
            extendBaseTree(trees.get(ttree.ID().getText()), ttree.dtree(), actions);
        }
    }

    /**
     * Extends a base tree of a state by inserting a transition tree to
     * an appropriate path following the list of positive action literals.
     * The base tree will be modified in place
     * @param baseTree
     * @param dtree
     * @param actions
     */
    private static void extendBaseTree(Tree baseTree, spuddParser.DtreeContext dtree, List<String> actions) {
        Tree decisionTree = Utils.createDtree(dtree, null);
        Tree parent = baseTree;

        while (parent.left != null && parent.right != null) {
            if (actions.contains(parent.node.name)) {
                parent = parent.left;
            } else {
                parent = parent.right;
            }
        }

        if (actions.contains(parent.node.name)) {
            parent.left = decisionTree;
        } else {
            parent.right = decisionTree;
        }
    }

}
