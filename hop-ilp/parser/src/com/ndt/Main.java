package com.ndt;

import com.google.gson.Gson;
import com.google.gson.GsonBuilder;
import com.ndt.builder.Model;
import com.ndt.builder.ModelBuilder;
import com.ndt.parser.spuddLexer;
import com.ndt.parser.spuddParser;
import org.antlr.v4.runtime.ANTLRFileStream;
import org.antlr.v4.runtime.ANTLRInputStream;
import org.antlr.v4.runtime.CommonTokenStream;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;

public class Main {

    public static void main(String[] args) {
        if (args.length < 2) {
            System.out.println("Usage: java -jar parser.jar <input_file> <output_dir|output_file>");
            return;
        }
        try {
            System.out.println("Parsing input file");
            String inputPath = args[0];
            ANTLRInputStream inputStream = new ANTLRFileStream(inputPath);
            spuddLexer lexer = new spuddLexer(inputStream);
            CommonTokenStream tokenStream = new CommonTokenStream(lexer);
            spuddParser parser = new spuddParser(tokenStream);
            spuddParser.InitContext init = parser.init();

            Gson gson = new GsonBuilder().setPrettyPrinting().create();
            ModelBuilder modelBuilder = new ModelBuilder();
            Model model = modelBuilder.visit(init);

            String inputFileName;
            int index = inputPath.lastIndexOf('.');
            if (index == -1) {
                inputFileName = inputPath.substring(inputPath.lastIndexOf('/') + 1);
            } else {
                inputFileName = inputPath.substring(inputPath.lastIndexOf('/') + 1, index);
            }
            File outputFile = new File(args[1]);
            if (outputFile.isDirectory()) {
                outputFile = new File(outputFile.getCanonicalPath() + "/" +  inputFileName + ".json");
            }
            System.out.println("Writing to " + outputFile.getAbsolutePath());
            FileWriter fileWriter = new FileWriter(outputFile);
            gson.toJson(model, fileWriter);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}
