package com.ndt;

public class Builder extends spuddBaseVisitor<Model> {
    private Model model;

    @Override
    public Model visitInit(spuddParser.InitContext ctx) {
        model = new Model();

        for (spuddParser.ConfigContext config : ctx.config()) {
            visit(config);
        }

        visitVariablesBlock(ctx.variablesBlock());
        visitInitBlock(ctx.initBlock());

        return model;
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
