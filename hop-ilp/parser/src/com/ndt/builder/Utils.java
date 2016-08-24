package com.ndt.builder;

import com.ndt.parser.spuddParser;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Utils {
    public static List<String> getActionsGroup(spuddParser.ActionBlockContext actionBlkCtx) {
        String actionsStr = actionBlkCtx.ID().getText();
        if (actionsStr.equals("noop")) {
            return new ArrayList<String>();
        }
        return Arrays.asList(actionsStr.split("___"));
    }
}
