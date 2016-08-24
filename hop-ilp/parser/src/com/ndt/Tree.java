package com.ndt;

public class Tree {
    public Node node;
    public Tree left = null;
    public Tree right = null;

    public static class Node {
        public String name = "";
        public Object value = null;

        public Node() {
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
