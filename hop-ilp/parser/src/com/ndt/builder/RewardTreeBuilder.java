package com.ndt.builder;

import com.ndt.parser.spuddParser;

import java.util.ArrayList;
import java.util.List;

public class RewardTreeBuilder {

    /**
     * Returns a reward Tree from actionBlock +AST.The returned reward tree
     * is an extended Tree whose leaves ' values contain a list of multiple subtrees
     * @param actions list of all action names
     * @param actionsBlocks list of actionBlock AST
     * @return the reward Tree
     */
    public static Tree createRewardTree(List<String> actions,
                                        List<spuddParser.ActionBlockContext> actionsBlocks) {
        List<List<String>> actionsGroups = Utils.getAllActionsGroups(actionsBlocks);
        Tree baseTree = Utils.createBaseTree(actions, actionsGroups);

        for (spuddParser.ActionBlockContext actionsBlock : actionsBlocks) {
            spuddParser.CostBlockContext costBlock = actionsBlock.costBlock();
            List<Tree> rewardTrees = new ArrayList<>();

            for (spuddParser.DtreeContext dtree : costBlock.dtree()) {
                rewardTrees.add(Utils.createDtree(dtree, (l) -> -l));
            }

            Tree parent = baseTree;
            actions = Utils.getActionsGroup(actionsBlock);
            while (parent.left != null && parent.right != null) {
                if (actions.contains(parent.node.name)) {
                    parent = parent.left;
                } else {
                    parent = parent.right;
                }
            }

            Tree extendedTree = new Tree(new Tree.Node("branches", rewardTrees));
            if (actions.contains(parent.node.name)) {
                parent.left = extendedTree;
            } else {
                parent.right = extendedTree;
            }
        }

        return baseTree;
    }
}
