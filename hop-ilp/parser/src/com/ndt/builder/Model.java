package com.ndt.builder;

import java.util.*;

public class Model {
    public int horizon;
    public int maxConcurrency = 0;
    public Map<String, Integer> variables = new HashMap<>();
    public List<String> actions;
    public Map<String, Tree> transitionTrees;
    public Tree rewardTree;
}
