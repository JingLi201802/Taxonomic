import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.ArrayList;
import java.util.HashMap;

/**
 * URLs: "https://biodiversity.org.au/nsl/services/APC"; "https://biodiversity.org.au/nsl/services/APNI";
 */

public class spider {
    public static String link = "";

    public static ArrayList<String> allInfo = new ArrayList<>();// store all information in the website (not analysis)

    public static String searchBox = "";

    public static int sbIndex = 0; //search box index in allInfo

    public static String outputNo = ""; //find number of return results, depends on key word "panel panel-info" (include head and body)

    public static int outputNoIndex = 0; // the number of return results

    //public static String output = ""; // return detail

    //public static int outputIndex = 0;

    public static String outputHeading = ""; //output heading include: "No result yet" or search result

    public static int outputHeadingIndex = 0; //the index of "panel-info" in allInfo

    public static String outputBody = ""; //output body include research result in "result" class in the page

    public static int outputBodyIndex = 0; //the index of "panel-body" in allInfo

    public static HashMap<Integer, Integer> range = new HashMap<>(); // store search box and output result start and end index

    /**
     * connect the the target search engine (https://biodiversity.org.au/nsl/services/APNI)
     * @param destination
     * @throws IOException
     */
    public static void getConnect(String destination) throws IOException {

        HttpURLConnection connection = null;
        URL url = null;
        InputStream in = null;
        BufferedReader reader = null;
        StringBuffer stringBuffer = null;

        try {
            url = new URL(destination);

            connection = (HttpURLConnection) url.openConnection();
            connection.setConnectTimeout(5000);
            connection.setReadTimeout(5000);
            connection.setDoInput(true);
            connection.connect();

            in = connection.getInputStream();
            reader = new BufferedReader(new InputStreamReader(in));
            stringBuffer = new StringBuffer();
            String line = null;

            while ((line = reader.readLine()) != null){
                stringBuffer.append(line);
                allInfo.add(line);
                //System.out.println(line);
            }
        }catch (Exception e){
            e.printStackTrace();
        }finally {
            connection.disconnect();

            try{
                in.close();
                reader.close();
            }catch (Exception e){
                e.printStackTrace();
            }
        }

        //String rtn = stringBuffer.toString();
        //System.out.println(rtn);
        //return rtn;
    }

    /**
     * find search box and output index
     */
    public static void find(){

        for (String x: allInfo) {

            if (x.contains("placeholder=\"Enter a name\"")){
                searchBox = x;
                sbIndex = allInfo.indexOf(x);
            }

            if (x.contains("class=\"panel-heading\"")){
                outputHeading = x;//now get the output start position, find the end symbol (</div>) to get the full output
                outputHeadingIndex = allInfo.indexOf(x);
            }

            if (x.contains("class=\"panel-body\"")){
                outputBody = x;
                outputBodyIndex = allInfo.indexOf(x);
            }
        }
    }


    /**
     * Find pair tags in HTML.
     * HTML structure is like
     * <div>
     *   <div></div>
     *   <div>
     *       <div></div>
     *   </div>
     * </div>
     * This function is for find all required information between start <div>  and end </div>
     */
    public static int findEndTags(int startPoint){
        if (startPoint <=0 || startPoint > allInfo.size()) return 0;
        int count = 1;
        int index = startPoint;
        while (count != 0){
            index++;
            if (allInfo.get(index).contains("<div")){
                count+=1;
            }
            if (allInfo.get(index).contains("</div>")){
                count -=1;
            }
        }
        return index;
    }


    /**
     * read the file, and find all data.
     * @param buffer
     * @param filePath
     * @throws Exception
     */
    public static void readFile(StringBuffer buffer, String filePath) throws Exception{
        try {
            File f = new File(filePath);
            if (f.isFile() && f.exists()) {
                InputStreamReader isr = new InputStreamReader(new FileInputStream(f));
                String line;
                BufferedReader reader = new BufferedReader(isr);
                line = reader.readLine();
                while (line != null) {
                    buffer.append(line);
                    buffer.append("\n");
                    line = reader.readLine();
                }
                reader.close();
            }else {
                System.out.println("Cannot find the file");
            }
        }catch (Exception e){
            System.out.println("Error detected");
            e.printStackTrace();
        }
    }

    /**
     * analysis the output and delete HTML tags
     */
    public static void parser(){

    }


    public static void main(String[] args) throws IOException {
        String search1 = "https://biodiversity.org.au/nsl/services/search?product=APNI&tree.id=&name=";
        String search2 = "&inc._scientific=&inc.scientific=on&inc._cultivar=&inc._other=&max=100&display=apni&search=true";
        String target = "";
        link = search1 + target + search2;
        URL url = new URL(link);
        getConnect(link);
        find();

        //for (String x: allInfo) System.out.println(x);
        System.out.println("sbIndex: " + sbIndex);
        System.out.println("SearchBox output: " + searchBox);
        //System.out.println(outputNoIndex);
        System.out.println("outputHeading return: " + outputHeading);
        System.out.println("outputHeadingIndex: " + outputHeadingIndex);
        System.out.println("outputBody: " + outputBody);
        System.out.println("outputBodyIndex: " + outputBodyIndex);
        System.out.println("allInfo size: " + allInfo.size());
        System.out.println("range size: " + range.size());
        System.out.println("range return: " + range);

        System.out.println("-------------------------------------------------------------------------------");
        int end = findEndTags(outputBodyIndex);
        for (int i = 667; i < 685; i++) {
            System.out.println(allInfo.get(i));
        }
        System.out.println("try to get full information, start at: " + outputBodyIndex + ", end at: " + end);
    }
}
