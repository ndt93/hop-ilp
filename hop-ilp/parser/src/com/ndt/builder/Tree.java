package com.ndt.builder;

public class Tree {
    public Node node;
    public Tree left = null;
    public Tree right = null;

    public static class Node {
        public String name = "";
        public Object value = null;

        public Node() {
        }

        /**
         * Copy constructor
         * @param sourceNode
         */
        public Node(Node sourceNode) {
            this(sourceNode.name, sourceNode.value);
        }

        public Node(String name) {
            this.name = name;
        }

        public Node(Object value) {
            this.value = value;
        }

        public Node(String name, Object value) {
            this.name = name;
            this.value = value;
        }
    }

    public Tree() {
        this.node = new Node();
    }

    /**
     * Copy constructor. This methods deep copy the source Tree
     * @param sourceTree
     */
    public Tree(Tree sourceTree) {
        this.node = new Node(sourceTree.node);
        if (sourceTree.left != null) {
            this.left = new Tree(sourceTree.left);
        }
        if (sourceTree.right != null) {
            this.right = new Tree(sourceTree.right);
        }
    }

    public Tree(Node node) {
        this.node = node;
    }

    public Tree(Tree left, Tree right) {
        this.left = left;
        this.right = right;
    }

    public Tree(Node node, Tree left, Tree right) {
        this.node = node;
        this.left = left;
        this.right = right;
    }
}
