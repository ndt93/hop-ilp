package com.ndt.builder;

import com.ndt.parser.spuddBaseVisitor;
import com.ndt.parser.spuddParser;

import java.util.*;
import java.util.stream.Collectors;

public class ModelBuilder extends spuddBaseVisitor<Model> {
    private Model model;

    @Override
    public Model visitInit(spuddParser.InitContext ctx) {
        model = new Model();

        for (spuddParser.ConfigContext config : ctx.config()) {
            visitConfig(config);
        }

        visitVariablesBlock(ctx.variablesBlock());
        visitInitBlock(ctx.initBlock());

        getAllActions(ctx.actionBlock());

        model.transitionTrees = TransitionTreeBuilder.createTransitionTrees(
                model.variables.keySet(), new ArrayList<>(model.actions), ctx.actionBlock());

        model.rewardTree = RewardTreeBuilder.createRewardTree(model.actions, ctx.actionBlock());

        return model;
    }

    private void getAllActions(List<spuddParser.ActionBlockContext> actionsBlocks) {
        List<List<String>> actionsGroups = Utils.getAllActionsGroups(actionsBlocks);
        List<String> allActions = actionsGroups.stream()
                                               .flatMap(List::stream)
                                               .collect(Collectors.toList());
        Set<String> allDistinctActions = new HashSet<>(allActions);
        allActions = new ArrayList<>(allDistinctActions);
        Collections.sort(allActions);
        model.actions = allActions;
        model.maxConcurrency = actionsGroups.stream()
                                            .max((a, b) -> a.size() - b.size())
                                            .get().size();
    }

    @Override
    public Model visitInitBlock(spuddParser.InitBlockContext ctx) {
        for (spuddParser.DtreeContext dtree : ctx.dtree()) {
            setVariableInitValue(dtree);
        }
        return model;
    }

    public void setVariableInitValue(spuddParser.DtreeContext ctx) {
        String varName = ctx.node().getText();
        model.variables.put(varName, (int)Float.parseFloat(ctx.left.left.node().getText()));
    }

    @Override
    public Model visitVariable(spuddParser.VariableContext ctx) {
        model.variables.put(ctx.ID().getText(), 0);
        return model;
    }

    @Override
    public Model visitRewardBlock(spuddParser.RewardBlockContext ctx) {
        return model;
    }

    @Override
    public Model visitDiscount(spuddParser.DiscountContext ctx) {
        return model;
    }

    @Override
    public Model visitHorizon(spuddParser.HorizonContext ctx) {
        model.horizon = Integer.parseInt(ctx.val.INT().getText());
        return model;
    }
}
