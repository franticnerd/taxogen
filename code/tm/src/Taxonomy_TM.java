
import cc.mallet.util.*;
import cc.mallet.types.*;
import cc.mallet.pipe.*;
import cc.mallet.pipe.iterator.*;
import cc.mallet.topics.*;

import java.util.*;
import java.util.regex.*;
import java.io.*;

public class Taxonomy_TM {

    public static void main(String[] args) throws Exception {

        // Begin by importing documents from text to feature sequences
        ArrayList<Pipe> pipeList = new ArrayList<Pipe>();

        // Pipes: lowercase, tokenize, remove stopwords, map to features
        pipeList.add( new CharSequenceLowercase() );
        pipeList.add( new CharSequence2TokenSequence(Pattern.compile("\\p{L}[\\p{L}\\p{P}]+\\p{L}")) );
        pipeList.add( new TokenSequenceRemoveStopwords(new File("/Users/taofangbo/Documents/mallet-2.0.8/stoplists/en.txt"), "UTF-8", false, false, false) );
        pipeList.add( new TokenSequence2FeatureSequence() );

        InstanceList instances = new InstanceList (new SerialPipes(pipeList));

        Reader fileReader = new InputStreamReader(new FileInputStream(new File("/Users/taofangbo/Documents/workspace/local-embedding/data/paper_phrases.txt.frequent.hardcode.long50k")), "UTF-8");
        instances.addThruPipe(new CsvIterator (fileReader, Pattern.compile("^(\\S*)[\\s,]*(\\S*)[\\s,]*(.*)$"),
                                               3, 2, 1)); // data, label, name fields

        
        // hierarchical LDA
        Randoms random = new Randoms();
        HierarchicalLDA hlda = new HierarchicalLDA();
        hlda.initialize(instances, null, 3, random);
        hlda.setAlpha(10000);
        hlda.setTopicDisplay(50, 15);
        hlda.estimate(500);
        hlda.printState(new PrintWriter("/Users/taofangbo/Documents/workspace/local-embedding/data/hlda"));
        System.out.println("HPAM\n\n\n");
        
        // hierarchical pam
        HierarchicalPAM lpam = new HierarchicalPAM(5, 5, 1.0, 1.0);
        lpam.estimate(instances, null, 300, 50, 0, 0, "/Users/taofangbo/Documents/workspace/local-embedding/data/hpam", random);
        lpam.printTopWords(15, true);
        
    }

}
