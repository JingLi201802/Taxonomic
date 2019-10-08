import java.net.URL;
import java.util.ArrayList;

public class test {
    public static void main(String[] args) throws Exception {
        StringBuffer sb = new StringBuffer();
        String filePath = "/Users/feone/IdeaProjects/accuracy_Test/src/inputTestSample";
        spider.readFile(sb, filePath);
        String testData = sb.toString();
        String[] allData = testData.split("\n");

        ArrayList<String> testSet = new ArrayList<>();
        ArrayList<String> arr = new ArrayList<>();

        for (int i = 0; i < allData.length; i++) {
            testSet.add(allData[i]);
        }

        for (int i = 0; i < testSet.size(); i++) {
            String search1 = "https://biodiversity.org.au/nsl/services/search?product=APNI&tree.id=&name=";
            String search2 = "&inc._scientific=&inc.scientific=on&inc._cultivar=&inc._other=&max=100&display=apni&search=true";
            String target = testSet.get(i);
            String link = search1 + target + search2;
            System.out.println(link);
            URL url = new URL(link);
            spider.getConnect(link);
            spider.find();

            for (int j = spider.outputHeadingIndex; j < spider.outputBodyIndex; j++) arr.add(spider.allInfo.get(j));

            //System.out.println(arr);
            System.out.println("------------------------------------------------------------------------------------------------------------------------");
            String tags = spider.findStringTags(arr);
            if (tags.equals("")){
                System.out.println("No result found, please check your in put");
            }else {
                System.out.println(tags);
            }

            System.out.println("------------------------------------------------------------------------------------------------------------------------");

        }
    }
}
