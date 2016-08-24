package com.ndt;

import com.ndt.builder.Builder;
import com.ndt.builder.Model;
import com.ndt.parser.spuddLexer;
import com.ndt.parser.spuddParser;
import org.antlr.v4.runtime.ANTLRFileStream;
import org.antlr.v4.runtime.ANTLRInputStream;
import org.antlr.v4.runtime.CommonTokenStream;

import java.io.IOException;

public class Main {

    public static void main(String[] args) {
        try {
            ANTLRInputStream inputStream = new ANTLRFileStream(args[0]);
            spuddLexer lexer = new spuddLexer(inputStream);
            CommonTokenStream tokenStream = new CommonTokenStream(lexer);
            spuddParser parser = new spuddParser(tokenStream);
            spuddParser.InitContext init = parser.init();

            Builder builder = new Builder();
            Model model = builder.visit(init);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
