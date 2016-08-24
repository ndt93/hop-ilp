package com.ndt.builder;

import java.util.*;

public class Model {
    public int horizon;
    public int maxConcurrency = 0;
    public Map<String, Integer> variables = new HashMap<String, Integer>();
    public Set<String> actions = new HashSet<String>();

    public void addActionsGroup(List<String> actionsGroup) {
        for (String a : actionsGroup) {
            actions.add(a);
            if (actionsGroup.size() > maxConcurrency) {
                maxConcurrency = actionsGroup.size();
            }
        }
    }
}
