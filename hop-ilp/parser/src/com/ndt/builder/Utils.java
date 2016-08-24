package com.ndt.builder;

import com.ndt.parser.spuddParser;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public final class Utils {
    @FunctionalInterface
    public interface LeafTransform {
        Object transform(float originalValue);
    }

    /**
     * Creates a Tree by combining paths
     * @param variables
     * @param paths
     * @return
     */
    public static Tree createBaseTree(Iterable<String> variables, List<List<String>> paths) {
        Tree result = null;

        for (List<String> p : paths) {
            Tree prevTree = null;
            Boolean prevVal = null;
            Tree curTree = result;

            for (String v : variables) {
                if (curTree == null) {
                    curTree = new Tree(new Tree.Node(v));
                    if (prevTree == null) {
                        result = curTree;
                    } else {
                        if (prevVal) {
                            prevTree.left = curTree;
                        } else {
                            prevTree.right = curTree;
                        }
                    }
                    prevTree = curTree;
                    prevVal = p.contains(v);
                    curTree = null;
                } else {
                    prevTree = curTree;
                    prevVal = p.contains(v);
                    if (prevVal) {
                        curTree = curTree.left;
                    } else {
                        curTree = curTree.right;
                    }
                }
            }
        }

        return result;
    }


    /**
     * Creates a decision tree from a dtree AST
     * @param dtree
     * @param leafTransform
     * @return
     */
    public static Tree createDtree(spuddParser.DtreeContext dtree, LeafTransform leafTransform) {
        if (dtree.left == null && dtree.right == null) {
            float val = Float.parseFloat(dtree.node().number().getText());
            Object valObj = val;

            if (leafTransform != null) {
                valObj = leafTransform.transform(val);
            }

            return new Tree(new Tree.Node("leaf", valObj));
        }

        Tree left = createDtree(dtree.left.left, leafTransform);
        Tree right = createDtree(dtree.right.left, leafTransform);
        if (left == null && right == null) {
            return null;
        }

        String identifier = dtree.node().ID().getText();
        if (identifier.endsWith("'")) {
            if (dtree.left.node().getText().equals("true")) {
                float val = (float) left.node.value;
                if (val >= 1e-6) {
                    return left;
                }
                return null;
            } else {
                float val = (float) right.node.value;
                if (val >= 1e-6) {
                    return right;
                }
                return null;
            }
        }

        Tree root = new Tree(new Tree.Node(identifier));
        if (dtree.left.node().getText().equals("true")) {
            root.left = left;
            root.right = right;
        } else {
            root.right = left;
            root.left = right;
        }

        return root;
    }


    public static List<List<String>> getAllActionsGroups(List<spuddParser.ActionBlockContext> actionsBlocks) {
        List<List<String>> result = new ArrayList<List<String>>();
        for (spuddParser.ActionBlockContext actionBlock : actionsBlocks) {
            result.add(getActionsGroup(actionBlock));
        }
        return result;
    }

    public static List<String> getActionsGroup(spuddParser.ActionBlockContext actionBlkCtx) {
        String actionsStr = actionBlkCtx.ID().getText();
        if (actionsStr.equals("noop")) {
            return new ArrayList<String>();
        }
        return Arrays.asList(actionsStr.split("___"));
    }
}
