package com.ndt;

import com.google.gson.Gson;
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
            String inputPath = args[0];
            Model model = parseModel(inputPath);
            File outputFile = getOutputFile(args[1], inputPath);
            writeToJson(model, outputFile);
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void writeToJson(Model model, File outputFile) throws IOException {
        System.out.println("Writing to " + outputFile.getAbsolutePath());
        FileWriter fileWriter = new FileWriter(outputFile);
        Gson gson = new Gson();
        gson.toJson(model, fileWriter);
        fileWriter.close();
    }

    private static File getOutputFile(String outputPath, String inputPath) throws IOException {
        String inputFileName;
        int index = inputPath.lastIndexOf('.');
        if (index == -1) {
            inputFileName = inputPath.substring(inputPath.lastIndexOf('/') + 1);
        } else {
            inputFileName = inputPath.substring(inputPath.lastIndexOf('/') + 1, index);
        }
        File outputFile = new File(outputPath);
        if (outputFile.isDirectory()) {
            outputFile = new File(outputFile.getCanonicalPath() + "/" +  inputFileName + ".json");
        }
        return outputFile;
    }

    private static Model parseModel(String inputPath) throws IOException {
        System.out.println("Parsing " + inputPath);
        ANTLRInputStream inputStream = new ANTLRFileStream(inputPath);
        spuddLexer lexer = new spuddLexer(inputStream);
        CommonTokenStream tokenStream = new CommonTokenStream(lexer);
        spuddParser parser = new spuddParser(tokenStream);
        spuddParser.InitContext init = parser.init();

        ModelBuilder modelBuilder = new ModelBuilder();
        return modelBuilder.visit(init);
    }
}
